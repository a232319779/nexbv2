# -*- coding: utf-8 -*-
# @Time     : 2022/08/22 10:57:55
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import os
import pytest
import json
from nextbv2.configs.binance_config import BINANCE_CONFIG
from nextbv2.configs.db_config import DB_CONFIG
from nextbv2.libs.binance.apis import NextBBiance
from nextbv2.libs.db.serialize import NextBSerialize


class TestNextBV2:
    def test_binance(self):
        api_key = BINANCE_CONFIG.get("api_key")
        api_secret = BINANCE_CONFIG.get("api_secret")
        proxies = BINANCE_CONFIG.get("proxies")
        nb = NextBBiance(api_key, api_secret, proxies)
        balance = nb.get_asset_balance()
        price = nb.get_symbol_ticker("BNBUSDT")
        klines = nb.get_klines("BNBUSDT", "1h", limit=2)
        assert "asset" in balance.keys()
        assert "price" in price.keys()
        assert len(klines) > 0
        print(json.dumps(balance, indent=4))
        print(json.dumps(price, indent=4))
        print(json.dumps(klines, indent=4))

    def test_serialize(self):
        data = [
            [
                1661166000000,
                "295.90000000",
                "297.40000000",
                "295.40000000",
                "296.00000000",
                "18474.84600000",
                1661169599999,
                "5470911.33180000",
                11545,
                "9218.77300000",
                "2730214.11650000",
                "0",
            ],
            [
                1661169600000,
                "296.00000000",
                "297.10000000",
                "295.70000000",
                "296.80000000",
                "3436.04700000",
                1661173199999,
                "1018695.00760000",
                1767,
                "2038.04000000",
                "604339.24460000",
                "0",
            ],
        ]
        data_path = DB_CONFIG.get("data_path")
        dir_path = os.path.dirname(data_path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        nbs = NextBSerialize(data_path)
        nbs.update_datas("BNBUSDT", data)
        assert nbs.dump_datas()
        assert nbs.load_datas()
