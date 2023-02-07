# -*- coding: utf-8 -*-
# @Time     : 2022/08/26 14:23:29
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : logs.py
# @Software : Visual Studio Code
# @WeChat   : NextB

__doc__ = """
nextb日志模块：
    1. debug()：打印调试日志信息
    2. info()：打印正常日志信息
    3. warn()：打印告警日志信息
    4. error()：打印错误日志信息
    5. critical()：打印严重日志信息
"""

import os
import logging
import logging.config

# 加载日志配置文件
curdir = os.path.dirname(os.path.abspath(__file__))
log_config = os.path.join(curdir, "logging.conf")
logging.config.fileConfig(log_config)

# 创建日志对象
logger = logging.getLogger('nextbv2')

# 输出配置文件路径
logger.debug("日志配置文件路径：{}，如有必要请按自己的需求进行修改。".format(log_config))

def debug(msg):
    """
    打印调试级别信息：
    msg：str类型，信息字符串
    """
    logger.debug(msg)

def info(msg):
    """
    打印正常级别信息：
    msg：str类型，信息字符串
    """
    logger.info(msg)

def warn(msg):
    """
    打印告警级别信息：
    msg：str类型，信息字符串
    """
    logger.warning(msg)

def error(msg):
    """
    打印错误级别信息：
    msg：str类型，信息字符串
    """
    logger.error(msg)

def critical(msg):
    """
    打印严重级别信息：
    msg：str类型，信息字符串
    """
    logger.critical(msg)
