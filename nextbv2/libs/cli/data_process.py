# -*- coding: utf-8 -*-
# @Time     : 2022/09/14 10:02:50
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : data_process.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import argparse
from nextbv2.version import NEXTB_V2_VERSION
from nextbv2.libs.common.constant import (
    MAX_LIMIT,
    ONE_HOUR_TIMESTAMP,
    DEFAULT_START_TIMESTAMP,
)
from nextbv2.libs.common.common import (
    parse_ini_config,
    create_binance,
    create_serialize,
)
from nextbv2.libs.common.nextb_time import get_now_timestamp, timestamp_to_time
from nextbv2.libs.logs.logs import info


def parse_cmd():
    """
    数据初始化和更新
    """
    parser = argparse.ArgumentParser(
        prog="nextb-v2-data-process",
        description="NextBv2下载、更新本地数据集工具。版本号：{}".format(NEXTB_V2_VERSION),
        epilog="使用方式：nextb-v2-data-process -c config_file",
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
    data_path = config.get("data_path")
    nextb_serialize = create_serialize(data_path)
    # 加载本地数据
    nextb_serialize.load_datas()

    # 读取配置中待处理的币种数据数据
    symbols = config.get("symbols")
    klines_interval = config.get("klines_interval")
    # 读取本地数据中已有的币种及更新信息
    local_symbol_info = nextb_serialize.get_symbol_info()
    for symbol in symbols:
        # 默认获取最大1000条数据
        limit = config.get("limit", MAX_LIMIT)
        # 默认从2022.01.01 00:00:00开始获取
        startTime = config.get("start_time", DEFAULT_START_TIMESTAMP)
        # 如果是更新，则计算需要更新的数据量
        if symbol in local_symbol_info:
            # 当前时间和数据集最后一条数据时间间隔小于1个小时，则不进行更新
            now_timestamp = get_now_timestamp()
            # 计算需要获取的数据量
            startTime = nextb_serialize.get_last_data_timestamp(symbol)
            if now_timestamp - startTime < 2 * ONE_HOUR_TIMESTAMP:
                info(
                    "{}数据已为最新数据集，无需更新，最新时间：{}".format(
                        symbol, timestamp_to_time(startTime)
                    )
                )
                continue
        # 从数据集的下一个时间节点开始获取数据
        startTime += 1
        # 从接口获取数据
        param = {
            "symbol": symbol,
            "interval": klines_interval,
            "limit": limit,
            "startTime": startTime,
            "endtTime": None,
        }
        datas = nextb_binance.get_klines(param)
        if datas:
            nextb_serialize.update_datas(symbol=symbol, datas=datas)
    # 保存更新结果
    nextb_serialize.dump_datas()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    data_process(args.config)
