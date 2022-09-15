# -*- coding: utf-8 -*-
# @Time     : 2022/09/15 11:31:59
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : test_nextbv2_common.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import os
from nextbv2.libs.common.common import *


class TestNextBV2Common:
    def test_parse_ini(self):
        curdir = os.path.dirname(os.path.abspath(__file__))
        config = parse_ini_config(os.path.join(curdir, "./nextbv2.conf"))
        assert "api_key" in config.keys()
        