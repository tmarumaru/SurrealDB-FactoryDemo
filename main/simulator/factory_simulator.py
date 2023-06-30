import datetime
from typing import Optional, List

from simpy import Environment

import util
from simulator.factory_model_builder import FactoryModelBuilder
from simulator.factory_models import Factory
from simulator.process.assembly_process import AssemblyProcess
from simulator.process.awork_manager import AWorkManager
from simulator.process.inspection_process import InspectionProcess
from simulator.process.intermediate_process import IntermediateProcess
from simulator.process.machine_process import MachineProcess
from simulator.process.storage_resource import StorageResource
from simulator.process.wip_creation_process import WipCreationProcess

START_DATETIME = '2023-01-01T00:00:00+00:00'  # シミュレーション開始時間


class FactorySimulator:
    """
    工場製造ライン シミュレータ
    0. 工場を登録する
    1. 製造ラインを登録する
    2. 貯蔵庫を登録する
    3. 製造ライン機器登録
    4. 作業班登録
    5. 原材料登録
    6. 工場シミュレーション実行
    """

    def __init__(self, env: Environment, factory_id: str, factory_name: str):
        """
        コンストラクタ
        :param env: simpy環境
        :param factory_id: 工場識別子
        :param factory_name: 工場名
        """
        self._env = env
        self._factory_id = factory_id
        self._factory_name = factory_name
        self.factory: Optional[Factory] = None
        self.production_line_processes: List[AWorkManager] = []
        self.machine_processes: List[MachineProcess] = []
        self.storage_resources: List[StorageResource] = []
        self.factory = FactoryModelBuilder.build_factory(id=self._factory_id, name=self._factory_name)
        self._init()

    def _init(self):
        factory_clock = util.convert_utc_string_to_datetime(START_DATETIME)
        self.create_storages()
        self.create_raw_materials()
        self.create_production_lines(factory_clock=factory_clock)
        self.create_machines(quantity=2)
        self.create_working_groups()
        self.create_machine_processes(factory_clock=factory_clock)

    def create_production_lines(self, factory_clock: datetime.datetime):
        """
        シミュレーション用の製造ラインを作成する
        :param self:
        :param factory_clock: 初期工場時間
        :return:
        """
        # 製造ライン１
        # 製品仕様：SP01
        # 製造工程：SP01-1
        production_line = FactoryModelBuilder.build_production_line(
            id=f'pl001',
            specification_id='SP01',
            process_id=f'SP01-1',
            name='製造ライン1'
        )
        self.factory.production_lines.append(production_line)

        # 製造ライン１用プロセス登録
        process = WipCreationProcess(
            env=self._env,
            factory_clock=factory_clock,
            production_line=production_line,
            in_storage=None,
            out_storage=self.storage_resources[0],
            repair_storage=self.storage_resources[6],
            raw_materials=self.factory.raw_materials,
            running_time=10
        )
        self._env.process(process.run(env=self._env))
        self.production_line_processes.append(process)

        # 製造ライン２
        # 製品仕様：SP01
        # 製造工程：SP01-2
        production_line = FactoryModelBuilder.build_production_line(
            id=f'pl002',
            specification_id='SP01',
            process_id=f'SP01-2',
            name='製造ライン2'
        )
        self.factory.production_lines.append(production_line)

        # 製造ライン２用プロセス登録
        process = IntermediateProcess(
            env=self._env,
            factory_clock=factory_clock,
            production_line=production_line,
            in_storage=self.storage_resources[0],
            out_storage=self.storage_resources[1],
            repair_storage=self.storage_resources[6],
            running_time=10
        )
        self._env.process(process.run(env=self._env))
        self.production_line_processes.append(process)

        # 製造ライン３（検査工程）
        # 製品仕様：SP01
        # 製造工程：SP01-Inspection
        production_line = FactoryModelBuilder.build_production_line(
            id=f'pl003',
            specification_id='SP01',
            process_id=f'SP01-inspection',
            name='製造ライン3'
        )
        self.factory.production_lines.append(production_line)

        # 製造ライン３用プロセス登録
        process = InspectionProcess(
            env=self._env,
            factory_clock=factory_clock,
            production_line=production_line,
            in_storage=self.storage_resources[1],
            out_storage=self.storage_resources[2],
            repair_storage=self.storage_resources[6],
            running_time=10
        )
        self._env.process(process.run(env=self._env))
        self.production_line_processes.append(process)

        # 製造ライン4
        # 製品仕様：SP02
        # 製造工程：SP02-1
        production_line = FactoryModelBuilder.build_production_line(
            id=f'pl004',
            specification_id='SP02',
            process_id=f'SP02-1',
            name='製造ライン4'
        )
        self.factory.production_lines.append(production_line)

        # 製造ライン４用プロセス登録
        process = WipCreationProcess(
            env=self._env,
            factory_clock=factory_clock,
            production_line=production_line,
            in_storage=None,
            out_storage=self.storage_resources[3],
            repair_storage=self.storage_resources[6],
            raw_materials=self.factory.raw_materials,
            running_time=10
        )
        self._env.process(process.run(env=self._env))
        self.production_line_processes.append(process)

        # 製造ライン５ (組立工程)
        # 製品仕様：SP02
        # 製造工程：SP02-assembly
        production_line = FactoryModelBuilder.build_production_line(
            id=f'pl005',
            specification_id='SP02',
            process_id=f'SP02-assembly',
            name='製造ライン5'
        )
        self.factory.production_lines.append(production_line)

        # 製造ライン５用プロセス登録
        process = AssemblyProcess(
            env=self._env,
            factory_clock=factory_clock,
            production_line=production_line,
            in_storage=self.storage_resources[3],
            out_storage=self.storage_resources[4],
            parts_storage=self.storage_resources[2],
            repair_storage=self.storage_resources[6],
            running_time=10
        )
        self._env.process(process.run(env=self._env))
        self.production_line_processes.append(process)

        # 製造ライン６ (検査工程)
        # 製品（仕様：SP02)
        # 製造工程：SP02-inspection
        production_line = FactoryModelBuilder.build_production_line(
            id=f'pl006',
            specification_id='SP02',
            process_id=f'SP02-inspection',
            name='製造ライン6'
        )
        self.factory.production_lines.append(production_line)

        # 製造ライン６用プロセス登録
        process = InspectionProcess(
            env=self._env,
            factory_clock=factory_clock,
            production_line=production_line,
            in_storage=self.storage_resources[4],
            out_storage=self.storage_resources[5],
            repair_storage=self.storage_resources[6],
            running_time=10
        )
        self._env.process(process.run(env=self._env))
        self.production_line_processes.append(process)

    def create_storages(self):
        """
        貯蔵庫情報作成
        :return:
        """
        storage = FactoryModelBuilder.build_storage(id='storage1', name='貯蔵庫1')
        self.factory.storages.append(storage)
        self.storage_resources.append(
            StorageResource(
                env=self._env,
                storage=storage,
                capacity=float('inf')))

        storage = FactoryModelBuilder.build_storage(id='storage2', name='貯蔵庫2')
        self.factory.storages.append(storage)
        self.storage_resources.append(
            StorageResource(
                env=self._env,
                storage=storage,
                capacity=float('inf')))

        storage = FactoryModelBuilder.build_storage(id='storage3', name='貯蔵庫3')
        self.factory.storages.append(storage)
        self.storage_resources.append(
            StorageResource(
                env=self._env,
                storage=storage,
                capacity=float('inf')))

        storage = FactoryModelBuilder.build_storage(id='storage4', name='貯蔵庫4')
        self.factory.storages.append(storage)
        self.storage_resources.append(
            StorageResource(
                env=self._env,
                storage=storage,
                capacity=float('inf')))

        storage = FactoryModelBuilder.build_storage(id='storage5', name='貯蔵庫5')
        self.factory.storages.append(storage)
        self.storage_resources.append(
            StorageResource(
                env=self._env,
                storage=storage,
                capacity=float('inf')))

        storage = FactoryModelBuilder.build_storage(id='storage6', name='製品倉庫')
        self.factory.storages.append(storage)
        self.storage_resources.append(
            StorageResource(
                env=self._env,
                storage=storage,
                capacity=float('inf')))

        storage = FactoryModelBuilder.build_storage(id='repair1', name='修理貯蔵庫')
        self.factory.storages.append(storage)
        self.storage_resources.append(
            StorageResource(
                env=self._env,
                storage=storage,
                capacity=float('inf')))

    def create_machines(self, quantity: int = 2):
        """
        製造ライン機器情報作成
        :return:
        """
        for i in range(len(self.factory.production_lines)):
            line = self.factory.production_lines[i]
            for j in range(quantity):
                machine = FactoryModelBuilder.build_machine(id=f'm{i:02}{j:02}', name=f'機器{i:02}{j:02}')
                line.machines.append(machine)
                self.factory.machines.append(machine)

    def create_working_groups(self):
        """
        作業班情報作成
        :return:
        """
        for i in range(len(self.factory.production_lines)):
            line = self.factory.production_lines[i]
            group = FactoryModelBuilder.build_operating_crew(id=f'g{i:04}', name=f'作業班-{i:04}')
            line.working_group_id = group.get_compound_id()
            self.factory.operating_crews.append(group)

    def create_raw_materials(self, quantity: int = 4):
        """
        原材料情報作成
        :param quantity: 原材料個数(省略時４）
        :return:
        """
        for i in range(quantity):
            self.factory.raw_materials.append(
                FactoryModelBuilder.build_raw_material(id=f'rm{i:03}', name=f'原材料-{i:03}'))

    def create_specifications(self):
        """
        製品仕様情報作成
        :return:
        """
        self.factory.specifications.append(
            FactoryModelBuilder.build_specification(
                id='SP01',
                name='Semi-Product specification',
            ))
        self.factory.specifications.append(
            FactoryModelBuilder.build_specification(
                id='SP02',
                name='Product specification',
            ))

    def create_machine_processes(self, factory_clock: datetime.datetime):
        """
        製造機器プロセス生成
        :param factory_clock: 工場時計
        :return:
        """
        for production_line in self.factory.production_lines:
            for machine in production_line.machines:
                process = MachineProcess(
                    env=self._env,
                    factory_clock=factory_clock,
                    production_line=production_line,
                    machine=machine,
                    running_time=2)
                self._env.process(process.run(env=self._env))
                self.machine_processes.append(process)

    def run(self, until: int = 100):
        """シミュレーション実行"""
        self._env.run(until=until)
