import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_DATA_DIR = 'json_data'
_JSON_FILE_NAME = 'factory_data.json'
_STREAMLIT_STARTER = '/opt/app/main/dashboard_main.py',


@dataclass
class Params:
    cmd: str                        # サブコマンド名('simulate', 'import')
    host: str                       # SurrealDB ホスト名
    port: int                       # SurrealDB ポート番号
    user: str                       # SurrealDB 認証ユーザ
    pw: str                         # SurrealDB 認証ユーザ パスワード
    database: str                   # SurrealDB 使用する名前空間名
    namespace: str                  # SurrealDB 使用するデータベース名
    json_file: str                  # 製造情報jsonファイルのパス
    clock: int                      # simulate で使用するシミュレータのクロック値

    @property
    def url(self) -> str:
        return f'http://{self.host}:{self.port:04d}'


def set_common_option(parser) -> Any:
    """ 共通オプション 定義 """

    parser.add_argument(
        '--server',
        dest='server',
        type=str,
        action='store',
        default='localhost',
        help='Specify SurrealDB hostname'
    )
    parser.add_argument(
        '--port',
        dest='port',
        type=int,
        action='store',
        default=8000,
        help='Specify SurrealDB port number'
    )
    parser.add_argument(
        '--user',
        dest='user',
        type=str,
        action='store',
        default='root',
        help='Specify the user to logging in to SurrealDB'
    )
    parser.add_argument(
        '--pw',
        dest='pw',
        type=str,
        action='store',
        default='root',
        help='Specifies the password of the user logging into surrealdb'
    )
    parser.add_argument(
        '--database',
        dest='database',
        type=str,
        action='store',
        default='test',
        help='Specify the database name to use'
    )
    parser.add_argument(
        '--namespace',
        dest='namespace',
        type=str,
        action='store',
        default='test',
        help='Specify the namespace to use'
    )
    return parser


def parse(
        args: []
) -> Params:
    """
    引数解釈
    :param args: コマンド引数
    :return: 解釈結果情報
    """
    parser = argparse.ArgumentParser()
    set_common_option(parser=parser)
    cwd = Path.cwd()
    json_data_file_path = Path.joinpath(cwd.parent, _DATA_DIR, _JSON_FILE_NAME)
    subparser = parser.add_subparsers(dest='cmd')
    simulate_parser = subparser.add_parser('simulate')
    simulate_parser.add_argument(
        '--file',
        dest='file',
        type=str,
        action='store',
        default=json_data_file_path,
        help='Specify the path of the json-data file that stores the factory data'
    )
    simulate_parser.add_argument(
        '--clock',
        dest='clock',
        type=int,
        action='store',
        default=500,
        help='Specify the clock on which to run the simulation'
    )

    import_parser = subparser.add_parser('import')
    import_parser.add_argument(
        '--file',
        dest='file',
        type=str,
        action='store',
        default=json_data_file_path,
        help='Specify the path of the json data file where the factory data is stored'
    )
    set_common_option(parser=import_parser)

    accepted_args = parser.parse_args(args=args)
    params = Params(
        cmd=accepted_args.cmd,
        json_file=accepted_args.file if accepted_args.cmd == 'simulate' or accepted_args.cmd == 'import' else '',
        clock=accepted_args.clock if accepted_args.cmd == 'simulate' else 0,
        host=accepted_args.server if accepted_args.cmd != 'simulate' else '',
        port=accepted_args.port if accepted_args.cmd != 'simulate' else '',
        user=accepted_args.user if accepted_args.cmd != 'simulate' else '',
        pw=accepted_args.pw if accepted_args.cmd != 'simulate' else '',
        database=accepted_args.database if accepted_args.cmd != 'simulate' else '',
        namespace=accepted_args.namespace if accepted_args.cmd != 'simulate' else '',
    )
    return params
