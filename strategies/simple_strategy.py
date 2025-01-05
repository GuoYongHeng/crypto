from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager
)

from vnpy.trader.constant import Interval

class SimpleStrategy(CtaTemplate):
    author = "gyh"

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, 2, self.on_2min_bar, Interval.MINUTE)
        self.place_holder = False
        self.orders = []


    def on_init(self):
        self.write_log("策略初始化")


    def on_start(self):
        self.write_log(f"测试策略启动, {self.trading}")


    def on_stop(self):
        self.write_log("策略停止")


    def on_tick(self, tick: TickData):
        print(f"tick, ask1:{tick.ask_price_1}, {tick.ask_volume_1}, bid:{tick.bid_price_1}, {tick.bid_volume_1}")
        print(f"my current pos is: {self.pos}, ask:{tick.ask_price_1}, bid: {tick.bid_price_1}")
        self.bg.update_tick(tick)



    def on_bar(self, bar: BarData):
        print("1分钟的k线数据", bar)
        self.bg.update_bar(bar)


    def on_2min_bar(self, bar: BarData):
        print("2分钟的k线数据", bar)


    def on_order(self, order: OrderData):
        print("策略推送过来的order:", order)


    def on_trade(self, trade: TradeData):
        print("最新的成交:", trade)


    def on_stop_order(self, stop_order: StopOrder):
        pass