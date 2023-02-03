# -*- coding: utf-8 -*-
# @Time     : 2023/02/03 14:07:58
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : trade_test.py
# @Software : Visual Studio Code
# @WeChat   : NextB

__doc__ = """
交易策略1：

1. 监测到每连续下跌N次，则按开盘价买入X%的仓位
2. 计算盈利值为Y的价格，挂单卖出
3. 如果下跌超过D%，则取消当前挂单，已当前开盘价买入2X%的仓位
4. 重新计算盈利值为Y的价格，挂单卖出
5. 继续3、4步
6. 若卖出则继续下一次，若仓位已满，则输出失败
"""