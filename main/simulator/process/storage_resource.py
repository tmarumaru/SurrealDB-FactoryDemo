from simpy import Store, Environment

from simulator.factory_models import Storage


class StorageResource(Store):
    """
    貯蔵庫、倉庫クラス
    仕掛品、半製品、製品をＦＩＦＯで管理する
    """
    def __init__(
            self,
            storage: Storage,
            env: Environment,
            capacity=float('inf')
    ):
        """
        コンストラクタ
        :param storage: 貯蔵庫情報
        :param env: Simpy.Environment
        :param capacity: 貯蔵庫容量（省略時は無限)
        """
        super(StorageResource, self).__init__(env=env, capacity=capacity)
        self.storage = storage

    def get_compound_id(self) -> str:
        return self.storage.get_compound_id()
