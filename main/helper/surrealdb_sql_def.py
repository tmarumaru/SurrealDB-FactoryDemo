
"""
 SurrealQL query 定義
"""
from simulator.factory_models import FactoryNodeTable

WORK_HISTORIES_TABLE = 'WORK_HISTORIES_TABLE'
TRANSFER_WORK_HISTORIES_TABLE = 'TRANSFER_WORK_HISTORIES_TABLE'
MEASUREMENTS_VALUE_TABLE = 'MEASUREMENTS_VALUE_TABLE'
WORK_START_END_TABLE = 'WORK_START_END_TABLE'

EXCLUSION_TABLE_NAMES = [
    FactoryNodeTable.FACTORY.name,
    FactoryNodeTable.PRODUCTION_LINE.name,
    FactoryNodeTable.STORAGE.name,
    FactoryNodeTable.MACHINE.name,
    FactoryNodeTable.OPERATING_CREW.name,
    FactoryNodeTable.SPECIFICATION.name,
    FactoryNodeTable.MANUFACTURER.name,
    FactoryNodeTable.RAW_MATERIAL.name,
]

# 全作業履歴検索
GET_PRODUCTION_HISTORIES = (
    'SELECT work_id, '
    'machines, '
    'working_teams,'
    'parts, '
    'raw_materials, '
    'function() {return this.production_line.length <= 0? null : this.production_line[0];} as production_line,'
    'function() {return this.product.length <= 0? null : this.product[0];} as product, '
    'function() {return this.started_by.length <= 0? null : this.started_by[0].data.timestamp;} as started,  '
    'function() {return this.ended_by.length <= 0? null : this.ended_by[0].data.timestamp;} as ended, '
    'function() {return this.result.length <= 0? null : this.result[0].data.detail;} as inspection, '
    'function() {return this.defect.length <= 0? null : this.defect[0].data.detail;} as defect '
    'FROM  (SELECT id AS work_id, '
    '<-(STARTED_BY AS started_by)<-PRODUCT AS product,'
    '<-(ENDED_BY AS ended_by),'
    '<-STARTED_BY<-PRODUCT<-USED_TO_PRODUCE<-RAW_MATERIAL  AS raw_materials, '
    '<-STARTED_BY<-PRODUCT->COMPRISED_OF->PRODUCT  AS parts, '
    '<-EXECUTES<-PRODUCTION_LINE AS production_line, '
    '<-EXECUTES<-PRODUCTION_LINE->CONSISTS_OF->MACHINE AS machines, '
    '<-EXECUTES<-PRODUCTION_LINE->HAS_WORKERS->WORKING_TEAM  AS working_teams, '
    '->RECORDS->INSPECTION_RESULT AS result, '
    '->RECORDS->DEFECT_INFORMATION AS defect  '
    'FROM (SELECT id AS work FROM WORK WHERE data.type="NormalWork" SPLIT work) '
    'FETCH product, started_by, ended_by,product, result, defect)'
)

INSERT_WORK_HISTORIES = f'INSERT INTO {WORK_HISTORIES_TABLE} (' + GET_PRODUCTION_HISTORIES + ');'

GET_PROCESSING_TIME = (
    'SELECT '
    '<-EXECUTES<-PRODUCTION_LINE.id AS production_line_id,'
    '<-STARTED_BY<-PRODUCT.id AS product_id,'
    '<-STARTED_BY.data.timestamp AS started_at,'
    '<-ENDED_BY.data.timestamp AS ended_at '
    'FROM WORK WHERE <-EXECUTES<-(PRODUCTION_LINE WHERE id = "$$production_line1$$") '
    'OR <-EXECUTES<-(PRODUCTION_LINE WHERE id = "$$production_line2$$") '
    'SPLIT production_line_id, product_id, started_at, ended_at '
    'FETCH started_at, ended_at '
)
PARAM_PRODUCTION_LINE1 = '$$production_line1$$'
PARAM_PRODUCTION_LINE2 = '$$production_line2$$'

# 全移動作業履歴検索
GET_TRANSFER_WORK_HISTORIES = (
    'SELECT work_id,'
    'product,'
    'function() {return this.to_line.length <= 0? this.to_storage[0] : this.to_line[0];} as to_id,'
    'function() {return this.from_line.length <= 0? this.from_storage[0] : this.from_line[0];} as from_id,'
    'function() {return this.moved_by.length <= 0? null : this.moved_by[0].data.timestamp;} as timestamp,'
    'time::unix(function() {return this.moved_by.length <= 0? null : this.moved_by[0].data.timestamp;}) AS timestamp_utime '
    'FROM (SELECT id AS work_id,'
    '             <-(MOVED_BY AS moved_by)<-PRODUCT AS product,'
    '             ->MOVE_TO->PRODUCTION_LINE AS to_line,'
    '             <-MOVE_FROM<-STORAGE AS from_storage,'
    '             ->MOVE_TO->STORAGE AS to_storage,'
    '             <-MOVE_FROM<-PRODUCTION_LINE AS from_line '
    '      FROM WORK WHERE  <-MOVED_BY<-PRODUCT '
    '      SPLIT product '
    '      FETCH moved_by) '
    'ORDER BY product, timestamp '
)

INSERT_TRANSFER_WORK_HISTORIES = f'INSERT INTO {TRANSFER_WORK_HISTORIES_TABLE} (' + GET_TRANSFER_WORK_HISTORIES + ');'
# INSERT_TRANSFER_WORK_HISTORIES = GET_TRANSFER_WORK_HISTORIES + ';'


GET_MEASUREMENTS_VALUE = (
    'SELECT production_line,'
    'machine,'
    'measurements.data.measurements.value AS value,'
    'measurements.timestamp AS timestamp '
    'FROM (SELECT id AS production_line, '
    '->CONSISTS_OF->(MACHINE AS machine)->RECORDS->MEASUREMENTS as measurements '
    'FROM PRODUCTION_LINE '
    'SPLIT production_line, machine, measurements '
    'FETCH measurements)'
)

INSERT_MEASUREMENTS_VALUE = f'INSERT INTO {MEASUREMENTS_VALUE_TABLE} ({GET_MEASUREMENTS_VALUE});'

SEARCH_FOR_PRODUCTS_AFFECTED_BY_RAW_MATERIAL_DEFECTS = (
    'SELECT ->USED_TO_PRODUCE->PRODUCT[WHERE data.type="PARTS"] AS parts,'
    '->USED_TO_PRODUCE->PRODUCT[WHERE data.type="PARTS"]<-COMPRISED_OF<-PRODUCT AS affected_products,'
    '->USED_TO_PRODUCE->PRODUCT[WHERE data.type="PRODUCT"] AS products '
    'FROM RAW_MATERIAL WHERE id="RAW_MATERIAL:rm001" '
    'FETCH parts, affected_products, products;'
)

GET_PRODUCTION_YIELD = (
    'SELECT id AS production_line,'
    'count(product_in) AS input_products_num,'
    'count(product_out) AS output_products_num,'
    'count(product_defect) AS defect_products_num '
    'FROM (SELECT id,'
    '->EXECUTES->WORK<-STARTED_BY<-PRODUCT AS product_in,'
    '->EXECUTES->WORK<-ENDED_BY<-PRODUCT AS product_out,'
    '->EXECUTES->WORK<-DEFECT_DETECTED_BY<-PRODUCT AS product_defect '
    'FROM PRODUCTION_LINE);'
)

GET_RELATIONSHIPS_ABOUT_NODE = (
    'SELECT <->(? AS relationship)<->(?) AS node '
    'FROM {0} '
    'WHERE id="{1}" '
    'FETCH relationship ;'
)

GET_PRODUCTION_WORK_HISTORIES = (
    'SELECT production_line,'
    'work_id AS work_id,'
    'product.id AS product,'
    'product.data.status AS product_status,'
    'function() {return this.started_by.length <= 0? null: this.started_by[0].data.timestamp;} as started,'
    'function() {return this.ended_by.length <= 0? null: this.ended_by[0].data.timestamp;} as ended ,'
    'time::unix(function() {return this.started_by.length <= 0? null : this.started_by[0].data.timestamp;}) as started_utime,'
    'time::unix(function() {return this.ended_by.length <= 0? null : this.ended_by[0].data.timestamp;}) as ended_utime, '
    'function() {return this.result.length <= 0? null : this.result[0].data.detail.result;} AS inspection_result '
    'FROM (SELECT <-EXECUTES<-PRODUCTION_LINE AS production_line,'
    '             id AS work_id,'
    '             <-(STARTED_BY AS started_by)<-PRODUCT AS product,'
    '             <-(ENDED_BY AS ended_by)<-PRODUCT,'
    '             ->RECORDS->INSPECTION_RESULT AS result '
    '     FROM WORK WHERE <-EXECUTES<-PRODUCTION_LINE  '
    '     SPLIT production_line, product '
    '     FETCH started_by, ended_by, product, result) '
    'ORDER BY production_line, started '
)
INSERT_WORK_START_END = f'INSERT INTO {WORK_START_END_TABLE} (' + GET_PRODUCTION_WORK_HISTORIES + ');'

GET_PRODUCT_INFO = (
    'SELECT *, '
    '       ->COMPRISED_OF->PRODUCT AS parts ,'
    '       <-USED_TO_PRODUCE<-RAW_MATERIAL AS raw_materials '
    'FROM PRODUCT; '
)
