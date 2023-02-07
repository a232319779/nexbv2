# -*- coding: utf-8 -*-
# @Time     : 2022/08/23 00:12:22
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : constant.py
# @Software : Visual Studio Code
# @WeChat   : NextB

from enum import Enum, IntEnum

# 通过实际测试, 币安api接口最大返回1000条数据
MAX_LIMIT = 1000
# 程序默认运行到2219年
MAX_TIMESTAMP = 7869808080000
CONFIG_SESSION_NAME = "NEXTBV2_CONFIG"
CONFIG_PROXY_ON = "on"
ONE_HOUR_TIMESTAMP = 1 * 3600 * 1000
# 默认起始时间2022.01.01 00:00:00
DEFAULT_START_TIMESTAMP = 1640966399000

# 最大价格上限
MAX_PRICE = 99999999.9

# 交易过程的默认参数
CONST_BASE = 100.0
CONST_MAGNIFICATION = 1.0
CONST_DECLINE = 0.03
CONST_PROFIT_RATIO = 0.013
CONST_CUTDOWN = 1
CONST_MAX_QUOTE = 1500
CONST_FORCE_BUY = False


class TradeStatus(Enum):
    UNKNOWN = -1
    SELLING = 0
    MERGE = 1
    DONE = 2


class BinanceDataFormat(IntEnum):
    OPEN_TIME = 0
    OPEN_PRICE = 1
    HIGH_PRICE = 2
    LOW_PRICE = 3
    CLOSE_PRICE = 4
    VOLUME = 5
    CLOSE_TIME = 6
    QUOTE_VOLUME = 7
    TRADES = 8
    TAKER_BASE = 9
    TAKER_QUOTE = 10
    IGNORED = 11
