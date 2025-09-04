from six import with_metaclass
import abc
from typing import Callable, Union, List
from .abstractPosition import AbstractPosition
from .abstractInstrument import AbstractInstrument
import datetime
import pandas as pd


class AbstractStrategyContext(with_metaclass(abc.ABCMeta)):
    """
    策略上下文的抽象接口类。
    """

    @abc.abstractmethod
    def plot_line(self, sec_code: str, name: str, value: float, desc=None):
        """
        画曲线
        :param sec_code:
        :param name:
        :param value:
        :param desc:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def plot_bar(self, sec_code: str, name: str, value: float, desc=None):
        """
        画柱状图
        :param sec_code:
        :param name:
        :param value:
        :param desc:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_monthly(self, func: Callable, monthday: int, time_str: str) -> None:
        """
        按月运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param monthday: 每月的第几个交易日, day (1-31)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_weekly(self, func: Callable, weekday: int, time_str: str) -> None:
        """
        按周运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param weekday: 每周的第几个交易日, 1 = monday, ... 7 = sunday
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        """
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
    def run_daily(self, func: Callable, time_str: str) -> None:
        """
        每天内何时运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_minutely(self, func: Callable, time_str: str, minutes: int = 1) -> None:
        """
        每天内何时开始，间隔n分钟执行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        :param minutes: 间隔执行的分钟数
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_secondly(self, func: Callable, time_str: str, seconds: int = 1) -> None:
        """
        每天内何时开始，间隔n秒执行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        :param seconds: 间隔执行的秒数
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cancel(self, order, force: bool = False):
        """
        取消订单委托
        :param force: 强制交易
        :param order: 回测中为order对象，实盘中为order_id
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def close(self, stock_code: str, force: bool = False):
        """
        以最新价平仓股票代码, 默认平仓数量为可用数量
        :param force: 强制交易
        :param stock_code: 需要平仓的股票代码
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
    def get_position(self, stock_code) -> AbstractPosition:
        """
        获取已经登录账号的股票持仓，返回个股持仓字典

        :param stock_code:
        :return: {'volume': 72000, 'can_use_volume': 0, 'open_price': 10.8, 'market_value': 1020240.0}
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_value(self,
                           stock_code: str,
                           target: float = 0.0,
                           price: float = None,
                           force: bool = False):
        """
        Place an order to rebalance a position to have final value of
        ``target``

        The current ``value`` is taken into account as the start point to
        achieve ``target``

          - If no ``target`` then close postion on data
          - If ``target`` > ``value`` then buy on data
          - If ``target`` < ``value`` then sell on data

        It returns either:

          - The generated order

          or

          - ``None`` if no order has been issued

        :param force: 强制交易
        :param stock_code: 目标持仓股票
        :param target: 目标持仓市值
        :param price:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_percent(self,
                             stock_code: str,
                             target: float = 0.0,
                             force: bool = False):
        """
        基于order_target_value（），按照总资产的百分比委托下单

        :param force: 强制交易
        :param stock_code:目标持仓股票
        :param target: 目标持仓比例
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_volume(self,
                            stock_code: str,
                            target: float = 0.0,
                            force: bool = False):
        """
        基于order_target_value()，按照个股的数量目标数量下单。注意，可能存在账户资金不足的情况。

        :param force: 强制交易
        :param stock_code: 目标持仓股票
        :param target: 目标持仓数量
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def constant(self):
        """
        上下文的系统常量
        :return:
        """
        raise NotImplementedError

    # @property
    # @abc.abstractmethod
    # def planned_trade_dates(self) -> list:
    #     """
    #     获取调仓交易日列表。
    #     :return:
    #     """
    #     raise NotImplementedError

    @property
    @abc.abstractmethod
    def previous_trade_date(self) -> datetime.date:
        """
        当前bar对应的前一个交易日
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parameters(self) -> dict:
        """
        执行策略的参数字典
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def stock_pool(self):
        """
        股票池
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def commission(self):
        """
        佣金费率
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def strategy_name(self):
        """
        策略名称
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unit(self):
        """
        unit: 单位时间长度，支持1d、1m，默认为1d
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
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
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def current_dt(self) -> datetime.datetime:
        """
        当前bar对应的日期/时间, format: %Y-%m-%d %H:%M:%S
        :return:
        """
        raise NotImplementedError

    # @property
    # @abc.abstractmethod
    # def next_trade_datetime(self):
    #     """
    #     当前bar对应的下一个日期/时间, format: %Y-%m-%d %H:%M:%S
    #     :return:
    #     """
    #     raise NotImplementedError

    @abc.abstractmethod
    def buy(self,
            stock_code: str,
            volume: int,
            price_type: int,
            price: float,
            force: bool = False):
        """
        证券买入委托
        Returns:
          - 委托的order_id
        """
        raise NotImplementedError

    @abc.abstractmethod
    def sell(self,
             stock_code: str,
             volume: int,
             price_type: int,
             price: float,
             force: bool = False):
        """
        证券卖出委托
        Returns:
          - 委托的order_id
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def portfolio(self):
        """
        策略投资组合，可通过该对象获取当前策略账户、持仓等信息
        """
        raise NotImplementedError

    @abc.abstractmethod
    def inout_cash(self, cash: float):
        """
        投资组合转入或转出资金，当日的出入金从当日开始记入成本，用于计算收益，即当日结束计算收益时的本金是包含当日出入金金额的
        :param cash: 可正可负，正为入金，负为出金。
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def run_info(self):
        """
        策略运行信息，包括回测过程中的所有参数。
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_security_info(self, sec_code: str) -> AbstractInstrument:
        """
        获取股票/基金/指数/期货的信息

        :param sec_code: 证券代码
        :return: 一个dict, 有如下属性:
                display_name: 中文名称
                name: 缩写简称
                start_date: 上市日期
                end_date: 退市日期（股票是最后一个交易日，不同于摘牌日期）， [datetime.date] 类型, 如果没有退市则为2200-01-01
                type:   'index'		#指数
                        'stock'		#股票
                        'fund'		#基金
                        'etf'		#ETF
        """
        raise NotImplementedError

    @abc.abstractmethod
    def query_new_purchase_limit(self):
        """
        查询新股申购额度
        :return:
            dict 新股申购额度数据集
            { type1: number1, type2: number2, ... }
            type - str 品种类型
            KCB - 科创板，SH - 上海，SZ - 深圳
            number - int 可申购股数
        """
        raise NotImplementedError

    @abc.abstractmethod
    def query_ipo_data(self):
        """
        查询当日新股新债信息
        :return:
            dict 新股新债信息数据集
            { stock1: info1, stock2: info2, ... }
                stock - str 品种代码，例如 '301208.SZ'
                info - dict 新股信息
                name - str 品种名称
                type - str 品种类型
                STOCK - 股票，BOND - 债券
                minPurchaseNum / maxPurchaseNum - int 最小 / 最大申购额度
                单位为股（股票）/ 张（债券）
                purchaseDate - str 申购日期
                issuePrice - float 发行价
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_factor(self,
                   sec_code_list: list = None,
                   factor_list: list = ...,
                   trade_date: str = None,
                   start_date: str = None,
                   end_date: str = None,
                   stock_pool: list = None,
                   expect_df: bool = True) -> pd.DataFrame:
        """
        TODO 返回给定的 sec_code 当日的因子，包括财务因子、alpha101 因子、技术指标 等

        :param trade_date: 指定交易日日期，默认为该日的前一个交易日
        :param sec_code_list:  合约代码
        :param factor_list: 因子名称
        :param start_date: 开始日期
        :param end_date:  结束日期
        :param stock_pool: 股票池，可选定指数的成分股，默认为 None，全市场
        :param expect_df: 默认返回 pandas dataframe
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def history(self, count, unit='1d', field='avg', security_list=None, expect_df=True, skip_paused=False,
                dividend_type='pre'):
        """
        获取历史数据，可查询多个标的单个数据字段，返回数据格式为 DataFrame 或 Dict(字典)

        :param count: 数量, 返回的结果集的行数
        :param unit: 单位时间长度, 几天或者几分钟, 现在支持'1d','1m'
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
        raise NotImplementedError

    @abc.abstractmethod
    def attribute_history(self,
                          security: str,
                          count: int,
                          unit: str = '1d',
                          fields: list = None,
                          skip_paused: bool = True,
                          expect_df: bool = True,
                          dividend_type: str = 'front'):
        """
        获取历史数据，可查询单个标的多个数据字段，返回数据格式为 DataFrame 或 Dict(字典)

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
        raise NotImplementedError

    @abc.abstractmethod
    def synthesize_portfolio(self,
                             count: int = None,
                             stock_pool: list = None,
                             start_date: str = None,
                             end_date: str = None,
                             freq: int = 5,
                             trade_date_lst: list = None,
                             sec_code: str = None,
                             sec_code_list: list = None,
                             factor_list=None,
                             expect_df: bool = False,
                             exact_match: bool = False,
                             stock_size: int = 10):
        """
        获取参数组合（stock_pool, start_date, end_date, freq）最优的合成因子数据所产生的股票组合。

        :param count: 获取最新的n期调仓日数据
        :param stock_pool: 股票池
        :param start_date: 因子取数的开始日期，也是合成因子回测的开始日期
        :param end_date: 因子取数的结束日期，也是合成因子回测的结束日期
        :param freq: 调仓周期，单位为天，默认值为5
        :param trade_date_lst: 限定调仓日列表
        :param sec_code: 股票
        :param sec_code_list: 股票代码列表
        :param factor_list: 合成因子列表，默认返回完整的合成因子列表
        :param expect_df: 若是True, 返回[pandas.DataFrame], 否则返回一个dict, 具体请看下面的返回值介绍. 默认是True.
        :param exact_match: 是否精确匹配（stock_pool, start_date, end_date, freq），或者近似匹配
        :param stock_size: 股票组合的股票个数
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_blacklist(self) -> list:
        """
        获取租户下定义的股票列表黑名单，黑名单的股票不建议持仓

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
    def get_plate_data(self, trade_date: str = None, end_time: str = "15:00", limit: int = 3) -> pd.DataFrame:
        """
        获取板块列表

        :param trade_date: 指定交易日的板块列表
        :param end_time: 指定板块排名的时间节点，从09:25开始到15:30结束，每个间隔5分钟
        :param limit: 按照板块强度倒序排名的板块数量
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_plate_members_lst(self, plate_code_list: list, trade_date: str = None):
        """
        获取板块的成分股
        :param plate_code_list:
        :param trade_date:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_stock_name(self, sec_code: str, trade_date: str = None):
        """
        获取股票代码的最新名称

        :param sec_code:
        :param trade_date:
            None：默认为当天，如果当天不是交易日，则获取上一个交易日。
            'YYYY-mm-dd'：具体日期的最新股票名称
        :return: 股票名称
        """
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

