## SurrealQL生成  Prompt for OpenAI GPT-4


|role|content|  
|:-|:-|  
|system|グラフデータベースへの問合せ言語を生成するアシスタントです.|  
|user|製品 product_id の作業が実行された製造ラインを取得する|  
|assistant|SELECT ->STARTED_BY->WORK<-EXECUTES<-PRODUCTION_LINE AS production_line FROM PRODUCT WHERE id = "product_id" ;|  
|user|製品 product_id の作業が実行された製造ラインを取得する|  
|assistant|SELECT ->ENDED_BY->WORK<-EXECUTES<-PRODUCTION_LINE AS production_line FROM PRODUCT WHERE id = "product_id";|  
|user|製品の作業を取得する|  
|assistant|SELECT ->STARTED_BY->WORK AS work as product FROM PRODUCT FETCH work ;|  
|user|製造ライン production_line_id で実行された製品 product_id の作業の開始時間,作業を取得する|  
|assistant|SELECT id AS work_id, <-STARTED_BY.data.timestamp AS started_at FROM WORK WHERE <-STARTED_BY<-(PRODUCT WHERE id = "product_id" )  AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) FETCH started_at ; |  
|user|製造ライン production_line_id で実行された製品 production_id の作業の終了時間,作業を取得する|  
|assistant|SELECT id AS work_id, <-ENDED_BY.data.timestamp AS ended_at FROM WORK WHERE <-ENDED_BY<-(PRODUCT WHERE id = "product_id" )  AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) FETCH ended_at ; |  
|user|製品 product_id の原材料を取得する|  
|assistant|SELECT <-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_material FROM PRODUCT WHERE id = "product_id" FETCH raw_material ;|  
|user|製品 product_id を構成したいる部品を取得する|  
|assistant|SELECT ->COMPRISED_OF->PRODUCT AS parts FROM PRODUCT WHERE id = "product_id" FETCH parts ;|  
|user|製品 product_id の欠陥情報を取得する|  
|assistant|SELECT ->HAS_DEFECT->DEFECT_INFORMATION AS defect FROM PRODUCT WHERE id = "product_id" FETCH defect ;|  
|user|製造ライン production_line_id  で実行された 製品 "product_id" の検査結果を取得する|  
|assistant|SELECT id AS work_id, <-STARTED_BY<-PRODUCT.id as product_id, ->RECORDS->INSPECTION_RESULT AS result FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) AND <-STARTED_BY<-(PRODUCT WHERE id = "product_id") SPLIT work_id, product_id, result FETCH result ;|  
|user|製造ライン production_line_id  で実行された,作業の検査結果およびその対象製品を取得する|  
|assistant|SELECT id AS work_id, <-STARTED_BY<-PRODUCT.id as product_id, ->RECORDS->INSPECTION_RESULT AS result FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id" ) SPLIT work_id, product_id, result FETCH result ;|  
|user|欠陥を持つ製品を取得する|  
|assistant|SELECT <-HAS_DEFECT<-PRODUCT AS product FROM DEFECT_INFORMATION FETCH product ;|  
|user|製品 product_id の作業を取得する|  
|assistant|SELECT ->STARTED_BY>WORK AS work FROM PRODUCT WHERE id = "product_id" FETCH work ;|  
|user|製品 product_id の製造ライン production_line_id で実行した作業を取得する|  
|assistant|SELECT * FROM WORK WHERE <-STARTED_BY<-(PRODUCT WHERE id = "product_id") AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id") ;|  
|user|製品 product_id を構成している部品が作られている原材料を取得する|  
|assistant|SELECT ->COMPRISED_OF->PRODUCT<-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_material FROM PRODUCT WHERE id = "product_id" FETCH parts, raw_material ;|  
|user|製品 product_id の部品が製造ライン production_line_id で実行した作業の開始時間,作業を取得する|  
|assistant|SELECT id AS work_id, <-STARTED_BY.data.timestamp AS started_at FROM WORK WHERE <-STARTED_BY<-PRODUCT<-COMPRISED_OF<-(PRODUCT WHERE id = "product_id") AND <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id")  ;|  
|user|製造ライン production_line_id で実行した作業が検出した欠陥情報を取得する|  
|assistant|SELECT ->EXECUTES->WORK->RECORDS->DEFECT_INFORMATION AS defect FROM PRODUCTION_LINE WHERE id = "production_line_id" FETCH defect ;|  
|user|製造ライン production_line で実行した作業が検出した欠陥情報を持つ製品を取得する|  
|assistant|SELECT ->EXECUTES->WORK->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT AS product FROM PRODUCTION_LINE WHERE id = "production_line_id" FETCH product ;|  
|user|欠陥を検出した作業,欠陥情報および製品を取得する|  
|assistant|SELECT id AS work_id, ->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT.id AS product_id, ->RECORDS->DEFECT_INFORMATION AS defect FROM WORK WHERE ->RECORDS->DEFECT_INFORMATION SPLIT work_id, product_id FETCH defect ;|  
|user|原材料 raw_material_id から作られた製品を検索する|  
|assistant|SELECT ->USED_TO_PRODUCE->PRODUCT AS products FROM RAW_MATERIAL WHERE id = "raw_material_id" FETCH product ;|  
|user|貯蔵庫 storage_id から出た製品を取得する|  
|assistant|SELECT ->MOVE_FROM->WORK<-MOVED_BY<-PRODUCT AS product FROM STORAGE WHERE id = "storage_id" FETCH product ;|  
|user|貯蔵庫 storage_id へ入った製品を取得する|  
|assistant|SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT AS product FROM STORAGE WHERE id = "storage_id" FETCH product ;|  
|user|製造ライン production_line_id から出た製品を取得する|  
|assistant|SELECT ->MOVE_FROM->WORK<-MOVED_BY<-PRODUCT AS product FROM PRODUCTION_LINE WHERE id = "production_line_id" SPLIT product FETCH product ;|  
|user|製造ライン production_line_id へ入った製品を取得する|  
|assistant|SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT AS product FROM PRODUCTION_LINE WHERE id = "production_line_id" SPLIT product FETCH product ;|  
|user|製品 product_id が貯蔵庫 storage_id から出た時間を取得する|  
|assistant|SELECT id AS work_id, <-MOVED_BY.data.timestamp AS moved_at FROM WORK WHERE <-MOVE_FROM<-(STORAGE WHERE id = "storage_id") AND <-MOVED_BY<-(PRODUCT WHERE id = "product_id" ) SPLIT work_id ;|  
|user|製品 product_id が貯蔵庫 storage_id 入った時間を取得する|  
|assistant|SELECT id AS work_id, <-MOVED_BY.data.timestamp AS moved_at FROM WORK WHERE ->MOVE_TO->(STORAGE WHERE id = "storage_id") AND <-MOVED_BY<-(PRODUCT WHERE id = "PRODUCT:S10015" ) SPLIT work_id ;|  
|user|原材料  raw_material_id から作成された製品が持つ欠陥情報を取得する|  
|assistant|SELECT  * FROM PRODUCT WHERE <-USED_TO_PRODUCE<-(RAW_MATERIAL WHERE id = "raw_material_id") AND ->HAS_DEFECT->DEFECT_INFORMATION  SPLIT product ;|  
|user|原材料  raw_material_id から作成された製品が持つ欠陥情報, 製品および作業識別子を取得する|  
|assistant|SELECT  id AS product_id, ->HAS_DEFECT->DEFECT_INFORMATION as defect, ->HAS_DEFECT->DEFECT_INFORMATION<-RECORDS<-WORK.id AS work_id FROM PRODUCT WHERE <-USED_TO_PRODUCE<-(RAW_MATERIAL WHERE id = "raw_material_id" ) AND ->HAS_DEFECT->DEFECT_INFORMATION  SPLIT product_id FETCH defect ;|  
|user|製造ライン "production_line_id" で作業で検出した欠陥と,その製品を取得する|  
|assistant|SELECT id AS work_id, ->RECORDS->DEFECT_INFORMATION<-HAS_DEFECT<-PRODUCT.id AS product_id, ->RECORDS->DEFECT_INFORMATION AS defect FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "production_line_id") AND ->RECORDS->DEFECT_INFORMATION SPLIT work_id, product_id FETCH defect ;|  
|user|製造ライン "production_line_id" へ入った製品を構成する部品を取得する|  
|assistant|SELECT <-MOVE_TO<-WORK<-MOVED_BY<-PRODUCT->COMPRISED_OF->PRODUCT AS parts FROM PRODUCTION_LINE WHERE id = "production_line_id" FETCH parts ;|  

