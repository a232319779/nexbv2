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

import os
import pickle
import datetime
from nextbv2.libs.logs.logs import *


class NextBSerialize(object):
    def __init__(self, data_path):
        """
        初始化序列化对象
        data_path：序列化对象路径
        """
        self.datas = dict()
        self.data_path = data_path
        info("初始化数据序列化对象，数据保存路径为：{}".format(data_path))

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
            error("加载序列化数据失败，失败原因：{}".format(str(e)))
            return False
        info(
            "加载序列化数据成功，数据路径：{}，数据大小：{}mb".format(
                self.data_path, os.path.getsize(self.data_path) / 1024 / 1024
            )
        )
        return True

    def dump_datas(self):
        """
        保存币种K线数据
        保存成功返回True，失败返回False
        数据格式见self.load_datas()
        """
        # 空字典则返回错误
        if not self.datas:
            error("保存序列化数据失败，失败原因：数据为空。")
            return False

        with open(self.data_path, "wb") as f:
            pickle.dump(self.datas, f, 2)
        info(
            "保存序列化数据成功，数据存储路径：{}，数据大小：{}mb".format(
                self.data_path, os.path.getsize(self.data_path) / 1024 / 1024
            )
        )
        return True

    def update_datas(self, symbol, datas):
        """
        更新指定币种的K线数据
        数据格式见self.load_datas()
        """
        # 只更新到上一个整点
        datas = datas[:-1]
        if len(datas) == 0:
            error("更新序列化数据失败，失败原因：更新数据集为空")
            return False
        # 获取上一个整点
        now_time = datetime.datetime.now() - datetime.timedelta(minutes=60)
        # 已包含指定币种数据，则直接追加更新
        if symbol in self.datas.keys():
            update_time_str = self.datas[symbol].get("update_time", "")
            if update_time_str == "":
                return False
            update_time = datetime.datetime.strptime(
                update_time_str, "%Y-%m-%d %H:00:00"
            )
            dlt_time = now_time - update_time
            time_hour = dlt_time.days * 24 + dlt_time.seconds // 3600
            # 只有当时间间隔与数据长度相等时才更新数据
            if time_hour > 0 and time_hour == len(datas):
                self.datas[symbol]["update_time"] = now_time.strftime(
                    "%Y-%m-%d %H:00:00"
                )
                self.datas[symbol]["data"].extend(datas)
                info("更新序列化数据成功，币种-{}新增{}条数据".format(symbol, len(datas)))
            else:
                error(
                    "更新序列化数据失败，失败原因：更新数据间隔时常与数据数量不一致或者不用更新。时间间隔为：{}，更新数据数量为：{}".format(
                        time_hour, len(datas)
                    )
                )
                return False
        else:
            self.datas[symbol] = dict()
            self.datas[symbol]["update_time"] = now_time.strftime("%Y-%m-%d %H:00:00")
            self.datas[symbol]["data"] = list()
            self.datas[symbol]["data"].extend(datas)
            info("更新序列化数据成功，新增币种类型：{}，新增数据数量：{}".format(symbol, len(datas)))

        return True

    def get_symbol_info(self):
        """
        返回当前数据集中包含的币种和时间信息
        """
        symbol_info = dict()
        for symobl, info in self.datas.items():
            symbol_info[symobl] = info.get("update_time")

        return symbol_info

    def get_datas(self):
        """
        返回数据集
        """
        return self.datas
