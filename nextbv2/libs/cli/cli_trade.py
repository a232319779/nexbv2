# -*- coding: utf-8 -*-
# @Time     : 2023/02/03 17:06:10
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : cli_trade.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import argparse
from nextbv2.version import NEXTB_V2_VERSION
from nextbv2.libs.common.constant import *
from nextbv2.libs.common.common import create_serialize
from nextbv2.libs.trade.trade_one import TradingStraregyOne
from nextbv2.libs.db.sqlite_db import NextBTradeDB
from nextbv2.libs.common.constant import TradeStatus



def parse_cmd():
    """
    数据初始化和更新
    """
    parser = argparse.ArgumentParser(
        prog="nextb-v2-trade",
        description="NextBv2交易工具。版本号：{}".format(NEXTB_V2_VERSION),
        epilog="使用方式：nextb-v2-data -h",
    )
    parser.add_argument(
        "-t",
        "--trading-straregy",
        help="交易策略名称，当前支持[trade_one]，默认值：trade_one",
        type=str,
        dest="trading_straregy",
        action="store",
        default="trade_one",
    )
    parser.add_argument(
        "-d",
        "--data",
        help="指定本地序列化数据路径。默认值为：./serialize.data",
        type=str,
        dest="serialize_data",
        action="store",
        default="./serialize.data",
    )
    parser.add_argument(
        "-s",
        "--symbol",
        help="指定交易币种。默认值为：BNBUSDT。",
        type=str,
        dest="symbol",
        action="store",
        default="BNBUSDT",
    )
    parser.add_argument(
        "-db",
        "--sqlite",
        help="指定交易数据库。默认值为：./NextV_V2_Trade.db。",
        type=str,
        dest="sqlite",
        action="store",
        default="./NextV_V2_Trade.db",
    )
    parser.add_argument(
        "-n",
        "--number",
        help="指定回测数据量，0表示全量。默认值为：0",
        type=int,
        dest="number",
        action="store",
        default=0,
    )

    args = parser.parse_args()

    return args


def trade_one(param):
    serialize_data = param.get("serialize_data")
    symbol = param.get("symbol")
    sqlite_path = param.get("sqlite")
    number = param.get("number")
    nb_db = NextBTradeDB(sqlite_path)
    nb_db.create_table()
    nb_db.create_session()
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    s_datas = nextbv2_serialize.get_datas()
    trade_datas = s_datas.get(symbol)
    if number != 0:
        trade_datas = trade_datas[-number:]
    config = {
        "down_count": 3
    }
    ts = TradingStraregyOne(config)
    data_len = len(trade_datas)
    user = "ddvv"
    sell_price = 9999999.9
    for i in range(0, data_len):
        iter_datas = trade_datas[:i+1]
        high_price = float(trade_datas[i][2])
        if ts.is_sell(sell_price, high_price):
            sell_price = 9999999.9
            sell_data = {
                "sell_time": trade_datas[i][0]
            }
            nb_db.status_done(user, sell_data)
        if nb_db.get_last_one_record_status(user) == TradeStatus.SELLING.value:
            continue
        if ts.is_buy_time(iter_datas):
            record_data = ts.buy(trade_datas[i])
            sell_price = record_data.get("sell_price")
            nb_db.add(record_data)
    

trade_func = {
    "trade_one": trade_one,
}


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    param = {
        "serialize_data": args.serialize_data,
        "symbol": args.symbol,
        "sqlite": args.sqlite,
        "number": args.number,
    }
    trade_func[args.trading_straregy](param)
