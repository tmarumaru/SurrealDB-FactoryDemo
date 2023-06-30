import datetime
from abc import ABC

from simpy import Environment

import util
from simulator.factory_models import ProductionLine, Machine
from simulator.process.awork_manager import AWorkManager


class MachineProcess(AWorkManager, ABC):
    """
    製造ライン機器シミュレーションプロセス
    """

    def __init__(
            self,
            env: Environment,
            factory_clock: datetime.datetime,
            production_line: ProductionLine,
            machine: Machine,
            running_time: int = 2
    ):
        """
        コンストラクタ
        :param env: simpy Environment
        :param factory_clock: 工場時計
        :param production_line: 製造ライン情報
        :param machine: 機器情報
        :param running_time: 測定時間間隔
        """
        super(MachineProcess, self).__init__(
            env=env,
            factory_clock=factory_clock,
            production_line=production_line,
            running_time=running_time,
            is_print=False,
        )
        self.machine = machine
        self.nonce = 0

    def _get_message_id(self) -> str:
        self.nonce += 1
        return f'm{self.machine.id}{self.nonce:08}'

    def get_machine_id(self) -> str:
        return self.machine.get_compound_id()

    def run(self, env: Environment):
        """ 実行 """
        while True:
            yield env.timeout(self.running_time)
            # 測定値メッセージ追加
            values = {'value': util.get_gaussian_distribution_value(average=0, scale=1)}
            self.add_measurement_message(
                created_by=self.machine.get_compound_id(),
                message_id=self._get_message_id(),
                measurement_values=values)
