from pqsdk.interface import AbstractRunInfo
from pqsdk.api import get_index_members_lst


class RunInfo(AbstractRunInfo):

    def __init__(self, kwargs: dict, context):
        self.__kwargs = kwargs
        self.context = context

    @property
    def tenant_id(self):
        return self.__kwargs.get('user').tenant_id

    @property
    def portfolio_id(self):
        """
        回测的时候，投资组合可能还未指定
        :return:
        """
        return -1

    @property
    def parameters(self):
        return self.__kwargs.get('parameters', {})

    @property
    def start_date(self):
        return self.__kwargs.get('start_date')

    @property
    def end_date(self):
        return self.__kwargs.get('end_date')

    @property
    def stock_starting_cash(self):
        return self.__kwargs.get('init_investment')

    @property
    def strategy_id(self):
        return self.__kwargs.get('strategy_id')

    @property
    def release_id(self):
        """
        回测的时候，策略代码可能还未发版
        :return:
        """
        return -1

    @property
    def strategy_name(self):
        return self.__kwargs.get('strategy_name')

    @property
    def strategy_remark(self):
        """
        策略备注
        :return:
        """
        return 'backtest'

    @property
    def is_queued_order(self):
        """
        回测中不拦截委托
        :return:
        """
        return False

    @property
    def benchmark(self):
        return self.__kwargs.get('benchmark')

    @property
    def stock_pool(self) -> list:
        return self.__kwargs.get('stock_pool')

    @property
    def stock_pool_members(self) -> list:
        """
        当日的股票池成员
        :return:
        """
        return get_index_members_lst(index_lst=self.stock_pool,
                                     trade_date=self.context.current_dt.strftime('%Y-%m-%d'))
