# -*- coding: utf-8 -*-
# @Time     : 2022/08/22 13:23:56
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : serialize.py
# @Software : Visual Studio Code
# @WeChat   : NextB

__doc__ = """
序列化交易币种K线数据：
    1. load_datas()：加载币种K线数据
    2. dump_datas()：保存币种K线数据
"""

import pickle
import datetime


class NextBSerialize(object):
    def __init__(self, data_path):
        """
        初始化序列化对象
        data_path：序列化对象路径
        """
        self.datas = dict()
        self.data_path = data_path

    def load_datas(self):
        """
        加载币种K线数据
        加载成功返回True，失败返回False
        数据格式如：
        {
            "BNBUSDT": {
                "update_time": "2020-08-22 10:00:00",
                "data": [
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
            }
        }
        """
        try:
            with open(self.data_path, "rb") as f:
                self.datas = pickle.load(f)
        except Exception as e:
            return False
        return True

    def dump_datas(self):
        """
        保存币种K线数据
        保存成功返回True，失败返回False
        数据格式见self.load_datas()
        """
        # 空字典则返回错误
        if not self.datas:
            return False
        update_time = self.datas.get("update_time", "")
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:00:00")
        # 避免同一小时内，多次更新导致数据不一致
        if update_time[:13] != now_time[:13]:
            with open(self.data_path, "wb") as f:
                pickle.dump(self.datas, f, 2)
        return True

    def update_datas(self, symbol, datas):
        """
        更新指定币种的K线数据
        数据格式见self.load_datas()
        """
        # 已包含指定币种数据，则直接追加更新
        if symbol in self.datas.keys():
            self.datas[symbol]["update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:00:00")
            self.datas[symbol]["data"].extend(datas)
        else:
            self.datas[symbol] = dict()
            self.datas[symbol]["update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:00:00")
            self.datas[symbol]["data"] = list()
            self.datas[symbol]["data"].extend(datas)
