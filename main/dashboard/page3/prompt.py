"""
OpenAI API prompt for converting from 日本語 to SurrealQL
"""
from texttable import Texttable

# GPT-3.5 model_name="text-davinci-003"用 プロンプト
# 目的： 日本語から SurrealQL言語を生成する
CONVERT_NL_TO_SURREALQL_PROMPT_jp = (
    '日本語からSurrealQLへの変換:\n'

    '#製品 product_id の作業が実行された製造ラインを取得する\n'
    'SELECT ->STARTED_BY->WORK<-EXECUTES<-PRODUCTION_LINE AS production_line FROM PRODUCT WHERE id = "product_id" ;\n'

    '#製品 product_id の作業が実行された製造ラインを取得する\n'
    'SELECT ->ENDED_BY->WORK<-EXECUTES<-PRODUCTION_LINE AS production_line FROM PRODUCT WHERE id = "product_id" ;\n'

    '#製品の作業を取得する\n'
    'SELECT ->STARTED_BY->WORK AS work as product FROM PRODUCT FETCH work ;\n'

    '#製造ライン production_line_id で実行された製品 product_id の作業の開始時間,作業を取得する\n'
    'SELECT id AS work_id, <-STARTED_BY.data.timestamp AS started_at '
    'FROM WORK WHERE <-STARTED_BY<-(PRODUCT WHERE id = "product_id" )  '
    'AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) FETCH started_at ; \n'

    '#製造ライン production_line_id で実行された製品 production_id の作業の終了時間,作業を取得する\n'
    'SELECT id AS work_id, <-ENDED_BY.data.timestamp AS ended_at '
    'FROM WORK WHERE <-ENDED_BY<-(PRODUCT WHERE id = "product_id" )  '
    'AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) FETCH ended_at ; \n'

    '#製品 product_id の原材料を取得する\n'
    'SELECT <-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_material FROM PRODUCT WHERE id = "product_id" FETCH raw_material ;\n'

    '#製品 product_id を構成したいる部品を取得する\n'
    'SELECT ->COMPRISED_OF->PRODUCT AS parts FROM PRODUCT WHERE id = "product_id" FETCH parts ;\n'

    '#製品 product_id の欠陥情報を取得する\n'
    'SELECT ->HAS_DEFECT->DEFECT_INFORMATION AS defect FROM PRODUCT WHERE id = "product_id" FETCH defect ;\n'

    '#製造ライン production_line_id  で実行された 製品 "product_id" の検査結果を取得する\n'
    'SELECT id AS work_id, <-STARTED_BY<-PRODUCT.id as product_id, ->RECORDS->INSPECTION_RESULT AS result '
    'FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) '
    'AND <-STARTED_BY<-(PRODUCT WHERE id = "product_id") SPLIT work_id, product_id, result FETCH result ;\n'

    '#製造ライン production_line_id  で実行された,作業の検査結果およびその対象製品を取得する\n'
    'SELECT id AS work_id, <-STARTED_BY<-PRODUCT.id as product_id, ->RECORDS->INSPECTION_RESULT AS result '
    'FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) '
    'SPLIT work_id, product_id, result FETCH result ;\n'

    '#欠陥を持つ製品を取得する\n'
    'SELECT <-HAS_DEFECT<-PRODUCT AS product FROM DEFECT_INFORMATION FETCH product ;\n'

    '#製品 product_id の作業を取得する\n'
    'SELECT ->STARTED_BY>WORK AS work FROM PRODUCT WHERE id = "product_id" FETCH work ;\n'

    '#製品 product_id の製造ライン production_line_id で実行した作業を取得する\n'
    'SELECT * FROM WORK WHERE <-STARTED_BY<-(PRODUCT WHERE id = "product_id") '
    'AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id") ;\n'

    '#製品 product_id を構成している部品が作られている原材料を取得する\n'
    'SELECT ->COMPRISED_OF->PRODUCT<-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_material '
    'FROM PRODUCT WHERE id = "product_id" FETCH parts, raw_material ;\n'

    '#製品 product_id の部品が製造ライン production_line_id で実行した作業の開始時間,作業を取得する\n'
    'SELECT id AS work_id, <-STARTED_BY.data.timestamp AS started_at '
    'FROM WORK WHERE <-STARTED_BY<-PRODUCT<-COMPRISED_OF<-(PRODUCT WHERE id = "product_id") '
    'AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id")  ;\n'

    '#製造ライン production_line_id で実行した作業が検出した欠陥情報を取得する\n'
    'SELECT ->EXECUTES->WORK->RECORDS->DEFECT_INFORMATION AS defect '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" FETCH defect ;\n'

    '#製造ライン production_line で実行した作業が検出した欠陥情報を持つ製品を取得する\n'
    'SELECT ->EXECUTES->WORK->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT AS product '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" FETCH product ;\n'

    '#欠陥を検出した作業,欠陥情報および製品を取得する\n'
    'SELECT id AS work_id, ->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT.id AS product_id, '
    '->RECORDS->DEFECT_INFORMATION AS defect '
    'FROM WORK WHERE ->RECORDS->DEFECT_INFORMATION SPLIT work_id, product_id FETCH defect ;\n'

    '#原材料 raw_material_id から作られた製品を検索する\n'
    'SELECT ->USED_TO_PRODUCE->PRODUCT AS products FROM RAW_MATERIAL WHERE id = "raw_material_id" FETCH product ;\n'

    '#貯蔵庫 storage_id から出た製品を取得する\n'
    'SELECT ->MOVE_FROM->WORK<-MOVED_BY<-PRODUCT AS product FROM STORAGE WHERE id = "storage_id" FETCH product ;\n'

    '#貯蔵庫 storage_id へ入った製品を取得する\n'
    'SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT AS product FROM STORAGE WHERE id = "storage_id" FETCH product ;\n'

    '#製造ライン production_line_id から出た製品を取得する\n'
    'SELECT ->MOVE_FROM->WORK<-MOVED_BY<-PRODUCT AS product '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" SPLIT product FETCH product ;\n'

    '#製造ライン production_line_id へ入った製品を取得する\n'
    'SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT AS product '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" SPLIT product FETCH product ;\n'

    '#製品 product_id が貯蔵庫 storage_id から出た時間を取得する\n'
    'SELECT id AS work_id, <-MOVED_BY.data.timestamp AS moved_at '
    'FROM WORK WHERE <-MOVE_FROM<-(STORAGE WHERE id = "storage_id") '
    'AND <-MOVED_BY<-(PRODUCT WHERE id = "product_id" ) SPLIT work_id ;\n'

    '#製品 product_id が貯蔵庫 storage_id 入った時間を取得する\n'
    'SELECT id AS work_id, <-MOVED_BY.data.timestamp AS moved_at '
    'FROM WORK WHERE ->MOVE_TO->(STORAGE WHERE id = "storage_id") '
    'AND <-MOVED_BY<-(PRODUCT WHERE id = "PRODUCT:S10015" ) SPLIT work_id ;\n'

    '#原材料  raw_material_id から作成された製品が持つ欠陥情報を取得する\n'
    'SELECT  * FROM PRODUCT WHERE <-USED_TO_PRODUCE<-(RAW_MATERIAL WHERE id = "raw_material_id") '
    'AND ->HAS_DEFECT->DEFECT_INFORMATION  SPLIT product ;\n'

    '#原材料  raw_material_id から作成された製品が持つ欠陥情報, 製品および作業識別子を取得する\n'
    'SELECT  id AS product_id, ->HAS_DEFECT->DEFECT_INFORMATION as defect, '
    '->HAS_DEFECT->DEFECT_INFORMATION<-RECORDS<-WORK.id AS work_id '
    'FROM PRODUCT WHERE <-USED_TO_PRODUCE<-(RAW_MATERIAL WHERE id = "raw_material_id" ) '
    'AND ->HAS_DEFECT->DEFECT_INFORMATION  SPLIT product_id FETCH defect ;\n'

    '#製造ライン "production_line_id" で作業で検出した欠陥と、その製品を取得する\n'
    'SELECT id AS work_id, '
    '->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT.id AS product_id, '
    '->RECORDS->DEFECT_INFORMATION AS defect '
    'FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id") '
    'AND ->RECORDS->DEFECT_INFORMATION SPLIT work_id, product_id FETCH defect ;\n'

    '#製造ライン "production_line_id" へ入った製品を構成する部品を取得する\n'
    'SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT->COMPRISED_OF->PRODUCT AS parts '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" FETCH parts ;\n'
)

# GPT-4  model="gpt-4" 用 メッセージ
# 目的： 日本語から SurrealQL言語を生成する
CONVERT_NL_TO_SURREALQL_MESSAGES_jp = [
    {
        "role": "system",
        "content": "グラフデータベースへの問合せ言語を生成するアシスタントです."
    },
    {
        "role": "user",
        "content": "製品 product_id の作業が実行された製造ラインを取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->STARTED_BY->WORK<-EXECUTES<-PRODUCTION_LINE AS production_line " 
                   "FROM PRODUCT WHERE id = 'product_id' ;"
    },
    {
        "role": "user",
        "content": "製品 product_id の作業が実行された製造ラインを取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->ENDED_BY->WORK<-EXECUTES<-PRODUCTION_LINE AS production_line " 
                   "FROM PRODUCT WHERE id = 'product_id';"
    },
    {
        "role": "user",
        "content": "製品の作業を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->STARTED_BY->WORK AS work as product FROM PRODUCT FETCH work ;"
    },
    {
        "role": "user",
        "content": "製造ライン production_line_id で実行された製品 product_id の作業の開始時間,作業を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, <-STARTED_BY.data.timestamp AS started_at "
                   "FROM WORK WHERE <-STARTED_BY<-(PRODUCT WHERE id = 'product_id' )  "
                   "AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = 'production_line_id' ) FETCH started_at ; "
    },
    {
        "role": "user",
        "content": '製造ライン production_line_id で実行された製品 production_id の作業の終了時間,作業を取得する'
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, <-ENDED_BY.data.timestamp AS ended_at " 
                   "FROM WORK WHERE <-ENDED_BY<-(PRODUCT WHERE id = 'product_id' )  "
                   "AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = 'production_line_id' ) FETCH ended_at ; "
    },
    {
        "role": "user",
        "content": '製品 product_id の原材料を取得する'
    },
    {
        "role": "assistant",
        "content": "SELECT <-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_material " 
                   "FROM PRODUCT WHERE id = 'product_id' FETCH raw_material ;"
    },
    {
        "role": "user",
        "content": "製品 product_id を構成したいる部品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->COMPRISED_OF->PRODUCT AS parts FROM PRODUCT WHERE id = 'product_id' FETCH parts ;"
    },
    {
        "role": "user",
        "content": "製品 product_id の欠陥情報を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->HAS_DEFECT->DEFECT_INFORMATION AS defect " 
                   "FROM PRODUCT WHERE id = 'product_id' FETCH defect ;"
    },
    {
        "role": "user",
        "content": "製造ライン production_line_id  で実行された 製品 'product_id' の検査結果を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, <-STARTED_BY<-PRODUCT.id as product_id, "
                   "->RECORDS->INSPECTION_RESULT AS result "
                   "FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = 'production_line_id' ) "
                   "AND <-STARTED_BY<-(PRODUCT WHERE id = 'product_id') " 
                   "SPLIT work_id, product_id, result FETCH result ;"
    },
    {
        "role": "user",
        "content": "製造ライン 'production_line_id'  で実行された,作業の検査結果およびその対象製品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, <-STARTED_BY<-PRODUCT.id as product_id, " 
                   "->RECORDS->INSPECTION_RESULT AS result "
                   "FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = 'production_line_id' ) "
                   "SPLIT work_id, product_id, result FETCH result ;"
    },
    {
        "role": "user",
        "content": "欠陥を持つ製品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT <-HAS_DEFECT<-PRODUCT AS product FROM DEFECT_INFORMATION FETCH product ;"
    },
    {
        "role": "user",
        "content": "製品 product_id の作業を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->STARTED_BY>WORK AS work FROM PRODUCT WHERE id = 'product_id' FETCH work ;"
    },
    {
        "role": "user",
        "content": "製品 product_id の製造ライン 'production_line_id' で実行した作業を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT * FROM WORK WHERE <-STARTED_BY<-(PRODUCT WHERE id = 'product_id') "
                   "AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = 'production_line_id') ;"
    },
    {
        "role": "user",
        "content": "製品 product_id を構成している部品が作られている原材料を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->COMPRISED_OF->PRODUCT<-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_material "
                   "FROM PRODUCT WHERE id = 'product_id' FETCH parts, raw_material ;"
    },
    {
        "role": "user",
        "content": "製品 product_id の部品が製造ライン 'production_line_id' で実行した作業の開始時間,作業を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, <-STARTED_BY.data.timestamp AS started_at "
                   "FROM WORK WHERE <-STARTED_BY<-PRODUCT<-COMPRISED_OF<-(PRODUCT WHERE id = 'product_id') "
                   "AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = 'production_line_id')  ;"
    },
    {
        "role": "user",
        "content": "製造ライン 'production_line_id' で実行した作業が検出した欠陥情報を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->EXECUTES->WORK->RECORDS->DEFECT_INFORMATION AS defect "
                   "FROM PRODUCTION_LINE WHERE id = 'production_line_id' FETCH defect ;"
    },
    {
        "role": "user",
        "content": "製造ライン production_line で実行した作業が検出した欠陥情報を持つ製品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->EXECUTES->WORK->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT AS product "
                   "FROM PRODUCTION_LINE WHERE id = 'production_line_id' FETCH product ;"
    },
    {
        "role": "user",
        "content": "欠陥を検出した作業,欠陥情報および製品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, ->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT.id AS product_id, "
                   "->RECORDS->DEFECT_INFORMATION AS defect "
                   "FROM WORK WHERE ->RECORDS->DEFECT_INFORMATION SPLIT work_id, product_id FETCH defect ;"
    },
    {
        "role": "user",
        "content": "原材料 raw_material_id から作られた製品を検索する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->USED_TO_PRODUCE->PRODUCT AS products " 
                   "FROM RAW_MATERIAL WHERE id = 'raw_material_id' FETCH product ;"
    },
    {
        "role": "user",
        "content": '貯蔵庫 storage_id から出た製品を取得する'
    },
    {
        "role": "assistant",
        "content": "SELECT ->MOVE_FROM->WORK<-MOVED_BY<-PRODUCT AS product " 
                   "FROM STORAGE WHERE id = 'storage_id' FETCH product ;"
    },
    {
        "role": "user",
        "content": "貯蔵庫 storage_id へ入った製品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT AS product " 
                   "FROM STORAGE WHERE id = 'storage_id' FETCH product ;"
    },
    {
        "role": "user",
        "content": "製造ライン production_line_id から出た製品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT ->MOVE_FROM->WORK<-MOVED_BY<-PRODUCT AS product "
                   "FROM PRODUCTION_LINE WHERE id = 'production_line_id' SPLIT product FETCH product ;\n"
    },
    {
        "role": "user",
        "content": "製造ライン production_line_id へ入った製品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT AS product "
                   "FROM PRODUCTION_LINE WHERE id = 'production_line_id' SPLIT product FETCH product ;"
    },
    {
        "role": "user",
        "content": "製品 product_id が貯蔵庫 storage_id から出た時間を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, <-MOVED_BY.data.timestamp AS moved_at "
                   "FROM WORK WHERE <-MOVE_FROM<-(STORAGE WHERE id = 'storage_id') "
                   "AND <-MOVED_BY<-(PRODUCT WHERE id = 'product_id' ) SPLIT work_id ;"
    },
    {
        "role": "user",
        "content": "製品 product_id が貯蔵庫 storage_id 入った時間を取得する\n"
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, <-MOVED_BY.data.timestamp AS moved_at "
                   "FROM WORK WHERE ->MOVE_TO->(STORAGE WHERE id = 'storage_id') "
                   "AND <-MOVED_BY<-(PRODUCT WHERE id = 'storage_id' ) SPLIT work_id ;"
    },
    {
        "role": "user",
        "content": "原材料  raw_material_id から作成された製品が持つ欠陥情報を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT  * FROM PRODUCT WHERE <-USED_TO_PRODUCE<-(RAW_MATERIAL WHERE id = 'raw_material_id') "
                   "AND ->HAS_DEFECT->DEFECT_INFORMATION  SPLIT product ;"
    },
    {
        "role": "user",
        "content": "原材料  raw_material_id から作成された製品が持つ欠陥情報, 製品および作業識別子を取得する\n"
    },
    {
        "role": "assistant",
        "content": "SELECT  id AS product_id, ->HAS_DEFECT->DEFECT_INFORMATION as defect, "
                "->HAS_DEFECT->DEFECT_INFORMATION<-RECORDS<-WORK.id AS work_id "
                "FROM PRODUCT WHERE <-USED_TO_PRODUCE<-(RAW_MATERIAL WHERE id = 'raw_material_id' ) "
                "AND ->HAS_DEFECT->DEFECT_INFORMATION  SPLIT product_id FETCH defect ;"
    },
    {
        "role": "user",
        "content": "製造ライン 'production_line_id' で作業で検出した欠陥と,その製品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT id AS work_id, "
                   "->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT.id AS product_id, "
                   "->RECORDS->DEFECT_INFORMATION AS defect "
                   "FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = 'production_line_id') "
                   "AND ->RECORDS->DEFECT_INFORMATION SPLIT work_id, product_id FETCH defect ;"
    },
    {
        "role": "user",
        "content": "製造ライン 'production_line_id' へ入った製品を構成する部品を取得する"
    },
    {
        "role": "assistant",
        "content": "SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT->COMPRISED_OF->PRODUCT AS parts "
                   "FROM PRODUCTION_LINE WHERE id = 'production_line_id' FETCH parts ;"
    },
]

# GPT-3.5 model_name="text-davinci-003"用 プロンプト
# 目的： 英語から SurrealQL言語を生成する
CONVERT_NL_TO_SURREALQL_PROMPT_en = (
    'Converting English natural language sentences to SurrealQL:\n'

    # '#製品 product_id の作業が実行された製造ラインを取得する\n'
    '#Get the manufacturing line on which the operation for the product with product_id was executed.'
    'SELECT ->STARTED_BY->WORK<-EXECUTES<-PRODUCTION_LINE AS production_line FROM PRODUCT WHERE id = "product_id" ;\n'

    # '#製品 product_id の作業が実行された製造ラインを取得する\n'
    '#Retrieve the manufacturing line where the operation for product with product_id was performed.\n'
    'SELECT ->ENDED_BY->WORK<-EXECUTES<-PRODUCTION_LINE AS production_line FROM PRODUCT WHERE id = "product_id" ;\n'

    # '#製品の作業を取得する\n'
    '#Retrieve the operation of a product.\n'
    'SELECT ->STARTED_BY->WORK AS work as product FROM PRODUCT FETCH work ;\n'

    # '#製造ライン production_line_id で実行された製品 product_id の作業の開始時間,作業を取得する\n'
    '#Retrieve the start time and operation of the product with product_id that was executed on the manufacturing line '
    'with production_line_id.\n'
    'SELECT id AS work_id, <-STARTED_BY.data.timestamp AS started_at '
    'FROM WORK WHERE <-STARTED_BY<-(PRODUCT WHERE id = "product_id" )  '
    'AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) FETCH started_at ; \n'

    # '#製品 product_id の製造ライン production_line_id で実行した作業の終了時間,作業を取得する\n'
    '#Retrieve the end time and operation of the product with product_id that was executed on the manufacturing line '
    'with production_line_id.\n'
    'SELECT id AS work_id, <-ENDED_BY.data.timestamp AS ended_at '
    'FROM WORK WHERE <-ENDED_BY<-(PRODUCT WHERE id = "product_id" )  '
    'AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) FETCH ended_at ; \n'

    # '#製品 product_id の原材料を取得する\n'
    '#Retrieve the raw materials of the product with product_id.'
    'SELECT <-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_material FROM PRODUCT WHERE id = "product_id" FETCH raw_material ;\n'

    # '#製品 product_id が組み込んでいる部品を取得する\n'
    '#Retrieve the components that make up the product with product_id.\n'
    'SELECT ->COMPRISED_OF->PRODUCT AS parts FROM PRODUCT WHERE id = "product_id" FETCH parts ;\n'

    # '#製品 product_id の欠陥情報を取得する\n'
    '#Retrieve the defect information of the product with product_id.\n'
    'SELECT ->HAS_DEFECT->DEFECT_INFORMATION AS defect FROM PRODUCT WHERE id = "product_id" FETCH defect ;\n'

    # '#製造ライン production_line_id  で, 製品 "product_id" の作業の検査結果を取得する\n'
    '#Retrieve the inspection results of the operation for the product "product_id" that was executed on '
    'the manufacturing line with production_line_id.\n'
    'SELECT id AS work_id, <-STARTED_BY<-PRODUCT.id as product_id, ->RECORDS->INSPECTION_RESULT AS result '
    'FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) '
    'AND <-STARTED_BY<-(PRODUCT WHERE id = "product_id") SPLIT work_id, product_id, result FETCH result ;\n'

    # '#製造ライン production_line_idで実行された作業の検査結果と、その対象製品を取得する。\n'
    '#Retrieve the inspection results for the operation that was executed on the manufacturing line with '
    'production_line_id, and the corresponding product it applies to.\n'
    'SELECT id AS work_id, <-STARTED_BY<-PRODUCT.id as product_id, ->RECORDS->INSPECTION_RESULT AS result '
    'FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) '
    'SPLIT work_id, product_id, result FETCH result ;\n'

    # '#欠陥を持つ製品を取得する\n'
    '#Retrieve the products that have defects.\n'
    'SELECT <-HAS_DEFECT<-PRODUCT AS product FROM DEFECT_INFORMATION FETCH product ;\n'

    # '#製品 product_id の作業を取得する\n'
    '#Retrieve the operations of the product with product_id.\n'
    'SELECT ->STARTED_BY>WORK AS work FROM PRODUCT WHERE id = "product_id" FETCH work ;\n'

    # '#製品 product_id の製造ライン production_line_id で実行した作業を取得する\n'
    '#Retrieve the operation that was executed on the manufacturing line with production_line_id '
    'for the product with product_id.\n'
    'SELECT * FROM WORK WHERE <-STARTED_BY<-(PRODUCT WHERE id = "product_id") '
    'AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id") ;\n'

    # '#製品 product_id を構成している部品の原材料を取得する\n'
    '#Retrieve the raw materials of the components that make up the product with product_id.\n'
    'SELECT ->COMPRISED_OF->PRODUCT<-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_material '
    'FROM PRODUCT WHERE id = "product_id" FETCH parts, raw_material ;\n'

    # '#製品 product_id を構成する部品が製造ライン production_line_id で実行した作業の開始時間および作業情報を取得する\n'
    '#Retrieve the start time and operation information of the operation that was executed on the manufacturing line '
    'with production_line_id for the components that make up the product with product_id.\n'
    'SELECT id AS work_id, <-STARTED_BY.data.timestamp AS started_at '
    'FROM WORK WHERE <-STARTED_BY<-PRODUCT<-COMPRISED_OF<-(PRODUCT WHERE id = "product_id") '
    'AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id")  ;\n'

    # '#製造ライン production_line_id で実行した作業で検出された欠陥情報を取得する\n'
    '#Retrieve the defect information detected by the operation that was executed on the manufacturing line '
    'with production_line_id.\n'
    'SELECT ->EXECUTES->WORK->RECORDS->DEFECT_INFORMATION AS defect '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" FETCH defect ;\n'

    # '#製造ライン production_line で実行した作業が検出した欠陥情報を持つ製品を取得する\n'
    '#Retrieve the products that have defect information detected by the operation that was executed '
    'on the manufacturing line with production_line_id.\n'
    'SELECT ->EXECUTES->WORK->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT AS product '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" FETCH product ;\n'

    # '#欠陥を検出した作業,欠陥情報および製品を取得する\n'
    '#Retrieve the operation, defect information, and product that has the defect detected.\n'
    'SELECT id AS work_id, ->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT.id AS product_id, '
    '->RECORDS->DEFECT_INFORMATION AS defect '
    'FROM WORK WHERE ->RECORDS->DEFECT_INFORMATION SPLIT work_id, product_id FETCH defect ;\n'

    # '#原材料 raw_material_id から作られた製品を取得する\n'
    '#Retrieve the products made from the raw material with raw_material_id.\n'
    'SELECT ->USED_TO_PRODUCE->PRODUCT AS products FROM RAW_MATERIAL WHERE id = "raw_material_id" FETCH product ;\n'

    # '#貯蔵庫 storage_id から出た製品を取得する\n'
    '#Retrieve the products that came out of the storage with storage_id.\n'
    'SELECT ->MOVE_FROM->WORK<-MOVED_BY<-PRODUCT AS product FROM STORAGE WHERE id = "storage_id" FETCH product ;\n'

    '#貯蔵庫 storage_id へ入った製品を取得する\n'
    '#Retrieve the products that entered the storage with storage_id.\n'
    'SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT AS product FROM STORAGE WHERE id = "storage_id" FETCH product ;\n'

    '#製造ライン production_line_id から出た製品を取得する\n'
    '#Retrieve products that came out of the production line with production_line_id.\n'
    'SELECT ->MOVE_FROM->WORK<-MOVED_BY<-PRODUCT AS product '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" SPLIT product FETCH product ;\n'

    # '#製造ライン production_line_id へ入った製品を取得する\n'
    '#Retrieve the products that entered the production line with  production_line_id.\n'
    'SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT AS product '
    'FROM PRODUCTION_LINE WHERE id = "production_line_id" SPLIT product FETCH product ;\n'

    # '#製品 product_id が貯蔵庫 storage_id から出た時間を取得する\n'
    '#Retrieve the time when the product with product_id left the storage_id.\n'
    'SELECT id AS work_id, <-MOVED_BY.data.timestamp AS moved_at '
    'FROM WORK WHERE <-MOVE_FROM<-(STORAGE WHERE id = "storage_id") '
    'AND <-MOVED_BY<-(PRODUCT WHERE id = "product_id" ) SPLIT work_id ;\n'

    # '#製品 product_id が貯蔵庫 storage_id 入った時間を取得する\n'
    '#Retrieve the time when the product with product_id entered the storage with ID "storage_id".\n'
    'SELECT id AS work_id, <-MOVED_BY.data.timestamp AS moved_at '
    'FROM WORK WHERE ->MOVE_TO->(STORAGE WHERE id = "storage_id") '
    'AND <-MOVED_BY<-(PRODUCT WHERE id = "PRODUCT:S10015" ) SPLIT work_id ;\n'

    # '#原材料  raw_material_id から作成された欠陥情報を持つ製品を取得する\n'
    '#Retrieve products that were created from the raw material with raw_material_id and have defect information.\n'
    'SELECT  * FROM PRODUCT WHERE <-USED_TO_PRODUCE<-(RAW_MATERIAL WHERE id = "raw_material_id") '
    'AND ->HAS_DEFECT->DEFECT_INFORMATION  SPLIT product ;\n'

    # '#原材料  raw_material_id をから作成された製品が持つ欠陥情報, 製品および作業情報を取得する\n'
    '#Retrieve defect information, product information, and work information for products made from '
    'raw material with raw_material_id.\n'
    'SELECT  id AS product_id, ->HAS_DEFECT->DEFECT_INFORMATION as defect, '
    '->HAS_DEFECT->DEFECT_INFORMATION<-RECORDS<-WORK.id AS work_id '
    'FROM PRODUCT WHERE <-USED_TO_PRODUCE<-(RAW_MATERIAL WHERE id = "raw_material_id" ) '
    'AND ->HAS_DEFECT->DEFECT_INFORMATION  SPLIT product_id FETCH defect ;\n'

    # '#製造ライン "production_line_id" の作業で検出した欠陥と、その製品を取得する\n'
    '#Retrieve the products and their defect information that were detected during the operations on '
    'the production line production_line_id.'
    'SELECT id AS work_id, '
    '->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT.id AS product_id, '
    '->RECORDS->DEFECT_INFORMATION AS defect '
    'FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "pl01") '
    'AND ->RECORDS->DEFECT_INFORMATION SPLIT work_id, product_id FETCH defect ;\n'

    # '#製造ライン "production_line_id" へ入った製品を構成する部品を取得する\n'
    '#Retrieve the components that make up the product that entered the production line "production_line_id".\n'
    'SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT->COMPRISED_OF->PRODUCT AS parts '
    'FROM PRODUCTION_LINE WHERE id = "pl002" FETCH parts ;\n'

)

# GPT-3.5 model_name="text-davinci-003"用 プロンプト
# 目的 SurrealDBからのquery結果Jsonを人間が理解できる形式へ変換するプロンプト
ANALYZE_RESPONSE_PROMPT_jp = (
    '私は高度に知的な質問・応答ボットである.'
    '質問とその質問の回答をJSONデータで与える.'
    'JSONデータの回答を人間が理解できるテキストへ変換して回答しろ.\n'
    'JSONデータが空の場合は、"該当する情報はありません"と回答する。\n'
    'JSONデータの日付は日本時間へ変換しろ.\n'
    '{additional}\n'
    '質問：{question}\n'
    '回答：{result}\n'
)

ANALYZE_RESPONSE_PROMPT_en = (
    'Convert the following questions and JSON data into human-readable text.\n'
    '{additional}\n'
    'Question：{question}\n'
    'Answer：{result}\n'
)

if __name__ == '__main__':

    table = Texttable(max_width=120)
    table.add_row(['Role', 'Content'])
    for entry in CONVERT_NL_TO_SURREALQL_MESSAGES_jp:
        table.add_row([entry.get('role', '?'), entry.get('content', '?')])
    print(table.draw())
