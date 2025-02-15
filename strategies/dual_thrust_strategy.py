from datetime import time
from zoneinfo import ZoneInfo

from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)

from vnpy.trader.constant import Interval

class DualThrustStrategy(CtaTemplate):
    """"""
    author = "GYH"

    n_day = 5

    first_bar = True

    fixed_size = 1
    k1 = 0.4
    k2 = 0.6

    day_open = 0

    range = 0
    buy_line = 0
    sell_line = 0

    long_entered = False 
    # 该变量用来保证一个交易日只买一次，
    # 我也不知道为什么一个交易日只买一次，
    # 因为vnpy官方实现代码中一个交易日只买一次
    # 我也就这样做了

    parameters = ["n_day", "k1", "k2", "fixed_size"]
    variables = ["range", "buy_line", "sell_line"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, 1, self.on_1day_bar,  Interval.DAILY, time(8, tzinfo=ZoneInfo('Asia/Shanghai')))
        self.am = ArrayManager(self.n_day + 1)


    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)


    def on_start(self):
        self.write_log("策略启动")

    
    def on_stop(self):
        self.write_log("策略停止")

    
    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)
    

    def on_bar(self, bar: BarData):
        self.cancel_all()

        self.bg.update_bar(bar)

        if not self.am.inited:
            return

        if self.first_bar:
            self.day_open = bar.open_price # 记录当日开盘价

            HH = max(self.am.high_array)  # n日最高价的最高价
            LC = min(self.am.close_array) # n日收盘价的最低价
            HC = max(self.am.close_array) # n日收盘价的最高价
            LL = min(self.am.low_array)   # n日最低价的最低价
            self.range = max(HH - LC, HC - LL) # 计算n日的波动幅度

            self.buy_line = self.day_open + self.k1 * self.range
            self.sell_line = self.day_open - self.k2 * self.range

            self.first_bar = False
            self.long_entered = False

        
        # 不管有没有持仓，只要突破上轨就买入
        if bar.close_price > self.buy_line and not self.long_entered:
            self.buy(bar.close_price, self.fixed_size)

        # 只要突破下轨，就全部卖出
        if bar.close_price < self.sell_line:
            if self.pos > 0:
                self.sell(bar.close_price, self.pos)


    def on_1day_bar(self, bar: BarData):
        """
        生成日k线
        """
        self.am.update_bar(bar)
        self.first_bar = True


    def on_order(self, order: OrderData):
        pass


    def on_trade(self, trade: TradeData):
        if self.pos > 0:
            self.long_entered = True


    def on_stop_order(self, stop_order: StopOrder):
        pass