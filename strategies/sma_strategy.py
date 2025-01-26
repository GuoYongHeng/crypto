from vnpy_ctastrategy import (
    CtaTemplate,
    BarData, 
    TickData,
    TradeData, 
    OrderData,
    StopOrder,
    ArrayManager, 
    BarGenerator
)

from vnpy.trader.constant import Interval
from datetime import datetime

class SmaStrategy(CtaTemplate):
    """Double SMA (simple moving average) strategy"""
    author: str = "GYH"

    fast_window: int = 10
    slow_window: int = 20

    fast_ma0: float = 0.0
    fast_ma1: float = 0.0

    slow_ma0: float = 0.0
    slow_ma1: float = 0.0

    parameters: list = [
        "fast_window",
        "slow_window",
    ]

    variables: list = [
        "fast_ma0",
        "slow_ma0",
        "fast_ma1",
        "slow_ma1",
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()


    def on_init(self) -> None:
        self.write_log("策略初始化")
        self.load_bar(10)


    def on_start(self) -> None:
        self.write_log("策略启动")


    def on_stop(self) -> None:
        self.write_log("策略停止")


    def on_tick(self, tick: TickData) -> None:
        self.bg.update_tick(tick)


    def on_bar(self, bar: BarData) -> None:
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1
        cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1

        if cross_over:
            if self.pos == 0:
                self.buy(bar.close_price, 1)
            elif self.pos < 0:
                self.cover(bar.close_price, 1)
                self.buy(bar.close_price, 1)
        elif cross_below:
            if self.pos == 0:
                self.short(bar.close_price, 1)
            elif self.pos > 0:
                self.sell(bar.close_price, 1)
                self.short(bar.close_price, 1)

    def on_order(self, order: OrderData) -> None:
        pass

    def on_trade(self, trade: TradeData) -> None:
        pass

    def on_stop_order(self, stop_order: StopOrder):
        pass

# reference:https://github.com/51bitquant/howtrader/blob/91072127078f1730a9c97cb040eb29634b2fa07f/examples/strategies/double_ma_strategy.py