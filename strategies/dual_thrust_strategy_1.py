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

from vnpy.trader.constant import Interval, Offset

class DualThrustStrategy(CtaTemplate):
    """"""
    author = "GYH"

    fixed_size = 1
    k1 = 0.6
    k2 = 0.4

    window_size = 5

    parameters = ["n_day", "k1", "k2", "fixed_size"]
    variables = ["range", "buy_line", "sell_line"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        # 将天数转换为分钟数
        self.window_size = self.window_size * 24 * 60

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(self.window_size + 1)

        self.highs = None
        self.lows = None
        self.opens = None
        self.closes = None
        self.volumes = None

        # 每小时获取一次小时线的开盘价，在分钟线进行操作
        self.open_price_this_period = None

        # 今天是否开仓
        self.today_open = False


    def on_init(self):
        self.write_log("策略初始化")
        #self.load_bar(self.window_size + 1)

    def on_start(self):
        self.write_log("策略启动")

    
    def on_stop(self):
        self.write_log("策略停止")

    
    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)
    

    def on_bar(self, bar: BarData):

        self.cancel_all()

        self.am.update_bar(bar)

        if not self.am.inited:
            return

        bar_time = bar.datetime.strftime("%H%M%S")
        if bar_time == "080000":
            #这是今天第一根bar，因为binance是从北京时间8点作为的日k线的开始
            # 今天第一个k线刚进来，今天肯定没开仓
            self.today_open = False
            # 记录当天开盘价
            self.open_price_this_period = bar.open_price
    
        if self.open_price_this_period is None:
            return

        self.highs = self.am.high[-self.window_size:]
        self.lows = self.am.low[-self.window_size:]
        self.opens = self.am.open[-self.window_size:]
        self.closes = self.am.close[-self.window_size:]
        self.volumes = self.am.volume[-self.window_size:]

        window_hh = max(self.highs)
        window_lc = min(self.closes)
        window_hc = max(self.closes)
        window_ll = min(self.lows)

        window_range = max(window_hh - window_lc, window_hc - window_ll)
        upper_bound = self.open_price_this_period + self.k1 * window_range
        lower_bound = self.open_price_this_period - self.k2 * window_range

        if bar.close_price > upper_bound:
            if self.pos == 0 and not self.today_open:
                self.buy(bar.close_price, self.fixed_size)

        elif bar.close_price < lower_bound:
            if self.pos > 0:
                self.sell(bar.close_price, self.pos)



    def on_order(self, order: OrderData):
        pass


    def on_trade(self, trade: TradeData):
        # 如果是开仓，则记录今天已经开仓
        if trade.offset == Offset.OPEN:
            self.today_open = True


    def on_stop_order(self, stop_order: StopOrder):
        pass