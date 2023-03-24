# -*- coding: utf-8 -*-
# @Time     : 2023/02/06 15:20:23
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : trade_two.py
# @Software : Visual Studio Code
# @WeChat   : NextB


__doc__ = """
交易策略2：

1. 监测到每连续下跌N次，则按开盘价买入固定的仓位
2. 计算盈利值为Y的价格，挂单卖出
3. 如果下跌超过D%，则取消当前挂单，以当前开盘价买入固定的仓位
4. 重新计算盈利值为Y1的价格，挂单卖出
5. 继续3、4步
6. 若卖出则继续下一次，否则继续等待
"""

from nextbv2.libs.common.constant import (
    TradeStatus,
    BinanceDataFormat,
    CONST_BASE,
    CONST_CUTDOWN,
    CONST_DECLINE,
    CONST_MAGNIFICATION,
    CONST_MAX_QUOTE,
    CONST_PROFIT_RATIO,
    CONST_FORCE_BUY,
    SYMBOL_CALC_CONFIG,
)


class TradingStraregyTwo(object):
    __name__ = "trade_two"

    def __init__(self, config):
        # 默认精确度
        self.symbol = config.get("symbol", "BNBUSDT")
        self.base = config.get("base", CONST_BASE)
        self.down = config.get("down", CONST_CUTDOWN)
        self.decline = config.get("decline", CONST_DECLINE)
        self.magnification = config.get("magnification", CONST_MAGNIFICATION)
        self.max_quote = config.get("max_quote", CONST_MAX_QUOTE)
        self.profit_ratio = config.get("profit_ratio", CONST_PROFIT_RATIO)
        self.force_buy = config.get("force_buy", CONST_FORCE_BUY)

    def get_param(self):
        param = {
            "down": self.down,
            "decline": self.decline,
            "profit_ratio": self.profit_ratio,
        }
        return param

    def set_param(self, param):
        self.down = param.get("down", CONST_CUTDOWN)
        self.decline = param.get("decline", CONST_DECLINE)
        self.profit_ratio = param.get("profit_ratio", CONST_PROFIT_RATIO)

    def is_buy_time(self, datas):
        """
        分析传入的数据，判断是否可以买入。本策略中，通过分析最近时间连续下跌次数来判断是否满足买入条件
        参数：datas，原始数据类型，参考NextBSerialize的结构
        返回值：True：买入，False：不买入
        """
        if self.force_buy:
            return True
        if self.down > len(datas):
            return False
        new_price = float(datas[-1][BinanceDataFormat.CLOSE_PRICE])
        old_price = float(datas[-self.down][BinanceDataFormat.OPEN_PRICE])
        ratio = round(1.0 - new_price / old_price, 4)
        # 跌幅达到指定指标
        if ratio > CONST_DECLINE / 2:
            return True
        # 连续下跌达到指定次数
        for i in range(-1, -self.down - 1, -1):
            open_price = float(datas[i][BinanceDataFormat.OPEN_PRICE])
            close_price = float(datas[i][BinanceDataFormat.CLOSE_PRICE])
            if close_price > open_price:
                return False

        return True

    def is_buy_again(self, current_data, trade_data):
        """
        分析传入的数据与交易数据跌幅
        """
        # 条件1：如果当前价格较上一次的买入价格跌幅达到指定阈值，则买入
        last_buy_price = trade_data.buy_price
        close_price = float(current_data[-1][BinanceDataFormat.CLOSE_PRICE])
        ratio = round(1.0 - close_price / last_buy_price, 4)
        if ratio > self.decline:
            return True

        # 条件2：如果当前价格，较3小时前内的开盘价跌幅达到指定阈值，则买入
        data_len = len(current_data)
        index = -data_len if data_len < 3 else -3
        last_3_open_price = float(current_data[index][BinanceDataFormat.OPEN_PRICE])
        hit_ratio = round(1.0 - close_price / last_3_open_price, 4)
        if hit_ratio > self.decline:
            return True
        # 否则不补仓
        return False

    def buy(self, data):
        # 获取交易币种的精确度信息等
        symbol_trade_config = SYMBOL_CALC_CONFIG.get(self.symbol)
        if symbol_trade_config is None:
            symbol_trade_config = SYMBOL_CALC_CONFIG.get("BNBUSDT")
        quantity_accuracy = symbol_trade_config["quantity_accuracy"]
        quantity_offset = symbol_trade_config["quantity_offset"]
        price_accuracy = symbol_trade_config["price_accuracy"]
        price_offset = symbol_trade_config["price_offset"]
        # 假设固定买入
        buy_quote = self.base
        buy_price = float(data[BinanceDataFormat.CLOSE_PRICE])
        # 向下取整，买入和卖出的数量就一致了
        quantity = round(buy_quote / buy_price - quantity_offset, quantity_accuracy)
        # 向上取整
        sell_price = round(
            buy_price * (1 + self.profit_ratio) + price_offset, price_accuracy
        )
        sell_quote = round(sell_price * quantity, 2)
        profit = round(sell_quote - buy_quote, 2)
        profit_ratio = round(profit / buy_quote, 3)
        record_data = {
            "buy_price": buy_price,
            "buy_quantity": quantity,
            "buy_quote": buy_quote,
            "buy_time": data[BinanceDataFormat.OPEN_TIME],
            "sell_price": sell_price,
            "sell_quantity": quantity,
            "sell_quote": sell_quote,
            "sell_time": data[BinanceDataFormat.OPEN_TIME],
            "profit": profit,
            "profit_ratio": profit_ratio,
            "status": TradeStatus.SELLING.value,
        }

        return record_data

    def is_sell(self, sell_price, high_price):
        """
        如果当前的最高价大于指定卖出价格，则返回True，否则返回False
        """
        if high_price > sell_price:
            return True
        return False

    def buy_again(self, data, trade_data):
        """
        已知上次交易的成本为a1，交易数量为b1，交易价格为c1，本次交易成本为a2,交易价格为c2，则交易数量b2=a2/c2。
        那么，结合上次的交易情况，本次的交易卖出价格应该设定为多少，能保证总的收益率达到1.1%。
        收益率公式为：本次卖出价格x2 * 总的交易数量(b1 + b2) / 总的交易成本(a1 + a2) - 1.0 = 0.011
        本次交易数量b2为： b2 = a2 / c2
        则x2 = 1.011 * (a1 + a2) / ( b1 + a2 / c2)
        则卖出价格是当前价格的百分比为: r = x2 / c2 - 1.0
        """
        # 获取交易币种的精确度信息等
        symbol_trade_config = SYMBOL_CALC_CONFIG.get(self.symbol)
        if symbol_trade_config is None:
            symbol_trade_config = SYMBOL_CALC_CONFIG.get("BNBUSDT")
        quantity_accuracy = symbol_trade_config["quantity_accuracy"]
        quantity_offset = symbol_trade_config["quantity_offset"]
        price_accuracy = symbol_trade_config["price_accuracy"]
        price_offset = symbol_trade_config["price_offset"]
        # 上一次的成本
        last_buy_quote = trade_data.buy_quote
        # 上一次的数量
        last_buy_quantity = trade_data.buy_quantity
        # 本次的成本
        buy_quote = self.base * self.magnification
        buy_price = float(data[BinanceDataFormat.CLOSE_PRICE])
        # 向下取整，买入和卖出的数量就一致了
        quantity = round(buy_quote / buy_price - quantity_offset, quantity_accuracy)
        quantity_total = round(last_buy_quantity + quantity, quantity_accuracy)
        buy_quote_total = last_buy_quote + buy_quote
        if buy_quote_total > self.max_quote:
            return {}
        # 向上取整
        sell_price = round(
            (1 + self.profit_ratio) * buy_quote_total / quantity_total + price_offset,
            price_accuracy,
        )
        sell_quote = round(sell_price * quantity_total, 2)
        profit = round(sell_quote - buy_quote_total, 2)
        profit_ratio = round(profit / buy_quote_total, 3)
        record_data = {
            "buy_price": buy_price,
            "buy_quantity": quantity_total,
            "buy_quote": buy_quote_total,
            "buy_time": data[BinanceDataFormat.OPEN_TIME],
            "sell_price": sell_price,
            "sell_quantity": quantity_total,
            "sell_quote": sell_quote,
            "sell_time": data[BinanceDataFormat.OPEN_TIME],
            "profit": profit,
            "profit_ratio": profit_ratio,
            "status": TradeStatus.SELLING.value,
            "new_buy_quantity": quantity,
        }

        return record_data

    def calc_buy_threasold(self, datas):
        """
        本策略不含此逻辑
        """
        return self.decline
