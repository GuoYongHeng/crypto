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
from vnpy_ctastrategy.engine import CtaEngine
from decimal import Decimal

class FixedTradeTimeStrategy(CtaTemplate):
    """
    基于时间的定投
    """
    author = "gyh"
    fixed_trade_money = 1000
    price_change_pct = 0.01

    parameters = ['fixed_trade_money', 'price_change_pct']

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg_2minute = BarGenerator(self.on_bar, 1, self.on_2minute_bar, Interval.HOUR)
        self.am = ArrayManager(size=10)

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(1)

    def on_start(self):
        self.write_log("我的策略启动")

    def on_stop(self):
        self.write_log("策略停止")

    def on_tick(self, tick : TickData):
        self.bg_2minute.update_tick(tick)

    def on_bar(self, bar : BarData):
        self.bg_2minute.update_bar(bar)

    def on_2minute_bar(self, bar:BarData):
        self.cancel_all()
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        print("开始执行交易策略啦，能不能成功执行就看命啦")

        last_close_price = self.am.close_array[-2]
        current_close_price = bar.close_price

        if (last_close_price - current_close_price)/last_close_price >= self.price_change_pct:
            price = bar.close_price * 1.001
            self.buy(price, self.fixed_trade_money/price)

    def on_order(self, order: OrderData):
        self.write_log("order")
    
    def on_trade(self, trade:TradeData):
        self.write_log("trade")
    
    def on_stop_order(self, stop_order : StopOrder):
        pass