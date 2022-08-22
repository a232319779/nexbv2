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

from binance.client import Client


class NextBBiance(object):
    def __init__(self, api_key, api_secret, proxies={}):
        """
        初始化币安API对象
        """
        # 使用代理服务器
        if proxies:
            self.client = Client(api_key, api_secret, {"proxies": proxies})
        else:
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
        return self.client.get_symbol_info(symbol=symbol)

    def get_klines(self, symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=500):
        """
        从币安API接口，返回指定币种的K线图
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
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

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
        return self.client.order_limit_buy(
            symbol=symbol, price=price, quantity=quantity
        )

    def order_limit_sell(self, symbol, price, quantity):
        """
        通过币安API接口，设定限价卖出单
        返回值格式，同：order_limit_buy
        """
        return self.client.order_limit_sell(
            symbol=symbol, price=price, quantity=quantity
        )

    def order_market_buy(self, symbol, quantity):
        """
        通过币安API接口，设定市价买入单: taker
        返回值格式，同：order_limit_buy
        """
        return self.client.order_market_buy(symbol=symbol, quantity=quantity)

    def order_market_sell(self, symbol, quantity):
        """
        通过币安API接口，设定市价卖出单: maker
        返回值格式，同：order_limit_buy
        """
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
        return self.client.cancel_order(symbol=symbol, orderId=orderId)

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
        return self.client.get_my_trades(symbol=symbol, limit=limit)
