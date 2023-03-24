# -*- coding: utf-8 -*-
# @Time     : 2023/02/06 16:29:24
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : cli_trade_simulation.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import argparse
import json
import numpy as np
from prettytable import PrettyTable
from tqdm import tqdm
from nextbv2.version import NEXTB_V2_VERSION
from nextbv2.libs.common.constant import *
from nextbv2.libs.logs.logs import info
from nextbv2.libs.common.common import create_serialize
from nextbv2.libs.common.nextb_time import timestamp_to_time
from nextbv2.libs.trade.trade_one import TradingStraregyOne
from nextbv2.libs.trade.trade_two import TradingStraregyTwo
from nextbv2.libs.trade.trade_three import TradingStraregyThree
from nextbv2.libs.db.sqlite_db import NextBTradeDB
from nextbv2.libs.common.constant import (
    TradeStatus,
    BinanceDataFormat,
    MAX_PRICE,
    CONST_BASE,
)


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
        help="交易策略名称，当前支持[trade_one, trade_two, trade_three]，默认值：trade_two",
        type=str,
        dest="trading_straregy",
        action="store",
        default="trade_two",
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
    parser.add_argument(
        "-u",
        "--user",
        help="指定用户名称。默认值为：nextb",
        type=str,
        dest="user",
        action="store",
        default="nextb",
    )
    parser.add_argument(
        "-a",
        "--auto",
        help="指定模拟方式，自动模拟时忽略用户参数、数量参数、数据库名称。[2：表示参数遍历模拟，1：表示时间维度的自动模拟，0：表示不自动模拟]默认值为：0",
        type=int,
        dest="auto",
        action="store",
        default=0,
    )
    parser.add_argument(
        "-tc",
        "--trade_config",
        help="指定交易参数配置文件，默认为空，使用默认参数配置。",
        type=str,
        dest="trade_config",
        action="store",
        default="",
    )

    args = parser.parse_args()

    return args


def get_config(file_name):
    if file_name:
        with open(file_name, "r", encoding="utf8") as f:
            data = f.read()
            return json.loads(data)
    else:
        config = {
            "symbol": "BNBUSDT",
            "base": 100.0,
            "down": 1,
            "decline": 0.03,
            "magnification": 1.0,
            "max_quote": 15000,
            "profit_ratio": 0.013,
            "force_buy": False,
        }
        return config


def simulation(ts, nb_db, user, symbol, trade_datas, is_print=True):
    data_len = len(trade_datas)
    sell_price = MAX_PRICE
    for i in tqdm(range(0, data_len), unit="row", desc="用户{}模拟中".format(user)):
        high_price = float(trade_datas[i][BinanceDataFormat.HIGH_PRICE])
        last_trade_one = nb_db.get_last_one(user)
        status = TradeStatus.UNKNOWN.value
        if last_trade_one:
            status = last_trade_one.status
        if ts.is_sell(sell_price, high_price):
            sell_price = MAX_PRICE
            sell_data = {"sell_time": trade_datas[i][BinanceDataFormat.OPEN_TIME]}
            nb_db.status_done(last_trade_one.id, sell_data)
        if status == TradeStatus.SELLING.value:
            # 动态计算补仓阈值
            ts.calc_buy_threasold(trade_datas[: i + 1])
            # 是否需要补仓
            if ts.is_buy_again(trade_datas[:i], last_trade_one):
                record_data = ts.buy_again(trade_datas[i], last_trade_one)
                if record_data:
                    # 取消当前订单
                    sell_data = dict()
                    sell_data["sell_time"] = trade_datas[i][
                        BinanceDataFormat.CLOSE_TIME
                    ]
                    nb_db.status_merge(last_trade_one.id, sell_data)
                    record_data["user"] = user
                    record_data["trading_straregy_name"] = ts.__name__
                    record_data["order_id"] = 1234
                    record_data["symbol"] = symbol
                    sell_price = record_data.get("sell_price")
                    nb_db.add(record_data)
                else:
                    quote = last_trade_one.buy_quote
                    info("当前交易额：{}U，已超过最大本金：{}".format(quote, quote + CONST_BASE))
            continue
        if ts.is_buy_time(trade_datas[: i + 1]):
            record_data = ts.buy(trade_datas[i])
            record_data["user"] = user
            record_data["trading_straregy_name"] = ts.__name__
            record_data["order_id"] = 1234
            record_data["symbol"] = symbol
            sell_price = record_data.get("sell_price")
            nb_db.add(record_data)
    count, total_profit, status = nb_db.get_total_ratio(
        user, float(trade_datas[i][BinanceDataFormat.CLOSE_PRICE])
    )
    max_quote = nb_db.get_max_quote(user)
    mean_quote, quote_ratio = nb_db.get_quote_use_ratio(user)
    profit_ratio = round(total_profit / max_quote * 100, 2)
    status_str = "未知状态"
    if status == TradeStatus.SELLING.value:
        status_str = "卖出中"
    elif status == TradeStatus.MERGE.value:
        status_str = "已合并"
    elif status == TradeStatus.DONE.value:
        status_str = "空仓中"
    # 统计资金使用情况
    qc_list = list()
    c_total = sum(quote_ratio.values())
    for q, c in quote_ratio.items():
        c_ratio = round(c / c_total * 100, 2)
        qc_list.append([q, c, "{}%".format(c_ratio)])
    if is_print:
        x = PrettyTable()
        x.field_names = ["资金(单位: U)", "使用次数", "使用占比"]
        x.add_rows(qc_list)
        print(x)
        # 输出汇总信息
        info(
            "开始交易时间：{}，共计交易：{}次，共计获利：{}U，最大投入成本：{}U，利润率: {}%, 当前交易状态: {}".format(
                timestamp_to_time(trade_datas[0][BinanceDataFormat.OPEN_TIME]),
                count,
                total_profit,
                max_quote,
                profit_ratio,
                status_str,
            )
        )
    return ",".join(
        [
            user,
            timestamp_to_time(trade_datas[0][BinanceDataFormat.OPEN_TIME]),
            str(count),
            str(total_profit),
            str(max_quote),
            str(profit_ratio),
            str(status),
        ]
    )


def auto_simulation(ts, nb_db, symbol, trade_datas):
    datas = list()
    for j in tqdm(
        range(0, len(trade_datas), 10), unit="user", desc="{}模拟交易中".format(symbol)
    ):
        user = "nextb_{}".format(j)
        new_trade_datas = trade_datas[j:]
        data_str = simulation(ts, nb_db, user, symbol, new_trade_datas)
        data_str += ",{},{}".format(
            new_trade_datas[0][BinanceDataFormat.OPEN_PRICE],
            new_trade_datas[0][BinanceDataFormat.CLOSE_PRICE],
        )
        datas.append(data_str)
    headers = "用户名,交易时间,交易次数,利润,最大投入成本,利润率,当前状态,开盘价,收盘价"
    with open("simulation.csv", "w", encoding="utf8") as f:
        f.write(headers + "\n")
        f.write("\n".join(datas))


def auto_mutli_work(ts, nb_db, symbol, trade_datas, down):
    init_param = ts.get_param()
    init_decline = init_param.get("decline", 0.03)
    init_profit_ratio = init_param.get("profit_ratio", 0.03)
    datas = list()
    for j in tqdm(np.arange(0.002, init_decline, 0.002), unit="time", desc="下跌幅度模拟交易中"):
        for k in tqdm(
            np.arange(0.001, init_profit_ratio, 0.001), unit="user", desc="收益率模拟交易中"
        ):
            j = round(j, 4)
            k = round(k, 4)
            param = {"down": down, "decline": j, "profit_ratio": k}
            ts.set_param(param)
            user = "nextb_{}_{}_{}".format(down, j, k)
            data_str = simulation(ts, nb_db, user, symbol, trade_datas, False)
            data_str += ",{},{},{}".format(down, j, k)
            datas.append(data_str)

    return datas


def auto2_simulation(ts, nb_db, symbol, trade_datas):
    """
    不同参数的收益情况模拟
    """
    init_param = ts.get_param()
    init_down = init_param.get("down", 3)
    datas = list()
    # 单进程
    for i in tqdm(range(1, init_down + 1), unit="time", desc="下跌次数模拟交易中"):
        data = auto_mutli_work(ts, nb_db, symbol, trade_datas, i)
        datas.extend(data)
    headers = "用户名,交易时间,交易次数,利润,最大投入成本,利润率,当前状态,下降次数,下跌幅度,利润率阈值"
    with open("simulation.csv", "w", encoding="utf8") as f:
        f.write(headers + "\n")
        f.write("\n".join(datas))


def trade(param):
    serialize_data = param.get("serialize_data")
    symbol = param.get("symbol")
    auto = param.get("auto")
    sqlite_path = param.get("sqlite")
    number = param.get("number")
    user = param.get("user")
    trading_straregy = param.get("trading_straregy")
    trade_config = param.get("trade_config")
    # 创建数据库
    nb_db = NextBTradeDB(sqlite_path)
    nb_db.create_table()
    nb_db.create_session()
    # 加载仿真数据
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    s_datas = nextbv2_serialize.get_datas()
    trade_datas = s_datas.get(symbol)
    # 加载交易配置
    config = get_config(trade_config)
    config["symbol"] = symbol
    # 加载对应交易策略
    ts = trade_func[trading_straregy](config)
    if number != 0:
        trade_datas = trade_datas[-number:]
    if auto == 0:
        simulation(ts, nb_db, user, symbol, trade_datas)
    elif auto == 1:
        auto_simulation(ts, nb_db, symbol, trade_datas)
    elif auto == 2:
        auto2_simulation(ts, nb_db, symbol, trade_datas)
    else:
        print("auto 参数配置错误，程序退出。")


def get_trade_one_ts(config):
    return TradingStraregyOne(config)


def get_trade_two_ts(config):
    return TradingStraregyTwo(config)


def get_trade_three_ts(config):
    return TradingStraregyThree(config)


trade_func = {
    "trade_one": get_trade_one_ts,
    "trade_two": get_trade_two_ts,
    "trade_three": get_trade_three_ts,
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
        "user": args.user,
        "auto": args.auto,
        "trading_straregy": args.trading_straregy,
        "trade_config": args.trade_config,
    }
    trade(param)
