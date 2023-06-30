import json
from os import path
from typing import Optional

from simulator.factory_model_builder import FactoryModelBuilder
from simulator.factory_models import Factory, FactoryRelationship, OperationType, FactoryNodeTable, WorkType


class FactoryDataReader:
    """
    工場シミュレーション結果情報をファイルから読み込み情報を再構築する
    """
    def __init__(
            self,
            json_data_file_path: str
    ):
        """
        コンストラクタ 
        :param json_data_file_path: jsonファイル名
        """""
        self._json_data_file_path = json_data_file_path
        self.factory: Optional[Factory] = None
        if not path.isfile(self._json_data_file_path):
            raise RuntimeError(f'File not found. ({self._json_data_file_path})')

    def rebuild(self) -> None:
        with open(self._json_data_file_path, 'r', encoding='utf-8') as f:
            factory_json_data = json.load(f)
        factory_data = factory_json_data.get('factory', None)
        if not factory_data:
            raise RuntimeError(f'Unable to parse the file contents. ({self._json_data_file_path}) ')
        production_lines_data = factory_data.get('production_lines', None)
        machines_data = factory_data.get('machines', None)
        storages_data = factory_data.get('storages', None)
        raw_materials_data = factory_data.get('raw_materials', None)
        operating_crews_data = factory_data.get('operating_crews', None)
        products_data = factory_data.get('products', None)
        production_histories_data = factory_data.get('production_histories', None)
        measurements_data = factory_data.get('measurements', None)
        if not (production_lines_data and machines_data and storages_data and raw_materials_data
                and production_histories_data and operating_crews_data and products_data and measurements_data):
            raise RuntimeError(f'Unable to parse file contents. ({self._json_data_file_path}) ')

        # Factory情報生成
        self.factory = FactoryModelBuilder.build_factory(
            id=factory_data.get('id', '?'),
            name=factory_data.get('name', '?'))

        # 製造ライン機器情報生成
        for machine_data in machines_data:
            machine = FactoryModelBuilder.build_machine_from_dict(source=machine_data)
            self.factory.machines.append(machine)

        # 製造ライン情報生成
        for production_line_data in production_lines_data:
            production_line = FactoryModelBuilder.build_production_line_from_dict(
                source=production_line_data,
                all_machines=self.factory.machines)
            self.factory.production_lines.append(production_line)
            # (Factory)-[CONSISTS_OF]->(ProductionLine)
            self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                from_id=self.factory.get_compound_id(),
                to_id=production_line.get_compound_id(),
                relationship=FactoryRelationship.CONSISTS_OF,
            ))
            # (ProductionLine)-[CONSISTS_OF]->(Machine)
            for machine in production_line.machines:
                self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                    from_id=production_line.get_compound_id(),
                    to_id=machine.get_compound_id(),
                    relationship=FactoryRelationship.CONSISTS_OF,
                ))
            # (ProductionLine)-[HAS_WORKERS]->(WorkingGroup)
            self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                from_id=production_line.get_compound_id(),
                to_id=production_line.working_group_id,
                relationship=FactoryRelationship.HAS_WORKERS,
            ))
        # 貯蔵庫情報生成
        for storage_data in storages_data:
            storage = FactoryModelBuilder.build_storage_from_dict(source=storage_data)
            self.factory.storages.append(storage)
            # (Factory)-[CONSISTS_OF]->(Storage)
            self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                from_id=self.factory.get_compound_id(),
                to_id=storage.get_compound_id(),
                relationship=FactoryRelationship.CONSISTS_OF,
            ))

        # 原材料情報生成
        for raw_material_data in raw_materials_data:
            raw_material = FactoryModelBuilder.build_raw_material_from_dict(source=raw_material_data)
            self.factory.raw_materials.append(raw_material)
            # (Factory)-[CONSISTS_OF]->(RawMaterial)
            self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                from_id=self.factory.get_compound_id(),
                to_id=raw_material.get_compound_id(),
                relationship=FactoryRelationship.CONSISTS_OF,
            ))

        # 作業班情報生成
        for operatio_crew in operating_crews_data:
            self.factory.operating_crews.append(FactoryModelBuilder.build_operating_crew_from_dict(source=operatio_crew))

        # 製品・部品・仕掛品情報生成
        for product in products_data:
            self.factory.products.append(FactoryModelBuilder.build_product_from_dict(source=product))

        # 作業履歴情報生成
        for production_history in production_histories_data:
            created_by = production_history.get('created_by', '?')
            messages = production_history.get('messages', [])
            if len(messages) <= 0:
                continue
            work_id = messages[0].get('work_id', '?')
            work = FactoryModelBuilder.build_work(
                work_id=work_id,
                name=f'work',
                created_by=created_by)
            self.factory.works.append(work)
            # (ProductionLine)-[EXECUTES]->(Work)
            self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                from_id=created_by,
                to_id=work.get_compound_id(),
                relationship=FactoryRelationship.EXECUTES,
            ))
            messages = production_history.get('messages', [])
            if len(messages) <= 0:
                continue
            for message_data in messages:
                #print(f'{message_data}')
                message = FactoryModelBuilder.build_production_event_message_from_dict(
                    source=message_data,
                    created_by=created_by)
                self.factory.process_messages.append(message)

        # 製造ライン機器からの測定情報生成
        for measurement in measurements_data:
            created_by = measurement.get('created_by', '')
            messages = measurement.get('messages', [])
            for message_data in messages:
                message = FactoryModelBuilder.build_measurement_message_from_dict(
                    created_by=created_by,
                    source=message_data)
                self.factory.measurement_messages.append(message)
                # (Machine)-[RECORDS]->(MeasurementMessage)
                self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                    from_id=created_by,
                    to_id=message.get_compound_id(),
                    relationship=FactoryRelationship.RECORDS,
                ))
        #
        # 工程作業メッセージから関係を生成する
        transfer_message_number = 0
        for process_message in self.factory.process_messages:
            match process_message.operation_type:

                case OperationType.OPERATION_START:
                    # (PRODUCT)-[STARTED_BY]->(WORK)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=FactoryDataReader.get_compound_id(FactoryNodeTable.WORK, process_message.work_id),
                        from_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.STARTED_BY,
                    ))

                case OperationType.OPERATION_END:
                    # (PRODUCT)-[ENDED_BY]->(WORK)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=FactoryDataReader.get_compound_id(FactoryNodeTable.WORK, process_message.work_id),
                        from_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.ENDED_BY,
                    ))

                case OperationType.CREATED:
                    # (RAW_MATERIAL)-[USED_TO_PRODUCT]->(PRODUCT)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=process_message.product_id,
                        from_id=process_message.raw_material,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.USED_TO_PRODUCE,
                    ))
                    # (PRODUCT)-[PRODUCED_BY]->(WORK)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=FactoryDataReader.get_compound_id(FactoryNodeTable.WORK, process_message.work_id),
                        from_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.PRODUCED_BY,
                    ))

                case OperationType.INSPECTION:
                    inspection_result_id = f'ir{process_message.id}'
                    inspection_result = FactoryModelBuilder.build_inspection_result(
                        id=inspection_result_id,
                        name='Inspection result',
                        timestamp=process_message.timestamp,
                        detail=process_message.inspection_result,
                    )
                    self.factory.inspection_results.append(inspection_result)
                    # (PRODUCT)-[TESTED_BY]->(WORK)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=FactoryDataReader.get_compound_id(FactoryNodeTable.WORK, process_message.work_id),
                        from_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.TESTED_BY,
                    ))
                    # (Work)-[RECORDS]->(InspectionResult)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=inspection_result.get_compound_id(),
                        from_id=FactoryDataReader.get_compound_id(FactoryNodeTable.WORK, process_message.work_id),
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.RECORDS,
                    ))
                    # (InspectionResult)-[TEST_RESULT_OF]->(Product)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        from_id=inspection_result.get_compound_id(),
                        to_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.TEST_RESULT_OF,
                    ))

                case OperationType.DEFECT_DETECTION:
                    defect_information_id = f'df{process_message.id}'
                    defect_info = FactoryModelBuilder.build_defect_information(
                        id=defect_information_id,
                        name='Defect information',
                        timestamp=process_message.timestamp,
                        detail=process_message.product_defect,
                    )
                    self.factory.defect_information.append(defect_info)
                    # (PRODUCT)-[DEFECT_DETECTED_BY]->(WORK)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=FactoryDataReader.get_compound_id(FactoryNodeTable.WORK, process_message.work_id),
                        from_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.DEFECT_DETECTED_BY,
                    ))

                    # (Work)-[RECORDS]->(DefectInformation)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=defect_info.get_compound_id(),
                        from_id=FactoryDataReader.get_compound_id(FactoryNodeTable.WORK, process_message.work_id),
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.RECORDS,
                    ))
                    # (Product)-[HAS_DEFECT]->(DefectInformation)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=defect_info.get_compound_id(),
                        from_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.HAS_DEFECT,
                    ))

                case OperationType.ASSEMBLY:
                    # (Product)-[ASSEMBLED_BY]->(Work)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=FactoryDataReader.get_compound_id(FactoryNodeTable.WORK, process_message.work_id),
                        from_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.ASSEMBLED_BY,
                    ))
                    # (Product)-[COMPRISED_OF]->(Parts)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=process_message.parts,
                        from_id=process_message.product_id,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.COMPRISED_OF,
                    ))

                case OperationType.FINISHED_PRODUCT:
                    # TODO この情報が必要か？
                    pass

                case OperationType.PUT_IN | OperationType.PUT_OUT:
                    # 移動Work作成
                    transfer_message_number += 1
                    transfer_work = FactoryModelBuilder.build_work(
                        work_id=f'tf{transfer_message_number:08}',
                        name='transfer work',
                        created_by=process_message.created_by,
                        work_type=WorkType.TransferWork,
                    )
                    self.factory.works.append(transfer_work)
                    # PUT_IN:  (Storage)-[MOVE_FROM]->(Work)
                    # PUT_OUT: (ProductionLine)-[MOVE_FROM]->(Work)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        to_id=transfer_work.get_compound_id(),
                        from_id=process_message.storage_id \
                            if process_message.operation_type == OperationType.PUT_IN  else process_message.created_by,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.MOVE_FROM,
                    ))
                    # PUT_IN:  (Work)-[MOVE_TO]->(ProductionLine)
                    # PUT_OUT: (Work)-[MOVE_TO]->(Storage)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        from_id=transfer_work.get_compound_id(),
                        to_id=process_message.created_by \
                            if process_message.operation_type==OperationType.PUT_IN else process_message.storage_id ,
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.MOVE_TO,
                    ))
                    # (Product)-[MOVED_BY]->(Work)
                    self.factory.relationships.append(FactoryModelBuilder.build_relationship(
                        from_id=process_message.product_id,
                        to_id=transfer_work.get_compound_id(),
                        timestamp=process_message.timestamp,
                        relationship=FactoryRelationship.MOVED_BY,
                    ))
                case _:
                    raise RuntimeError(f'Invalid operation type was specified. ({process_message.operation_type.name})')

    @staticmethod
    def get_compound_id(
            node_table: FactoryNodeTable,
            object_id: str
    ) -> str:
        return f'{node_table.name}:{object_id}'