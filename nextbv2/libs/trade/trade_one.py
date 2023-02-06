# -*- coding: utf-8 -*-
# @Time     : 2023/02/03 14:07:58
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : trade_one.py
# @Software : Visual Studio Code
# @WeChat   : NextB

__doc__ = """
交易策略1：

1. 监测到每连续下跌N次，则按开盘价买入固定的仓位
2. 计算盈利值为Y的价格，挂单卖出
3. 检查交易状态，如果完成，则开启下一轮，否则继续等待
"""

from nextbv2.libs.common.constant import TradeStatus


class TradingStraregyOne(object):
    def __init__(self, config):
        self.config = config

    def is_buy_time(self, datas):
        """
        分析传入的数据，判断是否可以买入。本策略中，通过分析最近时间连续下跌次数来判断是否满足买入条件
        参数：datas，原始数据类型，参考NextBSerialize的结构
        返回值：True：买入，False：不买入
        """
        down_count = self.config.get("down_count", 3)
        if down_count > len(datas):
            return False
        for i in range(-1, -down_count - 1, -1):
            open_price = float(datas[i][1])
            close_price = float(datas[i][4])
            if close_price > open_price:
                return False

        return True

    def buy(self, data):
        # 先假设固定买入100U
        buy_quote = 100.0
        buy_price = float(data[4])
        # 向下取整，买入和卖出的数量就一致了
        quantity = round(buy_quote / buy_price - 0.0005, 3)
        # 向上取整
        sell_price = round(buy_price * 1.011 + 0.05, 1)
        sell_quote = sell_price * quantity
        profit = sell_quote - buy_quote
        profit_ratio = profit / buy_quote
        record_data = {
            "order_id": 1234,
            "buy_price": buy_price,
            "buy_quantity": quantity,
            "buy_quote": buy_quote,
            "buy_time": data[0],
            "sell_price": sell_price,
            "sell_quantity": quantity,
            "sell_quote": sell_quote,
            "sell_time": data[0],
            "profit": sell_quote - buy_quote,
            "profit_ratio": profit_ratio,
            "status": TradeStatus.SELLING.value,
        }
        # to do: 调用币安api实现真正的买入
        # 
        # 目前假设买入
        return record_data

    def is_sell(self, sell_price, high_price):
        """
        如果当前的最高价大于指定卖出价格，则返回True，否则返回False
        """
        if high_price > sell_price:
            return True
        return False
