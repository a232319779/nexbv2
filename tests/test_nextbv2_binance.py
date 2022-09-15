# -*- coding: utf-8 -*-
# @Time     : 2022/08/28 10:57:55
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2_binance.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import json
from nextbv2.libs.binance.apis import NextBBinance
from nextbv2.libs.logs.logs import *
from nextbv2.libs.common.common import *
from nextbv2.libs.common.constant import *


class TestNextBV2Binance:
    def test_binance(self):
        curdir = os.path.dirname(os.path.abspath(__file__))
        config = parse_ini_config(os.path.join(curdir, "./nextbv2.conf"))
        # 初始化币安API对象
        api_key = config.get("api_key")
        api_secret = config.get("api_secret")
        proxies = {}
        if config.get("proxy").lower() == CONFIG_PROXY_ON:
            proxies["http"] = config.get("http_proxy")
            proxies["https"] = config.get("https_proxy")
        symbols = config.get("symbols")
        klines_interval = config.get("klines_interval")
        nbb = NextBBinance(api_key, api_secret, proxies)
        balance = nbb.get_asset_balance()
        price = nbb.get_symbol_ticker(symbols[0])
        klines = nbb.get_klines(symbols[0], klines_interval, limit=2)
        assert "asset" in balance.keys()
        assert "price" in price.keys()
        assert len(klines) > 0
        info("钱包持币信息：{}".format(json.dumps(balance)))
        info("币价信息：{}".format(json.dumps(price)))
        info("K线数据：{}".format(json.dumps(klines)))
