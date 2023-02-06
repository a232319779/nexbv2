# -*- coding: utf-8 -*-
# @Time     : 2023/02/03 16:37:15
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : sqlite_db.py
# @Software : Visual Studio Code
# @WeChat   : NextB

__doc__ = """
存储交易数据：
    1. NextBTradeDB()：连接交易sqlite数据库
    2. create_table()：创建交易数据表
    3. add()：插入交易记录
    4. status_done()：更新交易记录
    5. get_last_one()：获取指定用户最近一条卖出中的交易记录
    6. close()：关闭sqlite连接
    7. status_merge()：更新交易状态
"""


from sqlalchemy import create_engine, Column, String, BigInteger, and_
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime, Integer, Float
from nextbv2.libs.common.constant import TradeStatus
from nextbv2.libs.common.nextb_time import timestamp_to_datetime


Base = declarative_base()


class NextBTradeTable(Base):
    __tablename__ = "nextb_trade_table"
    # sqlite
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    # 用户名称
    user = Column(String(32))
    # 交易策略名称
    trading_straregy_name = Column(String(32))
    # 订单号
    order_id = Column(BigInteger)
    # 虚拟货币名称
    symbol = Column(String(32))
    # 买入价格
    buy_price = Column(Float)
    # 买入数量
    buy_quantity = Column(Float)
    # 买入成交额 = 买入价格 * 买入数量
    buy_quote = Column(Float)
    # 买入时间
    buy_time = Column(DateTime)
    # 卖出价格
    sell_price = Column(Float)
    # 卖出数量
    sell_quantity = Column(Float)
    # 卖出成交额 = 卖出价格 * 卖出数量
    sell_quote = Column(Float)
    # 卖出时间
    sell_time = Column(DateTime)
    # 收益
    profit = Column(Float)
    # 收益率
    profit_ratio = Column(Float)
    # 交易状态
    status = Column(Integer)


class NextBTradeDB:
    def __init__(self, sqlite_db_path):
        """
        初始化对象
        """
        if sqlite_db_path:
            self.engine = self.init_db_connection(sqlite_db_path)
            self.session_maker = None

    @staticmethod
    def init_db_connection(db_name):
        """
        链接数据库
        """
        conn_str = "sqlite:///{db_name}".format(db_name=db_name)
        engine = create_engine(conn_str)
        return engine

    def create_session(self):
        """
        创建数据库链接
        """
        if self.session_maker is None:
            self.session_maker = scoped_session(
                sessionmaker(autoflush=True, autocommit=False, bind=self.engine)
            )

    def close_session(self):
        self.session_maker.close_all()

    def close(self):
        """
        关闭数据库链接
        """
        # self.session_maker.close_all()
        self.engine.dispose()

    # 创建表
    def create_table(self):
        """
        初始化数据表
        """
        try:
            Base.metadata.create_all(self.engine)
            return True
        except Exception as e:
            return False

    def get_last_one_record_status(self, user):
        """
        获取指定用户的最近一条交易记录的交易状态
        """
        data = self.get_last_one(user)
        if data:
            return data.status
        return None

    def get_last_one(self, user):
        """
        获取指定用户的最近一条交易记录
        返回值：None表示没有记录
        """
        datas = self.get_last_records(user, 1)
        if datas:
            return datas[0]
        return None

    def get_last_records(self, user, number=10):
        """
        获取最近number条交易记录，默认最近10条
        """
        data = (
            self.session_maker.query(NextBTradeTable)
            .filter(NextBTradeTable.user == user)
            .order_by(NextBTradeTable.id.desc())
            .limit(number)
        )
        if data.count():
            datas = list()
            for d in data:
                datas.append(d)
            datas.reverse()
            return datas
        else:
            return []

    def add(self, data):
        """
        插入交易数据
        """
        try:
            new_data = NextBTradeTable()
            # 如果插入的数据有问题，则报错退出
            new_data.user = data.get("user")
            new_data.trading_straregy_name = data.get("trading_straregy_name")
            new_data.symbol = data.get("symbol")
            new_data.order_id = data.get("order_id")
            new_data.buy_price = data.get("buy_price")
            new_data.buy_quantity = data.get("buy_quantity")
            new_data.buy_quote = data.get("buy_quote")
            new_data.buy_time = timestamp_to_datetime(data.get("buy_time"))
            new_data.sell_price = data.get("sell_price")
            new_data.sell_quantity = data.get("sell_quantity")
            new_data.sell_quote = data.get("sell_quote")
            new_data.sell_time = timestamp_to_datetime(data.get("sell_time"))
            new_data.profit = data.get("profit")
            new_data.profit_ratio = data.get("profit_ratio")
            new_data.status = data.get("status")
            self.session_maker.add(new_data)
            self.session_maker.commit()
            return True
        except Exception as e:
            return False

    def status_merge(self, user):
        try:
            trading_datas = (
                self.session_maker.query(NextBTradeTable)
                .filter(
                    and_(
                        NextBTradeTable.user == user,
                        NextBTradeTable.status == TradeStatus.SELLING.value,
                    )
                )
                .order_by(NextBTradeTable.id.desc())
                .all()
            )
            for td in trading_datas:
                td.status = TradeStatus.MERGE.value
            self.session_maker.commit()
            return True
        except Exception as e:
            return False

    def status_done(self, user, data):
        try:
            trading_datas = (
                self.session_maker.query(NextBTradeTable)
                .filter(
                    and_(
                        NextBTradeTable.user == user,
                        NextBTradeTable.status == TradeStatus.SELLING.value,
                    ),
                )
                .order_by(NextBTradeTable.id.desc())
                .all()
            )
            for td in trading_datas:
                # td.sell_price = data.get("sell_price")
                # td.sell_quantity = data.get("sell_quantity")
                # td.sell_quote = data.get("sell_quote")
                # td.sell_time = data.get("sell_time")
                # td.profit = data.get("profit")
                # td.profit_ratio = data.get("profit_ratio")
                # td.status = data.get("status")
                td.sell_time = timestamp_to_datetime(data.get("sell_time"))
                td.status = TradeStatus.DONE.value
            # 同步完成才统一提交到数据库
            self.session_maker.commit()
            return True
        except Exception as e:
            return False

    def get_total_ratio(self, user, last_close_price):
        count = 0
        ratio_sum = 0.0
        status = 0
        try:
            trading_datas = (
                self.session_maker.query(NextBTradeTable)
                .filter(
                    NextBTradeTable.user == user,
                )
                .order_by(NextBTradeTable.id.desc())
                .all()
            )
            for td in trading_datas:
                count += 1
                if td.status == TradeStatus.DONE.value:
                    ratio_sum += td.profit
                elif td.status == TradeStatus.SELLING.value:
                    ratio_sum = (
                        ratio_sum + last_close_price * td.sell_quantity - td.buy_quote
                    )
            if trading_datas:
                status = trading_datas[-1].status
        except Exception as e:
            pass
        ratio_sum = round(ratio_sum, 3)
        return (count, ratio_sum, status)
