# coding=utf-8
from thriftpy2.transport import TTransportException

from .client import PQDataClient
from .utils import *
from typing import Union, List
import time
import datetime
from ..logger import log
import pandas as pd
# 使用LRU缓存减少数据库查询
from functools import lru_cache


class GlobalObject(object):
    """
    全局变量对象
    如果g中的某个变量不想被序列化, 可以让变量以 '__' 开头, 在序列化时会被忽略

    要在Python中通过pickle序列化自定义类，需要满足以下两个条件：

    1. 自定义类必须实现__getstate__()和__setstate__()方法。
        1) getstate() 方法应该返回一个包含对象状态的字典。这个字典将是 pickle 用于序列化对象的内容。
        2) setstate() 方法接收一个字典作为参数，并使用它来恢复对象状态。
    2. 自定义类必须是全局可访问的。

    """

    def __getstate__(self):
        return {name: getattr(self, name) for name in dir(self) if not name.startswith("__")}

    def __setstate__(self, state):
        # reset g
        for k, v in state.items():
            setattr(self, k, v)


@assert_auth
def get_factor(sec_code: Union[None, str, List[str]] = None,
               factor: Union[None, str, List[str]] = None,
               sec_code_list: list = None,
               factor_list: list = None,
               factor_group_list: list = None,
               trade_date: str = None,
               start_date: str = None,
               end_date: str = None,
               start_datetime: str = None,
               end_datetime: str = None,
               stock_pool: list = None,
               dividend_type: str = 'front',
               unit: str = '1d',
               expect_df: bool = True,
               count: int = None,
               fill_data: bool = False):
    """
    查询因子库数据.


    :param fill_data: bool 是否向后填充空缺数据, 目前支持unit = '1d'
    :param sec_code: 股票代码，支持字符串或者字符串数组. 为数组的时候等价于sec_code_list
    :param factor: 因子名称, 支持字符串或者字符串数组，为数组的时候，等价于factor_list
    :param sec_code_list: 股票代码列表
    :param factor_list: 因子列表，因子可能来源于不同的因子分组
    :param factor_group_list: 限定因子分组
    :param trade_date: 限定交易日
    :param start_date: 开始交易日
    :param end_date: 结束交易日
    :param start_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param end_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param stock_pool: 指数列表，仅加载指数成分股。
                       选出了历史中出现在指数中所有成分，此时有未来函数，等于把低价股票提前选入了沪深300的股票池中。
                       数据分析中需要结合crud.get_index_members_lst()一起使用，过滤掉未来函数的股票。
    :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param unit: 单位时间长度，支持1d、1m，默认为1d
    :param expect_df: 是否以DataFrame返回
    :param count: 数量, 返回最近的条目数
    :return:
    """
    if factor_list is None:
        factor_list = ['close']
    return PQDataClient.instance().get_factor(**locals())


@assert_auth
def get_transform_factor(sec_code: str = None,
                         sec_code_list: list = None,
                         factor_list=None,
                         factor_group_list: list = None,
                         trade_date: str = None,
                         start_date: str = None,
                         end_date: str = None,
                         stock_pool: list = None,
                         dividend_type='back',
                         unit: str = '1d',
                         expect_df: bool = True,
                         count: int = None):
    """
    查询因子数据的空值处理、去极值、标准化、市值中性化、行业中性化后的结果

    :param sec_code: 股票代码
    :param sec_code_list: 股票代码列表
    :param factor_list: 因子列表，因子可能来源于不同的因子分组
    :param factor_group_list: 限定因子分组
    :param trade_date: 限定交易日
    :param start_date: 开始交易日
    :param end_date: 结束交易日
    :param stock_pool: 指数列表，仅加载指数成分股。
                       选出了历史中出现在指数中所有成分，此时有未来函数，等于把低价股票提前选入了沪深300的股票池中。
                       数据分析中需要结合crud.get_index_members_lst()一起使用，过滤掉未来函数的股票。
    :param dividend_type: 复权选项
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param unit: 单位时间长度，支持1d、1m，默认为1d
    :param expect_df: 是否以DataFrame返回
    :param count: 数量, 返回的结果集的行数
    :return:
    """
    if factor_list is None:
        factor_list = ['close']
    return PQDataClient.instance().get_transform_factor(**locals())


@assert_auth
def get_history(count: int = None,
                unit: str = '1d',
                start_date: str = None,
                end_date: str = None,
                start_datetime: str = None,
                end_datetime: str = None,
                field: str = 'close',
                security_list=None,
                stock_pool: list = None,
                expect_df=True,
                skip_paused=False,
                dividend_type='front'):
    """
    获取历史数据，可查询多个标的单个数据字段，返回数据格式为 DataFrame 或 Dict(字典)

    :param stock_pool:
    :param start_date:
    :param end_date:
    :param count: 数量, 返回的结果集的行数
    :param unit: 单位时间长度, 几天或者几分钟, 现在支持'1d','1m'
    :param start_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param end_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
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
    return PQDataClient.instance().get_history(**locals())


@assert_auth
def get_attribute_history(security: str,
                          count: int = None,
                          unit: str = '1d',
                          start_date: str = None,
                          end_date: str = None,
                          start_datetime: str = None,
                          end_datetime: str = None,
                          fields: list = None,
                          skip_paused: bool = True,
                          expect_df: bool = True,
                          dividend_type: str = 'front'):
    """
    获取历史数据，可查询单个标的多个数据字段，返回数据格式为 DataFrame 或 Dict(字典)

    :param start_date:
    :param end_date:
    :param start_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param end_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param security: 股票代码
    :param count: 数量, 返回的结果集的行数
    :param unit: 单位时间长度, 1d, 1m
    :param fields: 股票属性的list, 支持：['open', ' high', 'low', 'close', 'volume', 'amount']
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
    return PQDataClient.instance().get_attribute_history(**locals())


@assert_auth
def get_synthesize_factor(stock_pool: list,
                          start_date: str,
                          end_date: str,
                          freq: int = 5,
                          trade_date: str = None,
                          sec_code: str = None,
                          sec_code_list: list = None,
                          factor_list=None,
                          expect_df: bool = True,
                          exact_match: bool = False):
    """
    获取参数组合（stock_pool, start_date, end_date, freq）最优的合成因子数据

    :param stock_pool: 股票池
    :param start_date: 因子取数的开始日期，也是合成因子回测的开始日期
    :param end_date: 因子取数的结束日期，也是合成因子回测的结束日期
    :param freq: 调仓周期，单位为天，默认值为5
    :param trade_date: 限定交易日
    :param sec_code: 股票
    :param sec_code_list: 股票代码列表
    :param factor_list: 合成因子列表，默认返回完整的合成因子列表
    :param expect_df: 若是True, 返回[pandas.DataFrame], 否则返回一个dict, 具体请看下面的返回值介绍. 默认是True.
    :param exact_match: 是否精确匹配（stock_pool, start_date, end_date, freq），或者近似匹配
    :return:
    """
    return PQDataClient.instance().get_synthesize_factor(**locals())


@assert_auth
def get_synthesize_portfolio(count: int = None,
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
    return PQDataClient.instance().get_synthesize_portfolio(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_trade_cal(start_date: str = '2018-01-01'):
    """
    获取交易日历，默认从2018-01-01开始
    :return:
    """
    return PQDataClient.instance().get_trade_cal(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_previous_trading_date(date: str, lookback_days: int = 1):
    """
    对于给定的日期，返回前第n天
    :param date:
    :param lookback_days: 前第n天，默认前1天
    :return:
    """
    return PQDataClient.instance().get_previous_trading_date(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_next_trading_date(date: str, lookahead_days: int = 1):
    """
    对于给定的日期，返回后第n天
    :param date:
    :param lookahead_days: 后第n天，默认前1天
    :return:
    """
    return PQDataClient.instance().get_next_trading_date(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_near_trade_date(trade_date: str, max_retries=5, retry_delay=2):
    """
    检查trade_date是否为交易日，否则，获取上一个交易日。
    如果返回值不是字符串类型，则重试，最多重试max_retries次，每次间隔retry_delay秒。

    :param trade_date: 输入的交易日期
    :param max_retries: 最大重试次数
    :param retry_delay: 每次重试之间的延迟时间（秒）
    :return: 最近的交易日（字符串类型）
    """
    retries = 0
    while retries < max_retries:
        res = PQDataClient.instance().get_near_trade_date(trade_date=trade_date)
        if isinstance(res, str):
            return res
        else:
            log.warning(f"返回值不是字符串类型，{res}，重试 {retries + 1}/{max_retries}...")
            retries += 1
            time.sleep(retry_delay)

            # 如果达到最大重试次数仍然失败，可以抛出一个异常或返回一个默认值
    raise ValueError("无法获取有效的交易日期，已达到最大重试次数")


@assert_auth
@lru_cache(maxsize=1024)
def get_open_trade_dates(start_date: str, end_date: str = None):
    """
    通过开始日期和结束日期，取得交易日。

    :param start_date:
    :param end_date:
    :return: df, 只有一个Column：trade_date
    """
    return PQDataClient.instance().get_open_trade_dates(**locals())


@assert_auth
def get_index_members_lst(index_lst: list, trade_date: str = None):
    """
    获取指数成分股列表

    :param trade_date: 截止trade_date最新一期的指数成分股，为None则返回历史出现过的所有成分股
    :param index_lst: 指数列表
    :return:
    """
    return PQDataClient.instance().get_index_members_lst(**locals())


@assert_auth
def get_concept_members(code: str = None, code_list: list = None, name: str = None, keyword: str = None):
    """
    获取概念成分股

    :param code: 概念编码
    :param code_list: 概念编码列表
    :param name: 概念名称
    :param keyword: 概念名称关键字
    :return: list 成分股列表
    """
    return PQDataClient.instance().get_concept_members(**locals())


@assert_auth
def get_concept(code: str = None,
                code_list: list = None,
                name: str = None,
                keyword: str = None,
                exchange: str = 'A',
                type: str = 'N') -> dict:
    """
    获取概念列表
    :param code: 概念编码
    :param code_list: 概念编码列表
    :param name: 概念名称
    :param keyword: 概念名称关键字
    :param exchange: 交易所
    :param type: 	N概念指数, S特色指数
    :return: dict {'864006.TI': {'name': '固态电池', 'count': 1}, '886032.TI': {'name': '固态电池', 'count': 62}}
    """
    return PQDataClient.instance().get_concept(**locals())


@assert_auth
def get_hot_concept(count: int,
                    trade_date: str,
                    code: str = None,
                    code_list: list = None,
                    name: str = None,
                    keyword: str = None,
                    exchange: str = 'A',
                    type: str = 'N',
                    order_by: str = 'pct_change desc'):
    """
    获取热门概念编号列表，默认以涨跌幅倒序排列
    :param count:
    :param trade_date:
    :param code:
    :param code_list:
    :param name:
    :param keyword:
    :param exchange:
    :param type:
    :param order_by:
    :return:
    """
    return PQDataClient.instance().get_hot_concept(**locals())


@assert_auth
def get_news_content(start_date: str, end_date: str, sec_code_list: list = None):
    return PQDataClient.instance().get_news_content(**locals())


@assert_auth
def get_stock_info(stock_lst: list,
                   fields=None,
                   stock_pool: list = None,
                   trade_date: str = None,
                   dividend_type: str = "front"):
    """
    获取股票基础信息。

    :param dividend_type: 对于历史数据，复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param trade_date: 指定交易日
    :param stock_pool: 指定股票池
    :param stock_lst: 指定股票列表
    :param fields: 可选，['sec_code', 'datetime', 'name', 'pre_close', 'up_limit', 'down_limit']
    :return: df:
        se_code	股票代码
        datetime 数据时间
        name 	合约名称
        pre_close 	前收盘价格
        up_limit	当日涨停价
        down_limit	当日跌停价
    """
    return PQDataClient.instance().get_stock_info(**locals())


@assert_auth
def get_suspend_info(trade_date: str, fields=None, stock_lst: list = None, suspend_type: str = 'S'):
    """
    获取股票在某日的停复牌状态

    :param trade_date:
    :param fields:
    :param stock_lst:
    :param suspend_type: 停牌：S，复牌：R
    :return:
    """
    return PQDataClient.instance().get_suspend_info(**locals())


@assert_auth
def get_stock_name_his(sec_code: str, trade_date: str):
    """
    获取股票代码的历史名称
    :param trade_date:
    :param sec_code:
    :return: {'sec_code': '000001.SZ', 'name': '平安银行', 'start_date': '2012-08-02', 'end_date': '2099-12-30'}
    """
    return PQDataClient.instance().get_stock_name_his(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def is_open_trade_date(date: str):
    """检查是否为交易日"""
    return PQDataClient.instance().is_open_trade_date(**locals())


@assert_auth
def get_last_ticks(sec_code_lst: list, index: bool = False, fields: list = None):
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
    return PQDataClient.instance().get_last_ticks(**locals())


@assert_auth
def get_plate_data(trade_date: str = None, end_time: str = "15:00", limit: int = 3):
    """
    获取板块列表

    :param trade_date: 指定交易日的板块列表
    :param end_time: 指定板块排名的时间节点，从09:25开始到15:30结束，每个间隔5分钟
    :param limit: 按照板块强度倒序排名的板块数量
    :return:
    """
    return PQDataClient.instance().get_plate_data(**locals())


@assert_auth
def get_hot_plate(trade_date: str = None, n_days: int = 5, top_n: int = 5, hot_n: int = 5, exclude_list: list = None):
    """
    获取最近n天 上榜(每天进入强度前n)天数最多的板块
    :param trade_date: 选股日期, 默认为前一个交易日
    :param n_days: 从最近多少天里筛选热门板块，默认 5
    :param top_n:  每天热度top n，默认top 5
    :param hot_n:  最终选出 最近n_days 天 热门的前n个板块
    :param exclude_list: 排除的板块清单，比如 ST板块，中报增长板块等
    :return: DataFrame
    """
    return PQDataClient.instance().get_hot_plate(**locals())


@assert_auth
def get_plate_members_lst(plate_code_list: list, trade_date: str = None):
    """
    获取板块的成分股
    :param plate_code_list:
    :param trade_date:
    :return:
    """
    return PQDataClient.instance().get_plate_members_lst(**locals())


@assert_auth
def get_member_plates(sec_code: str, trade_date: str = None) -> pd.DataFrame:
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
    return PQDataClient.instance().get_member_plates(**locals())


@assert_auth
def get_stock_name(sec_code: str, trade_date: str = None):
    """
    获取股票代码的最新名称

    :param sec_code:
    :param trade_date:
        None：默认为当天，如果当天不是交易日，则获取上一个交易日。
        'YYYY-mm-dd'：具体日期的最新股票名称
    :return: 股票名称
    """
    return PQDataClient.instance().get_stock_name(**locals())


@assert_auth
def get_stock_price(sec_code: str,
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
    return PQDataClient.instance().get_stock_price(**locals())


@assert_auth
def get_price_limit(sec_code: str,
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
    return PQDataClient.instance().get_price_limit(**locals())


@assert_auth
def get_auction_data(security: str,
                     count: int = None,
                     unit: str = '1m',
                     trade_date: str = None,
                     start_date: str = None,
                     end_date: str = None,
                     start_datetime: str = None,
                     end_datetime: str = None,
                     fields: list = None):
    """
    # 获取股票的集合竞价数据。集合竞价的规则如下：
    - 开盘竞价时间是9点15分到9点25分
    - 9:15到9:20是自由买卖阶段，可以下单，也可以撤单
    - 9:20到9点25下单后，这段时间可以下单但是禁止撤单

    # 参数互斥检查：
    - trade_date不能与其他日期参数(start_date/end_date/start_datetime/end_datetime)同时使用
    - start_date/end_date不能与start_datetime/end_datetime同时使用

    # 限定时间在09:15:00到09:25:00之间, 无论查询跨越多少天，每天都只返回这个时间段的数据
    # 日期处理逻辑：
    - 如果指定了trade_date，只查询该日期的数据
    - 如果指定了start_date/end_date，按日期范围查询
    - 如果指定了start_datetime/end_datetime，使用完整的时间范围查询
    - 如果没有指定任何日期参数，默认使用最近的交易日

    # 使用案例
    ## 使用start_date/end_date查询日期范围
    df = get_auction_data(security='000001.SZ',
                             start_date='2024-03-01',
                             end_date='2024-03-20')

    ## 使用trade_date查询单个交易日
    df = get_auction_data(security='000001.SZ',
                             trade_date='2024-03-20')

    ## 使用start_datetime/end_datetime查询时间范围，查询的结果会限定在09:15:00到09:25:00之间
    df = get_auction_data(security='000001.SZ',
                             start_datetime='2024-03-01 00:00:00',
                             end_datetime='2024-03-20 23:59:59')

    :param security: 股票代码
    :param count: 返回行数
    :param unit: 支持1m, 5m
    :param trade_date: 指定单个交易日，与其他日期参数互斥
    :param start_date: 开始日期，格式：YYYY-MM-DD
    :param end_date: 结束日期，格式：YYYY-MM-DD
    :param start_datetime: 开始时间，格式：YYYY-MM-DD HH:mm:SS
    :param end_datetime: 结束时间，格式：YYYY-MM-DD HH:mm:SS
    :param fields: 获取字段，范围：['open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount']
    :return: DataFrame，包含指定时间范围内每个交易日09:15:00到09:25:00的集合竞价数据
    """
    return PQDataClient.instance().get_auction_data(**locals())


@assert_auth
def get_abnormal_stocks(fields: list = None,
                        sec_code_list: list = None,
                        start_date: str = None,
                        end_date: str = None,
                        abnormal_type: int = None):
    """
    获取严重异动的股票，即其偏离值异动的股票
    :param fields: 获取数据的字段，默认：sec_code, 支持 sec_code, trade_date, abnormal_type
    :param sec_code_list: 指定的股票是否发生过异动
    :param start_date: 异动日期范围, 如果未指定起始日期，默认6个月前
    :param end_date: 异动日期范围
    :param abnormal_type: 股票偏离值异动类型
    :return:
    """
    return PQDataClient.instance().get_abnormal_stocks(**locals())


@assert_auth
def get_suspend_status(sec_code: str, trade_date: str = None):
    """
    合约停牌状态
    :param sec_code:
    :param trade_date:
    :return: int
            <=0 正常，-1 复牌，>0 停牌, >=1 停牌天数
    """
    return PQDataClient.instance().get_suspend_status(**locals())


@assert_auth
def get_prompt_query(query: str,
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
    params_dict = {"query": query,
                   "query_type": query_type,
                   "page_size": page_size,
                   }

    if page_num and loop is False:
        params_dict['page_num'] = page_num
        max_retry = 2  # 最多尝试次数
        result_on_except = []  # 如果尝试失败的返回默认结果
        return PQDataClient.instance().get_prompt_query(*(max_retry, result_on_except), **params_dict)

    elif isinstance(loop, bool) and loop is True:  # 分页查询，最终合并结果
        _page_num = 1
        result = []
        while True:
            params_dict['page_num'] = _page_num
            max_retry = 2  # 最多尝试次数
            result_on_except = []  # 如果尝试失败的返回默认结果
            stock_list = PQDataClient.instance().get_prompt_query(*(max_retry, result_on_except), **params_dict)
            result.extend(stock_list)
            _page_num += 1
            if len(stock_list) == 0:
                break
        return result
    elif isinstance(loop, int):  # 返回前x页
        loop = max(1, loop)
        params_dict['loop'] = loop
        return PQDataClient.instance().get_prompt_query(**params_dict)
    else:
        return PQDataClient.instance().get_prompt_query(**params_dict)


@assert_auth
def get_reduce_holdings(start_date: str, end_date: str):
    """
    获取指定日期范围内发布了减持公告的股票代码列表

    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: list，股票代码列表
    """
    return PQDataClient.instance().get_reduce_holdings(**locals())


@assert_auth
def get_board_members(boards: list,
                      status: str = "L",
                      start_date: str = None,
                      end_date: str = None,
                      is_hs: str = None):
    """
    获取板块的成分股

    :param boards: 板块列表
            [
            "sz.zh", # 深市主板
            "sh.zh", # 沪市主板
            "sz.cy", # 创业板
            "sh.kc", # 科创板
            "sz.zx",  # 中小板
            "bj.bj",  # 北交所
            ]
    :param status: 上市状态 L上市 D退市 P暂停上市
    :param start_date: # 上市日期范围
    :param end_date: # 上市日期范围
    :param is_hs: 是否沪深港通标的，N否 H沪股通 S深股通
    :return: list, 股票列表
    """
    return PQDataClient.instance().get_board_members(**locals())


@assert_auth
def get_up_limit_stocks(stock_list: list, trade_date: str, lookback_days: int = 1, dividend_type: str = 'front'):
    """
    获取连板涨停的股票列表。

    :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param stock_list:
    :param trade_date:
    :param lookback_days:
            0：昨日未涨停的股票
            >=1: 连板涨停的股票
    :return: list，股票代码列表
    """
    return PQDataClient.instance().get_up_limit_stocks(**locals())


@assert_auth
def get_leading_stocks(trade_date: str = None,
                       keywords: list = None,
                       src_type: str = 'tencent',
                       expect_df: bool = False):
    """
    获取某个交易日下的行业/概念龙头股票代码列表

    :param src_type: 数据来源，仅支持 'tencent' 或 'THS'，默认 'tencent'
    :param expect_df: 是否返回DataFrame，False返回股票列表，True返回DataFrame，默认 False
    :param trade_date: 指定交易日，格式为 'YYYY-MM-DD'，默认取前一交易日
    :param keywords: 行业/概念的关键字列表（如 ['创新药', '军工', '华为']），默认 None（匹配所有）
    :return: 股票列表（expect_df=False）或 DataFrame（expect_df=True）
    """
    return PQDataClient.instance().get_leading_stocks(**locals())


@assert_auth
def get_ohlcv(sec_code: str,
              current_dt: datetime.datetime = None,
              start_date: str = None,
              end_date: str = None,
              timeframe: str = '1d',
              size: int = 100,
              dividend_type: str = 'front'):
    """
    获取股票的OHLCV（开高低收成交量）数据

    该函数能够智能获取指定股票的历史和实时OHLCV数据，支持多种时间周期。
    在实盘交易中，会结合历史数据和当前实时数据，确保数据的完整性和准确性。

    Args:
        sec_code (str): 股票代码，格式如 '000001.SZ' 或 '600000.SH'
        current_dt: 指定当前的日期时间，datetime格式
        start_date: 获取数据的开始日期
        end_date: 获取数据的结束日期
        timeframe (str, optional): 时间周期，支持以下值：
            - '1m': 1分钟K线
            - '5m': 5分钟K线
            - '1d': 日K线
            默认为 '1d'
        size (int, optional): 获取的K线数量，默认为100根
        dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                    'front'
                    : 前复权, 默认是前复权
                    none
                    : 不复权, 返回实际价格
                    'back'
                    : 后复权

    Returns:
        pandas.DataFrame: 包含OHLCV数据的DataFrame，列结构如下：
            - datetime/trade_date: 时间戳（分钟级为datetime格式，日级为trade_date格式）
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量

    Raises:
        ValueError: 当参数无效时抛出异常
        Exception: 当数据获取失败时抛出异常，函数内部会捕获并记录错误日志

    Note:
        - 函数会自动处理实盘和回测环境的差异
        - 在实盘环境中，会通过get_last_ticks获取实时数据
        - 在回测环境中，会通过get_attribute_history获取历史数据
        - 返回的数据按时间升序排列，最新的数据在最后
        - 如果获取的数据超过指定size，会自动截取最新的size条记录

    """
    return PQDataClient.instance().get_ohlcv(**locals())


# ---------------------------------------------------------
# 外部可以访问的列表
# ---------------------------------------------------------
__all__ = ["GlobalObject", "is_open_trade_date"]
__all__.extend([name for name in globals().keys() if name.startswith("get")])
