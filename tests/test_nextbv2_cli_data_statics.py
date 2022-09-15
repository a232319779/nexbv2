# -*- coding: utf-8 -*-
# @Time     : 2022/08/28 10:57:55
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2_cli_data_process.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import os
from nextbv2.libs.cli.data_statics import statics_show, statics_mean


class TestNextBV2DataStatics:
    def test_data_statics_show(self):
        curdir = os.path.dirname(os.path.abspath(__file__))
        serialize_data = os.path.join(curdir, "./serialize.data")
        statics_show(serialize_data, 7)

    def test_data_statics_mean(self):
        curdir = os.path.dirname(os.path.abspath(__file__))
        serialize_data = os.path.join(curdir, "./serialize.data")
        statics_mean(serialize_data, 12)
