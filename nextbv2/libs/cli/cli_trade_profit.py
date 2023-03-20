# -*- coding: utf-8 -*-
# @Time     : 2023/03/17 17:29:16
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : cli_trade_profit.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import argparse
from prettytable import PrettyTable
from nextbv2.version import NEXTB_V2_VERSION
from nextbv2.libs.common.nextb_time import timestamp_to_time
from nextbv2.libs.common.constant import (
    DEFAULT_START_TIMESTAMP,
)
from nextbv2.libs.common.common import (
    parse_ini_config,
    create_binance,
)


def parse_cmd():
    """
    数据初始化和更新
    """
    parser = argparse.ArgumentParser(
        prog="nextb-v2-profit-ratio",
        description="NextBv2计算收益工具。版本号：{}".format(NEXTB_V2_VERSION),
        epilog="使用方式：nextb-v2-profit-ratio -c config_file",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="设置配置文件",
        type=str,
        dest="config",
        action="store",
        default="./nextbv2.conf",
    )

    args = parser.parse_args()

    return args


def statics(datas, open_datas):
    datas.reverse()
    symbol = datas[0].get("symbol")
    start_time = timestamp_to_time(datas[-1].get("time"))
    buy_total = 0.0
    sell_total = 0.0
    commission_total = 0.0
    for data in datas:
        quoteQty = float(data.get("quoteQty"))
        commission = float(data.get("commission"))
        commission_total += commission
        isBuyer = data.get("isBuyer")
        if isBuyer:
            buy_total += quoteQty
        else:
            sell_total += quoteQty
    for od in open_datas:
        price = float(od.get("price"))
        origQty = float(od.get("origQty"))
        sell = price * origQty
        sell_total += sell

    return [
        symbol,
        start_time,
        buy_total,
        sell_total,
        sell_total - buy_total,
        commission_total,
    ]


def total(datas):
    symbol = "汇总"
    buy_total = 0.0
    sell_total = 0.0
    profit_total = 0.0
    commission_total = 0.0
    start_time = datas[0][1]
    for data in datas:
        buy = data[2]
        sell = data[3]
        profit = data[4]
        commission = data[5]
        buy_total += buy
        sell_total += sell
        profit_total += profit
        commission_total += commission

    return [symbol, start_time, buy_total, sell_total, profit_total, commission_total]


def get_profit_ratio(config_file):
    """
    计算交易收益情况
    config_file：配置文件路径，str
    """
    # 读取配置
    config = parse_ini_config(config_file)

    # 创建币安API对象
    nextb_binance = create_binance(config)

    # 读取配置中待处理的币种数据数据
    symbols = config.get("symbols")
    limit = config.get("limit", 1000)
    x_datas = list()
    for symbol in symbols:
        # 默认从2023.02.01 00:00:00开始获取 1675180800000
        startTime = config.get("start_time", DEFAULT_START_TIMESTAMP)
        # 从接口获取数据
        datas = nextb_binance.get_my_trades(
            symbol=symbol, startTime=startTime, limit=limit
        )
        open_datas = nextb_binance.get_open_orders(symbol=symbol)
        x_datas.append(statics(datas, open_datas))
    x_datas.append(total(x_datas))

    x = PrettyTable()
    x.field_names = ["币种", "开始时间", "总支付金额", "总收入金额", "利润", "手续费"]
    x.add_rows(x_datas)
    print(x)


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    get_profit_ratio(args.config)
