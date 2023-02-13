# -*- coding: utf-8 -*-
# @Time     : 2023/02/07 23:05:10
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : cli_trade_online.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import argparse
import json
from time import sleep
from nextbv2.version import NEXTB_V2_VERSION
from nextbv2.libs.logs.logs import info, error
from nextbv2.libs.common.nextb_time import timestamp_to_time
from nextbv2.libs.trade.trade_two import TradingStraregyTwo
from nextbv2.libs.db.sqlite_db import NextBTradeDB
from nextbv2.libs.common.common import parse_ini_config, create_binance
from nextbv2.libs.common.constant import (
    TradeStatus,
    BinanceDataFormat,
    CONST_BASE,
)


def parse_cmd():
    """
    数据初始化和更新
    """
    parser = argparse.ArgumentParser(
        prog="nextb-v2-trade-online",
        description="NextBv2交易工具，实现线上交易。版本号：{}".format(NEXTB_V2_VERSION),
        epilog="使用方式：nextb-v2-trade-online -h",
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
            "symbol": "BUSDUSDT",
            "base": 10.0,
            "down": 1,
            "decline": 0.03,
            "magnification": 1.0,
            "max_quote": 15000,
            "profit_ratio": 0.013,
            "force_buy": False,
            "user": "nextb",
        }
        return config


class TradeOnline(object):
    def __init__(self, param):
        self.config_file = param.get("config")
        self.trade_config_file = param.get("trade_config")
        # 1. 开始：读取配置
        # 1.1 读取币安配置
        self.config = parse_ini_config(self.config_file)
        # 1.2 读取配置中待处理的币种数据数据
        self.symbol = self.config.get("symbols")[0]
        # 1.3 读取交易配置
        self.trade_config = get_config(self.trade_config_file)
        # 1.4 初始化交易策略对象
        self.user = self.trade_config.get("user")
        self.trade_config["symbol"] = self.symbol
        self.trading_straregy = TradingStraregyTwo(self.trade_config)
        # 1.5 创建币安API对象
        self.nextb_binance = create_binance(self.config)
        # 1.6 初始化数据库对象
        sqlite_path = self.config.get("sqlite_path")
        self.nextb_sqlite_db = NextBTradeDB(sqlite_path)
        self.nextb_sqlite_db.create_table()
        self.nextb_sqlite_db.create_session()
        self.is_can_trade = self.check_asset()
        if self.is_can_trade == False:
            info("资金不足，不进行交易")

    def check_asset(self):
        asset_balance = self.nextb_binance.get_asset_balance("BUSD")
        if asset_balance:
            free = float(asset_balance.get("free"))
            if free > self.trade_config["base"]:
                info("BUSD的数量为：{}".format(free))
                return True
        else:
            error("获取当前资产出错。")
        return False

    def get_binance_data(self):
        symbol = self.config.get("symbols")[0]
        klines_interval = self.config.get("klines_interval", "1h")
        limit = self.config.get("limit", 3)
        # 从接口获取数据
        param = {
            "symbol": symbol,
            "interval": klines_interval,
            "limit": limit,
            "startTime": None,
            "endtTime": None,
        }
        return self.nextb_binance.get_klines(param)

    def buy(self):
        # 获取最近3条交易数据
        datas = self.get_binance_data()
        if datas is None:
            error("查询{}数据失败。".format(self.symbol))
            exit()
        # 判断是否买入
        if self.trading_straregy.is_buy_time(datas):
            # 按当前价格计算。假设程序时间很短，买入价格就是计算的那个价格，后续可以考虑优化这里的计算值，提升收益率计算的准确性
            # 假设这个计算过程非常段，市场价格变化几乎可以忽略不计
            buy_data = self.trading_straregy.buy(datas[-1])
            buy_quantity = buy_data["buy_quantity"]
            # 调用币安接口买入
            trade_info = self.nextb_binance.order_market_buy(
                symbol=self.symbol, quantity=buy_quantity
            )
            orderId = trade_info["orderId"]
            status = trade_info["status"]
            workingTime = trade_info["workingTime"]
            # 最长等待15秒，等待交易完成
            for _ in range(0, 15):
                if status == "FILLED":
                    break
                order_info = self.nextb_binance.get_order(self.symbol, orderId)
                status = order_info["status"]
                workingTime = order_info["workingTime"]
                sleep(1)
            # 买入完成
            if status == "FILLED":
                buy_data["buy_time"] = workingTime
                # buy_data["buy_price"] = trade_info["fill"][0]["price"]
                buy_data["user"] = self.user
                buy_data["trading_straregy_name"] = self.trading_straregy.__name__
                buy_data["symbol"] = self.symbol
                sell_price = buy_data["sell_price"]
                sell_quantity = buy_data["sell_quantity"]
                sell_trade_info = self.nextb_binance.order_limit_sell(
                    self.symbol, sell_price, sell_quantity
                )
                sell_order_id = sell_trade_info["orderId"]
                # 仅保存挂单ID
                buy_data["order_id"] = sell_order_id
                self.nextb_sqlite_db.add(buy_data)
                info("卖出挂单号为：{}".format(sell_order_id))
            else:
                error(
                    "出现错误：{}市价（{}）买入{}个失败。订单ID：{}".format(
                        self.symbol, buy_data["buy_price"], buy_quantity, orderId
                    )
                )
                exit(0)
        else:
            info(
                "不买入。币种：{}，收盘价格：{}，收盘时间：{}".format(
                    self.symbol,
                    datas[-1][BinanceDataFormat.CLOSE_PRICE],
                    timestamp_to_time(datas[-1][BinanceDataFormat.CLOSE_TIME]),
                )
            )

    def buy_again(self, last_trade_one):
        datas = self.get_binance_data()
        # 判断是否需要买入
        if self.trading_straregy.is_buy_again(datas[-1], last_trade_one):
            buy_data = self.trading_straregy.buy_again(datas[-1], last_trade_one)
            if buy_data:
                # 取消当前订单
                order_id = last_trade_one.order_id
                self.nextb_binance.cancel_order(self.symbol, order_id)
                sleep(1)
                cancale_info = self.nextb_binance.get_order(self.symbol, order_id)
                cancale_status = cancale_info["status"]
                for _ in range(0, 15):
                    if cancale_status == "CANCELED":
                        break
                if cancale_status != "CANCELED":
                    error("取消订单失败，订单号：{}".format(order_id))
                # 更新交易状态
                sell_data = dict()
                sell_data["sell_time"] = cancale_info["workingTime"]
                self.nextb_sqlite_db.status_merge(self.user)
                # 补仓买入
                buy_quantity = buy_data["new_buy_quantity"]
                # 调用币安接口买入
                trade_info = self.nextb_binance.order_market_buy(
                    symbol=self.symbol, quantity=buy_quantity
                )
                orderId = trade_info["orderId"]
                status = trade_info["status"]
                workingTime = trade_info["workingTime"]
                # 最长等待15秒，等待交易完成
                for _ in range(0, 15):
                    if status == "FILLED":
                        break
                    order_info = self.nextb_binance.get_order(self.symbol, orderId)
                    status = order_info["status"]
                    workingTime = order_info["workingTime"]
                    sleep(1)
                # 买入完成
                if status == "FILLED":
                    buy_data["buy_time"] = workingTime
                    # buy_data["buy_price"] = trade_info["fill"][0]["price"]
                    buy_data["user"] = self.user
                    buy_data["trading_straregy_name"] = self.trading_straregy.__name__
                    buy_data["symbol"] = self.symbol
                    sell_price = buy_data["sell_price"]
                    sell_quantity = buy_data["sell_quantity"]
                    sell_trade_info = self.nextb_binance.order_limit_sell(
                        self.symbol, sell_price, sell_quantity
                    )
                    sell_order_id = sell_trade_info["orderId"]
                    info("卖出挂单号为：{}".format(sell_order_id))
                    # 仅保存挂单ID
                    buy_data["order_id"] = sell_order_id
                    self.nextb_sqlite_db.add(buy_data)
                else:
                    error(
                        "补仓出现错误：{}市价（{}）买入{}个失败。订单ID：{}".format(
                            self.symbol, buy_data["buy_price"], buy_quantity, orderId
                        )
                    )
                    exit(0)
            else:
                quote = last_trade_one.buy_quote
                error(
                    "当前交易额：{}U，当前资产：{}，已超过最大本金：{}".format(
                        quote,
                        self.trade_config["max_quote"],
                        quote + self.trade_config["max_quote"] - CONST_BASE,
                    )
                )
        else:
            buy_price = last_trade_one.buy_price
            close_price = float(datas[-1][BinanceDataFormat.CLOSE_PRICE])
            amp = round((1 - buy_price / close_price) * 100, 2)
            info("无需补仓，买入价格：{}，当前价格：{}，振幅：{}%".format(buy_price, close_price, amp))

    def run(self):
        # 2. 查询最近一条交易记录
        last_trade_one = self.nextb_sqlite_db.get_last_one(self.user)
        # 如果有交易记录，且交易状态为卖出中
        if last_trade_one and last_trade_one.status == TradeStatus.SELLING.value:
            order_id = last_trade_one.order_id
            trade_info = self.nextb_binance.get_order(self.symbol, order_id)
            status = trade_info["status"]
            # 交易完成
            if status == "FILLED":
                sell_data = dict()
                sell_data["sell_time"] = trade_info["workingTime"]
                self.nextb_sqlite_db.status_done(self.user, sell_data)
                if self.is_can_trade:
                    # 开始下一次购买
                    self.buy()
            # 卖出中
            elif status in ["NEW", "PARTIALLY_FILLED"]:
                if self.is_can_trade:
                    self.buy_again(last_trade_one)
            # 取消订单（人工干预）
            elif status == "CANCELED":
                sell_data = dict()
                sell_data["sell_time"] = trade_info["workingTime"]
                self.nextb_sqlite_db.status_canceled(last_trade_one.id, sell_data)
                info("最后一条交易记录已取消，订单号：{}。".format(last_trade_one.order_id))
                info("重头开始买入。")
                if self.is_can_trade:
                    self.buy()
            # 其他状态
            else:
                error("订单：{}状态异常，异常信息：{}".format(order_id, json.dumps(trade_info)))
        # 没有交易记录
        else:
            self.buy()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    param = {
        "config": args.config,
        "trade_config": args.trade_config,
    }
    # 每小时的第59分钟运行程序，先sleep30秒，尽可能保证程序使用收盘价
    sleep(30)
    to = TradeOnline(param)
    to.run()
