import datetime
from typing import List, Optional, Union

import util
from simulator.factory_models import ProductType, ProductStatus, Product, Machine, OperatingCrew, ProductionLine, \
    FactoryNodeTable, Work, WorkType, InspectionResult, Specification, RawMaterial, Storage, Factory, DefectInformation, \
    Measurement, FactoryRelationship, ANode, Relationship, ProductionEventMessage, OperationType, MeasurementMessage
from simulator.process.production_history_manager import ProductionHistory


class FactoryModelBuilder:

    @staticmethod
    def build_product(
            id: str,
            name: str,
            specification_id='',
            product_type: ProductType = ProductType.PRODUCT,
            product_status: ProductStatus = ProductStatus.FINISHED_PRODUCT,
    ) -> Product:
        """
        製品情報ビルダ
        :param id: 識別子
        :param name: 名前
        :param product_type: 製品型
        :param product_status: 製品・部品・仕掛品状態
        :param specification_id: 製品仕様識別子
        :return: 製品情報
        """
        return (
            Product(
                id=id,
                name=name,
                product_type=product_type,
                status=product_status,
                specification_id=specification_id,
            ))

    @staticmethod
    def build_product_from_dict(
            source: dict,
    ) -> Product:
        object_id, data = FactoryModelBuilder._get_id(source)
        return FactoryModelBuilder.build_product(
            id=object_id,
            name=data.get('name', '?'),
            specification_id=data.get('specification', ''),
            product_type=ProductType(data.get('type', '')),
            product_status=ProductStatus(data.get('status', '')),
        )

    @staticmethod
    def build_work_in_progress(
            id: str,
            name: str,
            product_type: ProductType = ProductType.WIP,
            specification_id='',
    ) -> Product:
        """
        仕掛品情報ビルダ
        :param id: 識別子
        :param name:  名前
        :param product_type: 製品型
        :param specification_id: 製品仕様識別子
        :return: 仕掛品情報
        """
        return (
            Product(
                id=id,
                name=name,
                product_type=product_type,
                status=ProductStatus.WORK_IN_PROGRESS,
                specification_id=specification_id,
            ))

    @staticmethod
    def build_production_line(
            id: str,
            name: str,
            specification_id: str = '',
            process_id: str = '',
            working_group: Optional[Union[str, OperatingCrew]] = None,
            machines: Optional[List[Machine]] = None,
    ):
        """
        製造ライン情報ビルダ
        :param id: 識別子
        :param name: 名前
        :param specification_id: 製品仕様識別子
        :param process_id: 工程識別子
        :param working_group: 作業班情報
        :param machines: 機器情報群
        :return: ProductionLine: 製造ライン情報
        """
        working_group_id = '' if not working_group \
            else working_group if type(working_group) == str \
            else working_group.get_compound_id() if type(working_group) == OperatingCrew \
            else ''
        return ProductionLine(
            table=FactoryNodeTable.PRODUCTION_LINE.name,
            id=id,
            name=name,
            specification_id=specification_id,
            process_id=process_id,
            machines=machines if machines else [],
            working_group_id=working_group_id,
        )

    @staticmethod
    def build_production_line_from_dict(
            source: dict,
            all_machines: Optional[List[Machine]] = None
    ) -> ProductionLine:
        """
        製造ライン情報ビルダ
        :param source: 製造ライン情報
        :param all_machines: 全機器情報
        :return: ProductionLine: 製造ライン情報
        """
        object_id, data = FactoryModelBuilder._get_id(source)
        machine_ids = data.get('machines', [])
        machines = []
        if all_machines:
            machines = [m for m in all_machines if m.get_compound_id() in machine_ids]
        return FactoryModelBuilder.build_production_line(
            id=object_id,
            name=data.get('name', '?'),
            process_id=data.get('process_id'),
            working_group=data.get('working_group_id', '?'),
            specification_id='',
            machines=machines,
        )

    @staticmethod
    def build_work(
            work_id: str,
            name: str,
            created_by: str,
            work_type: WorkType = WorkType.NormalWork,
    ) -> Work:
        """
        作業情報ビルダ
        :param work_id: 作業識別子
        :param name: 作業名前
        :param work_type: 作業種別
        :param created_by: 作業指示元識別子
        :return: Work: 作業情報
        """
        return Work(
            table=FactoryNodeTable.WORK.name,
            id=work_id,
            name=name,
            created_by=created_by,
            work_type=work_type,
        )

    @staticmethod
    def build_transfer_work(
            work_id: str,
            name: str,
            created_by: str,
    ) -> Work:
        """
        移動作業情報ビルダ
        :param work_id: 識別子
        :param name: 名前
        :param created_by: メッセージ作成元識別子
        :return: Work: 移動作業情報
        """
        return Work(
            table=FactoryNodeTable.WORK.name,
            id=work_id,
            name=name,
            created_by=created_by,
            work_type=WorkType.TransferWork,
        )

    @staticmethod
    def build_inspection_result(
            id: str,
            name: str,
            timestamp: datetime.datetime,
            detail: {} = None
    ) -> InspectionResult:
        """
        検査結果情報ビルダ
        :param id: 検査情報識別子
        :param name: 名前
        :param timestamp: タイムスタンプ
        :param detail: 詳細情報
        :return: InspectionResult: 検査結果情報
        """
        return InspectionResult(
            id=id,
            name=name,
            timestamp=timestamp,
            detail=detail if detail else {}
        )

    @staticmethod
    def build_machine(
            id: str,
            name: str,
    ) -> Machine:
        """
        機器情報ビルダ
        :param id: 識別子
        :param name: 名前
        :return: Machine: 機器情報
        """
        return Machine(
            table=FactoryNodeTable.MACHINE.name,
            id=id,
            name=name,
        )

    @staticmethod
    def build_machine_from_dict(
            source: dict,
    ) -> Machine:
        """
        機器情報ビルダ
        :param source: 機器情報
        :return: Machine: 機器情報
        """
        object_id, data = FactoryModelBuilder._get_id(source)
        return FactoryModelBuilder.build_machine(
            id=object_id,
            name=data.get('name', '?'),
        )

    @staticmethod
    def build_operating_crew(
            id: str,
            name: str,
    ) -> OperatingCrew:
        """
        作業班情報ビルダ
        :param id: 識別子
        :param name: 名前
        :return: WorkingGroup: 作業班情報
        """
        return OperatingCrew(
            table=FactoryNodeTable.OPERATING_CREW.name,
            id=id,
            name=name,
        )

    @staticmethod
    def build_operating_crew_from_dict(
            source: dict,
    ) -> OperatingCrew:
        """
        作業班情報ビルダ
        :param source: 作業班情報
        :return: WorkingGroup: 作業班情報
        """
        object_id, data = FactoryModelBuilder._get_id(source)
        return FactoryModelBuilder.build_operating_crew(
            id=object_id,
            name=data.get('name', '?'),
        )

    @staticmethod
    def build_specification(
            id: str,
            name: str,
    ) -> Specification:
        """
        製品仕様情報ビルダ
        :param id: 識別子
        :param name: 名前
        :return: Specification: 製品仕様情報
        """
        return Specification(
            table=FactoryNodeTable.SPECIFICATION.name,
            id=id,
            name=name,
        )

    @staticmethod
    def build_raw_material(
            id: str,
            name: str,
    ) -> RawMaterial:
        """
        原材料情報ビルダ
        :param id: 識別子
        :param name: 名前
        :return: RawMaterial: 原材料情報
        """
        return RawMaterial(
            table=FactoryNodeTable.RAW_MATERIAL.name,
            id=id,
            name=name,
        )

    @staticmethod
    def build_raw_material_from_dict(
            source: dict,
    ) -> RawMaterial:
        object_id, data = FactoryModelBuilder._get_id(source)
        return FactoryModelBuilder.build_raw_material(
            id=object_id,
            name=data.get('name', '?'),
        )

    @staticmethod
    def build_storage(
            id: str,
            name: str,
    ) -> Storage:
        """
        貯蔵庫情報ビルダ
        :param id: 識別子
        :param name: 名前
        :return: Storage: 貯蔵庫情報
        """
        return Storage(
            table=FactoryNodeTable.STORAGE.name,
            id=id,
            name=name,
        )

    @staticmethod
    def build_storage_from_dict(
            source: dict,
    ) -> Storage:
        object_id, data = FactoryModelBuilder._get_id(source)
        return FactoryModelBuilder.build_storage(
            id=object_id,
            name=data.get('name', '?'),
        )

    @staticmethod
    def build_factory(
            id: str,
            name: str,
    ) -> Factory:
        """
        工場情報ビルダ
        :param id: 識別子
        :param name: 名前
        :return: Factory: 工場情報
        """
        return Factory(
            table=FactoryNodeTable.FACTORY.name,
            id=id,
            name=name,
        )

    @staticmethod
    def build_defect_information(
            id: str,
            name: str,
            timestamp: datetime.datetime,
            detail: {} = None
    ) -> DefectInformation:
        """
        欠陥情報ビルダ
        :param id: 識別子
        :param name: 名前
        :param timestamp:  タイムスタンプ
        :param detail:  詳細情報
        :return: DefectInformation: 欠陥情報
        """
        return DefectInformation(
            id=id,
            name=name,
            timestamp=timestamp,
            detail=detail if detail else {}
        )

    @staticmethod
    def build_measurement(
            id: str,
            name: str,
            timestamp: datetime.datetime,
            measurement_values: {}
    ) -> Measurement:
        """
        機器測定値情報ビルダ
        :param id: 識別子
        :param name: 名前
        :param timestamp: 事象発生日時
        :param measurement_values: 測定値情報
        :return: Measurement: 機器測定値情報
        """
        return Measurement(
            table=FactoryNodeTable.MEASUREMENTS.name,
            id=id,
            name=name,
            timestamp=timestamp,
            measurement_values=measurement_values,
        )

    @staticmethod
    def build_relationship(
            relationship: FactoryRelationship,
            from_id: Union[ANode, str],
            to_id: Union[ANode, str],
            timestamp: Optional[datetime.datetime] = None,
            detail: {} = None
    ) -> Relationship:
        """
        関係情報ビルダ
        関係：(from_node)-[relationship]->(to_node)
        :param relationship: 関係名
        :param from_id: 元ノード または 元ノード識別子
        :param to_id: 先ノード または 先ノード識別子
        :param timestamp: タイムスタンプ
        :param detail: 詳細情報
        :return: Relationship: 関係情報
        """
        real_from_id = from_id if isinstance(from_id, str) \
            else from_id.get_compound_id() if isinstance(from_id, ANode) \
            else RuntimeError(f'Invalid parameter "from_id" ({type(from_id)})')
        real_to_id = to_id if isinstance(to_id, str) \
            else to_id.get_compound_id() if isinstance(to_id, ANode) \
            else RuntimeError(f'Invalid parameter "to_id" ({type(to_id)})')

        return (Relationship(
            from_id=real_from_id,
            to_id=real_to_id,
            timestamp=timestamp if timestamp else datetime.datetime.now(),
            relationship=relationship.name,
            detail=detail if detail else {},
        ))

    @staticmethod
    def _get_id(source: dict) -> (str, dict):
        object_id = source.get('id', '?')
        data = source.get('data', {})
        return object_id, data

    @staticmethod
    def build_production_event_message(
            work_id: str,
            mid: str,
            created_by: str,
            production_history: ProductionHistory,
    ) -> ProductionEventMessage:
        """
        工程メッセージビルダ
        :param work_id:  作業識別子
        :param mid: メッセージ識別子
        :param created_by: 工程メッセージ作成元識別子
        :param production_history: 作業履歴
        :return: ProcessMessage: 工程メッセージ
        """
        result: Optional[ProductionEventMessage] = None
        if production_history.operation_type == OperationType.OPERATION_START:
            pass
        elif production_history.operation_type == OperationType.OPERATION_END:
            pass
        elif production_history.operation_type == OperationType.PUT_IN:
            pass
        elif production_history.operation_type == OperationType.PUT_OUT:
            pass
        elif production_history.operation_type == OperationType.CREATED:
            pass
        elif production_history.operation_type == OperationType.FINISHED_PRODUCT:
            pass
        elif production_history.operation_type == OperationType.INSPECTION:
            pass
        elif production_history.operation_type == OperationType.ASSEMBLY:
            pass
        elif production_history.operation_type == OperationType.DEFECT_DETECTION:
            pass
        else:
            raise RuntimeError(f'Invalid operation_type was specified. ({production_history.operation_type})')

        result = ProductionEventMessage(
            mid=mid,
            work_id=work_id,
            timestamp=production_history.timestamp,
            created_by=created_by,
            operation_type=production_history.operation_type,
            product_id=production_history.product.get_compound_id() if production_history.product else '',
            product_type=production_history.product.product_type if production_history.product else None,
            product_status=production_history.status if production_history.status else None,
            storage_id=production_history.storage.get_compound_id() if production_history.storage else None,
            raw_material_id=production_history.raw_material.get_compound_id() if production_history.raw_material else '',
            parts_id=production_history.parts.get_compound_id() if production_history.parts else '',
            product_defect=production_history.detail_info \
                if production_history.operation_type == OperationType.DEFECT_DETECTION else {},
            inspection_result=production_history.detail_info \
                if production_history.operation_type == OperationType.INSPECTION else {},
        )
        return result

    @staticmethod
    def build_production_event_message_from_dict(
            created_by: str,
            source: dict,
    ) -> Optional[ProductionEventMessage]:
        """
        作業履歴情報からProcessMessage情報を生成する
        :param created_by: メッセージ作成元識別子
        :param source: 作業履歴情報
        :return: ProcessMessage: 工程メッセージ
        """
        work_id = source.get('work_id', None)
        timestamp = util.convert_utc_string_to_datetime(source.get('timestamp', '?'))
        data = source.get('data', None)
        if not (work_id and data):
            return None

        operation_type = data.get('work_type') if data.get('work_type', None) else 'NONE'
        product_type = data.get('product_type') if data.get('product_type', None) else 'NONE'
        product_status = data.get('product_status') if data.get('product_status', None) else 'NONE'
        return ProductionEventMessage(
            mid=data.get('mid', ''),
            work_id=work_id,
            created_by=created_by,
            timestamp=timestamp,
            operation_type=OperationType(operation_type),
            product_id=data.get('product_id', '?'),
            product_type=ProductType(product_type),
            product_status=ProductStatus(product_status),
            storage_id=data.get('storage_id', ''),
            raw_material_id=data.get('raw_material_id', ''),
            parts_id=data.get('parts_id', ''),
            inspection_result=data.get('inspection_result', {}),
            product_defect=data.get('product_defect', {}),
        )

    @staticmethod
    def build_measurement_message_from_dict(
            created_by: str,
            source: dict
    ) -> Optional[MeasurementMessage]:
        """
        測定情報ビルダ
        :param created_by: 測定情報作成元識別子
        :param source: 測定情報
        :return: MeasurementMessage: 測定情報
        """
        timestamp_str = source.get('timestamp', None)
        timestamp = util.convert_utc_string_to_datetime(timestamp_str) \
            if timestamp_str else datetime.datetime.now()
        mid = source.get('id', None)
        data = source.get('data', None)
        measurements = data.get('measurements', None)
        if not (mid and data):
            return None
        return MeasurementMessage(
            mid=mid,
            created_by=created_by,
            timestamp=timestamp,
            measurement_values=measurements,
        )
