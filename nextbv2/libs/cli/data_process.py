# -*- coding: utf-8 -*-
# @Time     : 2022/09/14 10:02:50
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : data_process.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import os
import datetime
import argparse
from nextbv2.libs.common.common import parse_ini_config
from nextbv2.libs.common.constant import *
from nextbv2.libs.binance.apis import NextBBinance
from nextbv2.libs.db.serialize import NextBSerialize
from nextbv2.libs.logs.logs import *


def parse_cmd():
    """
    数据初始化和更新
    """
    parser = argparse.ArgumentParser(
        prog="nextbv2-data-process",
        description="NextBv2下载、更新本地数据集工具。版本号：2.0.1",
        epilog="使用方式：nextbv2-data-process -c config_file",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="设置配置文件",
        type=str,
        dest="config",
        action="store",
        default="./nextbv2.conf",
    )

    args = parser.parse_args()

    return args


def create_binance(config):
    """
    创建币安API对象
    config：配置对象，dict
    """
    # 初始化币安API对象
    api_key = config.get("api_key")
    api_secret = config.get("api_secret")
    proxies = {}
    if config.get("proxy").lower() == CONFIG_PROXY_ON:
        proxies["http"] = config.get("http_proxy")
        proxies["https"] = config.get("https_proxy")
    try:
        return NextBBinance(api_key, api_secret, proxies)
    except Exception as e:
        error("初始化币安API对象失败，程序结束，失败原因：{}".format(str(e)))
        exit(0)


def create_serialize(config):
    """
    创建本地序列化存储数据对象
    config：配置对象，dict
    """
    # 初始化序列化对象
    data_path = config.get("data_path")
    dir_path = os.path.dirname(data_path)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    try:
        return NextBSerialize(data_path)
    except Exception as e:
        error("初始化序列化对象失败，程序结束，失败原因：{}".format(str(e)))
        exit(0)


def calc_update_data_len(update_time_str):
    """
    计算从上次更新到当前时间需要更新的数据长度
    update_time_str：上次更新的时间，str，时间格式如，%Y-%m-%d %H:00:00
    """
    if update_time_str == "":
        return False
    now_time = datetime.datetime.now()
    update_time = datetime.datetime.strptime(update_time_str, "%Y-%m-%d %H:00:00")
    dlt_time = now_time - update_time
    time_hour = dlt_time.days * 24 + dlt_time.seconds // 3600

    return time_hour


def data_process(config_file):
    """
    初始化或者更新本地数据
    config_file：配置文件路径，str
    """
    # 读取配置
    config = parse_ini_config(config_file)

    # 创建币安API对象
    nextb_binance = create_binance(config)

    # 创建序列化数据对象
    nextb_serialize = create_serialize(config)
    # 加载本地数据
    nextb_serialize.load_datas()

    # 读取配置中待处理的币种数据数据
    symbols = config.get("symbols")
    klines_interval = config.get("klines_interval")
    # 读取本地数据中已有的币种及更新信息
    local_symbol_info = nextb_serialize.get_symbol_info()
    for symbol in symbols:
        # 默认获取最近500条数据
        limit = MAX_LIMIT
        # 如果是更新，则计算需要更新的数据量
        if symbol in local_symbol_info.keys():
            # 计算需要获取的数据量
            limit = calc_update_data_len(local_symbol_info[symbol])
        if limit == 0:
            info("币种-{}当前为最新数据，上次更新时间：{}，本次不用更新。".format(symbol, local_symbol_info[symbol]))
            continue
        # 从接口获取数据
        datas = nextb_binance.get_klines(
            symbol=symbol, interval=klines_interval, limit=limit
        )
        if datas:
            nextb_serialize.update_datas(symbol=symbol, datas=datas)
            info("更新币种-{}数据，更新{}条数据。".format(symbol, limit))
    # 保存更新结果
    nextb_serialize.dump_datas()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    data_process(args.config)
