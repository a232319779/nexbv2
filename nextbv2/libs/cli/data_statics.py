# -*- coding: utf-8 -*-
# @Time     : 2022/09/15 18:07:43
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : data_statics.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import argparse
import datetime
from nextbv2.libs.common.constant import *
from nextbv2.libs.common.common import create_serialize


def parse_cmd():
    """
    数据初始化和更新
    """
    parser = argparse.ArgumentParser(
        prog="nextbv2-data-statics",
        description="NextBv2本地数据集统计分析工具。版本号：2.0.0",
        epilog="使用方式：nextbv2-data-statics -h",
    )
    parser.add_argument(
        "-t",
        "--type",
        help="指定统计方法。当前支持方法[show/mean]，show：显示最近N条收盘价格，mean：显示最近N条价格的均值。",
        type=str,
        dest="serialize_type",
        action="store",
        default="show",
    )
    parser.add_argument(
        "-s",
        "--data",
        help="指定本地序列化数据路径。",
        type=str,
        dest="serialize_data",
        action="store",
        default="./serialize.data",
    )
    parser.add_argument(
        "-n",
        "--number",
        help="指定数据数量。",
        type=int,
        dest="number",
        action="store",
        default=7,
    )

    args = parser.parse_args()

    return args


def statics_show(serialize_data, number):
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    datas = nextbv2_serialize.get_datas()
    print("币种,时间,收盘价,振幅")
    for key, value in datas.items():
        update_time_str = value.get("update_time", "")
        if update_time_str == "":
            print("获取数据时间错误，退出程序。")
            exit(0)
        update_time = datetime.datetime.strptime(update_time_str, "%Y-%m-%d %H:00:00")
        for i in range(0, number):
            data = value.get("data", [])[-1 - i]
            open_price = float(data[1])
            high_price = float(data[2])
            low_price = float(data[3])
            close_price = float(data[4])
            amplitude_A = (high_price - low_price) / low_price * 100.0
            amplitude_B = (close_price - open_price) / close_price * 100.0
            print(
                "{},{},{},{},{}".format(
                    key,
                    update_time.strftime("%Y-%m-%d %H:00:00"),
                    data[4],
                    amplitude_A,
                    amplitude_B
                )
            )
            update_time -= datetime.timedelta(minutes=60)


def statics_mean(serialize_data, number):
    nextbv2_serialize = create_serialize(serialize_data)
    nextbv2_serialize.load_datas()
    datas = nextbv2_serialize.get_datas()
    print("币种,{0}小时最高均值,{0}小时最低均值,{0}小时收盘均值".format(number))
    for key, value in datas.items():
        high_sum = 0.0
        low_sum = 0.0
        close_sum = 0.0
        for i in range(0, number):
            data = value.get("data", [])[-1 - i]
            high_sum += float(data[2])
            low_sum += float(data[3])
            close_sum += float(data[4])
        print(
            "{},{},{},{}".format(
                key,
                high_sum / number,
                low_sum / number,
                close_sum / number,
            )
        )


statics_func = {
    "show": statics_show,
    "mean": statics_mean,
}


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    statics_func[args.serialize_type](args.serialize_data, args.number)
