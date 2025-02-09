from datetime import time

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

class DualThrustStrategy(CtaTemplate):
    """"""
    author = "GYH"

    fixed_size = 1
    k1 = 0.4
    k2 = 0.6

    bars = []

    day_open = 0
    day_high = 0
    day_low = 0

    day_range = 0
    long_entry = 0
    short_entry = 0

    long_entered = False
    short_entered = False

    parameters = ["k1", "k2", "fixed_size"]
    variables = ["day_range", "long_entry", "short_entry"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()
        self.bars = []


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
        
        self.bars.append(bar)
        if len(self.bars) <= 2:
            return
        else:
            self.bars.pop(0)
        last_bar: BarData = self.bars[-2]

        if last_bar.datetime.date() != bar.datetime.date():
            if self.day_high:
                self.day_range = self.day_high - self.day_low
                self.long_entry = bar.open_price + self.k1 * self.day_range
                self.short_entry = bar.open_price - self.k2 * self.day_range

            self.day_open = bar.open_price
            self.day_high = bar.high_price
            self.day_low = bar.low_price

            self.long_entered = False
            self.short_entered = False
        else:
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)

        if not self.day_range:
            return

        if self.pos == 0:
            if bar.close_price > self.day_open:
                if not self.long_entered:
                    self.buy(self.long_entry, self.fixed_size, stop = True)
            else:
                if not self.short_entered:
                    self.short(self.short_entry, self.fixed_size, stop = True)
        elif self.pos > 0:
            self.long_entered = True

            self.sell(self.short_entry, self.fixed_size, stop = True)

            if not self.short_entered:
                self.short(self.short_entry, self.fixed_size, stop = True)
        elif self.pos < 0:
            self.short_entered = True

            self.cover(self.long_entry, self.fixed_size, stop = True)

            if not self.long_entered:
                self.buy(self.long_entry, self.fixed_size, stop = True)


    def on_order(self, order: OrderData):
        pass


    def on_trade(self, trade: TradeData):
        pass


    def on_stop_order(self, stop_order: StopOrder):
        pass