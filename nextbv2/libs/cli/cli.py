# -*- coding: utf-8 -*-
# @Time     : 2022/08/23 00:08:19
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : cli.py
# @Software : Visual Studio Code
# @WeChat   : NextB

from nextbv2.libs.common.constant import *

class NextBV2CLI(object):
    def __init__(self, **args):
        """
        初始化命令行对象
        """
        self.nbb = args.get("nextb_binance", None)
        self.nbs = args.get("nextb_serialize", None)

    @staticmethod
    def __check__(obj):
        """
        检查对象是否为空
        """
        return True if obj is None else False

    def cli_init_data(self, symbol):
        """
        初始化指定币种数据，并保存到本地
        """
        # 币安API对象或者存储对象不存在，则返回失败
        return self.cli_update_data(symbol=symbol, limit=MAX_LIMIT)

    def cli_update_data(self, symbol, limit=1):
        """
        更新本地指定币种数据
        """
        if self.__check__(self.nbb) and self.__check__(self.nbs):
            return False
        datas = self.nbb.get_klines(symbol=symbol, limit=limit)
        if not datas:
            return False
        if not self.nbs.update_datas(symbol=symbol, datas=datas):
            return False
        return self.nbs.dump_datas()
            