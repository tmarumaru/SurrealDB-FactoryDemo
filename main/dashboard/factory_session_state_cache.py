from dataclasses import dataclass
from typing import Optional

import streamlit as st

from helper.factory_db_helper import FactoryDBHelper
from simulator.factory_models import FactoryNodeTable, ProductStatus, ProductType, WorkType, FactoryRelationship


@dataclass
class FactoryDataCache:
    production_lines: []
    machines: []
    products: []
    storages: []
    factories: []
    works: []
    working_teams: []
    inspection_results: []
    defect_info: []
    raw_materials: []
    relationships: []

    def find_node(self, node_id: str) -> {}:
        nodes = self._get_nodes(node_id=node_id)
        for node in nodes:
            if node_id == node.get('id', '?'):
                return node
        else:
            return {}

    def _get_nodes(self, node_id: str) -> {}:
        match node_id.split(':')[0]:
            case FactoryNodeTable.FACTORY.name:
                return self.factories
            case FactoryNodeTable.PRODUCTION_LINE.name:
                return self.production_lines
            case FactoryNodeTable.MACHINE.name:
                return self.machines
            case FactoryNodeTable.PRODUCT.name:
                return self.products
            case FactoryNodeTable.STORAGE.name:
                return self.storages
            case FactoryNodeTable.WORK.name:
                return self.works
            case FactoryNodeTable.INSPECTION_RESULT.name:
                return self.inspection_results
            case FactoryNodeTable.DEFECT_INFORMATION.name:
                return self.defect_info
            case FactoryNodeTable.RAW_MATERIAL.name:
                return self.raw_materials
            case FactoryNodeTable.OPERATING_CREW.name:
                return self.working_teams
            case _:
                return []


def get_table_name(s: str) -> str:
    return s[:s.index(':')]


def get_id(s: str) -> str:
    return s[s.index(':') + 1:]


async def get_production_lines(
        client: FactoryDBHelper,
) -> {}:
    if 'production_lines' not in st.session_state:
        production_lines = await client.get_all_records_from_table(table=FactoryNodeTable.PRODUCTION_LINE.name)
        st.session_state.production_lines = production_lines
    return st.session_state.production_lines


async def get_machines(
        client: FactoryDBHelper
) -> {}:
    if 'machines' not in st.session_state:
        machines = await client.get_all_records_from_table(table=FactoryNodeTable.MACHINE.name)
        st.session_state.machines = machines
    return st.session_state.machines


async def get_products(
        client: FactoryDBHelper
) -> {}:
    if 'products' not in st.session_state:
        products = await client.get_all_records_from_table(table=FactoryNodeTable.PRODUCT.name)
        st.session_state.products = products
    return st.session_state.products


async def get_storages(
        client: FactoryDBHelper
) -> {}:
    if 'storages' not in st.session_state:
        storages = await client.get_all_records_from_table(table=FactoryNodeTable.STORAGE.name)
        st.session_state.storages = storages
    return st.session_state.storages


async def get_works(
        client: FactoryDBHelper
) -> {}:
    if 'works' not in st.session_state:
        works = await client.get_all_records_from_table(table=FactoryNodeTable.WORK.name)
        st.session_state.works = works
    return st.session_state.works


async def get_working_teams(
        client: FactoryDBHelper
) -> {}:
    if 'working_teams' not in st.session_state:
        working_teams = await client.get_all_records_from_table(table=FactoryNodeTable.OPERATING_CREW.name)
        st.session_state.working_teams = working_teams
    return st.session_state.working_teams


async def get_result_info(
        client: FactoryDBHelper
) -> {}:
    if 'inspection_results' not in st.session_state:
        inspection_results = await client.get_all_records_from_table(table=FactoryNodeTable.INSPECTION_RESULT.name)
        st.session_state.inspection_results = inspection_results
    return st.session_state.inspection_results


async def get_defect_info(
        client: FactoryDBHelper
) -> {}:
    if 'defect_info' not in st.session_state:
        defect_info = await client.get_all_records_from_table(table=FactoryNodeTable.DEFECT_INFORMATION.name)
        st.session_state.defect_info = defect_info
    return st.session_state.defect_info


async def get_raw_materials(
        client: FactoryDBHelper
) -> {}:
    if 'materials' not in st.session_state:
        materials = await client.get_all_records_from_table(table=FactoryNodeTable.RAW_MATERIAL.name)
        st.session_state.materials = materials
    return st.session_state.materials


async def get_factory(
        client: FactoryDBHelper
):
    if 'factories' not in st.session_state:
        factories = await client.get_all_records_from_table(table=FactoryNodeTable.FACTORY.name)
        st.session_state.factories = factories
    return st.session_state.factories


async def get_relationships_from_cache(
        client: FactoryDBHelper
):
    if 'relationships' not in st.session_state:
        relationships = await client.get_relationships(relationships=[r.name for r in list(FactoryRelationship)])
        st.session_state.relationships = relationships
    return st.session_state.relationships


async def get_product_work_histories_from_cache(
        client: FactoryDBHelper
):
    if 'product_work_histories' not in st.session_state:
        product_work_histories = await client.get_product_work_histories()
        st.session_state.product_work_histories = product_work_histories
    return st.session_state.product_work_histories


async def get_transfer_working_histories_from_cache(
        client: FactoryDBHelper
):
    if 'transfer_working_histories' not in st.session_state:
        product_work_histories = await client.get_transfer_work_histories()
        st.session_state.get_transfer_work_histories = product_work_histories
    else:
        product_work_histories = st.session_state.get_transfer_work_histories
    return product_work_histories


def get_node_name(
        node_id: str,
        factory_data_cache: FactoryDataCache,
        is_show_node_id: bool = False,
) -> str:
    ids = node_id.split(':')
    match ids[0]:
        case FactoryNodeTable.FACTORY.name:
            result = f'工場'

        case FactoryNodeTable.PRODUCTION_LINE.name:
            result = f'製造ライン({ids[1]})'

        case FactoryNodeTable.PRODUCT.name:
            node = factory_data_cache.find_node(node_id)
            product_type = node.get('data', {}).get('type', '')
            product_status = node.get('data', {}).get('status')
            if product_status == ProductStatus.WORK_IN_PROGRESS.name:
                result = '仕掛品'
            elif product_status == ProductStatus.DEFECT_DETECTION.name:
                result = '欠陥品'
            elif product_status == ProductStatus.FINISHED_PRODUCT.name:
                result = '製品' if product_type == ProductType.PRODUCT.name else '部品'
            else:
                result = '仕掛品?'
            result += f'({node_id.split(":")[1]})' if is_show_node_id else ''

        case FactoryNodeTable.STORAGE.name:
            result = f'貯蔵庫({ids[1]})'

        case FactoryNodeTable.WORK.name:
            result = f'作業' if node_id.split(':')[1].startswith('w') else '移動'
            result += f'({node_id.split(":")[1]})' if is_show_node_id else ''

        case FactoryNodeTable.MACHINE.name:
            result = f'機器({ids[1]})'
        case FactoryNodeTable.RAW_MATERIAL.name:
            result = f'原材料({ids[1]})'

        case FactoryNodeTable.SPECIFICATION.name:
            result = f'仕様({ids[1]})'

        case FactoryNodeTable.MANUFACTURER.name:
            result = f'供給者({ids[1]})'

        case FactoryNodeTable.MEASUREMENTS.name:
            result = f'測定値({ids[1]})'

        case FactoryNodeTable.OPERATING_CREW.name:
            result = f'作業班({ids[1]})'

        case FactoryNodeTable.INSPECTION_RESULT.name:
            result = f'検査結果'
            result += f'({node_id.split(":")[1]})' if is_show_node_id else ''

        case FactoryNodeTable.DEFECT_INFORMATION.name:
            result = f'欠陥情報'
            result += f'({node_id.split(":")[1]})' if is_show_node_id else ''

        case _:
            result = f'?({node_id})'
    return result


def confirm_work_type(
        node_id: str,
        work_type: WorkType,
        works: []
) -> bool:
    if node_id.split(':')[0] == FactoryNodeTable.WORK.name:
        for work in works:
            if node_id == work.get('id', '?') and work.get('data', {}).get('type', '?') == work_type.name:
                return True
        else:
            return False
    else:
        return True

