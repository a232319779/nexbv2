# -*- coding: utf-8 -*-
# @Time     : 2023/04/14 17:26:27
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : cli_trade_cost.py
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
        prog="nextb-v2-profit-cost",
        description="NextBv2计算成本工具。版本号：{}".format(NEXTB_V2_VERSION),
        epilog="使用方式：nextb-v2-profit-cost -c config_file",
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


def statics(datas):
    datas.reverse()
    symbol = datas[0].get("symbol")
    out_datas = list()
    for data in datas:
        price = data.get("price")
        buy_time = timestamp_to_time(data.get("time"))
        qty = float(data.get("qty"))
        quoteQty = float(data.get("quoteQty"))
        commission = float(data.get("commission"))
        isBuyer = data.get("isBuyer")
        if isBuyer:
            out_datas.append([symbol, buy_time, price, qty, quoteQty, commission])

    return out_datas


def total(datas):
    symbol = "{}汇总".format(datas[0][0])
    total_qty = sum([d[3] for d in datas])
    total_quote_qty = sum([d[4] for d in datas])
    total_commission = sum([d[-1] for d in datas])
    price = round(total_quote_qty / total_qty, 4)

    return [symbol, "/", price, total_qty, total_quote_qty, total_commission]


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
        # 默认从2022.01.01 00:00:00开始获取 1640966400000
        startTime = config.get("start_time", DEFAULT_START_TIMESTAMP)
        # 从接口获取数据
        datas = nextb_binance.get_my_trades(
            symbol=symbol, startTime=startTime, limit=limit
        )
        if datas:
            s_datas = statics(datas)
            x_datas.extend(s_datas)
            x_datas.append(total(s_datas))
        else:
            print("没有{}币种的交易信息".format(symbol))

    x = PrettyTable()
    x.field_names = ["币种", "交易时间", "买入价格", "买入数量", "支付金额", "手续费"]
    x.add_rows(x_datas)
    print(x)


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    get_profit_ratio(args.config)
