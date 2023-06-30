import datetime
import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain import PromptTemplate, LLMChain, OpenAI
from openai import InvalidRequestError

import openai
import streamlit as st
from openai.error import APIConnectionError, AuthenticationError
from streamlit_chat import message

from arguments_parser import Params
from dashboard.page3.prompt import CONVERT_NL_TO_SURREALQL_PROMPT_jp, CONVERT_NL_TO_SURREALQL_PROMPT_en, \
    CONVERT_NL_TO_SURREALQL_MESSAGES_jp, ANALYZE_RESPONSE_PROMPT_jp
from helper.factory_db_helper import FactoryDBHelper

load_dotenv()

# APIキーの設定
openai.api_key = os.environ.get("OPENAI_KEY", "")
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_KEY", "")


API_TIMEOUT = 10


def query(
        payload: Any,
        prompt_lang='日本語'
) -> Any:
    """
    OpenAI API GTP-3.5 による 日本語からSurrealQL生成
    :param payload: 入力データ
    :param prompt_lang: プロンプトの言語指定
    :return: GTPからの結果
    """

    prompt = CONVERT_NL_TO_SURREALQL_PROMPT_jp if prompt_lang == '日本語' else CONVERT_NL_TO_SURREALQL_PROMPT_en
    prompt += "\n#" + payload.get("inputs", {}).get("text", "?")
    try:
        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0,
            timeout=API_TIMEOUT,
        )
        sql = completions.choices[0].text
    except (APIConnectionError, AuthenticationError) as e:
        print(f'{e}')
        sql = ""
    return {
        'generated_text': sql,
    }


def query4(
        payload: Any,
        prompt_lang='日本語'
) -> Any:
    """
    OpenAI API GTP-4 による 日本語からSurrealQL生成
    :param payload: 入力データ
    :param prompt_lang: プロンプトの言語指定
    :return: GPTからの結果
    """

    messages = CONVERT_NL_TO_SURREALQL_MESSAGES_jp.copy()
    messages.append({
        "role": "user",
        "content": payload.get("inputs", {}).get("text", "?")
    })

    try:
        completions = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            timeout=API_TIMEOUT,
        )
        sql = completions.choices[0].message.content
    except (APIConnectionError, AuthenticationError) as e:
        print(f'{e}')
        sql = ''

    return {
        'generated_text': sql,
    }


def create_response_message(
        response_from_db: Any,
        user_input: str,
        additional_input: str = '',
) -> str:
    """
    GTP-3.5 による SurrealDBの問合せ結果を日本語化する
    :param response_from_db: DBからの結果
    :param user_input: 質問文
    :param additional_input: 追加の情報
    :return: GTPからの結果
    """
    try:
        template = ANALYZE_RESPONSE_PROMPT_jp
        prompt2 = PromptTemplate(
            template=template,
            input_variables=["additional", "question", "result"]
        )
        analyze_result_chain = LLMChain(
            llm=OpenAI(
                model_name="text-davinci-003",
                max_tokens=1000,
                n=1,
                temperature=0.5,
            ),
            prompt=prompt2,
        )
        json_result = json.dumps(response_from_db)

        s = datetime.datetime.now()
        print(f'started: OpenAI Completion API for analyze response')
        final_result = analyze_result_chain.predict(
            question=user_input,
            result=json_result,
            additional=additional_input
        )
        e = datetime.datetime.now()
        print(f'ended: OpenAI Completion API for analyze response {e - s}')
    except TimeoutError as e:
        final_result = 'OpenAI API was Timeout'
        print(f'OpenAI Completion API error {e}')
    except InvalidRequestError as e:
        final_result = f'{e}'
    except (APIConnectionError, AuthenticationError) as e:
        final_result = f'{e}'
    return final_result


async def run(param: Params):

    st.header("製造ライン情報検索")
    st.sidebar.text('設定')
    view_result = st.sidebar.checkbox('DB問合せ結果表示')

    container1 = st.container()
    container2 = st.container()

    with FactoryDBHelper(
            url=param.url,
            username=param.user,
            password=param.pw,
            database=param.database,
            namespace=param.namespace,
    ) as client:

        if 'generated' not in st.session_state:
            st.session_state['generated'] = []
        if 'past' not in st.session_state:
            st.session_state['past'] = []
        container1.write('##### 問合せ')
        user_input = container1.text_area(
            label="query",
            value='',
            key="input",
            label_visibility='collapsed'
        )
        entered = container1.button("問合せ実行")
        if entered and len(user_input) > 0:
            s = datetime.datetime.now()

            print(f'started: OpenAI Completion API for query')
            try:
                output = query4(
                    {
                        "inputs": {
                            "past_user_inputs": st.session_state.past,
                            "generated_responses": st.session_state.generated,
                            "text": user_input,
                        },
                        "parameters": {
                            "repetition_penalty": 1.33
                        },
                    }
                )
            except TimeoutError as e:
                output["generated_text"] = ""
                print(f'OpenAI Completion API error {e}')

            e = datetime.datetime.now()
            print(f'ended: OpenAI Completion API for query {e - s}')
            sql = output["generated_text"]
            if len(sql) > 0:
                result = await client.exec_sql(sql=sql)
                final_result = create_response_message(
                    response_from_db=result,
                    user_input=user_input
                )
            else:
                final_result = 'SurrealQLが生成できません'
            st.session_state.past.append(user_input)
            container1.write('##### 生成されたSurrealQL')
            container1.text_area(
                label='sql',
                value=f'{sql}',
                label_visibility='collapsed'
            )
            st.session_state.generated.append(final_result)
            if view_result:
                container1.write('##### 問合せ結果')
                container1.text(f'{json.dumps(result, indent=2)}')

            # チャット履歴表示
            with container2:
                container2.write('---  ')
                container2.write('##### チャット')
                if st.session_state['generated']:
                    for i in range(len(st.session_state['generated']) - 1, -1, -1):
                        message(st.session_state["generated"][i], key=str(i))
                        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

