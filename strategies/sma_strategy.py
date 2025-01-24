from vnpy_ctastrategy import (
    CtaTemplate,
    BarData, 
    TickData,
    TradeData, 
    OrderData,
    ArrayManager, 
    BarGenerator
)

from vnpy.trader.constant import Interval
from datetime import datetime

class SmaStrategy(CtaTemplate):
    """Double SMA (simple moving average) strategy"""
    author: str = "GYH"

    fast_window: int = 5
    slow_window: int = 20
    trading_symbol: str = ""
    trading_size: int = 1

    fast_ma: int = 0
    slow_ma: int = 0
    trading_target: int = 0
    trading_pos: int = 0

    parameters: list = [
        "fast_window",
        "slow_window",
        "trading_symbol",
        "trading_size"
    ]

    variables: list = [
        "fast_ma",
        "slow_ma",
        "trading_target",
        "trading_pos"
    ]

    def on_init(self) -> None:
        self.trading_symbol: str = self.vt_symbol
        self.bar_dt: datetime = None

        self.bg: BarGenerator = BarGenerator(
            on_bar=self.on_bar,
            window=1,
            on_window_bar=self.on_window_bar,
            interval=Interval.MINUTE
        )

        self.am: ArrayManager = ArrayManager()

        self.load_bar(10, Interval.MINUTE)
        
        self.write_log("Strategy is inited.")


    def on_start(self) -> None:
        self.write_log("Strategy is started")


    def on_stop(self) -> None:
        self.write_log("Strategy is stopped")


    def on_tick(self, tick: TickData) -> None:
        self.bg.update_tick(tick)


    def on_bar(self, bar: BarData) -> None:
        self.bg.update_bar(bar)


    def on_window_bar(self, bar: BarData) -> None:
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self.fast_ma = self.am.sma(self.fast_window)
        self.slow_ma = self.am.sma(self.slow_window)

        if self.fast_ma > self.slow_ma:
            self.trading_target = self.trading_size # 多开
        else:
            self.trading_target = -self.trading_size # 空开

        trading_volume: int = self.trading_target - self.trading_pos

        if trading_volume > 0:
            self.buy(self.trading_symbol, bar.close_price * 1.01, abs(trading_volume))
        else:
            self.short(self.trading_symbol, bar.close_price * 0.99, abs(trading_volume))


    def on_trade(self, trade: TradeData) -> None:
        pass


    def on_order(self, order: OrderData) -> None:
        pass