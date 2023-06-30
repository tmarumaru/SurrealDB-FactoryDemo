import datetime
import random
from dateutil import tz
import numpy as np

UTC = tz.gettz("UTC")

# 欠陥品発生確率
_ERROR_RATE = 0.1


def to_iso88601_datatime(data: datetime.datetime) -> str:
    r = data.isoformat()
    return r


def convert_utc_string_to_datetime(utc_string) -> datetime.datetime:
    # Parse the UTC string into a datetime object
    datetime_object = datetime.datetime.strptime(utc_string, '%Y-%m-%dT%H:%M:%S%z')
    return datetime_object


def addMinutes(date: datetime.datetime, minutes: int) -> datetime.datetime:
    return date + datetime.timedelta(minutes=minutes)


def get_gaussian_distribution_value(average: int, scale: float = 2) -> int:
    """
    指定された数値を平均にとるガウス分布に従った数値を返す
    :param average: 平均値
    :param scale: 標準偏差（省略時 σ=2)
    :return: ガウス分布値
    """
    result = np.random.normal(
        loc=average,  # 平均
        scale=scale,  # 標準偏差
        size=1,  # 出力配列のサイズ(タプルも可)
    )
    return round(result[0])


def get_failure_rate() -> float:
    return _ERROR_RATE


def get_processing_result_randomly() -> bool:
    """
    get_failure_rate()で取得される歩留り率に従った検査結果を返す
    :return: True: 良品  False: 不良品
    """
    return random.random() > get_failure_rate()


def generate_defect_info() -> {}:
    """
    欠陥情報生成
    :return: 欠陥情報
    """
    x = get_gaussian_distribution_value(5)
    y = get_gaussian_distribution_value(5)
    code = 99
    return {
        'location': {'x': x, 'y': y},
        'defect_code': code
    }


def to_markdown_table(data, cols: [], disp: [] = None):
    header = '|'
    header2 = '|'
    if not disp:
        disp = []
    if not data:
        data = [[]]
    for i in range(len(data[0])):
        if len(disp) > 0 and disp[i] == 0:
            continue
        c = norm_line(cols[i])
        header += f'{c}|'
        header2 += ':-|'
    result = f'{header}\n{header2}\n'

    for line in data:
        s = '|'
        for i in range(len(line)):
            if len(disp) > 0 and disp[i] == 0:
                continue
            c = norm_line(line[i])
            s += f'{c}|'
        if len(s) > 1:
            result += s + '\n'
    return result


def to_markdown_table_ex(data, cols: [], disp: [] = None):
    header = ''
    header2 = ''
    if not disp:
        disp = []
    for i in range(len(data[0])):
        if len(disp) > 0 and disp[i] == 0:
            continue
        c = norm_line(cols[i])
        header += ('|' if len(header) > 0 else '') + f'{c}'
        header2 += ('|' if len(header2) > 0 else '-')
    result = f'{header}\n{header2}\n'

    for line in data:
        s = ''
        for i in range(len(line)):
            if len(disp) > 0 and disp[i] == 0:
                continue
            c = norm_line(line[i])
            s += ('|' if len(s) > 0 else '') + f'{c}'
        if len(s) > 1:
            result += s + '\n'
    return result


def norm_line(line):
    if type(line) is not str:
        return line
    return line.replace('\n', '<br>')
