import datetime
import os
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Union, List, Optional

import streamlit as st
from matplotlib import pyplot as plt, ticker

import util
from arguments_parser import Params
from helper.factory_db_helper import FactoryDBHelper

# Matplotlibで使用するフォント名
FONT_NAME = 'Meiryo'

# 歩留率 ※デモ用のため値そものに意味はない
YIELD_RATE = 0.9

# 計画製造数 ※デモ用のため値そのものに意味はない
KEIKAKU = 100

PRODUCTION_LINE_IDS = [
    'PRODUCTION_LINE:pl001',
    'PRODUCTION_LINE:pl002',
    'PRODUCTION_LINE:pl003',
    'PRODUCTION_LINE:pl004',
    'PRODUCTION_LINE:pl005',
    'PRODUCTION_LINE:pl006',
]

# 部品 先頭工程識別子
PARTS_FIRST_PROCESS = 'PRODUCTION_LINE:pl001'

# 部品 最終工程識別子
PARTS_LAST_PROCESS = 'PRODUCTION_LINE:pl003'

# 製品 先頭工程識別子
PRODUCT_FIRST_PROCESS = 'PRODUCTION_LINE:pl004'

# 製品 最終工程識別子
PRODUCT_LAST_PROCESS = 'PRODUCTION_LINE:pl006'


@dataclass
class ProductionLineStatus:
    production_line: str
    input_products: int
    output_products: int
    defect_products: int
    defect_delta: int
    list_data: List[int]


def show_production_line_status(
        production_line_status: List[ProductionLineStatus]
) -> None:
    """
    製造ライン状況表示
    :param production_line_status: 製造ライン情報
    :return:
    """
    parts_production_lines = ['pl001', 'pl002', 'pl003']
    product_production_lines = ['pl004', 'pl005', 'pl006']

    total_parts_output_products = \
        sum([data.output_products for data in production_line_status if data.production_line == 'pl003'])
    total_parts_defect_products = \
        sum([data.defect_products for data in production_line_status if data.production_line in parts_production_lines])
    total_parts_input_products = total_parts_output_products + total_parts_defect_products

    defect_delta = int(
        total_parts_input_products * (1.0 - (YIELD_RATE * YIELD_RATE * YIELD_RATE))) - total_parts_defect_products
    defect_delta = 0 if defect_delta > 0 else defect_delta
    total_parts_production_line_status = ProductionLineStatus(
        production_line='SP1 部品 製造実績',
        input_products=total_parts_input_products,
        output_products=total_parts_output_products,
        defect_products=total_parts_defect_products,
        defect_delta=defect_delta,
        list_data=[
            total_parts_output_products,
            0,
            total_parts_defect_products
        ],
    )

    total_output_products = \
        sum([data.output_products for data in production_line_status if data.production_line == 'pl006'])
    total_defect_products = \
        sum([data.defect_products for data in production_line_status if
             data.production_line in product_production_lines])
    total_input_products = total_output_products + total_defect_products
    defect_delta = int(total_input_products * (1.0 - (YIELD_RATE * YIELD_RATE * YIELD_RATE))) - total_defect_products
    defect_delta = 0 if defect_delta > 0 else defect_delta

    total_production_line_status = ProductionLineStatus(
        production_line='SP2 製品 製造実績',
        input_products=total_input_products,
        output_products=total_output_products,
        defect_products=total_defect_products,
        defect_delta=defect_delta,
        list_data=[
            total_output_products,
            0,
            total_defect_products
        ],
    )

    # 部品製造ラインの全体状況
    show_manufacturing_metrics(
        total_parts_production_line_status,
        yield_rate=YIELD_RATE * YIELD_RATE * YIELD_RATE,
        title='SP1部品 製造実績',
    )

    # 製品製造ラインの全体状況
    show_manufacturing_metrics(
        total_production_line_status,
        yield_rate=YIELD_RATE * YIELD_RATE * YIELD_RATE,
        title='SP2製品 製造実績',
    )


def show_manufacturing_metrics(
        data: ProductionLineStatus,
        title: Optional[str] = None,
        yield_rate: float = YIELD_RATE,
        keikaku: int = KEIKAKU,
) -> None:
    """
    製造データ メトリック表示
    :param title:
    :param data: 製造ラインデータ
    :param yield_rate: 歩留率
    :param keikaku: 製造計画数
    :return:
    """
    container = st.container()
    cols = container.columns((3, 3, 7), gap='medium')
    sub_cols = cols[2].columns((3, 3, 3, 3), )

    # 作業実績円グラフ
    show_pie_chart(
        col=cols[0],
        list_data=data.list_data,
        labels=['合格品', '仕掛中', '欠陥品'],
        colors=["lime", "blue", "orange", ],
        title=f'製造ライン {data.production_line} 実績' if not title else title,
    )

    # 製造進捗率円グラフ
    show_pie_chart(
        col=cols[1],
        list_data=[data.output_products, keikaku - data.output_products],
        labels=['実績', '残'],
        colors=['lime', 'darkgray'],
        title=f'製造進捗率(実績/計画)',
        pctdistance=1.17,
    )

    # 製造ラインへ入力された仕掛品数
    show_metric(
        sub_cols[0],
        label=f'入力',
        value=f'{data.input_products} 個'
    )

    # 製造ラインから検査合格した仕掛品数
    show_metric(
        sub_cols[1],
        label=f'出力',
        value=f'{data.output_products} 個'
    )

    # 検査で欠陥が検知された仕掛品数
    show_metric(
        sub_cols[2],
        label=f'欠陥品',
        value=f'{data.defect_products} 個',
        delta=data.defect_delta,
    )

    # 該当製造ラインの歩留率
    show_metric(
        sub_cols[3],
        label=f'歩留',
        value=f'{((data.output_products / (data.output_products + data.defect_products)) * 100):.1f} %',
        delta=f'{((data.output_products / (data.output_products + data.defect_products) - yield_rate) * 100):.1f} %',
    )


def show_production_time_histograms(
        title: List[str],
        labels: List[str],
        processing_times_list: List[{}]
) -> None:
    """
    製造平均時間、仕掛品の製造時間ヒストグラム、仕掛品の製造時間ヒストグラムを表示する
    :return:
    """
    col_layout = [3] * 4
    container = st.container()
    cols = container.columns(col_layout, gap='medium')
    data_list: List[List[datetime.timedelta]] = []
    for processing_times in processing_times_list:
        data_list.append(
            [processing_times[key].get('delta')
             for key in processing_times.keys() if processing_times[key].get('delta', None)]
        )

    # 製造平均時間
    show_boxplot(
        col=cols[0],
        data_list=data_list,
        labels=labels,
        title=title[0]
    )

    for i, data in enumerate(data_list):
        # 製造時間ビストグラム
        show_histogram(
            col=cols[i + 1],
            data=data,
            title=title[i + 1]
        )


def get_production_data(
        production_yield: Any
) -> List[ProductionLineStatus]:
    """
    製造ラインのデータ実績データを作成する
    :param production_yield: SurrealDBからの検索結果
    :return: 製造ライン実績データ
    """

    result: List[ProductionLineStatus] = []
    for production_data in production_yield:
        input_products = int(production_data.get("input_products_num", "-1"))
        output_products = int(production_data.get("output_products_num", "-1"))
        defect_products = int(production_data.get("defect_products_num", "-1"))
        defect_delta = int(input_products * (1.0 - YIELD_RATE)) - defect_products
        defect_delta = 0 if defect_delta > 0 else defect_delta
        list_data = [output_products, input_products - output_products, defect_products]

        result.append(
            ProductionLineStatus(
                production_line=f'{production_data.get("production_line", "?").split(":")[1]}',
                input_products=input_products,
                output_products=output_products,
                defect_products=defect_products,
                defect_delta=defect_delta,
                list_data=list_data,
            )
        )
    return result


def show_metric(
        col: Any,
        label: str,
        value: Union[int | float | str],
        delta: Union[int | float | str | None] = None,
        delta_color: str = 'normal',  # normal, inverse, off
) -> None:
    """
    メトリック表示
    :param col: streamlitのカラム
    :param label: メトリック名
    :param value: 値
    :param delta: 差分
    :param delta_color: 差分色
    :return:
    """
    col.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def show_pie_chart(
        col: Any,
        list_data: List[Union[int | float | str]],
        labels: List[str],
        colors: List[str],
        title: str = '',
        pctdistance=1.15,
) -> None:
    """
    円グラフ描画
    :param col: streamlit のカラム
    :param list_data: データ
    :param labels: データラベル
    :param colors: データ色
    :param title: グラフタイトル
    :param pctdistance: データの配置指定
    :return:
    """

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie(
        list_data,
        labels=labels,
        autopct='%1.1f%%',
        counterclock=False,
        startangle=90,
        wedgeprops={"edgecolor": "white", "width": 0.2},
        pctdistance=pctdistance,
        labeldistance=None,
        colors=colors,
    )
    ax.legend(loc='center')
    ax.set_title(title)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    col.image(buf)
    plt.close()


def show_histogram(
        col: Any,
        data: List[datetime.timedelta],
        title: str,
) -> None:
    """
    作業時間のヒストグラムを Matplotlibのhistを使用して表示する
    :param col: グラフを表示する場所(streamlitのカラム)
    :param data: 作業時間データ
    :param title: グラフ名
    :return:
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(5))
    ax.set_xlabel('時間[分]', fontsize='16')
    ax.set_ylabel('頻度[回]', fontsize='16')
    ax.set_title(title, fontsize='16')
    data = [int(d.total_seconds() / 60) for d in data]
    data.sort(reverse=False)
    ax.set_xlim(xmin=0, xmax=int(max(data) * 1.2))
    ax.hist(data, bins='auto', ec='black')
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    buf = BytesIO()
    fig.savefig(buf, format="png")
    col.image(buf)
    plt.close()


def show_boxplot(
        col: Any,
        data_list: List[List[datetime.timedelta]],
        labels: List[str],
        title: str = '',
) -> None:
    """
    平均作業時間をMatplotlib Boxplot 使用して表示する
    :param col: グラフを表示する場所(streamlitのカラム)
    :param labels: ラベル
    :param data_list: 製品製造情報
    :param title: グラフタイトル
    :return:
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    real_data: List[List[int]] = []
    for data in data_list:
        real_data.append([int(d.total_seconds() / 60) for d in data])
    ax.boxplot(real_data)
    ax.set_xticklabels(labels, fontsize='16')
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.title(title, fontsize='16')
    plt.ylabel('作業時間[分]', fontsize='16')
    buf = BytesIO()
    fig.savefig(buf, format="png")
    col.image(buf)
    plt.close()


async def get_production_duration(
        client: FactoryDBHelper
) -> ({}, {}, {}):
    """
    部品、製品の製造に費やした時間を求める
    :param client: SurrealDBヘルパ
    :return: (部品情報: {}, 製品情報: {})
    """
    all_production_lines_processing_times: {str, []} = {}

    # 部品製造工程情報を取得
    parts_processing_info = await client.get_production_time_records(
        last_process=PARTS_LAST_PROCESS,
        first_process=PARTS_FIRST_PROCESS,
    )

    # 製品製造工程情報を取得
    product_processing_info = await client.get_production_time_records(
        last_process=PRODUCT_LAST_PROCESS,
        first_process=PRODUCT_FIRST_PROCESS,
    )

    # 部品の先頭工程から最終工程までの製造時間を集計する
    parts_processing_times = calculate_production_time(
        first_process=PARTS_FIRST_PROCESS,
        last_process=PARTS_LAST_PROCESS,
        work_info=parts_processing_info,
    )

    # 製品の先頭工程から最終工程までの製造時間を集計する
    product_processing_times = calculate_production_time(
        first_process=PRODUCT_FIRST_PROCESS,
        last_process=PRODUCT_LAST_PROCESS,
        work_info=product_processing_info,
    )

    # 各製造ライン工程毎の製造時間を集計する
    for production_line_id in PRODUCTION_LINE_IDS:
        processing_info = await client.get_production_time_records(
            last_process=production_line_id,
            first_process=production_line_id,
        )
        all_production_lines_processing_times[production_line_id.split(':')[1]] = \
            calculate_production_time(
                first_process=production_line_id,
                last_process=production_line_id,
                work_info=processing_info,
            )

    return parts_processing_times, product_processing_times, all_production_lines_processing_times


def calculate_production_time(
        first_process: str,
        last_process: str,
        work_info: [],
) -> {}:
    """
    最終工程の作業終了時間と先頭製造工程の作業開始時間から製造時間を求める.
    :param first_process: 先頭工程識別子
    :param last_process: 最終工程識別子
    :param work_info: 全作業履歴情報
    :return: 仕掛品毎の製造時間情報
    """

    product_processing_times = {}
    for work in work_info:
        product_id = work.get('product_id', None)
        production_line_id = work.get('production_line_id', None)
        product_data = product_processing_times.get(product_id) \
            if product_processing_times.get(product_id, None) else {}

        if production_line_id == first_process == last_process:
            product_data['started_at'] = util.convert_utc_string_to_datetime(work.get('started_at', None))
            product_data['ended_at'] = util.convert_utc_string_to_datetime(work.get('ended_at', None))
            product_data['delta'] = product_data['ended_at'] - product_data['started_at']
        elif production_line_id == first_process:
            product_data['started_at'] = util.convert_utc_string_to_datetime(work.get('started_at', None))
        elif production_line_id == last_process:
            product_data['ended_at'] = util.convert_utc_string_to_datetime(work.get('ended_at', None))
            product_data['delta'] = product_data['ended_at'] - product_data['started_at']
        else:
            pass
        product_processing_times[product_id] = product_data
    return product_processing_times


async def get_storage_duration(
        client: FactoryDBHelper,
) -> {}:
    """
    貯蔵庫に仕掛品が滞留している時間を計算する
    :param client: FactoryDBHelper
    :return: 仕掛品貯蔵庫滞留時間
    """
    result = await client.get_transfer_work_histories()
    return calculate_storage_time(transfer_work_histories=result) if result else {}


def calculate_storage_time(
        transfer_work_histories: {}
) -> {}:
    """
    貯蔵庫に仕掛品が滞留している時間を計算する
    :param transfer_work_histories: 仕掛品移動情報
    :return: 仕掛品貯蔵庫滞留時間
    """
    storage_duration = {}
    for work in transfer_work_histories:
        x = work.get('to_id')
        storage_id = work.get('to_id') if x.startswith('STORAGE:') else work.get('from_id')
        storage_id = storage_id.split(':')[1]
        product_id = work.get('product')
        timestamp = work.get('timestamp', None)
        if storage_id not in storage_duration:
            storage_duration[storage_id] = {}
        if product_id not in storage_duration[storage_id]:
            storage_duration[storage_id][product_id] = {
                'storage_entry_time': None,
                'storage_exit_time': None,
                'delta': None,
            }
        product_data = storage_duration[storage_id][product_id]
        if work.get('to_id').startswith('STORAGE:'):
            product_data['storage_entry_time'] = util.convert_utc_string_to_datetime(timestamp) if timestamp else None
        else:
            product_data['storage_exit_time'] = util.convert_utc_string_to_datetime(timestamp) if timestamp else None
        if not product_data['delta'] and product_data['storage_entry_time'] and product_data['storage_exit_time']:
            product_data['delta'] = product_data['storage_exit_time'] - product_data['storage_entry_time']
    return storage_duration


async def run(
        param: Params
) -> None:
    """
    製造状況ダッシュボード
    :param param: 
    :return: 
    """

    # matplotlib設定
    if os.name == 'nt':
        plt.rcParams['font.family'] = FONT_NAME
    else:
        plt.rcParams['font.family'] = "IPAexGothic"

    if 'production_data' not in st.session_state:
        # 製造データをSurrealDBから取得する
        with FactoryDBHelper(
                url=param.url,
                username=param.user,
                password=param.pw,
                database=param.database,
                namespace=param.namespace,
        ) as client:
            production_yield = await client.get_production_yield()
            # measurements_values = await get_measurements_values(client=client)
            parts_processing_times, product_processing_times, all_production_lines_processing_times = \
                await get_production_duration(client=client)
            storage_duration = await get_storage_duration(client=client)

        production_data = get_production_data(production_yield=production_yield)
        st.session_state.production_data = production_data
        st.session_state.parts_processing_times = parts_processing_times
        st.session_state.product_processing_times = product_processing_times
        st.session_state.all_production_lines_processing_times = all_production_lines_processing_times
        st.session_state.storage_duration = storage_duration

    production_data = st.session_state.production_data
    if len(production_data) <= 0:
        st.write('### データが見つかりません')
        return

    parts_processing_times = st.session_state.parts_processing_times
    product_processing_times = st.session_state.product_processing_times
    all_production_lines_processing_times = st.session_state.all_production_lines_processing_times
    storage_duration = st.session_state.storage_duration
    selected_summary_view = True

    st.sidebar.write('製造ライン状況表示')
    selected_production_line = st.sidebar.selectbox(
        label='製造ライン選択',
        options=['', 'all', 'pl001', 'pl002', 'pl003', 'pl004', 'pl005', 'pl006'],
    )

    st.sidebar.write('---')
    st.sidebar.write('貯蔵庫仕掛品滞留時間表示')
    selected_storage = st.sidebar.selectbox(
        label='貯蔵庫選択',
        options=['', 'all', 'storage1', 'storage2', 'storage3', 'storage4', 'storage5']
    )

    if selected_summary_view:
        st.write("### 全体状況")
        show_production_line_status(production_data)
        show_production_time_histograms(
            title=['製造時間分布', 'SP1部品 製造時間分布', 'SP2製品 製造時間分布'],
            labels=['SP1部品', 'SP2製品'],
            processing_times_list=[parts_processing_times, product_processing_times],
        )
        st.write('---')

    if selected_production_line:
        st.session_state.production_line = selected_production_line
        st.write("### 製造ライン状況")

    for data in production_data:
        if (selected_production_line and selected_production_line == 'all') \
                or (selected_production_line and data.production_line == selected_production_line):
            st.write(f"#### 製造ライン: {data.production_line} ")
            show_manufacturing_metrics(data=data, title='製造実績')
            show_production_time_histograms(
                title=['製造時間分布', '製造時間分布'],
                labels=[data.production_line],
                processing_times_list=[all_production_lines_processing_times.get(data.production_line)],
            )
            st.write('---')

    # 貯蔵庫での仕掛品滞留時間表示
    if selected_storage:
        st.session_state.storage = selected_storage
        st.write("### 貯蔵庫仕掛品滞留時間")

    for storage_id in ['storage1', 'storage2', 'storage3', 'storage4', 'storage5']:
        storage_data = storage_duration.get(storage_id)
        if selected_storage == 'all' or storage_id == selected_storage:
            st.write(f"#### 貯蔵庫: {storage_id}")
            show_production_time_histograms(
                title=['滞留時間分布', '滞留時間分布'],
                labels=[storage_id],
                processing_times_list=[storage_data],
            )
            st.write('---')

