from typing import Optional, List

from helper.db_helper import DBHelper
from helper.surrealdb_sql_def import GET_PRODUCT_INFO, GET_PRODUCTION_HISTORIES, GET_PRODUCTION_YIELD, \
    GET_PRODUCTION_WORK_HISTORIES, GET_TRANSFER_WORK_HISTORIES, GET_PROCESSING_TIME, PARAM_PRODUCTION_LINE1, \
    PARAM_PRODUCTION_LINE2, GET_RELATIONSHIPS_ABOUT_NODE, EXCLUSION_TABLE_NAMES, GET_MEASUREMENTS_VALUE


class FactoryDBHelper(DBHelper):

    def __init__(
            self,
            url: str = 'http://localhost:8000',
            namespace: str = 'test',
            database: str = 'test',
            username: str = 'root',
            password: str = 'root'
    ):
        """
        コンストラクタ
        :param url: SurrealDB server url
        :param namespace: 名前空間
        :param database: データベース名
        :param username: 認証ユーザ
        :param password: パスワード
        """
        super(FactoryDBHelper, self).__init__(
            url=url,
            namespace=namespace,
            database=database,
            username=username,
            password=password
        )

    def __enter__(self):
        super(FactoryDBHelper, self).__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        super(FactoryDBHelper, self).__exit__(exc_type, exc_val, exc_tb)

    def _close(self):
        pass

    async def exec_sql(
            self,
            sql: str,
    ) -> {}:
        """
        SurrealQL実行
        :param sql: SurrealQL文字列
        :return: SurrealDBからのレスポンス
        """
        response = None
        try:
            response = await self.execute(query=sql)
        except Exception as e:
            print(f'{e}')
            return {}
        return response

    async def get_all_records_from_table(
            self,
            table: str,
    ) -> {}:
        """
        指定されたテーブルの全レコード取得
        :param table: テーブル識別子
        :return: レコード群
        """
        sql = f"SELECT * FROM {table};"
        result = await self.exec_sql(sql=sql)
        return result

    async def get_relationships(
            self,
            relationships: List[str],
    ) -> {}:
        """
        指定された関係情報を取得する
        :param relationships: 取得する関係リスト
        :return: 関係情報群
        """
        result = {}
        for relationship in [r for r in relationships]:
            sql = f"SELECT * FROM {relationship};"
            response = await self.exec_sql(sql=sql)
            result[relationship] = response
        return result

    async def get_neighboring_nodes(
            self,
            table: Optional[str] = None,
            object_id: Optional[str] = None,
    ) -> ({}, {}):
        """
        隣接ノード情報取得
        :param table: テーブル識別子
        :param object_id: 中心ノード識別子
        :return: 隣接ノード情報群 (関係情報群、ノード情報群）
        """
        if not (object_id and table):
            return {}, {}
        sql = f'SELECT <->(? AS relationship)<->(? AS nodes) FROM {table} WHERE id="{object_id}";'
        response = await self.exec_sql(sql=sql)
        if len(response) <= 0:
            return {}, {}
        return response[0].get('relationship', {}), response[0].get('nodes', {})

    async def get_product_data_from_db(
            self
    ) -> {}:
        """
        全製品情報取得
        :return: 製品情報群
        """
        sql = f"{GET_PRODUCT_INFO}"
        result = await self.exec_sql(sql=sql)
        return result

    async def get_work_histories(
            self,
    ) -> {}:
        """
        全作業情報取得
        :return: 作業情報群
        """
        sql = f"{GET_PRODUCTION_HISTORIES};"
        result = await self.exec_sql(sql=sql)
        return result

    async def get_production_yield(
            self,
    ) -> {}:
        """
        製造実績情報取得
        :return: 製造実績
        """
        sql = f'{GET_PRODUCTION_YIELD}'
        result = await self.exec_sql(sql=sql)
        return result

    async def get_product_work_histories(
            self,
    ) -> {}:
        """
        全製品の作業履歴取得
        :return: 作業情報群
        """
        sql = GET_PRODUCTION_WORK_HISTORIES + ';'
        result = await self.exec_sql(sql=sql)
        return result

    async def get_transfer_work_histories(
            self,
    ) -> {}:
        """
        全移動作業情報取得
        :return: 移動作業情報
        """
        sql = GET_TRANSFER_WORK_HISTORIES + ';'
        result = await self.exec_sql(sql=sql)
        return result

    async def get_production_time_records(
            self,
            last_process: str,
            first_process: str,
    ) -> {}:
        """
        製造時間取得
        :param last_process: 開始製造ライン識別子
        :param first_process: 終了製造ライン識別子
        :return: 製造時間情報
        """
        sql = (GET_PROCESSING_TIME
               .replace(f'{PARAM_PRODUCTION_LINE1}', first_process)) \
                  .replace(f'{PARAM_PRODUCTION_LINE2}', last_process) + ';'
        result = await self.exec_sql(sql=sql)
        return result

    async def get_relationships_of_node(
            self,
            node_id: str,
            relationships: [] = None,
            nodes: [] = None,
            traversed_nodes: [] = None,
    ) -> ([{}], [str], [str]):
        """
        指定されたノードに関連する「関係」と「ノード」を検索する
        :param node_id:          起点ノード
        :param relationships:    省略引数. 検索された関係.
        :param nodes:            省略引数. 検索されたノード群
        :param traversed_nodes:  省略引数. 検索起点となったノード群
        :return: (検索された関係群: [{}], 検索されたノード群: [str], 検索起点ノード群: [str])
        """
        _relationships = relationships if relationships else []
        _nodes = nodes if nodes else []
        _traversed_nodes = traversed_nodes if traversed_nodes else []
        _found_nodes = []
        while True:
            _table = node_id.split(':')[0]
            if _table in EXCLUSION_TABLE_NAMES:
                break
            if node_id in _traversed_nodes:
                break

            _traversed_nodes.append(node_id)
            if node_id not in _nodes:
                _nodes.append(node_id)

            _sql = GET_RELATIONSHIPS_ABOUT_NODE.format(_table, node_id)
            _response = await self.exec_sql(sql=_sql)
            if not _response or len(_response) <= 0:
                break
            for _r in _response[0].get('relationship', []):
                _rid = (_r.get('id', '?'))
                if not any(map(lambda x: x.get('id', '') == _rid, _relationships)):
                    _relationships.append(_r)
                else:
                    continue
                for _n in [_r.get('in', None), _r.get('out', None)]:
                    if _n not in _nodes:
                        _nodes.append(_n)
                        _found_nodes.append(_n)

            for _n in _found_nodes:
                if not _n.split(':')[0] in EXCLUSION_TABLE_NAMES and (_n not in _traversed_nodes):
                    _relationships, _nodes, _traversed_nodes = \
                        await self.get_relationships_of_node(
                            node_id=_n,
                            relationships=_relationships,
                            nodes=_nodes,
                            traversed_nodes=_traversed_nodes,
                        )
                    _traversed_nodes.append(_n)
        return _relationships, _nodes, _traversed_nodes

    async def get_measurements_values(
            self,
    ) -> {}:
        """
        機器の測定情報取得
        :return: 測定情報群
        """
        sql = GET_MEASUREMENTS_VALUE + ';'
        result = await self.exec_sql(sql=sql)
        return result
