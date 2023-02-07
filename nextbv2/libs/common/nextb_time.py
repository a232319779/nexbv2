# -*- coding: utf-8 -*-
# @Time     : 2023/02/01 15:13:34
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : nextb_time.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import datetime


def timestamp_to_datetime(time_stamp):
    """
    时间戳转datetime对象
    timestamp: 13位时间戳, 如: 1640966400000, 精确到毫秒
    返回值: datetime对象
    """
    time_stamp = int(time_stamp / 1000)
    datetime_obj = datetime.datetime.fromtimestamp(time_stamp)
    return datetime_obj


def timestamp_to_time(time_stamp):
    """
    时间戳转时间字符串
    timestamp: 13位时间戳, 如: 1640966400000, 精确到毫秒
    返回值: 时间字符串
    """
    datetime_obj = timestamp_to_datetime(time_stamp)
    date_time = datetime.datetime.strftime(datetime_obj, "%Y-%m-%d %H:%M:%S")
    return date_time


def time_to_timestamp(date_time):
    """
    时间字符串转时间戳
    time: 时间字符串, 如: "2022-01-01 00:00:00", 精确到秒
    返回值: 13位时间戳
    """
    datetime_obj = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    time_stamp = int(datetime.datetime.timestamp(datetime_obj)) * 1000
    return time_stamp


def get_now_timestamp():
    """
    获取当前小时的时间戳
    """
    now = datetime.datetime.now()
    time_stamp = int(now.timestamp()) * 1000
    return time_stamp
