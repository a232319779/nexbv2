# -*- coding: utf-8 -*-
# @Time     : 2022/09/15 12:51:02
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : common.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import os
import configparser
from nextbv2.libs.common.constant import *
from nextbv2.libs.logs.logs import *
from nextbv2.libs.binance.apis import NextBBinance
from nextbv2.libs.db.serialize import NextBSerialize


def parse_ini_config(file_name):
    """
    读取配置文件，并转为字典存储
    file_name：配置文件路径，str
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    nexbv2_config = config[CONFIG_SESSION_NAME]
    config_dict = {}
    for key in nexbv2_config:
        key = key.lower()
        # symbols按","分隔
        if key == "symbols":
            config_dict[key] = nexbv2_config[key].split(",")
        else:
            config_dict[key] = nexbv2_config[key]
    
    return config_dict

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

def create_serialize(data_path):
    """
    创建本地序列化存储数据对象
    config：配置对象，dict
    """
    # 初始化序列化对象
    dir_path = os.path.dirname(data_path)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    try:
        return NextBSerialize(data_path)
    except Exception as e:
        error("初始化序列化对象失败，程序结束，失败原因：{}".format(str(e)))
        exit(0)