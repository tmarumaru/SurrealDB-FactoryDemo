import sys

from arguments_parser import parse, Params
from importer import factory_data_import_manager
from simulator import simulator_manager


def simulate_command(params: Params):
    simulator_manager.main(params)


def import_command(params: Params):
    factory_data_import_manager.main(params)


SUB_COMMANDS = {
    'simulate': simulate_command,
    'import': import_command,
}

if __name__ == '__main__':
    """
    simulatorおよびimporterの主処理
    
    [引数]  
    simulate 
        [--clock 500]                                  製造ラインシミュレータ クロック
        [--file PJ-DIR/json_data/factory_data.json]    製造データ格納jsonファイルパス 
        
    import  
        [--file PJ-DIR/json_data/factory_data.json]    製造データ格納jsonファイルパス 
        [--server localhost]                           SurrealDB ホスト名
        [--prot 8000]                                  SurrealDB ポート番号
        [--namespace test]                             SurrealDB 名前空間名
        [--database test]                              SurrealDB データベース名
        [--user root]                                  SurrealDB 認証ユーザ
        [--PW root]                                    SurrealDB 認証ユーザ パスワード
    ※PJ-DIR: project root directory
    """
    args = sys.argv
    params = parse(args=args[1:])
    if SUB_COMMANDS.get(params.cmd, None):
        SUB_COMMANDS.get(params.cmd)(params)
