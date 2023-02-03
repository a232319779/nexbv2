# -*- coding: utf-8 -*-
# @Time     : 2022/08/23 00:12:22
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : constant.py
# @Software : Visual Studio Code
# @WeChat   : NextB

from enum import Enum

# 通过实际测试, 币安api接口最大返回1000条数据
MAX_LIMIT = 1000
# 程序默认运行到2219年
MAX_TIMESTAMP = 7869808080000
CONFIG_SESSION_NAME = "NEXTBV2_CONFIG"
CONFIG_PROXY_ON = "on"
ONE_HOUR_TIMESTAMP = 1 * 3600 * 1000
# 默认起始时间2022.01.01 00:00:00
DEFAULT_START_TIMESTAMP = 1640966399000

class TradeStatus(Enum):
    SELLING = 0
    MERGE = 1
    DONE = 2