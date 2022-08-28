# -*- coding: utf-8 -*-
# @Time     : 2022/08/28 11:31:59
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2_logs.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import pytest
from nextbv2.libs.logs.logs import *


class TestNextBV2Logs:
    def test_logs(self):
        debug('debug message')
        info('info message')
        warn('warn message')
        error('error message')
        critical('critical message')