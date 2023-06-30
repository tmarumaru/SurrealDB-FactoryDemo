import datetime
import random
from abc import abstractmethod
from typing import List, Optional

from simpy import Environment

import util
from simulator.factory_model_builder import FactoryModelBuilder
from simulator.factory_models import ProductionLine, RawMaterial, Product, AMessage, MeasurementMessage, ProductType
from simulator.process.production_history_manager import ProductionHistoryManager
from simulator.process.storage_resource import StorageResource


class AWorkManager:
    """
    製造ラインプロセス 抽象クラス
    """
    WORKING_INTERVAL = 2

    def __init__(
            self,
            env: Environment,
            factory_clock: datetime.datetime,
            production_line: ProductionLine,
            in_storage: Optional[StorageResource] = None,
            out_storage: Optional[StorageResource] = None,
            parts_storage: Optional[StorageResource] = None,
            repair_storage: Optional[StorageResource] = None,
            raw_materials: Optional[List[RawMaterial]] = None,
            running_time: int = 10,
            is_print: bool = True,
            transfer_working_time=2,
    ):
        """
        コンストラクタ
        :param env: Simpy.Environment
        :param factory_clock: 工場時計
        :param production_line: 製造ライン情報
        :param in_storage: 入力貯蔵庫(省略可）
        :param out_storage: 出力貯蔵庫(省略可）
        :param parts_storage: 拡張入力貯蔵庫(省略可）
        :param repair_storage: 修復貯蔵庫(省略可）
        :param running_time: 該当工程の処理時間（分）
        """
        self.products: List[Product] = []
        self.messages: List[AMessage] = []
        self._production_history_managers: List[ProductionHistoryManager] = []

        self.env = env
        self.factory_clock = factory_clock
        self.count = 0
        self.production_no = 0
        self.production_line = production_line
        self.in_storage = in_storage
        self.out_storage = out_storage
        self.parts_storage = parts_storage
        self.repair_storage = repair_storage
        self.raw_materials = raw_materials
        self.running_time = running_time
        self._is_print = is_print
        self._work_id = 0
        self._transfer_working_time = transfer_working_time

    def _get_current_datetime(self) -> datetime.datetime:
        """シミュレーション現時刻取得"""
        return util.addMinutes(self.factory_clock, self.env.now)

    def add_product(self, product: Product):
        self.products.append(product)

    def get_products(self):
        return self.products

    def add_measurement_message(
            self,
            message_id: str,
            created_by: str,
            measurement_values: {},
    ):
        message = MeasurementMessage(
            mid=message_id,
            created_by=created_by,
            measurement_values=measurement_values,
            timestamp=self._get_current_datetime(),
        )
        self.messages.append(message)

    def _get_production_no(self) -> int:
        self.production_no += 1
        return self.production_no

    def build_production_history_manager(self) -> ProductionHistoryManager:
        wm = ProductionHistoryManager(
            production_line=self.production_line,
            in_storage=self.in_storage.storage if self.in_storage else None,
            out_storage=self.out_storage.storage if self.out_storage else None,
            extra_storage=self.parts_storage.storage if self.parts_storage else None,
            repair_storage=self.repair_storage.storage if self.repair_storage else None,
        )
        self._production_history_managers.append(wm)
        return wm

    def get_production_history_managers(self) -> List[ProductionHistoryManager]:
        return self._production_history_managers

    def create_product(
            self,
            raw_material: RawMaterial
    ) -> Product:
        """
        仕掛品生成
        :param raw_material: 原材料情報
        :return:
        """
        prefix = 'S' if self.production_line.specification_id == 'SP01' else 'P'
        product_id = f'{prefix}{self.production_line.id[-1]}{self._get_production_no():04}'
        product_type = ProductType.PARTS if self.production_line.specification_id == 'SP01' else ProductType.PRODUCT
        product = FactoryModelBuilder.build_work_in_progress(
            id=product_id,
            name=f'Product for {self.production_line.specification_id}',
            specification_id=self.production_line.specification_id,
            product_type=product_type,
        )
        # 仕掛品登録
        self.add_product(product=product)
        return product

    def get_raw_material_at_random(self) -> RawMaterial:
        """
        ランダムに原材料情報を取得する
        :return:
        """
        return self.raw_materials[random.randrange(0, len(self.raw_materials))] if self.raw_materials else None

    def print_product_info(self, product: Optional[Product] = None):
        """仕掛品情報出力"""
        if self._is_print:
            print(f'{self.production_line.name}, ', end='')
            print(f'製品仕様: {self.production_line.specification_id}, ', end='')
            if product:
                print(f'仕掛品識別子: {product.get_compound_id()}, ', end='')
                print(f'製品型: {product.product_type.name} ', end='')
            print()

    def get_transfer_work_time(self) -> int:
        """移動作業時間取得"""
        return abs(util.get_gaussian_distribution_value(average=self._transfer_working_time))

    @abstractmethod
    def run(self, env: Environment):
        raise NotImplemented(f'Not implemented "run" method')
