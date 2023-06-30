import datetime
import json
from dataclasses import dataclass, field
from typing import Any, List

import util
from simulator.factory_models import OperationType, Product, ProductStatus, Storage, RawMaterial, ProductionLine


@dataclass
class ProductionHistory:
    timestamp: datetime.datetime
    operation_type: OperationType
    product: Product = field(default=None)
    status: ProductStatus = field(default=None)
    storage: Storage = field(default=None)
    extra_storage: Storage = field(default=None)
    parts: Product = field(default=None)
    raw_material: RawMaterial = field(default=None)
    detail_info: {} = field(default=None)

    def get_json(self):
        return {
            'timestamp': util.to_iso88601_datatime(self.timestamp),
            'operation_type': self.operation_type.name,
            'product': self.product.get_compound_id() if self.product else '',
            'storage': self.storage.get_compound_id() if self.storage else '',
            'extra_storage': self.extra_storage.get_compound_id() if self.extra_storage else '',
            'parts': self.parts.get_compound_id() if self.parts else '',
            'raw_material': self.raw_material.get_compound_id() if self.raw_material else '',
            'detail_info': self.detail_info if self.detail_info else {},
        }


@dataclass()
class ProductionHistoryManager:
    production_line: ProductionLine
    in_storage: Storage
    out_storage: Storage
    repair_storage: Storage
    extra_storage: Storage = field(default=None)
    product: Product = field(default=None)
    _production_histories: List[ProductionHistory] = field(default_factory=lambda: [])

    class _Encoder(json.JSONEncoder):
        def default(self, o: Any) -> Any:
            if isinstance(o, ProductionHistory):
                return o.get_json
            elif isinstance(o, datetime.datetime):
                return util.to_iso88601_datatime(o)
            else:
                return str(o)

    def get_production_histories(self):
        return self._production_histories

    def add_production_history(
            self,
            production_history: ProductionHistory
    ):
        self._production_histories.append(production_history)

    def get_json(self):
        result = {
            'production_line_id': self.production_line.get_compound_id(),
            'in_storage_id': self.in_storage.get_compound_id(),
            'out_storage_id': self.out_storage.get_compound_id(),
            'repair_storage_id': self.repair_storage.get_compound_id(),
            'extra_storage_id': self.extra_storage.get_compound_id() if self.extra_storage else '',
            'product_id': self.product.get_compound_id() if self.product else '',
            'operations': json.dumps(self._production_histories, cls=ProductionHistoryManager._Encoder)
        }
        return result
