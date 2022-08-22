# -*- coding: utf-8 -*-
# @Time     : 2022/08/22 10:57:55
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import pytest
import json
from nextbv2.configs.binance_config import BINANCE_CONFIG
from nextbv2.libs.binance.apis import NextBBiance

class TestNextBV2():
    def test_binance(self):
        api_key = BINANCE_CONFIG.get("api_key")
        api_secret = BINANCE_CONFIG.get("api_secret")
        proxies = BINANCE_CONFIG.get("proxies")
        nb = NextBBiance(api_key, api_secret, proxies)
        balance = nb.get_asset_balance()
        price = nb.get_symbol_ticker("BNBUSDT")
        klines = nb.get_klines("BNBUSDT", "1h", limit=2)
        assert 'asset' in balance.keys()
        assert 'price' in price.keys()
        assert len(klines) > 0
        print(json.dumps(balance, indent=4))
        print(json.dumps(price, indent=4))
        print(json.dumps(klines, indent=4))
