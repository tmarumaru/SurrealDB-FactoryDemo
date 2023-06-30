from dataclasses import dataclass, field
from typing import List, Any, Self

from helper.factory_db_helper import FactoryDBHelper
from simulator.factory_models import FactoryNodeTable


@dataclass
class SidebarParameter:
    all_wip: bool = field(default=False)
    wip: str = field(default='')
    work_node_type: str = field(default='')
    layout_type: str = field(default='')
    factory_on: bool = field(default=False)
    production_line_on: bool = field(default=False)
    product_on: bool = field(default=False)
    machine_on: bool = field(default=False)
    storage_on: bool = field(default=False)
    raw_material_on: bool = field(default=False)
    working_team_on: bool = field(default=False)
    work_on: bool = field(default=False)
    inspection_result_on: bool = field(default=False)
    defect_info_on: bool = field(default=False)
    is_show_node_id: bool = field(default=False)
    is_show_legend: bool = field(default=True)


@dataclass
class ProductInformation:
    product_id: str
    product_info_index: int = field(default=-1)
    production_histories: List[int] = field(default_factory=list)
    transfer_work_histories: List[int] = field(default_factory=list)


class ProductionLineDataCache:

    def __init__(
            self,
    ):
        self._production_lines = None
        self._storages = None
        self._products = None
        self._products_hash_table = {}
        self._parts_hash_table = {}
        self._product_work_histories: List[{}] = []
        self._product_transfer_work_histories: List[{}] = []
        self._products_data: {str, ProductInformation} = {}

    async def build(
            self,
            client: FactoryDBHelper,
    ) -> Self:

        # 製造ライン情報取得
        self._production_lines = await client.get_all_records_from_table(table=FactoryNodeTable.PRODUCTION_LINE.name)

        # 貯蔵庫情報取得
        self._storages = await client.get_all_records_from_table(table=FactoryNodeTable.STORAGE.name)

        # 仕掛品情報取得
        self._products = await client.get_product_data_from_db()
        for product in self._products:
            pid = product.get('id').split(':')[1]
            self._products_hash_table[pid] = product
            parts_id = product.get('parts')[0].split(':')[1] if len(product.get('parts', [])) > 0 else None
            if parts_id:
                self._parts_hash_table[parts_id] = pid

        # 作業履歴取得
        self._product_work_histories = await client.get_product_work_histories()

        # 移動作業履歴取得
        self._product_transfer_work_histories = await client.get_transfer_work_histories()

        # 作業履歴を仕掛品毎に集約
        for i, history in enumerate(self._product_work_histories):
            product_id = history.get('product', None)
            if not product_id:
                print(f'Invalid production history data was found. (index={i})')
                print(f'{history=}')
                continue
            if product_id not in self._products_data:
                self._products_data[product_id] = ProductInformation(product_id=product_id)
            product_info: ProductInformation = self._products_data[product_id]
            product_info.production_histories.append(i)

        for i, transfer_history in enumerate(self._product_transfer_work_histories):
            product_id = transfer_history.get('product', None)
            if not product_id:
                print(f'Invalid transfer production history data was found. (index={i})')
                continue
            if product_id not in self._products_data:
                self._products_data[product_id] = ProductInformation(product_id=product_id)
            product_info: ProductInformation = self._products_data[product_id]
            product_info.transfer_work_histories.append(i)

        # 仕掛品毎に作業履歴、移動履歴紐づけ
        for i, product in enumerate(self._products):
            product_id = product.get('id', None)
            if not product_id:
                print(f'Invalid product data was found. (index={i})')
                continue
            if product_id not in self._products_data:
                print(f'product was not found in products_data. (product={product_id})')
                continue
            product_info = self._products_data[product_id]
            product_info.product_info_index = i
        return self

    @property
    def production_lines(self) -> Any:
        return self._production_lines

    @property
    def storages(self) -> Any:
        return self._storages

    @property
    def products(self) -> Any:
        return self._products

    @property
    def products_hash_table(self) -> Any:
        return self._products_hash_table

    @property
    def parts_hash_table(self) -> Any:
        return self._parts_hash_table

    @property
    def product_work_histories(self) -> Any:
        return self._product_work_histories

    @property
    def product_transfer_work_histories(self) -> Any:
        return self._product_transfer_work_histories

    @property
    def products_data(self) -> Any:
        return self._products_data
