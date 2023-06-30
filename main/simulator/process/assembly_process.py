import datetime
from typing import Optional

from simpy import Environment

import util
from simulator.factory_models import ProductionLine, OperationType, ProductStatus
from simulator.process.awork_manager import AWorkManager
from simulator.process.production_history_manager import ProductionHistory
from simulator.process.storage_resource import StorageResource


class AssemblyProcess(AWorkManager):

    def __init__(
            self,
            env: Environment,
            factory_clock: datetime.datetime,
            production_line: ProductionLine,
            in_storage: Optional[StorageResource] = None,
            out_storage: Optional[StorageResource] = None,
            parts_storage: Optional[StorageResource] = None,
            repair_storage: Optional[StorageResource] = None,
            running_time: int = 10):
        """
        コンストラクタ
        :param env: simpy環境
        :param factory_clock: 工場時計
        :param production_line: 製造ライン情報
        :param in_storage: 入力貯蔵庫
        :param out_storage: 出力貯蔵庫
        :param parts_storage: 部品貯蔵庫
        :param repair_storage: 修復貯蔵庫
        :param running_time: 該当工程の作業時間（分）
        """
        super(AssemblyProcess, self).__init__(
            env=env,
            factory_clock=factory_clock,
            production_line=production_line,
            in_storage=in_storage,
            out_storage=out_storage,
            parts_storage=parts_storage,
            repair_storage=repair_storage,
            running_time=running_time)

    def run(self, env: Environment):
        """
        組立工程シミュレータ
        :param env: simpy環境情報
        :return:
        """
        while True:
            wm = self.build_production_history_manager()

            # 同じ工程の開始のインターバル
            yield env.timeout(self.WORKING_INTERVAL)

            # 中間工程なので貯蔵庫(in_storage)から仕掛品を取り出す
            product = yield self.in_storage.get()
            # 移動時間を待つ
            transfer_working_time = self.get_transfer_work_time()
            yield env.timeout(transfer_working_time)

            self.print_product_info(product=product)
            wm.product = product

            # 貯蔵庫から仕掛品を製造ラインへ移動事象登録
            wm.add_production_history(ProductionHistory(
                operation_type=OperationType.PUT_IN,
                product=product,
                status=product.status,
                storage=self.in_storage.storage,
                timestamp=self._get_current_datetime(),
            ))

            # 工程開始メッセージ追加
            wm.add_production_history(ProductionHistory(
                operation_type=OperationType.OPERATION_START,
                product=product,
                status=product.status,
                timestamp=self._get_current_datetime(),
            ))

            # 組立工程
            # 部品貯蔵庫(Parts storage)から部品を移動し仕掛品へ組み込む
            parts_product = yield self.parts_storage.get()
            wm.add_production_history(ProductionHistory(
                operation_type=OperationType.PUT_IN,
                storage=self.parts_storage.storage,
                product=parts_product,
                status=product.status,
                timestamp=self._get_current_datetime(),
            ))

            # 該当工程の作業実施
            # 加工作業時間を待つ
            processing_time = util.get_gaussian_distribution_value(average=self.running_time)
            yield env.timeout(processing_time)

            # 組立メッセージ追加
            wm.add_production_history(ProductionHistory(
                operation_type=OperationType.ASSEMBLY,
                product=product,
                status=product.status,
                parts=parts_product,
                timestamp=self._get_current_datetime(),
            ))

            # ある比率で良品／不良品に振り分ける
            product.status = ProductStatus.WORK_IN_PROGRESS \
                if util.get_processing_result_randomly() else ProductStatus.DEFECT_DETECTION

            # 検査事象登録
            wm.add_production_history(ProductionHistory(
                operation_type=OperationType.INSPECTION,
                product=product,
                status=product.status,
                timestamp=self._get_current_datetime(),
                detail_info={
                    'result': 'NG' if product.status == ProductStatus.DEFECT_DETECTION else 'OK'
                }
            ))

            if product.status == ProductStatus.DEFECT_DETECTION:
                # 欠陥情報登録
                wm.add_production_history(ProductionHistory(
                    operation_type=OperationType.DEFECT_DETECTION,
                    product=product,
                    status=product.status,
                    detail_info=util.generate_defect_info(),
                    timestamp=self._get_current_datetime(),
                ))

            # # 該当工程完了事象登録
            # wm.add_work_history(WorkOperationHistory(
            #     operation_type=OperationType.OPERATION_END,
            #     product=product,
            #     status=product.status,
            #     timestamp=self._get_current_datetime(),
            # ))

            # 移動時間を待つ
            transfer_working_time = self.get_transfer_work_time()
            yield env.timeout(transfer_working_time)
            # 良品／不良品により移動する貯蔵庫を割り振ること
            if product.status == ProductStatus.WORK_IN_PROGRESS:
                # 良品
                yield self.out_storage.put(product)
                # 仕掛品を倉庫へ移動事象登録
                wm.add_production_history(ProductionHistory(
                    operation_type=OperationType.PUT_OUT,
                    storage=self.out_storage.storage,
                    product=product,
                    status=product.status,
                    timestamp=self._get_current_datetime(),
                ))
            else:
                # 不良品
                yield self.repair_storage.put(product)
                # 仕掛品を修理貯蔵庫へ移動事象登録
                wm.add_production_history(ProductionHistory(
                    operation_type=OperationType.PUT_OUT,
                    storage=self.repair_storage.storage,
                    product=product,
                    status=product.status,
                    timestamp=self._get_current_datetime(),
                ))

            # 完了事象登録
            wm.add_production_history(ProductionHistory(
                operation_type=OperationType.OPERATION_END,
                product=product,
                status=product.status,
                timestamp=self._get_current_datetime(),
            ))
