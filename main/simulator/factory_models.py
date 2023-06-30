import datetime
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

import util


class FactoryNodeTable(Enum):
    """
    工場構成要素定義(ノード）
    """
    FACTORY = 'FACTORY'                     # 工場
    RAW_MATERIAL = 'RAW_MATERIAL'           # 原材料
    PRODUCTION_LINE = 'PRODUCTION_LINE'     # 製造ライン
    STORAGE = 'STORAGE'                     # 貯蔵庫
    MACHINE = 'MACHINE'                     # 製造機器
    OPERATING_CREW = 'OPERATING_CREW'       # 作業班
    PRODUCT = 'PRODUCT'                     # 製品・部品・仕掛品
    WORK = 'WORK'                           # 製造ライン上の作業
    # 製造ラインの作業で生成される情報
    INSPECTION_RESULT = 'INSPECTION_RESULT'     # 検査結果
    DEFECT_INFORMATION = 'DEFECT_INFORMATION'   # 欠陥情報

    MEASUREMENTS = 'MEASUREMENTS'           # 機器測定値
    SPECIFICATION = 'SPECIFICATION'         # 製品仕様
    MANUFACTURER = 'MANUFACTURER'           # 原材料供給者
    PROCESS_MESSAGE = 'PROCESS_MESSAGE'     # 工程メッセージ


class FactoryRelationship(Enum):
    """
    関係定義
    """
    CONSISTS_OF = 'CONSISTS_OF'             # A-[CONSISTS_OF]->B  BはAの構成要素
    HAS_WORKERS = 'HAS_WORKERS'             # A-[HAS_WORKERS]->B  Aは作業班Bを持つ
    RECORDS = 'RECORDS'                     # A-[RECORDS]->B AはBを記録する
    PURCHASED_FROM = 'PURCHASED_FROM'       # A-[PURCHASED_FROM]->B AはBから購入する
    PRODUCED_BY = 'PRODUCED_BY'             # A-[PRODUCED_BY]->B  AはBによって作成される
    EXECUTES = 'EXECUTES'                   # A-[EXECUTES]->B  AはBを実行する
    USED_TO_PRODUCE = 'USED_TO_PRODUCE'     # A-[USED_TO_PRODUCE]->B AはBを作るために使用される
    COMPRISED_OF = 'COMPRISED_OF'           # A-[COMPRISED_OF]->B  AはBから構成される
    ASSEMBLED_BY = 'ASSEMBLED_BY'           # A-[ASSEMBLED_BY]->B AはBを組み立てる
    STARTED_BY = 'STARTED_BY'               # A-[STARTED_BY]->B AはBによって開始される
    ENDED_BY = 'ENDED_BY'                   # A-[ENDED_BY}->B AはBによって終了される
    TESTED_BY = 'TESTED_BY'                 # A-[TESTED_BY]->B AはBによって検査される
    TEST_RESULT_OF = 'TEST_RESULT_OF'       # A-[TEST_RESULT_OF]->B AはBの検査結果
    DEFECT_DETECTED_BY = 'DEFECT_DETECTED_BY'  # A-[DEFECT_DETECTED_BY]->B BがAの欠陥を検知する
    HAS_DEFECT = 'HAS_DEFECT'               # A-[HAS_DEFECT]->B AはBの欠陥情報を持つ
    BECOMES = 'BECOMES'                     # A-[BECOMES]->B AはBに成る
    INSPECTED_BY = 'INSPECTED_BY'           # A-[INSPECTED_BY]->B AはBによって製品検査される
    MOVE_FROM = 'MOVE_FROM'                 # A-[MOVE_FROM]->B BがAから何かを移動した
    MOVE_TO = 'MOVE_TO'                     # A-[MOVE_TO]->B BがAへ何かを移動した
    MOVED_BY = 'MOVED_BY'                   # A-[MOVED_BY]->B AはBによって移動された


class OperationType(Enum):
    """
    作業種別定義
    """
    OPERATION_START = 'OPERATION_START'     # 工程開始
    OPERATION_END = 'OPERATION_END'         # 工程終了
    CREATED = 'CREATED'                     # 仕掛品生成
    FINISHED_PRODUCT = 'FINISHED_PRODUCT'   # 製品完成
    ASSEMBLY = 'ASSEMBLY'                   # 組立
    INSPECTION = 'INSPECTION'               # 検査
    DEFECT_DETECTION = 'DEFECT_DETECTION'   # 欠陥検出
    PUT_IN = 'PUT_IN'                       # 移動 製造ライン⇒貯蔵庫
    PUT_OUT = 'PUT_OUT'                     # 移動 貯蔵庫⇒製造ライン
    SPOILAGE = 'SPOILAGE'                   # 仕掛品廃棄
    NONE = 'NONE'                           # 意味なし


class ProductStatus(Enum):
    """
    製品状態定義
    """
    WORK_IN_PROGRESS = 'WORK_IN_PROGRESS'   # 仕掛品
    FINISHED_PRODUCT = 'FINISHED_PRODUCT'   # 製品
    DEFECT_DETECTION = 'DEFECT_DETECTION'   # 欠陥品
    REPAIR = 'REPAIR'                       # 修理中
    SPOILAGE = 'SPOILAGE'                   # 廃棄
    NONE = 'NONE'                           # 意味なし


class ProductType(Enum):
    """
    製品種別
    """
    PRODUCT = 'PRODUCT'                     # 製品
    PARTS = 'PARTS'                         # 部品
    WIP = 'WIP'                             # 仕掛品
    NONE = 'NONE'                           # 意味なし


class WorkType(Enum):
    NormalWork = 'NormalWork'               # 製造作業
    TransferWork = 'TransferWork'           # 移動作業
    InspectionWork = 'InspectionWork'       # 検査作業
    NONE = 'NONE'                           # 意味なし


class MessageType(Enum):
    """
    メッセージ対象定義
    """
    PROCESS = 'PROCESS'                     # 工程
    MEASUREMENT = 'MEASUREMENT'             # 機器
    NONE = 'NONE'                           # 意味なし


class ANode:
    """
    ノード基底クラス
    """

    @abstractmethod
    def get_dict(self) -> {}:
        pass

    @staticmethod
    def gen_compound_id(table: str, data_id: str) -> str:
        return f'{table}:{data_id}'

    @abstractmethod
    def get_compound_id(self):
        pass


@dataclass
class AProduct(ANode, ABC):
    """
    製品（仕掛品、半製品、製品）情報定義
    """
    table: str                              # テーブル名
    id: str                                 # 製品識別子
    name: str                               # 製品名
    product_type: ProductType               # 製品型
    status: ProductStatus                   # 製品状態
    specification_id: str                   # 製品仕様

    def get_dict(self):
        return {
            'id': self.id,
            'data': {
                'name': self.name,
                'type': self.product_type.name,
                'status': self.status.name,
                'specification': self.specification_id,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


class Product(AProduct):
    """
    製品情報定義
    """

    def __init__(
            self,
            id: str,                        # 製品識別子
            name: str,                      # 名称
            product_type: ProductType,      # 製品型
            status: ProductStatus,          # 製品状態
            specification_id: Optional[str] = None  # 製品仕様
    ):
        super(Product, self).__init__(
            table=FactoryNodeTable.PRODUCT.name,
            id=id,
            name=name,
            product_type=product_type,
            status=status,
            specification_id=specification_id if specification_id else '',
        )


@dataclass
class Machine(ANode):
    """
    製造用治具情報定義
    """
    table: str                              # テーブル名
    id: str                                 # 治具識別子
    name: str                               # 治具名

    def get_dict(self):
        return {
            'id': self.id,
            'data': {
                'name': self.name,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class ProductionLine(ANode):
    """
    製造ライン情報定義
    """
    table: str                              # テーブル名
    id: str                                 # 製造ライン識別子
    name: str                               # 製造ライン名
    specification_id: str                   # 製品仕様
    process_id: str                         # 工程識別子
    machines: List[Machine]                 # 製造用治具識別子群
    working_group_id: str                   # 担当作業班識別子

    def get_dict(self):
        return {
            'id': self.id,
            'data': {
                'name': self.name,
                'process_id': self.process_id,
                'machines': [machine.get_compound_id() for machine in self.machines],
                'working_group_id': self.working_group_id
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class Work(ANode):
    """
    作業定義
    """
    table: str                              # テーブル名
    id: str                                 # 作業識別子
    name: str                               # 作業名
    work_type: WorkType                     # 作業種別
    created_by: str                         # 作成元

    def get_dict(self):
        return {
            'id': self.id,
            'data': {
                'name': self.name,
                'type': self.work_type.name,
                'created_by': self.created_by,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class Specification(ANode):
    """
    製品仕様定義
    """
    table: str                              # テーブル名
    id: str                                 # 製品仕様識別子
    name: str                               # 製品仕様名

    def get_dict(self):
        return {
            'id': self.id,
            'data': {
                'name': self.name,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class OperatingCrew(ANode):
    """
    作業班定義
    """
    table: str                              # テーブル名
    id: str                                 # 作業班識別子
    name: str                               # 作業班名

    def get_dict(self) -> {}:
        return {
            'id': self.id,
            'data': {
                'name': self.name,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class RawMaterial(ANode):
    """
    原材料定義
    """
    table: str                              # テーブル名
    id: str                                 # 原材料識別子
    name: str                               # 原材料名

    def get_dict(self) -> {}:
        return {
            'id': self.id,
            'data': {
                'name': self.name,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class Storage(ANode):
    """
    貯蔵庫情報定義
    """
    table: str                              # テーブル名
    id: str                                 # 貯蔵庫識別子
    name: str                               # 貯蔵庫名

    def get_dict(self) -> {}:
        return {
            'id': self.id,
            'data': {
                'name': self.name,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class Relationship:
    """
    関係情報定義
    """
    from_id: str                            # 関係元
    to_id: str                              # 関係先
    relationship: str                       # 関係名
    timestamp: datetime.datetime            # タイムスタンプ
    detail: {}                              # 詳細情報


@dataclass
class Measurement(ANode):
    table: str                              # テーブル名
    id: str                                 # 測定値識別子
    name: str                               # 装置名
    timestamp: datetime.datetime            # タイムスタンプ
    measurement_values: {}                  # 測定値

    def get_dict(self):
        return {
            'id': self.id,
            'data': {
                'name': self.name,
                'timestamp': util.to_iso88601_datatime(self.timestamp),
                'measurement_values': self.measurement_values
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class AResult(ANode):
    """
    作業結果情報
    """
    table: str                              # テーブル名
    id: str                                 # 検査結果識別子
    name: str                               # 検査名
    timestamp: datetime.datetime            # タイムスタンプ
    detail: {}                              # 詳細情報

    def get_dict(self):
        return {
            'id': self.id,
            'data': {
                'name': self.name,
                'detail': self.detail,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


class InspectionResult(AResult):
    """
    検査結果
    """

    def __init__(
            self,
            id: str,
            name: str,
            timestamp: datetime.datetime,
            detail: {},
    ):
        """
        検査結果情報
        :param id: 識別子
        :param name: 名称
        :param timestamp: タイムスタンプ
        :param detail: 詳細情報
        """
        super(InspectionResult, self).__init__(
            table=FactoryNodeTable.INSPECTION_RESULT.name,
            id=id,
            name=name,
            timestamp=timestamp,
            detail=detail,
        )


class DefectInformation(AResult):
    """
    欠陥情報
    """

    def __init__(
            self,
            id: str,
            name: str,
            timestamp: datetime.datetime,
            detail: {},
    ):
        """
        欠陥情報
        :param id: 識別子
        :param name: 名称
        :param timestamp: タイムスタンプ
        :param detail: 詳細情報
        """
        super(DefectInformation, self).__init__(
            table=FactoryNodeTable.DEFECT_INFORMATION.name,
            id=id,
            name=name,
            timestamp=timestamp,
            detail=detail,
        )


# detail_info 定義
DETAIL_INFO_PRODUCTION_LINE_ID = 'production_line_id'
DETAIL_INFO_PRODUCT_ID = 'product_id'
DETAIL_INFO_STORAGE_ID = 'storage_id'
DETAIL_INFO_PROCESS_STATUS = 'work_type'
DETAIL_INFO_MEASUREMENTS = 'measurements'
DETAIL_INFO_PRODUCT_TYPE = 'product_type'
DETAIL_INFO_PRODUCT_STATUS = 'product_status'
DETAIL_INFO_DEFECT = 'product_defect'
DETAIL_INFO_RAW_MATERIAL = 'raw_material_id'
DETAIL_INFO_PARTS = 'parts_id'
DETAIL_INF_OPERATION = 'operation'
DETAIL_INFO_INSPECTION_RESULT = 'inspection_result'
DETAIL_INFO_MID = 'mid'


@dataclass
class AMessage(ANode, ABC):
    """ 抽象メッセージ定義 """
    table: str                                  # テーブル名
    id: str                                     # メッセージ識別子
    message_type: MessageType                   # メッセージ型
    created_by: str                             # 発生源
    timestamp: datetime.datetime                # 発生日時
    work_id: str = field(default='')            # 作業識別子
    data: {} = field(default=None)              # 詳細情報

    def get_dict(self):
        """ 辞書情報取得"""
        return {
            'id': self.id,
            'work_id': self.work_id,
            'message_type': self.message_type.name,
            'timestamp': util.to_iso88601_datatime(self.timestamp),
            'data': self.data if self.data else {},
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


class ProductionEventMessage(AMessage, ABC):
    """ 製造ライン事象メッセージ定義 """

    def __init__(
            self,
            mid: str,
            created_by: str,
            work_id: str,
            timestamp: datetime.datetime,
            operation_type: OperationType,
            product_id: str,
            product_type: Optional[ProductType] = None,
            product_status: Optional[ProductStatus] = None,
            storage_id: Optional[str] = None,
            raw_material_id: Optional[str] = None,
            parts_id: Optional[str] = None,
            product_defect: Optional[dict] = None,
            inspection_result: Optional[dict] = None,
    ):
        """
        コンストラクタ
        :param mid:             メッセージ識別子
        :param created_by:      メッセージ作成元製造ライン識別子
        :param timestamp:       メッセージ事象発生日時
        :param operation_type:  処理種別
        :param product_id:      仕掛品・半製品・製品識別子
        :param product_status:  仕掛品・半製品・製品状態
        :param raw_material_id:    原材料識別子
        :param parts_id:           組立される半製品識別子
        :param product_defect:  検出された欠陥情報
        """
        super(ProductionEventMessage, self).__init__(
            table=FactoryNodeTable.PROCESS_MESSAGE.name,
            id=mid,
            work_id=work_id,
            message_type=MessageType.PROCESS,
            created_by=created_by,
            timestamp=timestamp,
            data={
                DETAIL_INFO_MID: mid,
                DETAIL_INFO_PROCESS_STATUS: operation_type.name,
                DETAIL_INFO_PRODUCT_ID: product_id,
                DETAIL_INFO_PRODUCT_TYPE: product_type.name if product_type else '',
                DETAIL_INFO_PRODUCT_STATUS: product_status.name if product_status else '',
                DETAIL_INFO_INSPECTION_RESULT: inspection_result if inspection_result else {},
                DETAIL_INFO_DEFECT: product_defect if product_defect else {},
                DETAIL_INFO_RAW_MATERIAL: raw_material_id if raw_material_id else '',
                DETAIL_INFO_PARTS: parts_id if parts_id else '',
                DETAIL_INFO_STORAGE_ID: storage_id if storage_id else '',
            }
        )
        self.mid = mid
        self.work_id = work_id
        self.operation_type = operation_type
        self.product_id = product_id
        self.product_status = product_status
        self.raw_material = raw_material_id
        self.parts = parts_id
        self.product_defect = product_defect
        self.inspection_result = inspection_result
        self.storage_id = storage_id
        self.created_by = created_by


class MeasurementMessage(AMessage, ABC):
    """ 製造ライン機器（センサー等）事象メッセージ定義 """

    def __init__(
            self,
            mid: str,
            created_by: str,
            measurement_values: {},
            timestamp: datetime.datetime,
    ):
        """
        コンストラクタ
        :param mid:                 メッセージ識別子
        :param created_by:          機器識別子
        :param measurement_values:  測定値
        :param timestamp:           測定日時
        """
        super(MeasurementMessage, self).__init__(
            table=FactoryNodeTable.MEASUREMENTS.name,
            id=mid,
            message_type=MessageType.MEASUREMENT,
            created_by=created_by,
            timestamp=timestamp,
            data={
                DETAIL_INFO_MEASUREMENTS: measurement_values,
            }
        )

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)


@dataclass
class WorkOperation:
    """
    製造ラインでの作業情報定義
    """
    operation_type: OperationType                       # 作業種別
    timestamp: datetime.datetime                        # タイムスタンプ
    product: Product = field(default=None)              # 対象仕掛品
    raw_material: RawMaterial = field(default=None)     # 原材料
    inspection_result: {} = field(default=None)         # 検査結果
    defect_information: {} = field(default=None)        # 欠陥情報


@dataclass
class Factory(ANode):
    """
    工場情報定義
    """
    table: str                                          # テーブル名
    id: str                                             # 工場識別子
    name: str                                           # 工場名

    production_lines: List[ProductionLine] = field(default_factory=list)            # 製造ライン情報
    machines: List[Machine] = field(default_factory=list)                           # 製造ライン 機器情報
    storages: List[Storage] = field(default_factory=list)                           # 貯蔵庫情報
    raw_materials: List[RawMaterial] = field(default_factory=list)                  # 原材料情報
    operating_crews: List[OperatingCrew] = field(default_factory=list)              # 作業班情報
    products: List[Product] = field(default_factory=list)                           # 製品（仕掛品、部品）情報
    works: List[Work] = field(default_factory=list)                                 # 作業情報
    measurement_messages: List[MeasurementMessage] = field(default_factory=list)    # 機器 測定値情報
    inspection_results: List[InspectionResult] = field(default_factory=list)        # 検査結果情報
    defect_information: List[DefectInformation] = field(default_factory=list)       # 欠陥情報
    process_messages: List[ProductionEventMessage] = field(default_factory=list)    # 処理メッセージ
    specifications: List[Specification] = field(default_factory=list)               # 製品仕様情報
    relationships: List[Relationship] = field(default_factory=list)                 # グラフデータ関係情報

    def get_dict(self):
        return {
            'id': self.id,
            'data': {
                'name': self.name,
            }
        }

    def get_compound_id(self) -> str:
        return self.gen_compound_id(table=self.table, data_id=self.id)

