# -*- coding: utf-8 -*-
# @Time     : 2022/08/28 10:57:55
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2_db.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import os
from nextbv2.configs.db_config import DB_CONFIG
from nextbv2.libs.db.serialize import NextBSerialize
from nextbv2.libs.db.nbsqlite import NextBSqlite


class TestNextBV2Serialize:
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
        # 初始化序列化对象
        data_path = DB_CONFIG.get("data_path")
        dir_path = os.path.dirname(data_path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        nbs = NextBSerialize(data_path)
        nbs.update_datas("BNBUSDT", data)
        assert nbs.dump_datas()
        assert nbs.load_datas()

class TestNextBSqlite:
    def test_sqlite(self):
        data = {
            "user_id": 1,
            "trading_straregy_name": "网格交易策略",
            "order_id": 123456789,
            "symbol": "btc",
            "buy_price": 20000.0,
            "buy_quantity": 1.01,
            "buy_quote": 0.0,
            "buy_time": "2022-09-13 20:00:00",
            "sell_price": 0.0,
            "sell_quantity": 0.0,
            "sell_quote": 0.0,
            "sell_time": "1970-01-01 00:00:00",
            "profit": 0.0,
            "profit_ratio": 0.0,
            "status": 1,
            "tickSize_index": 2,
            "stepSize_index": 2,
        }
        # 初始化序列化对象
        sqlite_path = DB_CONFIG.get("sqlite_path")
        dir_path = os.path.dirname(sqlite_path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        nbs = NextBSqlite(sqlite_path)
        assert nbs.create_table()
        assert nbs.add(data)
        new_data = nbs.get_last_one(data.get("user_id", 0))
        assert new_data
        new_data["sell_price"] = 20010.0
        new_data["sell_quantity"] = 1.01
        new_data["sell_quote"] = 1.01
        new_data["sell_time"] = "2022-09-13 20:00:00"
        new_data["profit"] = 10.0
        new_data["profit_ratio"] = 0.001
        new_data["status"] = 2
        new_data["tickSize_index"] = 2
        new_data["stepSize_index"] = 2
        assert nbs.update(new_data)
        nbs.close()