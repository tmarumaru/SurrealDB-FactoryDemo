import asyncio
import json
import sys
from typing import List

import simpy
from simpy import Environment

from arguments_parser import parse, Params
from simulator.factory_model_builder import FactoryModelBuilder
from simulator.factory_models import Relationship, Work, Product, Measurement
from simulator.factory_simulator import FactorySimulator


class SimulatorManager:
    """
    工場シュミレータを実行し、生成された情報をファイルへ出力する
    """

    def get_factory_simulator(
            self
    ) -> FactorySimulator:
        return self._factory_simulator

    def __init__(
            self,
            json_data_file_path: str,
            until: int = 100,
    ):
        """
        工場シミュレータ管理
        :param json_data_file_path: 実行結果保存ファイル名(未使用)
        :param until: シミュレーション ユニット
        """
        self._env: Environment
        self._until = until
        self.relationships: List[Relationship] = []
        self.works: List[Work] = []
        self.products: List[Product] = []
        self.measurements: List[Measurement]
        self.json_data_file_path = json_data_file_path
        self._nonce = 0
        self._init()

    def _init(self) -> None:
        """
        工場シミュレータ初期化
        :return:
        """
        self._env = simpy.Environment()
        self._factory_simulator = FactorySimulator(
            env=self._env,
            factory_id='f01',
            factory_name='factory#1'
        )

    async def run(
            self,
    ):
        """
        シミュレーション実行
        :return:
        """
        try:
            self._env.run(until=self._until)
            self.create_factory_simulator_results(json_data_file_path=self.json_data_file_path)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print()
            print(f'Fatal Error was occurred. {e}')
            print(sys.exc_info())
            return

    def create_factory_simulator_results(
            self,
            json_data_file_path: str
    ) -> str:
        """
        シミュレーション実行結果をファイルへ保存する
        :param json_data_file_path: 実行結果格納ファイル名(未使用）
        :return: 工場情報jsonファイル名
        """
        result = self.write_factory_data_to_file(json_data_file_path=json_data_file_path)
        return result

    def write_factory_data_to_file(
            self,
            json_data_file_path: str
    ) -> str:
        """
        製造ライン情報をjsonファイルへ出力する
        :param json_data_file_path: 出力ファイル名
        :return: jsonファイルパス
        """
        production_lines = []
        storages = []
        machines = []
        operating_crews = []
        products = []
        histories = []
        measurements = []
        raw_materials = []

        factory = self._factory_simulator.factory

        for production_line in factory.production_lines:
            production_lines.append(production_line.get_dict())

        for machine in factory.machines:
            machines.append(machine.get_dict())

        for storage in factory.storages:
            storages.append(storage.get_dict())

        for operating_crew in factory.operating_crews:
            operating_crews.append(operating_crew.get_dict())

        for production_line_process in self._factory_simulator.production_line_processes:
            for product in production_line_process.products:
                products.append(product.get_dict())

        for raw_material in factory.raw_materials:
            raw_materials.append(raw_material.get_dict())

        work_id = 0
        mid = 0
        for production_line_process in self._factory_simulator.production_line_processes:
            for production_history_manager in production_line_process.get_production_history_managers():
                production_histories = []
                work_id += 1
                for history in production_history_manager.get_production_histories():
                    mid += 1
                    message = FactoryModelBuilder.build_production_event_message(
                        work_id=f'w{production_line_process.production_line.id}{work_id:05}',
                        mid=f'm{mid:08}',
                        created_by=production_line_process.production_line.get_compound_id(),
                        production_history=history,
                    )
                    production_histories.append(message.get_dict())
                histories.append({
                    'created_by': production_line_process.production_line.get_compound_id(),
                    'messages': production_histories,
                })

        for machine in self._factory_simulator.machine_processes:
            machine_messages = []
            for message in machine.messages:
                machine_messages.append(message.get_dict())
            measurements.append({
                'created_by': machine.get_machine_id(),
                'messages': machine_messages,
            })

        factory = {
            'factory': {
                'id': factory.id,
                'name': factory.name,
                'production_lines': production_lines,
                'storages': storages,
                'machines': machines,
                'operating_crews': operating_crews,
                'raw_materials': raw_materials,
                'products': products,
                'production_histories': histories,
                'measurements': measurements
            }
        }

        with open(json_data_file_path, "w", encoding='utf-8') as f:
            json.dump(factory, f, indent=2, ensure_ascii=False)
        print(f'json file: {json_data_file_path}')
        return str(json_data_file_path)


def main(params: Params):
    try:
        simulator_manager = SimulatorManager(until=params.clock, json_data_file_path=params.json_file)
        # 工場シミュレーション実行
        asyncio.run(simulator_manager.run())
    except Exception as e:
        print(f'{e}')


if __name__ == '__main__':
    args = sys.argv
    params = parse(args=args[1:])
    main(params=params)
