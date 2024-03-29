# -*- coding: utf-8 -*-
# @Time     : 2022/09/15 18:07:43
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : data_statics.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import argparse
from tqdm import tqdm
import numpy as np
from nextbv2.version import NEXTB_V2_VERSION
from nextbv2.libs.common.constant import BinanceDataFormat
from nextbv2.libs.common.common import create_serialize
from nextbv2.libs.common.nextb_time import timestamp_to_time
from nextbv2.libs.logs.logs import info


help_str = """
指定统计方法。当前支持方法[show/mean/cos/csv]，默认值为：show。\
show：显示最近N条收盘价格，\
mean：显示最近N条价格的均值，\
cos：比较币种之间K线的余弦相似度，\
csv：分析数据并导出到csv文件，\
data：导出原始数据到csv文件
"""


def parse_cmd():
    """
    数据初始化和更新
    """
    parser = argparse.ArgumentParser(
        prog="nextb-v2-data-statics",
        description="NextBv2本地数据集统计分析工具。版本号：{}".format(NEXTB_V2_VERSION),
        epilog="使用方式：nextb-v2-data-statics -h",
    )
    parser.add_argument(
        "-t",
        "--type",
        help=help_str,
        type=str,
        dest="serialize_type",
        action="store",
        default="show",
    )
    parser.add_argument(
        "-s",
        "--data",
        help="指定本地序列化数据路径。默认值为：./serialize.data",
        type=str,
        dest="serialize_data",
        action="store",
        default="./serialize.data",
    )
    parser.add_argument(
        "-n",
        "--number",
        help="指定数据数量。默认值为：7。",
        type=int,
        dest="number",
        action="store",
        default=7,
    )
    parser.add_argument(
        "-b",
        "--base-symbol",
        help="指定余弦相似度的基准币种。默认值为：BNBUSDT。",
        type=str,
        dest="base_symbol",
        action="store",
        default="BNBUSDT",
    )
    parser.add_argument(
        "-f",
        "--file-name",
        help="指定分析结果保存的csv文件名称。默认值为：./NextB_V2.csv。",
        type=str,
        dest="file_name",
        action="store",
        default="./NextB_V2.csv",
    )

    args = parser.parse_args()

    return args


def statics_show(param):
    serialize_data = param.get("serialize_data")
    number = param.get("number")
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    datas = nextbv2_serialize.get_datas()
    info("币种,时间,收盘价,最高振幅,最低振幅")
    for key, value in datas.items():
        for i in range(0, number):
            data = value[-1 - i]
            update_time = timestamp_to_time(data[BinanceDataFormat.OPEN_TIME])
            open_price = float(data[BinanceDataFormat.OPEN_PRICE])
            high_price = float(data[BinanceDataFormat.HIGH_PRICE])
            low_price = float(data[BinanceDataFormat.LOW_PRICE])
            close_price = float(data[BinanceDataFormat.CLOSE_PRICE])
            amplitude_A = (high_price - low_price) / low_price * 100.0
            amplitude_B = (close_price - open_price) / close_price * 100.0
            info(
                "{},{},{},{},{}".format(
                    key,
                    update_time,
                    data[BinanceDataFormat.CLOSE_PRICE],
                    amplitude_A,
                    amplitude_B,
                )
            )


def statics_mean(param):
    serialize_data = param.get("serialize_data")
    number = param.get("number")
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    datas = nextbv2_serialize.get_datas()
    info("币种,{0}小时最高均值,{0}小时最低均值,{0}小时收盘均值".format(number))
    for key, value in datas.items():
        high_sum = 0.0
        low_sum = 0.0
        close_sum = 0.0
        for i in range(0, number):
            data = value[-1 - i]
            high_sum += float(data[BinanceDataFormat.HIGH_PRICE])
            low_sum += float(data[BinanceDataFormat.LOW_PRICE])
            close_sum += float(data[BinanceDataFormat.CLOSE_PRICE])
        info(
            "{},{},{},{}".format(
                key,
                high_sum / number,
                low_sum / number,
                close_sum / number,
            )
        )


def cosine_similarity(param):
    serialize_data = param.get("serialize_data")
    base_symbol = param.get("base_symbol")
    number = param.get("number")
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    datas = nextbv2_serialize.get_datas()
    base_symbol_data = [
        float(d[BinanceDataFormat.CLOSE_PRICE]) for d in datas[base_symbol][-number:]
    ]
    base_vec = np.array([d for d in base_symbol_data])
    for symbol, data in datas.items():
        match_symbol_data = [
            float(d[BinanceDataFormat.CLOSE_PRICE]) for d in data[-number:]
        ]
        match_vec = np.array([d for d in match_symbol_data])
        cos_sim = np.dot(base_vec, match_vec) / (
            np.linalg.norm(base_vec) * np.linalg.norm(match_vec)
        )
        info("{}与{}最近{}个小时的余弦相似度为: {}".format(symbol, base_symbol, number, cos_sim))


def gen_analyse_csv_file(param):
    """
    生成csv文件，便于使用xlsx分析
    行头包括：币种,开盘时间,开盘价,收盘价,收盘涨跌幅度,最高涨幅,最高跌幅,最大振幅,成交量,吃单数
    """
    serialize_data = param.get("serialize_data")
    number = param.get("number")
    csv_file_name = param.get("file_name")
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    datas = nextbv2_serialize.get_datas()
    rows = list()
    for symbol in datas.keys():
        for d in tqdm(datas[symbol][-number:], unit="row", desc="{}分析中".format(symbol)):
            open_price = float(d[BinanceDataFormat.OPEN_PRICE])
            high_price = float(d[BinanceDataFormat.HIGH_PRICE])
            low_price = float(d[BinanceDataFormat.LOW_PRICE])
            close_price = float(d[BinanceDataFormat.CLOSE_PRICE])
            row = list()
            row.append(symbol)
            row.append(timestamp_to_time(d[BinanceDataFormat.OPEN_TIME]))
            row.append(d[BinanceDataFormat.OPEN_PRICE])
            row.append(d[BinanceDataFormat.CLOSE_PRICE])
            row.append(str((close_price - open_price) / open_price))
            row.append(str((high_price - open_price) / open_price))
            row.append(str((low_price - open_price) / open_price))
            row.append(str((high_price - low_price) / open_price))
            row.append(d[BinanceDataFormat.VOLUME])
            row.append(d[BinanceDataFormat.TAKER_BASE])
            rows.append(",".join(row))

    headers = "币种,开盘时间,开盘价,收盘价,收盘涨跌幅度,最高涨幅,最高跌幅,最大振幅,成交量,吃单量"
    with open(csv_file_name, "w", encoding="utf8") as f:
        f.write(headers + "\n")
        f.write("\n".join(rows))


def data_export_csv_file(param):
    """
    导出数据为csv文件，便于使用xlsx分析
    行头包括：币种,开盘时间,开盘价,最高价,最低价,收盘价,成交量,成交额,交易单数,吃单量,吃单数
    """
    serialize_data = param.get("serialize_data")
    number = param.get("number")
    csv_file_name = param.get("file_name")
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    datas = nextbv2_serialize.get_datas()
    rows = list()
    for symbol in datas.keys():
        for d in tqdm(datas[symbol][-number:], unit="row", desc="{}导出中".format(symbol)):
            row = list()
            row.append(symbol)
            row.append(timestamp_to_time(d[BinanceDataFormat.OPEN_TIME]))
            row.append(d[BinanceDataFormat.OPEN_PRICE])
            row.append(d[BinanceDataFormat.HIGH_PRICE])
            row.append(d[BinanceDataFormat.LOW_PRICE])
            row.append(d[BinanceDataFormat.CLOSE_PRICE])
            row.append(d[BinanceDataFormat.VOLUME])
            row.append(d[BinanceDataFormat.QUOTE_VOLUME])
            row.append(str(d[BinanceDataFormat.TRADES]))
            row.append(d[BinanceDataFormat.TAKER_BASE])
            row.append(d[BinanceDataFormat.TAKER_QUOTE])
            rows.append(",".join(row))

    headers = "币种,开盘时间,开盘价,最高价,最低价,收盘价,成交量(个),成交额(U),交易单数,吃单量(个),吃单额(U)"
    with open(csv_file_name, "w", encoding="utf8") as f:
        f.write(headers + "\n")
        f.write("\n".join(rows))


statics_func = {
    "show": statics_show,
    "mean": statics_mean,
    "cos": cosine_similarity,
    "csv": gen_analyse_csv_file,
    "data": data_export_csv_file,
}


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    param = {
        "serialize_data": args.serialize_data,
        "number": args.number,
        "base_symbol": args.base_symbol,
        "file_name": args.file_name,
    }
    statics_func[args.serialize_type](param)
