# -*- coding: utf-8 -*-
# @Time     : 2022/08/28 10:57:55
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2_cli_data_process.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import os
from nextbv2.libs.cli.data_process import data_process


class TestNextBV2DataProcess:
    def test_data_process(self):
        curdir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(curdir, "./nextbv2.conf")
        data_process(config_file)
