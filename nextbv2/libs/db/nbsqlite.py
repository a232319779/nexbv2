# -*- coding: utf-8 -*-
# @Time     : 2022/09/13 17:42:57
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : nbsqlite.py
# @Software : Visual Studio Code
# @WeChat   : NextB

__doc__ = """
存储交易数据：
    1. NextBSqlite()：连接交易sqlite数据库
    2. create_table()：创建交易数据表
    3. add()：插入交易记录
    4. update()：更新交易记录
    5. get_last_one()：获取指定用户最近一条卖出中的交易记录
    6. add()：关闭sqlite连接
"""


import sqlite3
from nextbv2.libs.logs.logs import *


class NextBSqlite(object):
    def __init__(self, sqlite_db_path):
        """
        初始化sqlite连接对象
        sqlite_db_path：序列化对象路径
        """
        try:
            self.conn = sqlite3.connect(sqlite_db_path)
            self.__table_name__ = "trade_table"
            if self.conn:
                info("连接{}数据库成功。".format(sqlite_db_path))
            else:
                self.conn = None
                error("连接{}数据库失败。".format(sqlite_db_path))
        except Exception as e:
            self.conn = None
            error("连接{}数据库失败。失败原因：{}".format(sqlite_db_path, str(e)))

    def __check_conn__(self):
        """
        校验数据库连接是否成功。
        成功返回True，失败返回False
        """
        return False if self.conn is None else True

    def create_table(self):
        """
        创建交易数据表，数据表格式如下：
        id：本地交易序号，自增长
        user_id：用户ID，整数，不允许为空
        trading_straregy_name：交易策略名称，字符串，不允许空
        order_id：交易订单编号，大整数，允许空
        symbol：交易币种符号，字符串，不允许空
        buy_price：买入价格，浮点数，允许空
        buy_quantity：买入数量，浮点数，允许空
        buy_quote：？,浮点数，允许空
        buy_time：买入时间，时间类型，允许空
        sell_price：卖出价格，浮点数，允许空
        sell_quantity：卖出数量，浮点数，允许空
        sell_quote：？，浮点数，允许空
        sell_time：卖出时间，时间类型，允许空
        profit：收益，浮点数，允许空
        profit_ratio：收益率，浮点数，允许空
        status：当前订单状态，整数，允许空
        tickSize_index：最小价格精度，整数，不允许空
        stepSize_index：最小买入精度，证书，不允许空
        """
        if not self.__check_conn__():
            error("创建交易数据表失败，失败原因：未连接到数据库。")
            return False
        cursor = self.conn.cursor()
        sql = """CREATE TABLE {}
            (id                         INTEGER             PRIMARY KEY     AUTOINCREMENT,
            user_id                     INT                 NOT NULL,
            trading_straregy_name       NCHAR(55)           NOT NULL,
            order_id                    UNSIGNED BIG INT,
            symbol                      NCHAR(55)           NOT NULL,
            buy_price                   FLOAT,
            buy_quantity                FLOAT,
            buy_quote                   FLOAT,
            buy_time                    TEXT,
            sell_price                  FLOAT,
            sell_quantity               FLOAT,
            sell_quote                  FLOAT,
            sell_time                   TEXT,
            profit                      FLOAT,
            profit_ratio                FLOAT,
            status                      INT,
            tickSize_index              INT                NOT NULL,
            stepSize_index              INT                NOT NULL
            );""".format(
            self.__table_name__
        )
        try:
            cursor.execute(sql)
            self.conn.commit()
            info("trade_table数据表创建成功")
        except Exception as e:
            info(str(e))
        return True

    @staticmethod
    def dict_to_add_str(data):
        """
        将字段转为插入语句的str类型
        """
        key_str = ""
        value_str = ""
        for key, value in data.items():
            if isinstance(value, str):
                key_str += "{},".format(key)
                value_str += "'{}',".format(value)
            else:
                key_str += "{},".format(key)
                value_str += "{},".format(value)
        return key_str[:-1], value_str[:-1]

    @staticmethod
    def dict_to_update_str(data):
        """
        将字段转为插入语句的str类型
        """
        format_str = ""
        for key, value in data.items():
            # user_id逻辑上不能更新
            if key == "user_id":
                continue
            if isinstance(value, str):
                format_str += "{} = '{}',".format(key, value)
            else:
                format_str += "{} = {},".format(key, value)
        return format_str[:-1]

    def add(self, data):
        """
        插入数据
        data：数据字典
        """
        if not self.__check_conn__():
            error("插入数据失败，失败原因：未连接到数据库。")
            return False
        key_str, value_str = self.dict_to_add_str(data)
        cursor = self.conn.cursor()
        sql = "INSERT INTO {} ({}) VALUES ({})".format(
            self.__table_name__, key_str, value_str
        )
        cursor.execute(sql)
        self.conn.commit()
        info("插入数据成功, 命令内容：{}".format(sql))
        return True

    def update(self, data):
        """
        更新数据
        data：数据字典
        """
        if not self.__check_conn__():
            error("更新数据数据失败，失败原因：未连接到数据库。")
            return False
        data_str = self.dict_to_update_str(data)
        cursor = self.conn.cursor()
        sql = "UPDATE {} set {} where id = {}".format(
            self.__table_name__, data_str, data.get("id", 0)
        )
        cursor.execute(sql)
        self.conn.commit()
        info("更新数据成功, 命令内容：{}".format(sql))
        return True

    def get_last_one(self, user_id):
        """
        获取指定用户的最近一条记录
        """
        data = dict()
        if not self.__check_conn__():
            error("查询数据数据失败，失败原因：未连接到数据库。")
            return data
        cursor = self.conn.cursor()
        sql = "SELECT * from {} where user_id = {} and status = 1 order by id desc limit 1".format(
            self.__table_name__, user_id
        )
        cursor.execute(sql)
        for row in cursor:
            info("查询数据成功, 命令内容：{}".format(sql))
            data["id"] = row[0]
            data["user_id"] = row[1]
            data["trading_straregy_name"] = row[2]
            data["order_id"] = row[3]
            data["symbol"] = row[4]
            data["buy_price"] = row[5]
            data["buy_quantity"] = row[6]
            data["buy_quote"] = row[7]
            data["buy_time"] = row[8]
            data["sell_price"] = row[9]
            data["sell_quantity"] = row[10]
            data["sell_quote"] = row[11]
            data["sell_time"] = row[12]
            data["profit"] = row[13]
            data["profit_ratio"] = row[14]
            data["status"] = row[15]
            data["tickSize_index"] = row[16]
            data["stepSize_index"] = row[17]
            return data

    def close(self):
        """
        关闭数据库连接
        """
        self.conn.close()
