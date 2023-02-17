# -*- coding: utf-8 -*-
# @Time     : 2022/08/22 10:07:32
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : apis.py
# @Software : Visual Studio Code
# @WeChat   : NextB

__doc__ = """
从币安交易平台获取数据，提供方法包括：
    1. get_symbol_info()：返回指定币种信息
    2. get_klines()：返回指定币种的K线图
    3. get_asset_balance()：返回账户指定币种余额
    4. get_symbol_ticker()：返回指定币种的当前价格
    5. order_limit_buy()：限价买入单
    6. order_limit_sell：限价卖出单
    7. order_market_buy()：市价买入单
    8. order_market_sell()：市价卖出单
    9. get_order()：获取订单状态
    10. cancel_order()：取消订单
    11. get_my_trades()：获取历史成交记录
"""

import json
from binance.client import Client
from nextbv2.libs.logs.logs import *


class NextBBinance(object):
    def __init__(self, api_key, api_secret, proxies={}):
        """
        初始化币安API对象
        """
        # 使用代理服务器
        if proxies:
            debug("初始化币安api接口对象，代理地址设置为：{}".format(json.dumps(proxies)))
            self.client = Client(api_key, api_secret, {"proxies": proxies})
        else:
            debug("初始化币安api接口对象，不使用代理。")
            self.client = Client(api_key, api_secret)

    def get_symbol_info(self, symbol):
        """
        从币安API接口，返回指定币种信息
        返回值格式：
        {
            "symbol": "ETHBTC",
            "status": "TRADING",
            "baseAsset": "ETH",
            "baseAssetPrecision": 8,
            "quoteAsset": "BTC",
            "quotePrecision": 8,
            "orderTypes": ["LIMIT", "MARKET"],
            "icebergAllowed": false,
            "filters": [
                {
                    "filterType": "PRICE_FILTER",
                    "minPrice": "0.00000100",
                    "maxPrice": "100000.00000000",
                    "tickSize": "0.00000100"
                }, {
                    "filterType": "LOT_SIZE",
                    "minQty": "0.00100000",
                    "maxQty": "100000.00000000",
                    "stepSize": "0.00100000"
                }, {
                    "filterType": "MIN_NOTIONAL",
                    "minNotional": "0.00100000"
                }
            ]
        }
        """
        info("查询币种-{}的信息。".format(symbol))
        return self.client.get_symbol_info(symbol=symbol)

    def get_klines(self, param):
        """
        从币安API接口，返回指定币种的K线图
        :symbol: 币种名称, 字符串, 必填
        :interval: K线类型, 字符串
        :limit: 单次返回数据长度, 整数, 最大默认1000条
        :startTime: 查询起始时间, 时间戳类型
        :endTime: 查询结束时间, 时间戳类型
        返回值格式：
        [
            [
                1499040000000,      # Open time
                "0.01634790",       # Open
                "0.80000000",       # High
                "0.01575800",       # Low
                "0.01577100",       # Close
                "148976.11427815",  # Volume
                1499644799999,      # Close time
                "2434.19055334",    # Quote asset volume
                308,                # Number of trades
                "1756.87402397",    # Taker buy base asset volume
                "28.46694368",      # Taker buy quote asset volume
                "17928899.62484339" # Can be ignored
            ]
        ]
        """
        try:
            r_param = {
                "symbol": param.get("symbol", ""),
                "interval": param.get("interval", Client.KLINE_INTERVAL_1HOUR),
                "limit": param.get("limit", 1000),
                "startTime": param.get("startTime", None),
                "endtTime": param.get("endtTime", None),
            }
            symbol = r_param.get("symbol")
            if symbol == "":
                error("获取币种-{}K线数据失败，失败原因：{}".format(symbol, "未指定币种信息。"))
                return None
            debug("获取币种-{}的K线数据。".format(symbol))
            return self.client.get_klines(**r_param)
        except Exception as e:
            error("获取币种-{}K线数据失败，失败原因：{}".format(symbol, str(e)))
            return None

    def get_asset_balance(self, symbol="USDT"):
        """
        从币安API接口，返回账户指定币种余额
        返回值格式：
        {
            "asset": "BTC",
            "free": "4723846.89208129",
            "locked": "0.00000000"
        }
        """
        debug("查询钱包中币种-{}的数量。".format(symbol))
        return self.client.get_asset_balance(symbol)

    def get_symbol_ticker(self, symbol):
        """
        从币安API接口，返回指定币种的当前价格
        返回值格式：
        {
            "symbol": "LTCBTC",
            "price": "4.00000200"
        }
        """
        info("查询币种-{}的价格。".format(symbol))
        return self.client.get_symbol_ticker(symbol=symbol)

    def order_limit_buy(self, symbol, price, quantity):
        """
        通过币安API接口，设定限价买入单
        返回值格式：
        {
            "symbol": "BTCUSDT",
            "orderId": 28,
            "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
            "transactTime": 1507725176595,
            "price": "0.00000000",
            "origQty": "10.00000000",
            "executedQty": "10.00000000",
            "status": "FILLED",
            "timeInForce": "GTC",
            "type": "MARKET",
            "side": "SELL",
            "fills": [
                {
                    "price": "4000.00000000",
                    "qty": "1.00000000",
                    "commission": "4.00000000",
                    "commissionAsset": "USDT"
                },
                {
                    "price": "3999.00000000",
                    "qty": "5.00000000",
                    "commission": "19.99500000",
                    "commissionAsset": "USDT"
                },
                {
                    "price": "3998.00000000",
                    "qty": "2.00000000",
                    "commission": "7.99600000",
                    "commissionAsset": "USDT"
                },
                {
                    "price": "3997.00000000",
                    "qty": "1.00000000",
                    "commission": "3.99700000",
                    "commissionAsset": "USDT"
                },
                {
                    "price": "3995.00000000",
                    "qty": "1.00000000",
                    "commission": "3.99500000",
                    "commissionAsset": "USDT"
                }
            ]
        }
        """
        info("设定币种-{}的买入价格，价格为：{}，数量为：{}。".format(symbol, price, quantity))
        return self.client.order_limit_buy(
            symbol=symbol, price=price, quantity=quantity
        )

    def order_limit_sell(self, symbol, price, quantity):
        """
        通过币安API接口，设定限价卖出单
        返回值格式，同：order_limit_buy
        """
        info("设定币种-{}的卖出价格，价格为：{}，数量为：{}。".format(symbol, price, quantity))
        return self.client.order_limit_sell(
            symbol=symbol, price=price, quantity=quantity
        )

    def order_market_buy(self, symbol, quantity):
        """
        通过币安API接口，设定市价买入单: taker
        返回值格式，同：order_limit_buy
        """
        info("按市价买入币种-{}，数量为：{}。".format(symbol, quantity))
        return self.client.order_market_buy(symbol=symbol, quantity=quantity)

    def order_market_sell(self, symbol, quantity):
        """
        通过币安API接口，设定市价卖出单: maker
        返回值格式，同：order_limit_buy
        """
        info("按市价卖出币种-{}，数量为：{}。".format(symbol, quantity))
        return self.client.order_market_sell(symbol=symbol, quantity=quantity)

    def get_order(self, symbol, orderId):
        """
        通过币安API接口，获取订单状态
        返回值格式：
        {
            "symbol": "LTCBTC",
            "orderId": 1,
            "clientOrderId": "myOrder1",
            "price": "0.1",
            "origQty": "1.0",
            "executedQty": "0.0",
            "status": "NEW",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "stopPrice": "0.0",
            "icebergQty": "0.0",
            "time": 1499827319559
        }
        """
        info("查询币种-{}的订单信息，订单编号：{}。".format(symbol, orderId))
        return self.client.get_order(symbol=symbol, orderId=orderId)

    def cancel_order(self, symbol, orderId):
        """
        通过币安API接口，取消订单
        返回值格式：
        {
            "symbol": "LTCBTC",
            "origClientOrderId": "myOrder1",
            "orderId": 1,
            "clientOrderId": "cancelMyOrder1"
        }
        """
        try:
            info("取消币种-{}的订单，订单编号：{}。".format(symbol, orderId))
            return self.client.cancel_order(symbol=symbol, orderId=orderId)
        except Exception as e:
            error("取消订单失败，失败原因：{}".format(str(e)))
        return None

    def get_my_trades(self, symbol, limit=5):
        """
        通过币安API接口，获取历史成交记录
        返回值格式：
        [
            {
                "id": 28457,
                "price": "4.00000100",
                "qty": "12.00000000",
                "commission": "10.10000000",
                "commissionAsset": "BNB",
                "time": 1499865549590,
                "isBuyer": true,
                "isMaker": false,
                "isBestMatch": true
            }
        ]
        """
        info("查询币种-{}最近的{}次交易信息。".format(symbol, limit))
        return self.client.get_my_trades(symbol=symbol, limit=limit)
