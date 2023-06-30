from enum import IntEnum
from typing import Any

import streamlit as st

from pyecharts import options as opts
from pyecharts.charts import Graph

from dashboard.factory_session_state_cache import FactoryDataCache, get_production_lines, get_machines, get_products, \
    get_storages, get_factory, get_works, get_working_teams, get_result_info, get_defect_info, get_raw_materials, \
    get_relationships_from_cache, get_node_name
from dashboard.page2.production_line_data_cache import SidebarParameter
from helper.factory_db_helper import FactoryDBHelper
from simulator.factory_models import FactoryNodeTable, WorkType, ProductStatus, ProductType


class FactoryCategory(IntEnum):
    FACTORY = 0,
    PRODUCTION_LINE = 1,
    MACHINE = 2,
    STORAGE = 3,
    PRODUCT = 4,
    WORK = 5,
    INSPECTION_RESULT = 6,
    DEFECT_INFORMATION = 7,
    WORKING_TEAM = 8,
    RAW_MATERIAL = 9,
    TRANSFER = 10,


CATEGORY_MAP = {
    FactoryNodeTable.FACTORY.name: FactoryCategory.FACTORY.value,
    FactoryNodeTable.PRODUCTION_LINE.name: FactoryCategory.PRODUCTION_LINE.value,
    FactoryNodeTable.PRODUCT.name: FactoryCategory.PRODUCT.value,
    FactoryNodeTable.STORAGE.name: FactoryCategory.STORAGE.value,
    FactoryNodeTable.WORK.name: FactoryCategory.WORK.value,
    FactoryNodeTable.INSPECTION_RESULT.name: FactoryCategory.INSPECTION_RESULT.value,
    FactoryNodeTable.DEFECT_INFORMATION.name: FactoryCategory.DEFECT_INFORMATION.value,
    FactoryNodeTable.OPERATING_CREW.name: FactoryCategory.WORKING_TEAM.value,
    FactoryNodeTable.RAW_MATERIAL.name: FactoryCategory.RAW_MATERIAL.value,
    FactoryNodeTable.MACHINE.name: FactoryCategory.MACHINE.value,
    FactoryNodeTable.MANUFACTURER.name: -1,
    FactoryNodeTable.MEASUREMENTS.name: -1,
    'TRANSFER': FactoryCategory.TRANSFER.value,
}

# The markup types provided by ECharts include 'circle', 'rect', 'roundRect', 'triangle',
# 'diamond', 'pin', 'arrow', 'none'
FACTORY_NODE_CATEGORIES = [
    {
        'name': '工場(Factory)',
        'symbol': 'roundRect',
    },
    {
        'name': '製造ライン(Production Line)',
        'symbol': 'roundRect',
    },
    {
        'name': '機器(Machine)',
        'symbol': 'roundRect',
    },
    {
        'name': '貯蔵庫(Storage)',
        'symbol': 'roundRect',
    },
    {
        'name': '仕掛品(Product)',
    },
    {
        'name': '作業(Work)',
        'symbol': 'diamond',
    },
    {
        'name': '検査結果(Result)',
    },
    {
        'name': '欠陥情報(Defect)',
    },
    {
        'name': '作業班(Team)',
        'symbol': 'roundRect',
    },
    {
        'name': '原材料(Raw_material)',
        'symbol': 'roundRect',
    },
    {
        'name': '移動作業(Transfer work)',
        'symbol': 'triangle',
    },
]

_COLORS = [
    '#ADD8E6',  # lightblue
    '#E6E6FA',  # lavender
    '#F5F5F5',  # whitesmoke
    '#FFFAFA',  # snow
    '#FFFACD',  # lemonchiffon
]
_BG_COLOR = _COLORS[3]


def get_node_category(
        node_id: str,
        factory_data_cache: FactoryDataCache,
) -> int:
    if node_id.split(':')[0] == FactoryNodeTable.WORK.name:
        node = factory_data_cache.find_node(node_id=node_id)
        if node.get('data', {}).get('type', '') == WorkType.TransferWork.name:
            category = CATEGORY_MAP.get('TRANSFER')
        else:
            category = CATEGORY_MAP.get(node_id.split(':')[0], -1)
    else:
        category = CATEGORY_MAP.get(node_id.split(':')[0], -1)
    return category


async def create_factory_data_cache(client: FactoryDBHelper) -> FactoryDataCache:
    return FactoryDataCache(
        production_lines=await get_production_lines(client=client),
        machines=await get_machines(client=client),
        products=await get_products(client=client),
        storages=await get_storages(client=client),
        factories=await get_factory(client=client),
        works=await get_works(client=client),
        working_teams=await get_working_teams(client=client),
        inspection_results=await get_result_info(client=client),
        defect_info=await get_defect_info(client=client),
        raw_materials=await get_raw_materials(client=client),
        relationships=await get_relationships_from_cache(client=client)
    )


async def show_product_operation_graph(
        sidebar_parameter: SidebarParameter,
        client: FactoryDBHelper,
        height: str = "1000px",
        width: str = "auto",
) -> Any:
    """
    指定された製品とその作業の関係のデータグラフを表示する
    :param sidebar_parameter: 選択された製品情報
    :param client: SurrealDB Helper
    :param height: グラフデータの高さ
    :param width: グラフデータの幅
    :return:
    """

    if 'factory_data_cache' not in st.session_state:
        factory_data_cache = await create_factory_data_cache(client=client)
        st.session_state.factory_data_cache = factory_data_cache
    factory_data_cache = st.session_state.factory_data_cache

    nodes_data = []
    links_data = []
    relationships = []
    nodes = []
    traverse_nodes = []

    if not sidebar_parameter.all_wip:
        relationships, nodes, traverse_nodes = \
            await client.get_relationships_of_node(node_id=sidebar_parameter.wip)

    for node in nodes:
        nodes_data.append(
            opts.GraphNode(
                name=node,
                symbol_size=30,
                category=get_node_category(
                    node_id=node,
                    factory_data_cache=factory_data_cache
                ),
                label_opts=opts.LabelOpts(
                    is_show=True,
                    formatter=get_node_name(
                        node_id=node,
                        factory_data_cache=factory_data_cache,
                        is_show_node_id=sidebar_parameter.is_show_node_id,
                    )
                )
            ))

    for relationship in relationships:
        label_name = relationship.get("id", "?").split(':')[0]
        source = relationship.get('in', '')
        target = relationship.get('out', '')
        links_data.append(
            opts.GraphLink(
                source=source,
                target=target,
                label_opts=opts.LabelOpts(
                    is_show=True,
                    #font_size=10,
                    position="middle",
                    formatter=f'{label_name}'
                )
            )
        )

    wip_product = sidebar_parameter.wip.split(":")[0]
    wip_id = sidebar_parameter.wip.split(":")[1]
    wip_node = factory_data_cache.find_node(node_id=sidebar_parameter.wip)
    wip_type = '製品' if wip_node.get("data", {}).get("type", "") == ProductType.PRODUCT.name else '部品'
    match wip_node.get('data', {}).get('status'):
        case ProductStatus.FINISHED_PRODUCT.name:
            wip_status = '完了'
        case ProductStatus.WORK_IN_PROGRESS.name:
            wip_status = '仕掛中'
        case ProductStatus.DEFECT_DETECTION.name:
            wip_status = '欠陥検出'
        case _:
            wip_status = '?'
    g = Graph(
        init_opts=opts.InitOpts(
            height=height,
            width=width,
            bg_color=_BG_COLOR
        )
    )
    g.add(
        "",
        nodes_data,
        links_data,
        categories=FACTORY_NODE_CATEGORIES,
        repulsion=4000,
        layout=sidebar_parameter.layout_type,
        edge_length=2,
        is_draggable=True,
        edge_symbol=['', 'arrow'],
        linestyle_opts=opts.LineStyleOpts(curve=0.2),
        gravity=0.8,
        is_layout_animation=True,
    )
    g.set_global_opts(
        title_opts=opts.TitleOpts(title=f'仕掛品：{wip_id}'),
        legend_opts=opts.LegendOpts(
            orient='right',
            align='right',
            pos_right=0,
            pos_bottom=0,
            is_show=sidebar_parameter.is_show_legend
        ),
        tooltip_opts=opts.TooltipOpts(
            is_show=True,
            trigger_on='click'
        ),
        datazoom_opts=[
        ],
    )
    html = g.render_embed()
    return html
