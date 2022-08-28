# -*- coding: utf-8 -*-
# @Time     : 2022/08/28 10:57:55
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2_binance.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import pytest
import json
from nextbv2.configs.binance_config import BINANCE_CONFIG
from nextbv2.libs.binance.apis import NextBBinance
from nextbv2.libs.logs.logs import *


class TestNextBV2Binance:
    def test_binance(self):
        # 初始化币安API对象
        api_key = BINANCE_CONFIG.get("api_key")
        api_secret = BINANCE_CONFIG.get("api_secret")
        proxies = BINANCE_CONFIG.get("proxies")
        nbb = NextBBinance(api_key, api_secret, proxies)
        balance = nbb.get_asset_balance()
        price = nbb.get_symbol_ticker("BNBUSDT")
        klines = nbb.get_klines("BNBUSDT", "1h", limit=2)
        assert "asset" in balance.keys()
        assert "price" in price.keys()
        assert len(klines) > 0
        info("钱包持币信息：{}".format(json.dumps(balance)))
        info("币价信息：{}".format(json.dumps(price)))
        info("K线数据：{}".format(json.dumps(klines)))
