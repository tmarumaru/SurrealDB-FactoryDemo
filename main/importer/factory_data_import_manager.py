import asyncio
import datetime
import sys
import traceback

import util
from arguments_parser import Params, parse
from helper.db_helper import DBHelper
from importer.factory_data_reader import FactoryDataReader


async def import_factory_data(
        param: Params,
        factory_data_reader: FactoryDataReader
):
    factory = factory_data_reader.factory
    try:
        with DBHelper(
                url=param.url,
                username=param.user,
                password=param.pw,
                database=param.database,
                namespace=param.namespace,
        ) as client:
            # 工場登録
            response = await client.create_one(
                table=factory.table,
                id=factory.id,
                data=factory.get_dict())

            # 製造ライン登録
            for line in factory.production_lines:
                response = await client.create_one(
                    table=line.table,
                    id=line.id,
                    data=line.get_dict())
            print(f'{len(factory.production_lines)} production lines were created.')

            # 貯蔵庫登録
            for storage in factory.storages:
                response = await client.create_one(
                    table=storage.table,
                    id=storage.id,
                    data=storage.get_dict())
            print(f'{len(factory.storages)} storages were created.')

            # 製造ライン機器登録
            for machine in factory.machines:
                response = await client.create_one(
                    table=machine.table,
                    id=machine.id,
                    data={}
                )
                # data=machine.get_dict())
            print(f'{len(factory.machines)} machines were created.')

            # 作業班登録
            for group in factory.operating_crews:
                response = await client.create_one(
                    table=group.table,
                    id=group.id,
                    data=group.get_dict())
            print(f'{len(factory.operating_crews)} operation crews were created.')
            # 原材料登録
            for raw_material in factory.raw_materials:
                response = await client.create_one(
                    table=raw_material.table,
                    id=raw_material.id,
                    data=raw_material.get_dict())
            print(f'{len(factory.raw_materials)} raw materials were created.')

            # 仕掛品・部品・製品登録
            for product in factory.products:
                response = await client.create_one(
                    table=product.table,
                    id=product.id,
                    data=product.get_dict())
            print(f'{len(factory.products)} products were created.')

            # 作業登録
            for work in factory.works:
                response = await client.create_one(
                    table=work.table,
                    id=work.id,
                    data=work.get_dict())
            print(f'{len(factory.works)} works were created.')

            # 検査結果登録
            for inspection_result in factory.inspection_results:
                response = await client.create_one(
                    table=inspection_result.table,
                    id=inspection_result.id,
                    data=inspection_result.get_dict())
            print(f'{len(factory.inspection_results)} Inspection results were created.')

            # 欠陥情報登録
            for defect_info in factory.defect_information:
                response = await client.create_one(
                    table=defect_info.table,
                    id=defect_info.id,
                    data=defect_info.get_dict())
            print(f'{len(factory.defect_information)} defect information were created.')

            for measurement in factory.measurement_messages:
                response = await client.create_one(
                    table=measurement.table,
                    id=measurement.id,
                    data=measurement.get_dict())
            print(f'{len(factory.measurement_messages)} measurements information were created. ')

            # 関係登録
            for relationship in factory.relationships:
                response = await client.relate(
                    from_id=relationship.from_id,
                    to_id=relationship.to_id,
                    relation=relationship.relationship,
                    timestamp=util.to_iso88601_datatime(relationship.timestamp),
                )
            print(f'{len(factory.relationships)} relationships were created.')

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f'Exception was occurred. ({e})')


def main(params: Params):
    try:
        data_reader = FactoryDataReader(json_data_file_path=params.json_file)
        data_reader.rebuild()
        # 工場データをSurrealDBへ移入する
        s = datetime.datetime.now()
        print(f'{s.isoformat()}: started importing factory data into SurrealDB.')
        asyncio.run(import_factory_data(param=params, factory_data_reader=data_reader))
        e = datetime.datetime.now()
        print(f'{e.isoformat()}: finished importing factory data into SurrealDB. elapsed time: {e - s}')
    except Exception as e:
        print(f'{e}')
        traceback.print_exc()


if __name__ == '__main__':
    args = sys.argv
    params = parse(args=args[1:])
    main(params=params)
