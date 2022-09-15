# -*- coding: utf-8 -*-
# @Time     : 2022/09/15 12:51:02
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : common.py
# @Software : Visual Studio Code
# @WeChat   : NextB

import configparser
from nextbv2.libs.common.constant import CONFIG_SESSION_NAME

def parse_ini_config(file_name):
    config = configparser.ConfigParser()
    config.read(file_name)
    nexbv2_config = config[CONFIG_SESSION_NAME]
    config_dict = {}
    for key in nexbv2_config:
        key = key.lower()
        if key == "symbols":
            config_dict[key] = nexbv2_config[key].split(",")
        else:
            config_dict[key] = nexbv2_config[key]
    
    return config_dict