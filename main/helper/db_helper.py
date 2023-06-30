from typing import Any, Optional

from surrealdb import SurrealHTTP


class DBHelper:
    """
    SurrealDB Client Wrapper
    """

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
        self.client = None
        self.url = url
        self.namespace = namespace
        self.database = database
        self.username = username
        self.password = password

    def __enter__(self):
        self.client = SurrealHTTP(
            url=self.url,
            namespace=self.namespace,
            database=self.database,
            username=self.username,
            password=self.password
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        pass

    async def relate(
            self,
            from_id: str,
            to_id: str,
            relation: str,
            timestamp: Optional[str] = None,
    ) -> Any:
        """
        リレーションシップ登録
        (FROMノード）-[関係]->(TOノード)
        :param from_id: FROMノード識別子
        :param to_id: TOノード識別子
        :param relation: 関係
        :param timestamp: タイムスタンプ
        :return:
        """
        timestamp_str = f'type::datetime("{timestamp}")' if timestamp else 'time::now()'
        content = {
            'data': {
                'timestamp': '$timestamp',
            }
        }
        sql = f'let $timestamp = {timestamp_str} ;' \
              + f'RELATE {from_id}->{relation}->{to_id} CONTENT ' \
              + '{ data: {timestamp: ' \
              + f'"{timestamp}" ' \
              + '}}'
        response = await self.client.query(sql)
        return response

    async def create_one(
            self,
            table: str,
            id: str,
            data: Any
    ):
        """
        1レコード登録
        :param table: 対象テーブル識別子
        :param id: レコード識別子
        :param data: 詳細データ
        :return: SurrealDB レスポンス
        """
        response = await self.client.create(thing=table + ':' + id, data=data)
        return response

    async def execute(
            self,
            query: str
    ):
        """
        SurrealQL実行
        :param query: SurrealQL文字列
        :return: SurrealDBからのレスポンス
        """
        response = await self.client.query(sql=query)
        result = response[0].get('result') if len(response) > 0 and response[0].get('result', None) else None
        return result






