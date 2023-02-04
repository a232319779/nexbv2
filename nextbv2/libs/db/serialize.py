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
from nextbv2.libs.logs.logs import *
from nextbv2.libs.common.nextb_time import timestamp_to_time, get_now_timestamp
from nextbv2.libs.common.constant import ONE_HOUR_TIMESTAMP


class NextBSerialize(object):
    def __init__(self, data_path):
        """
        初始化序列化对象
        data_path：序列化对象路径
        """
        self.datas = dict()
        self.data_path = data_path
        debug("初始化数据序列化对象，数据保存路径为：{}".format(data_path))

    def load_datas(self):
        """
        加载币种K线数据
        加载成功返回True，失败返回False
        数据格式如：
        {
            "BNBUSDT": [
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
        """
        try:
            with open(self.data_path, "rb") as f:
                self.datas = pickle.load(f)
        except Exception as e:
            error("加载序列化数据失败，失败原因：{}".format(str(e)))
            return False
        debug(
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
        if len(datas) == 0:
            error("更新序列化数据失败，失败原因：更新数据集为空")
            return False
        # 已包含指定币种数据，则直接追加更新
        if symbol in self.datas.keys():
            last_dataset_timestamp = self.datas[symbol][-1][0]
            first_data_timestamp = datas[0][0]
            # 数据集中的最后一条数据与更新数据集数据时间间隔大于1个小时，则表示数据不连续，不进行更新
            if first_data_timestamp - last_dataset_timestamp > ONE_HOUR_TIMESTAMP:
                error(
                    "更新序列化数据失败，失败原因：更新时间不连续。数据集最后一条数据时间为：{}，更新数据第一条时间为：{}".format(
                        timestamp_to_time(last_dataset_timestamp),
                        timestamp_to_time(first_data_timestamp),
                    )
                )
                return False
            # 更新数据集最后一条数据与当前时间间隔小于一小时，则删除最后一条数据
            last_data_timestamp = datas[-1][0]
            now_timestamp = get_now_timestamp()
            if now_timestamp - last_data_timestamp < ONE_HOUR_TIMESTAMP:
                del datas[-1]
            # 默认币安返回的数据是连续的，直接插入数据集末尾
            self.datas[symbol].extend(datas)
            info(
                "更新序列化数据成功，币种-{}新增{}条数据，交易数据已新至: {}".format(
                    symbol, len(datas), timestamp_to_time(datas[-1][0])
                )
            )
        else:
            self.datas[symbol] = list()
            self.datas[symbol].extend(datas)
            info(
                "更新序列化数据成功，新增币种：{}，新增数据数量：{}，交易数据已新至: {}".format(
                    symbol, len(datas), timestamp_to_time(datas[-1][0])
                )
            )

        return True

    def get_symbol_info(self):
        """
        返回当前数据集中包含的币种信息
        """
        symbol_info = self.datas.keys()
        return symbol_info

    def get_datas(self):
        """
        返回数据集
        """
        return self.datas

    def get_last_data_timestamp(self, symbol):
        return self.datas[symbol][-1][0]
