import asyncio
import sys
import traceback

import streamlit as st

from arguments_parser import Params, parse
from dashboard.page1 import factory_dashboard
from dashboard.page2 import production_work_history_view
from dashboard.page3 import factory_chatbot

PAGE1 = '全体状況'
PAGE2 = '製造ライン作業履歴'
PAGE3 = '製造ライン情報Chatbot'


async def main(param: Params):
    st.set_page_config(
        page_title='manufacturing-line-dashboard-with-surrealdb',
        layout='wide',
    )

    selected_menu = st.sidebar.radio("メニュー", [PAGE1, PAGE2, PAGE3])
    st.sidebar.markdown('---')

    if selected_menu == PAGE1:
        await factory_dashboard.run(param)

    elif selected_menu == PAGE2:
        await production_work_history_view.run(param)

    elif selected_menu == PAGE3:
        await factory_chatbot.run(param)

    else:
        pass


if __name__ == '__main__':
    # [引数]
    #    [--server localhost]                           SurrealDB ホスト名
    #    [--prot 8000]                                  SurrealDB ポート番号
    #    [--namespace test]                             SurrealDB 名前空間名
    #    [--database test]                              SurrealDB データベース名
    #    [--user root]                                  SurrealDB 認証ユーザ
    #    [--PW root]                                    SurrealDB 認証ユーザ パスワード
    args = sys.argv
    param = parse(args=args[1:])
    asyncio.run(main(param))
