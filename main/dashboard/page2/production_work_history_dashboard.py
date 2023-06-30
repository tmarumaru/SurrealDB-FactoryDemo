import datetime
import os
from typing import Any, Optional

import streamlit as st
import streamlit.components.v1 as components
from matplotlib import pyplot as plt

# matplotlibで日本語表示のためのimport
# pip install japanize-matplotlib
import japanize_matplotlib

from arguments_parser import Params
from dashboard.page1.factory_dashboard import FONT_NAME
from dashboard.page2.product_operation_view import show_product_operation_graph
from dashboard.page2.production_line_data_cache import ProductionLineDataCache, SidebarParameter
from dashboard.page2.production_lines_status_view import ProductionLinesStatusView
from helper.factory_db_helper import FactoryDBHelper
from util import to_markdown_table, convert_utc_string_to_datetime


def create_md_for_product(
        column: Any,
        target_product: str,
        production_data_cache: ProductionLineDataCache,
) -> Any:
    """
    指定された仕掛品情報をmarkdownの表へ変換する
    :param column: 表示カラム
    :param target_product: 仕掛品識別子
    :param production_data_cache: 製造情報
    :return: markdownデータ
    """

    # 仕掛品の詳細情報を表示
    product_ix_info = production_data_cache.products_data['PRODUCT:' + target_product]
    product_detail = production_data_cache.products[product_ix_info.product_info_index]
    parts = product_detail.get('parts', [])
    parts_product = parts[0].split(':')[1] if len(parts) > 0 else None
    raw_materials = product_detail.get('raw_materials', [])
    rows = [
        ['仕様', f'{product_detail.get("data", {}).get("specification", "?")}'],
        ['原材料', f'{raw_materials[0].split(":")[1] if len(raw_materials) > 0 else "-"}'],
        ['構成部品', f'{parts_product if parts_product else "-"}'],
    ]
    md = to_markdown_table(rows, ['項目', '値'])
    column.markdown(md)
    column.write('')
    if target_product:
        # 仕掛品作業履歴表示
        rows = []
        for i in product_ix_info.production_histories:
            r = []
            work_history = production_data_cache.product_work_histories[i]
            r.append(work_history.get('production_line', '?').split(':')[1])
            r.append(format_datetime_str(work_history.get('started', None)))
            r.append(format_datetime_str(work_history.get('ended', None)))
            inspection_result = work_history.get('inspection_result', '?')
            r.append('合格' if inspection_result == 'OK' else '不合格')
            r.append(work_history.get('work_id', '?').split(':')[1])
            rows.append(r)
        column.write(f'#### {target_product} 作業履歴')
        md = to_markdown_table(rows, ['製造ライン', '開始', '終了', '検査結果', '識別子'])
        column.markdown(md)

        # 移動作業履歴表示
        rows = []
        for i in product_ix_info.transfer_work_histories:
            r = []
            transfer_history = production_data_cache.product_transfer_work_histories[i]
            r.append(transfer_history.get('from_id', '?').split(':')[1])
            r.append(transfer_history.get('to_id', '?').split(':')[1])
            r.append(format_datetime_str(transfer_history.get('timestamp', None)))
            r.append(transfer_history.get('work_id', '?').split(':')[1])
            rows.append(r)
        column.write(f'#### {target_product} 移動作業')
        md = to_markdown_table(rows, ['移動元', '移動先', '移動時刻', '識別子'])
        column.markdown(md)


def format_datetime_str(timestamp_str: str) -> str:
    result = ''
    if timestamp_str:
        timestamp = convert_utc_string_to_datetime(utc_string=timestamp_str)
        result = timestamp.strftime('%Y/%m/%d %H:%M')
    return result


def highlight_wip(reset: bool = False):
    """
    指定された仕掛品を強調表示する
    :param reset: True 画面初期化  False 仕掛品を強調表示
    :return:
    """
    if 'selected_product' not in st.session_state:
        return
    if 'production_data_visualizer' not in st.session_state:
        return

    production_data_visualizer = st.session_state.production_data_visualizer
    production_data_visualizer.highlight_product_production_history(
        selected_product_id=st.session_state.selected_product,
        reset=reset,
    )


def on_product_selected():
    """
    Select-Box コールバック関数
    :return:
    """
    if 'selected_product' not in st.session_state:
        return
    if 'production_data_visualizer' not in st.session_state:
        return
    highlight_wip(reset=st.session_state.selected_product == 'all')


async def run(param: Params) -> None:
    """
    仕掛品の作業履歴表示
    :return:
    """
    production_line_data_cache: ProductionLineDataCache = Optional[None]
    production_data_visualizer: ProductionLinesStatusView = Optional[None]

    # matplotlib設定
    if os.name == 'nt':
        plt.rcParams['font.family'] = FONT_NAME
    else:
        pass

    if 'ready' not in st.session_state:
        st.session_state.ready = False

    st.sidebar.markdown('製造ライン 作業状況')
    col1 = st.container()

    with FactoryDBHelper(
            url=param.url,
            username=param.user,
            password=param.pw,
            database=param.database,
            namespace=param.namespace,
    ) as client:

        if 'production_data_visualizer' not in st.session_state:
            # 製造情報を取得しキャッシュへ格納
            production_line_data_cache = await ProductionLineDataCache().build(client=client)

            # 図形要素生成
            st.session_state.production_data_visualizer = production_data_visualizer = \
                ProductionLinesStatusView(production_data_cache=production_line_data_cache)
            production_data_visualizer.build()

        production_data_visualizer = st.session_state.production_data_visualizer
        if len(production_data_visualizer.production_data_cache.products_data) <= 0:
            pass
        else:
            products_list = ['all']
            products_list.extend([p.get('id', '?').split(':')[1]
                                  for p in production_data_visualizer.production_data_cache.products])
            selected_product = st.sidebar.selectbox(
                label='仕掛品選択',
                index=0,
                options=products_list,
                key='selected_product',
                on_change=on_product_selected,
            )

            select_all_products = selected_product == 'all'

            # 表示時間帯選択スライダバー
            # 1時間ごとの日時を生成
            # X軸の最初と最後の時間の端数をそろえる
            real_start_date = production_data_visualizer.trx(x=production_data_visualizer.window.min.x)
            start_date = real_start_date - datetime.timedelta(minutes=real_start_date.minute,
                                                              seconds=real_start_date.second)
            real_end_date = production_data_visualizer.trx(production_data_visualizer.window.max.x)
            end_date = real_end_date - datetime.timedelta(minutes=real_end_date.minute, seconds=real_end_date.second)
            end_date += datetime.timedelta(minutes=30)

            # 日数を計算
            days = (end_date - start_date).days + 1
            date_list = []
            tmp_date = start_date
            while True:
                if tmp_date > end_date:
                    break
                date_list.append(tmp_date)
                tmp_date += datetime.timedelta(minutes=30, )

            # 日時をエポック秒に変換したリストを作成
            epoch_list = [d.timestamp() for d in date_list]

            # select_sliderで日時を選択
            selected_date = st.sidebar.select_slider(
                "工程状況表示の時間帯指定",
                options=epoch_list,
                value=(epoch_list[0], epoch_list[-1]),
                format_func=lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime('%H:%M'))

            # 選択された日時を表示
            st.sidebar.write("表示開始:",
                             datetime.datetime.fromtimestamp(selected_date[0], tz=datetime.timezone.utc).strftime(
                                 '%Y/%m/%d %H:%m'))
            st.sidebar.write("表示終了:",
                             datetime.datetime.fromtimestamp(selected_date[1], tz=datetime.timezone.utc).strftime(
                                 '%Y/%m/%d %H:%m'))
            st.session_state.start_date = selected_date[0]
            st.session_state.end_date = selected_date[1]
            view_x_min = st.session_state.start_date if 'start_date' in st.session_state else None
            view_x_max = st.session_state.end_date if 'end_date' in st.session_state else None

            ax = production_data_visualizer.ax
            ax.set_xlim(
                left=production_data_visualizer.trx(view_x_min),
                right=production_data_visualizer.trx(view_x_max)
            )

            with col1:
                # 製造ライン、貯蔵庫 作業履歴表示
                fig, window2 = production_data_visualizer.build()
                st.markdown('### 製造ライン作業状況')
                st.pyplot(fig)
                st.session_state.ready = True

            with col1:
                if not select_all_products:
                    st.markdown('---  ')
                    st.write('### 作業履歴')
                    # 仕掛品の詳細情報を表示
                    target_product = selected_product if not select_all_products else None
                    st.markdown(f'#### {target_product} {"仕掛品" if target_product[0] == "P" else "部品"}情報')
                    md = create_md_for_product(
                        column=col1,
                        target_product=target_product,
                        production_data_cache=production_data_visualizer.production_data_cache,
                    )

                    product_ix_info = production_data_visualizer.production_data_cache.products_data[
                        'PRODUCT:' + target_product]
                    product_detail = production_data_visualizer.production_data_cache.products[
                        product_ix_info.product_info_index]
                    parts = product_detail.get('parts', [])
                    parts_product = parts[0].split(':')[1] if len(parts) > 0 else None
                    if parts_product:
                        # 部品情報表示
                        st.markdown('---')
                        st.markdown(f'#### {parts_product} 部品情報')
                        target_product = parts_product
                        md = create_md_for_product(
                            column=col1,
                            target_product=target_product,
                            production_data_cache=production_data_visualizer.production_data_cache,
                        )

            with col1:
                if not select_all_products:
                    st.sidebar.markdown('---  ')
                    st.sidebar.write('グラフデータ表示')
                    is_show_node_id = st.sidebar.checkbox(
                        label='ノード識別子表示',
                        value=False,
                    )
                    is_show_legend = st.sidebar.checkbox(
                        label='凡例表示',
                        value=False,
                    )
                    # グラフデータ表示
                    st.markdown('---  ')
                    st.write('### グラフデータ')
                    # 指定された仕掛品関連ノードを表示
                    sidebar_parameter = SidebarParameter(
                        wip='PRODUCT:' + selected_product if not select_all_products else None,
                        layout_type='force',
                        work_node_type='選択',
                        is_show_node_id=is_show_node_id,
                        is_show_legend=is_show_legend,
                    )

                    html = await show_product_operation_graph(
                        client=client,
                        sidebar_parameter=sidebar_parameter,
                        height="1000px",
                    )
                    components.html(html, height=1200, scrolling=False)
                else:
                    st.write('---')
