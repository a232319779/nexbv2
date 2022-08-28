# -*- coding: utf-8 -*-
# @Time     : 2022/08/28 10:57:55
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2_cli.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import os
import pytest
from nextbv2.configs.binance_config import BINANCE_CONFIG
from nextbv2.configs.db_config import DB_CONFIG
from nextbv2.libs.binance.apis import NextBBinance
from nextbv2.libs.db.serialize import NextBSerialize
from nextbv2.libs.cli.cli import NextBV2CLI


class TestNextBV2CLI:
    def test_cli(self):
        # 初始化币安API对象
        api_key = BINANCE_CONFIG.get("api_key")
        api_secret = BINANCE_CONFIG.get("api_secret")
        proxies = BINANCE_CONFIG.get("proxies")
        nbb = NextBBinance(api_key, api_secret, proxies)
        # 初始化序列化对象
        data_path = DB_CONFIG.get("data_path")
        dir_path = os.path.dirname(data_path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        nbs = NextBSerialize(data_path)
        # 初始化命令行对象
        self.nbc = NextBV2CLI(nextb_binance=nbb, nextb_serialize=nbs)
        assert self.nbc.cli_init_data("BNBUSDT")
        assert self.nbc.cli_update_data("BNBUSDT", limit=1) == False
