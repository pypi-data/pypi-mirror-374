import datetime
from typing import Callable, Union, List
import pandas as pd
from pqsdk.interface import AbstractStrategyContext, AbstractInstrument, AbstractPosition, Constant
from pqsdk.utils.timer_factory import TimerFactory
from .portfolio import Portfolio
from .position import Position
from .order import Order
from .current_data import CurrentDataCacheDict
from .instrument import Instrument
from pqsdk import log, pqconstant
from pqsdk.api import *
from .run_info import RunInfo


class StrategyContext(AbstractStrategyContext):

    def __init__(self, kwargs: dict, timer_factory: TimerFactory):
        # 自定义定时器
        self.__tf = timer_factory
        self.__constant = Constant()  # 初始化常量
        # 策略执行信息
        self.__run_info = RunInfo(kwargs=kwargs, context=self)
        # 回测的当前日期，每日set_dt重置
        self.__dt = None
        # 回测当前日期的Benchmark收益率
        self.__benchmark_value = None
        self.__unit = kwargs.get('unit', '1d')  # 行情周期
        self.__parameters = kwargs.get('parameters')
        self.__dividend_type = kwargs.get('dividend_type', 'back')
        self.__strategy_name = kwargs.get('strategy_name', None)
        self.__commission = kwargs.get('commission', 0.0)  # 佣金费率
        self.__stock_pool = kwargs.get('stock_pool')

        # 初始化Portfolio
        self._portfolio = Portfolio(self)

        # 初始化委托编号
        self.order_id = 0

        # 初始化空的当前数据字典，通过self.current_data_dict[sec_code]按需获取数据, 每日reset_current_data()被重置
        self.current_data_dict = None

        # 历史委托列表, 从notify_order()函数收集委托数据，回测结束后写入数据库
        self.orders = []

        """
        回测过程中画出曲线
        self.plot_data = {"000001.SZ": {"startExitPrice": {"type": "line", "xAxis": [], "yAxis": [], "desc": ""}}}
        """
        self.plot_data = dict()

        """
        记录投资组合的转入或转出资金历史
        self.inout_cash_his = [{"datetime": self.current_dt: "cash": cash}]
        """
        self.inout_cash_his = []

    def notify_order(self, order):
        """
        新创建委托的通知
        :param order: 委托的对象
        :return:
        """
        order_dict = {"order_id": order.order_id,
                      "sec_code": order.security,
                      "volume": order.volume,
                      "price": order.price,
                      "is_buy": order.is_buy,
                      "avg_cost": order.avg_cost,
                      "comm": order.commission,
                      "add_time": order.add_time,
                      "trade_date": order.add_time.strftime('%Y-%m-%d')}
        self.orders.append(order_dict)
        # log.debug(f"order: {order_dict}")

    def plot_line(self, sec_code: str, name: str, value: float, desc=None):
        """
        画曲线
        :param sec_code:
        :param name:
        :param value:
        :param desc:
        :return:
        """
        self.__plot_chart(chart_type='line', sec_code=sec_code, name=name, value=value, desc=desc)

    def plot_bar(self, sec_code: str, name: str, value: float, desc=None):
        """
        画柱状图
        :param sec_code:
        :param name:
        :param value:
        :param desc:
        :return:
        """
        self.__plot_chart(chart_type='bar', sec_code=sec_code, name=name, value=value, desc=desc)

    def __plot_chart(self, chart_type: str, sec_code: str, name: str, value: float, desc=None):
        """
        画图表
        :param chart_type: chart类型：line， bar
        :param sec_code: 股票代码
        :param name: 曲线名称
        :param value: 曲线yAxis的值
        :param desc: value的描述
        :return:
        """
        if self.unit in ['1d']:
            dt = self.current_dt.strftime('%Y-%m-%d')
        else:
            dt = self.current_dt.strftime('%Y-%m-%d %H:%M')
        if sec_code not in self.plot_data:
            self.plot_data[sec_code] = {name: {"type": chart_type,
                                               "xAxis": [dt],
                                               "yAxis": [round(value, 2)],
                                               "desc": [desc]}}
        elif name not in self.plot_data[sec_code]:
            self.plot_data[sec_code][name] = {"type": chart_type,
                                              "xAxis": [dt],
                                              "yAxis": [round(value, 2)],
                                              "desc": [desc]}
        else:
            self.plot_data[sec_code][name]["xAxis"].append(dt)
            self.plot_data[sec_code][name]["yAxis"].append(round(value, 2))
            self.plot_data[sec_code][name]["desc"].append(desc)

    def reset_current_data(self):
        """
        重置当日的股票数据字典，包括当日最新价、涨停价、跌停价、是否停牌、是否ST等
        :return:
        """
        self.current_data_dict = CurrentDataCacheDict(context=self, run_info=self.run_info)

    def run_monthly(self, func: Callable, monthday: int, time_str: str) -> None:
        """
        按月运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param monthday: 每月的第几个交易日
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；在实盘中才生效
        """

        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str, monthdays=[monthday],
                            monthcarry=True)

    def run_weekly(self, func: Callable, weekday: int, time_str: str) -> None:
        """
        按周运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param weekday: 每周的第几个交易日, 1 = monday, ... 7 = sunday
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；在实盘中才生效
        """
        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str, weekdays=[weekday], weekcarry=True)

    def run_periodically(self,
                         func: Callable,
                         days: int,
                         time_str: str,
                         start_date: str = None,
                         end_date: str = None) -> None:
        """
        按调仓周期运行，如果遇到调仓日为非交易日，则顺延到下一个交易日。

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param days : 间隔天数执行，start_date为第一次执行日期
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；在实盘中才生效
        :param start_date: 开始日期，默认为回测开始日期
        :param end_date: 结束日期, 默认为回测结束日期
        """
        if start_date is None:
            start_date = self.run_info.start_date
        if end_date is None:
            end_date = self.run_info.end_date

        # 将字符串日期转换为datetime对象
        start_date_ = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date_ = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        # 初始化日期列表
        dates = []
        # 当当前日期小于或等于结束日期时，将其添加到列表中，并向前移动interval_days天
        current_date = start_date_
        while current_date <= end_date_:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=days)

        self.__tf.add_timer(callback=func,
                            kwargs={"context": self},
                            when=time_str,
                            dates=dates,
                            datecarry=True)

    def run_daily(self, func: Callable, time_str: str) -> None:
        """
        每天内何时运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；在实盘中才生效
        """
        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str)

    def run_minutely(self, func: Callable, time_str: str, minutes: int = 1) -> None:
        """
        每天内何时开始，间隔n分钟执行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        :param minutes: 间隔执行的分钟数
        """
        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str, minutes=minutes)

    def run_secondly(self, func: Callable, time_str: str, seconds: int = 1) -> None:
        """
        每天内何时开始，间隔n秒执行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        :param seconds: 间隔执行的秒数
        """
        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str, seconds=seconds)

    def cancel(self, order, force: bool = False):
        pass

    def get_current_data(self):
        """
        获取当前单位时间（当天/当前分钟）的涨跌停价, 是否停牌，当天的开盘价等

        :return: 一个dict, 其中 key 是股票代码, value 是拥有如下属性的对象, 返回的结果只在当天有效:
                last_price : 最新价
                high_limit: 涨停价
                low_limit: 跌停价
                paused: 是否停止或者暂停了交易, 当停牌、未上市或者退市后返回 True
                is_st: 是否是 ST(包括ST, *ST)，是则返回 True，否则返回 False
                day_open: 当天开盘价
                name: 股票现在的名称, 可以用这个来判断股票当天是否是 ST, *ST, 是否快要退市
                industry_code: 股票现在所属行业代码
        """
        return self.current_data_dict

    def get_position(self, stock_code) -> AbstractPosition:
        positions = self.portfolio.positions
        if stock_code in positions:
            return positions[stock_code]
        else:
            # 返回一个空的持仓对象
            return Position(stock_code=stock_code, volume=0, price=0, init_time=datetime.datetime.now(), context=self)

    @property
    def constant(self):
        return self.__constant

    @property
    def commission(self):
        """
        佣金费率
        :return:
        """
        return self.__commission

    @property
    def previous_trade_date(self) -> datetime.date:
        pre_trade_date_str = get_previous_trading_date(self.current_dt.strftime('%Y-%m-%d'))
        return datetime.datetime.strptime(pre_trade_date_str, '%Y-%m-%d').date()

    @property
    def run_info(self):
        return self.__run_info

    def get_security_info(self, sec_code: str) -> AbstractInstrument:
        return Instrument(stock_code=sec_code, run_info=self.run_info, context=self)

    def query_new_purchase_limit(self):
        pass

    def query_ipo_data(self):
        pass

    def get_factor(self,
                   count: int = None,
                   sec_code: Union[None, str, List[str]] = None,
                   factor: Union[None, str, List[str]] = None,
                   unit: str = '1d',
                   sec_code_list: list = None,
                   factor_list: list = None,
                   trade_date: str = None,
                   start_date: str = None,
                   end_date: str = None,
                   dividend_type: str = None,
                   stock_pool: list = None,
                   expect_df: bool = True) -> pd.DataFrame:
        """
        返回给定的 sec_code 当日的因子，包括财务因子、alpha101 因子、技术指标 等
        当取天数据时, 不包括当天的, 即使是在收盘后；分钟数据不包括当前分钟的数据，没有未来
        unit= 1d：默认截止到昨日收盘价
        unit= 1m, 5m:默认截止到前1分钟收盘价

        :param count: 返回最近的条目数
        :param sec_code: 股票代码，支持字符串或者字符串数组. 为数组的时候等价于sec_code_list
        :param factor: 因子名称, 支持字符串或者字符串数组，为数组的时候，等价于factor_list
        :param unit: 单位时间长度，支持1d、1m，默认为1d
        :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
        :param sec_code_list:  合约代码，默认为股票池的指数成分股。
        :param factor_list: 因子名称
        :param trade_date: 指定交易日日期，如果同时[开始日期]和[结束日期]都为None，默认为该日的前一个交易日
        :param start_date: 开始日期
        :param end_date:  结束日期
        :param stock_pool: 股票池，可选定指数的成分股，默认为 None，全市场
        :param expect_df: 默认返回 pandas dataframe
        :return:
        """

        if count is None and start_date is None and trade_date is None:
            raise Exception(f"attribute_history()函数必须指定count, start_date, trade_date之一")

        # if sec_code_list is None:
        #     sec_code_list = self.run_info.stock_pool_members

        # 如果未提供时间范围，且trade_date=None，则默认获取上一个交易日
        if count is None and not start_date and not end_date:
            pre_trade_date = get_previous_trading_date(self.current_dt.strftime('%Y-%m-%d'))
            trade_date = trade_date if trade_date else pre_trade_date

        dividend_type = dividend_type if dividend_type is not None else self.dividend_type

        # 防止获取未来数据
        if unit in ['1m', '5m']:
            end_datetime = (self.current_dt - datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        elif unit == '1d':  # 不需要输入end_datetime
            end_datetime = None
            if end_date:
                end_date = min(end_date, (self.current_dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
            else:
                end_date = (self.current_dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            raise Exception("unit is wrong, correct one should be '1m', '5m' or '1d'.")

        df = get_factor(count=count,
                        sec_code=sec_code,
                        factor=factor,
                        unit=unit,
                        stock_pool=stock_pool,
                        factor_list=factor_list,
                        sec_code_list=sec_code_list,
                        trade_date=trade_date,
                        dividend_type=dividend_type,
                        start_date=start_date,
                        end_date=end_date,
                        end_datetime=end_datetime,
                        expect_df=expect_df)
        df.reset_index(inplace=True)

        return df

    def history(self,
                count=None,
                unit='1d',
                field='close',
                start_date: str = None,
                end_date: str = None,
                security_list=None,
                stock_pool: list = None,
                expect_df=True,
                skip_paused=False,
                dividend_type=None):
        """
        获取历史数据，可查询多个标的单个数据字段，返回数据格式为 DataFrame 或 Dict(字典)。
        当取天数据时, 不包括当天的, 即使是在收盘后；分钟数据不包括当前分钟的数据，没有未来
        unit= 1d：默认截止到昨日收盘价
        unit= 1m, 5m:默认截止到前1分钟收盘价

        :param end_date:
        :param start_date:
        :param stock_pool:
        :param count: 数量, 返回的结果集的行数
        :param unit: 单位时间长度, 几天或者几分钟, 现在支持'1d','1m'。当取1d数据时, 不包括当天的, 即使是在收盘后；1m数据不包括当前分钟
        :param field: 要获取的数据字段
        :param security_list: 要获取数据的股票列表
        :param expect_df: expect_df=True: [pandas.DataFrame]对象, 行索引是[datetime.datetime]对象, 列索引是股票代号
                   expect_df=False: dict, key是股票代码, value是一个numpy数组[numpy.ndarray]
        :param skip_paused: 是否跳过不交易日期(包括停牌, 未上市或者退市后的日期)
        :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                    'front'
                    : 前复权, 默认是前复权
                    none
                    : 不复权, 返回实际价格
                    'back'
                    : 后复权
        :return:
        """
        # 避免遍历整个数据库
        if count is None and start_date is None:
            raise Exception(f"history()函数必须指定count参数或者start_date参数")

        dividend_type = dividend_type if dividend_type is not None else self.dividend_type

        # 防止获取未来数据
        if unit in ['1m', '5m']:
            end_datetime = (self.current_dt - datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        elif unit == '1d':  # 不需要输入end_datetime
            end_datetime = None
            if end_date:
                end_date = min(end_date, (self.current_dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
            else:
                end_date = (self.current_dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            raise Exception("unit is wrong, correct one should be '1m', '5m' or '1d'.")

        return get_history(count=count,
                           unit=unit,
                           start_date=start_date,
                           end_date=end_date,
                           end_datetime=end_datetime,
                           field=field,
                           security_list=security_list,
                           stock_pool=stock_pool,
                           expect_df=expect_df,
                           skip_paused=skip_paused,
                           dividend_type=dividend_type)

    def attribute_history(self,
                          security: str,
                          count: int = None,
                          unit: str = '1d',
                          fields: list = None,
                          start_date: str = None,
                          end_date: str = None,
                          skip_paused: bool = True,
                          expect_df: bool = True,
                          dividend_type: str = None):
        """
        获取历史数据，可查询单个标的多个数据字段，返回数据格式为 DataFrame 或 Dict(字典)
        当取天数据时, 不包括当天的, 即使是在收盘后；分钟数据不包括当前分钟的数据，没有未来
        unit= 1d：默认截止到昨日收盘价
        unit= 1m, 5m:默认截止到前1分钟收盘价

        :param end_date:
        :param start_date:
        :param security: 股票代码
        :param count: 数量, 返回的结果集的行数
        :param unit: 单位时间长度, 1d, 1m
        :param fields: 股票属性的list, 支持：['open', ' close', 'low', 'high', 'volume', 'money', 'factor',
                                           'high_limit',' low_limit', 'avg', ' pre_close', 'paused']
        :param skip_paused: 是否跳过不交易日期(包括停牌, 未上市或者退市后的日期).
        :param expect_df: 若是True, 返回[pandas.DataFrame], 否则返回一个dict, 具体请看下面的返回值介绍. 默认是True.
        :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                    'front'
                    : 前复权, 默认是前复权
                    none
                    : 不复权, 返回实际价格
                    'back'
                    : 后复权
        :return:
        """
        # 避免遍历整个数据库
        if count is None and start_date is None:
            raise Exception(f"attribute_history()函数必须指定count参数或者start_date参数")

        dividend_type = dividend_type if dividend_type is not None else self.dividend_type

        # 防止获取未来数据
        if unit in ['1m', '5m']:
            end_datetime = (self.current_dt - datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        elif unit == '1d':  # 不需要输入end_datetime
            end_datetime = None
            if end_date:
                end_date = min(end_date, (self.current_dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
            else:
                end_date = (self.current_dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            raise Exception("unit is wrong, correct one should be '1m', '5m' or '1d'.")

        return get_attribute_history(security=security,
                                     count=count,
                                     unit=unit,
                                     start_date=start_date,
                                     end_date=end_date,
                                     end_datetime=end_datetime,
                                     fields=fields,
                                     skip_paused=skip_paused,
                                     expect_df=expect_df,
                                     dividend_type=dividend_type)

        # if unit == '1m':
        #     end_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')
        #     # end_datetime = (self.current_dt + datetime.timedelta(minutes=-1))
        #     # if end_datetime.date() < self.current_dt.date():  # 上1分钟在昨天
        #     #     # end_datetime_str = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')
        #     #     end_datetime_str = self.current_dt.strftime('%Y-%m-%d') + ' 23:00:00'  # 获取当天的最后一分钟
        #     # else:  # 上1分钟在今日
        #     #     end_datetime_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        #
        #     return get_attribute_history(security=security,
        #                                  count=count,
        #                                  unit=unit,
        #                                  start_date=start_date,
        #                                  end_date=end_date,
        #                                  end_datetime=end_datetime,
        #                                  fields=fields,
        #                                  skip_paused=skip_paused,
        #                                  expect_df=expect_df,
        #                                  dividend_type=dividend_type)
        # elif unit == '1d':  # 截止当前日期的昨日
        #     end_date = (self.current_dt + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        #     return get_attribute_history(security=security,
        #                                  count=count,
        #                                  unit=unit,
        #                                  end_date=end_date,
        #                                  fields=fields,
        #                                  skip_paused=skip_paused,
        #                                  expect_df=expect_df,
        #                                  dividend_type=dividend_type)
        # else:
        #     raise Exception("unit is wrong, correct one should be '1m' or '1d'.")

    def synthesize_portfolio(self, count: int = None, stock_pool: list = None, start_date: str = None,
                             end_date: str = None, freq: int = 5, trade_date_lst: list = None, sec_code: str = None,
                             sec_code_list: list = None, factor_list=None, expect_df: bool = False,
                             exact_match: bool = False, stock_size: int = 10):
        pass

    def get_blacklist(self) -> list:
        """
        TODO 获取租户下定义的股票列表黑名单，黑名单的股票不建议持仓
        :return:
        """
        return []

    def get_last_ticks(self, sec_code_lst: list, index: bool = False, fields: list = None):
        """
        获取当前最新的Tick数据。
        注意：不是历史某个回测时间点的Tick数据。

        :param sec_code_lst:
        :param fields: 返回的字段列表
        :param index: 是否设置sec_code为Index
        :return:
                [{
                'sec_code', 股票代码
                ’datetime'  tick时间字符串： %Y-%m-%d %H:%M:%S
                'open', 当日开盘价
                'high', 当日收盘价
                'low', 当日最低价
                'last_price', 当日最新价格
                'pre_close', 昨日收盘价
                'volume', 当日成交量，单位：手
                'amount', 当日成交额
                }]
        """
        df = get_last_ticks(sec_code_lst=sec_code_lst, index=index, fields=fields)
        return df

    def get_plate_data(self, trade_date: str = None, end_time: str = "15:00", limit: int = 3) -> pd.DataFrame:
        """
        获取板块列表

        :param trade_date: 指定交易日的板块列表
        :param end_time: 指定板块排名的时间节点，从09:25开始到15:30结束，每个间隔5分钟
        :param limit: 按照板块强度倒序排名的板块数量
        :return:
        """
        if trade_date is None:
            trade_date = self.current_dt.strftime('%Y-%m-%d')

        return get_plate_data(trade_date=trade_date, end_time=end_time, limit=limit)

    def get_plate_members_lst(self, plate_code_list: list, trade_date: str = None):
        """
        获取板块的成分股
        :param plate_code_list:
        :param trade_date:
        :return:
        """
        if trade_date is None:
            trade_date = self.current_dt.strftime('%Y-%m-%d')
            
        return get_plate_members_lst(plate_code_list=plate_code_list, trade_date=trade_date)

    def get_member_plates(self, sec_code: str, trade_date: str = None) -> pd.DataFrame:
        """
        获取股票代码所属的板块, 一个股票可能属于多个板块。除了获取板块外，额外提供板块强度，并且按照板块强度倒序排列。
        :param sec_code: 股票代码
        :param trade_date: 交易日，不同交易下的板块可能不同
        :return: DataFrame， 字段包括 板块代码，板块名称，板块强度
               plate_code plate_name  intensity
        0      801660         通信       2306
        1      801250       并购重组       1834
        2      801218       华为概念       1610
        3      801328       消费电子        640
        4      801001         芯片        456
        5      801878       端侧AI        296
        6      801408       智能家居        246
        7      801519        汽车类        227
        8      801857      PPP概念        136
        9      801033       国有企业         44
        10     801382     分拆上市预期         38
        """
        if trade_date is None:
            trade_date = self.current_dt.strftime('%Y-%m-%d')
        return get_member_plates(sec_code=sec_code, trade_date=trade_date)

    def get_stock_name(self, sec_code: str, trade_date: str = None):
        """
        获取股票代码的最新名称

        :param sec_code:
        :param trade_date:
            None：默认为当天，如果当天不是交易日，则获取上一个交易日。
            'YYYY-mm-dd'：具体日期的最新股票名称
        :return: 股票名称
        """
        return get_stock_name(sec_code=sec_code, trade_date=trade_date)

    def get_stock_price(self,
                        sec_code: str,
                        trade_date: str = None,
                        end_time: str = None,
                        dividend_type: str = "front"):
        """
        获取最新的股票价格

        :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                    'front'
                    : 前复权, 默认是前复权
                    none
                    : 不复权, 返回实际价格
                    'back'
                    : 后复权
        :param trade_date: 指定交易日, 格式: 2024-07-15
        :param end_time: 如果trade_date不是系统日期当日，可以指定历史数据的具体分钟，格式：09:30
        :param sec_code:
        :return:
        """
        if trade_date is None:
            trade_date = self.current_dt.strftime('%Y-%m-%d')
        return get_stock_price(sec_code=sec_code,
                               trade_date=trade_date,
                               end_time=end_time,
                               dividend_type=dividend_type)

    def get_price_limit(self,
                        sec_code: str,
                        trade_date: str = None,
                        dividend_type: str = "front"):
        """
        股票代码涨跌停价格
        假设：
        - 600xxx, 601xxx, 603xxx：上海主板，涨跌停限制10%
        - 000xxx：深圳主板，涨跌停限制10%
        - 002xxx：深圳中小板，涨跌停限制10%
        - 300xxx：深圳创业板，涨跌停限制20%
        - 688xxx：上海科创板，涨跌停限制20%

        :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                    'front'
                    : 前复权, 默认是前复权
                    none
                    : 不复权, 返回实际价格
                    'back'
                    : 后复权
        :param sec_code:
        :param trade_date: 指定日期的涨跌停价格
        :return: (昨日收盘价格, 今日涨停价, 今日跌停价)
        """
        if trade_date is None:
            trade_date = self.current_dt.strftime('%Y-%m-%d')

        return get_price_limit(sec_code=sec_code,
                               trade_date=trade_date,
                               dividend_type=dividend_type)

    def get_prompt_query(self,
                         query: str,
                         query_type: str = 'stock',
                         page_num: int = None,
                         page_size: int = None,
                         loop: Union[bool, int] = False):
        """
        通过Prompt Query的方式进行选股。
        举例：2024-10-16,DDE大单净量>0.25, 非科创板,非创业板,非北交所,非ST
        将获取相关的股票列表：
            ['002793.SZ', '000838.SZ', '600837.SH', '000972.SZ', '600889.SH', ...]

        :param query: 通过文本的方式进行选股
        :param query_type: 支持: stock: 股票，fund: 基金
        :param page_num: 可选，查询的页号，默认为1
        :param page_size: 可选，每页行数, 最小50， 最大100，默认为100
        :param loop: 是否循环分页，返回多页合并数据。默认值为False，可以设置为True或具体数值. 当为数值的时候，1-n的多页数据一起返回
        :return: list, 股票代码列表
        """
        return get_prompt_query(query=query, query_type=query_type, page_num=page_num, page_size=page_size, loop=loop)

    def get_auction_data(self,
                         security: str,
                         count: int = None,
                         unit: str = '1m',
                         trade_date: str = None,
                         start_datetime: str = None,
                         end_datetime: str = None,
                         fields=None):
        """
        获取股票的集合竞价数据。

        :param security: 股票代码
        :param count: 返回行数
        :param unit: 支持1m, 5m
        :param trade_date: 交易日
        :param start_datetime: 开始时间
        :param end_datetime: 结束时间
        :param fields: 获取字段，范围：['open', 'high', 'low', 'close', 'pre_close']
        :return:
        """
        if trade_date is None:
            trade_date = self.current_dt.strftime('%Y-%m-%d')

        return get_auction_data(security=security,
                                count=count,
                                unit=unit,
                                trade_date=trade_date,
                                start_datetime=start_datetime,
                                end_datetime=end_datetime,
                                fields=fields)

    def get_orders(self, trade_date: str = None, is_buy: bool = None, include_canceled: bool = True):
        """
        获取交易日的委托单，返回DataFrame

        :param include_canceled: 是否包括已撤的委托
        :param trade_date:
        :param is_buy:
        :return: DataFrame,
            字段：['order_code', 委托编号
                'sec_code',  股票代码
                'order_time', 委托时间
                'is_buy', 委托买卖方向：买单=1， 卖单=0
                'order_volume',  委托数量
                'order_price']  委托价格
        """
        df = pd.DataFrame(self.orders)
        df.rename(columns={"order_id": "order_code",
                           "add_time": "order_time",
                           "volume": "order_volume",
                           "price": "order_price"}, inplace=True)

        if not df.empty and trade_date is not None:
            df = df[df['trade_date'] == trade_date]

        if not df.empty:
            if is_buy is not None:
                df = df[df['is_buy'] == is_buy]

            df['is_buy'] = df['is_buy'].apply(lambda x: 1 if True else 0)

            # 与实盘保持输出一致
            df = df[['order_code', 'sec_code', 'order_time', 'is_buy', 'order_volume', 'order_price']]
        return df

    def set_benchmark_value(self, value: float):
        """
        设置回测过程中当前日期的benchmark的收益率
        :param value:
        :return:
        """
        self.__benchmark_value = value

    @property
    def benchmark_value(self):
        """
        当前日期的benchmark close价格
        :return:
        """
        return self.__benchmark_value

    def set_dt(self, dt):
        self.__dt = dt

    @classmethod
    def __calculate_size(cls, price, cash):
        """
        返回指定价格和现金的股数，需要考虑一手为100股的情况。

        :param price:
        :param cash:
        :return:
        """
        return int(cash // price // 100) * 100

    def order_target_value(self, stock_code: str, target: float = 0.0, price: float = None, force: bool = False):
        # 获取价格
        if price is None:
            # trade_date = self.current_dt.strftime('%Y-%m-%d')
            if self.unit in ['1d']:
                trade_date = self.current_dt.strftime('%Y-%m-%d')
                trade_datetime = None
            else:
                trade_date = None
                trade_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')
            price_df = get_history(count=1,
                                   end_date=trade_date,
                                   end_datetime=trade_datetime,
                                   unit=self.unit,
                                   field='close',
                                   security_list=[stock_code],
                                   dividend_type=self.dividend_type,
                                   expect_df=True)
            if price_df.empty:
                log.warning(f"股票停牌，取消买入: stock_code={stock_code}, trade_date={trade_date}")
                return
            else:
                price = price_df.iloc[0, 0]

        position: Position = self.portfolio.positions.get(stock_code, None)
        if position is None:
            market_value = 0.0
        else:
            market_value = position.volume * price

        if target > market_value:  # Buy
            size = self.__calculate_size(price=price, cash=target - market_value)
            if size < 100:
                content = f"策略名称={self.strategy_name}, 类型=Buy, 股票代码={stock_code}, " \
                          f"目标市值={target}, 持仓市值={market_value}, " \
                          f"委托价格={round(price, 2)},交易股数不足100股，放弃交易"
                log.warning(content)
                return None  # 未满足交易条件
            else:
                return self.buy(stock_code=stock_code,
                                volume=size,
                                price_type=pqconstant.FIX_PRICE,
                                price=price,
                                force=force)

        elif target < market_value:  # Sell
            # 计算可交易股数
            if int(target) == 0:  # 平仓
                size = position.can_use_volume
            else:
                size = self.__calculate_size(price=price, cash=market_value - target)

            if size < 100:
                content = f"策略名称={self.strategy_name}, 类型=Sell, 股票代码={stock_code}, " \
                          f"目标市值={target}, 持仓市值={market_value}, 持仓可用数量={position.can_use_volume}，" \
                          f"委托价格={round(price, 2)},委托数量={size}, 交易股数不足100股，放弃交易"
                log.warning(content)
                return None  # 未满足交易条件
            else:
                if position.can_use_volume >= size >= 100:
                    content = f"策略名称={self.strategy_name}, 类型=Sell, 股票代码={stock_code}, " \
                              f"目标市值={target}, 持仓市值={market_value}, " \
                              f"委托价格={round(price, 2)}, 持仓可用数量={position.can_use_volume}， 委托数量={size}"
                    log.debug(content)
                    return self.sell(stock_code=stock_code,
                                     volume=size,
                                     price_type=pqconstant.FIX_PRICE,
                                     price=price,
                                     force=force)
                else:
                    content = f"策略名称={self.strategy_name}, 类型=Sell, 股票代码={stock_code}, " \
                              f"目标市值={target}, 持仓市值={market_value}, " \
                              f"委托价格={round(price, 2)},持仓数量={position.volume}, 委托数量={size}, " \
                              f"可用数量（{position.can_use_volume}）不足，放弃交易"
                    log.warning(content)
                    return None  # 未满足交易条件
        else:  # target = market_value
            log.warning(f"调仓目标等于持仓数量，放弃交易")
            return None

    def order_target_percent(self, stock_code: str, target: float = 0.0, force: bool = False):
        total_value = self.portfolio.total_value
        target *= total_value
        return self.order_target_value(stock_code=stock_code, target=target, force=force)

    def order_target_volume(self, stock_code: str, target: float = 0.0, force: bool = False):
        # 获取价格
        # trade_date = self.current_dt.strftime('%Y-%m-%d')
        if self.unit in ['1d']:
            trade_date = self.current_dt.strftime('%Y-%m-%d')
            trade_datetime = None
        else:
            trade_date = None
            trade_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')

        price_df = get_history(count=1,
                               end_date=trade_date,
                               end_datetime=trade_datetime,
                               unit=self.unit,
                               field='close',
                               security_list=[stock_code],
                               dividend_type=self.dividend_type,
                               expect_df=True)
        if price_df.empty:
            log.warning(f"股票停牌，取消买入: stock_code={stock_code}, trade_date={trade_date}")
            return
        else:
            price = price_df.iloc[0, 0]

        estimated_target_value = target * price
        return self.order_target_value(stock_code=stock_code, target=estimated_target_value, force=force)

    def close(self, stock_code: str, force: bool = False):
        """
        以最新价平仓股票代码, 默认平仓数量为可用数量

        :param stock_code:
        :param force:
        :return:
        """
        # 持仓查询
        position: Position = self.portfolio.positions.get(stock_code, None)
        volume = position.can_use_volume

        return self.sell(stock_code=stock_code, volume=volume, force=force)

    @property
    def unit(self):
        """
        unit: 单位时间长度，支持1d、1m，默认为1d
        :return:
        """
        return self.__unit

    @property
    def strategy_name(self):
        return self.__strategy_name

    @property
    def stock_pool(self):
        return self.__stock_pool

    @property
    def dividend_type(self):
        """
        dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
        :return:
        """
        return self.__dividend_type

    @property
    def parameters(self) -> dict:
        """
        执行策略的参数字典
        :return:
        """
        return self.__parameters

    @property
    def current_dt(self) -> datetime.datetime:
        return self.__dt

    def buy(self,
            stock_code: str,
            volume: int,
            price_type: int = pqconstant.FIX_PRICE,
            price: float = None,
            force: bool = False):
        """

        :param stock_code: 股票代码
        :param volume: 数量
        :param price_type: 价格类型
        :param price: 买入价格
        :param force: 如果force == True, 则直接交易，忽略是否进行委托队列。仅在实盘中有效, 在回测中忽略
        :return:
        """
        # 检查股票是否已经停牌
        if get_suspend_status(sec_code=stock_code, trade_date=self.current_dt.strftime('%Y-%m-%d')) > 0:
            log.warning(
                f"股票停牌，取消买入: stock_code={stock_code}, trade_date={self.current_dt.strftime('%Y-%m-%d')}")
            return

        # 获取价格
        if price_type != pqconstant.FIX_PRICE or price is None:
            # trade_date = self.current_dt.strftime('%Y-%m-%d')
            if self.unit in ['1d']:
                trade_date = self.current_dt.strftime('%Y-%m-%d')
                trade_datetime = None
            else:
                trade_date = None
                trade_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')
            price_df = get_history(count=1,
                                   end_date=trade_date,
                                   end_datetime=trade_datetime,
                                   unit=self.unit,
                                   field='close',
                                   security_list=[stock_code],
                                   dividend_type=self.dividend_type,
                                   expect_df=True)
            if price_df.empty:
                log.warning(f"无法获取股票价格，取消买入: stock_code={stock_code}, trade_date={trade_date}")
                return
            else:
                price = price_df.iloc[0, 0]

        # 更新Portfolio cash
        cost = volume * price
        if self.portfolio.available_cash < cost:
            log.warning(f"可用现金不足，放弃买入. cash={self.portfolio.available_cash}, cost={cost}")
            return
        else:
            self.portfolio.add_cash(cost * -1)

        # 更新Portfolio Positions
        position: Position = self.portfolio.positions.get(stock_code, None)
        if position:
            # 已经有头寸
            position.update_position(volume=volume, price=price, transact_time=self.current_dt)
        else:
            # 创建新的头寸
            position = Position(stock_code=stock_code,
                                volume=volume,
                                price=price,
                                init_time=self.current_dt,
                                context=self)
            self.portfolio.positions[stock_code] = position

        # 更新委托Id
        self.order_id += 1
        order = Order(order_id=self.order_id, stock_code=stock_code, direction='buy', order_volume=volume,
                      order_price=price, avg_cost=price, context=self)
        self.notify_order(order)
        return order

    def sell(self,
             stock_code: str,
             volume: int,
             price_type: int = pqconstant.FIX_PRICE,
             price: float = None,
             force: bool = False):
        """
        卖出股票
        :param stock_code:
        :param volume:
        :param price_type:
        :param price:
        :param force:
        :return:
        """
        # 检查股票是否已经停牌
        if get_suspend_status(sec_code=stock_code, trade_date=self.current_dt.strftime('%Y-%m-%d')) > 0:
            log.warning(
                f"股票停牌，取消卖出: stock_code={stock_code}, trade_date={self.current_dt.strftime('%Y-%m-%d')}")
            return

        # 获取价格
        if price_type != pqconstant.FIX_PRICE or price is None:
            # trade_date = self.current_dt.strftime('%Y-%m-%d')
            if self.unit in ['1d']:
                trade_date = self.current_dt.strftime('%Y-%m-%d')
                trade_datetime = None
            else:
                trade_date = None
                trade_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')
            price_df = get_history(count=1,
                                   end_date=trade_date,
                                   end_datetime=trade_datetime,
                                   unit=self.unit,
                                   field='close',
                                   security_list=[stock_code],
                                   dividend_type=self.dividend_type,
                                   expect_df=True)
            if price_df.empty:
                log.warning(f"无法获取股票价格，取消卖出: stock_code={stock_code}, trade_date={trade_date}")
                return
            else:
                price = price_df.iloc[0, 0]

        position: Position = self.portfolio.positions.get(stock_code, None)
        if position is None:
            log.error(f"stock_code: {stock_code} 无持仓，取消卖出")
            return
        if position.can_use_volume < volume:
            log.error(f"stock_code: {stock_code} 持仓数量不足，取消卖出")
            return

        # 持仓成本
        avg_price = position.avg_price

        # 更新持仓
        update_status = position.update_position(volume=volume * -1, price=price, transact_time=self.current_dt)

        # 检查是否已经平仓, 如是，则删除头寸记录
        position: Position = self.portfolio.positions.get(stock_code, None)
        if position and position.volume == 0:
            del self.portfolio.positions[stock_code]

        # 更新Portfolio cash
        if update_status:
            self.portfolio.add_cash(volume * price)

        # 更新委托Id
        self.order_id += 1
        order = Order(order_id=self.order_id, stock_code=stock_code, direction='sell', order_volume=volume,
                      order_price=price, avg_cost=avg_price, context=self)
        self.notify_order(order)
        return order

    @property
    def portfolio(self):
        """
        策略投资组合，可通过该对象获取当前策略账户、持仓等信息
        """
        return self._portfolio

    def inout_cash(self, cash: float):
        """
        投资组合转入或转出资金，当日的出入金从当日开始记入成本，用于计算收益，即当日结束计算收益时的本金是包含当日出入金金额的
        :param cash: 可正可负，正为入金，负为出金。
        :return:
        """
        # 记录出入金历史
        self.inout_cash_his.append({"datetime": self.current_dt, "cash": cash})
        # 把出入金更新到投资组合的可以资金
        self.portfolio.add_cash(cash=cash)
