from strategies.fix_trade_price_strategy import FixedTradeTimeStrategy
from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy.trader.constant import Interval
from datetime import datetime
import plotly.graph_objects as go


if __name__ == "__main__":
    engine = BacktestingEngine()

    engine.set_parameters(
        vt_symbol="BTC/USDT.BINANCE",
        interval=Interval.MINUTE,
        start=datetime(2024,1,2),
        end=datetime(2024,3,2),
        rate=1/1000,
        slippage=0,
        size=1,
        pricetick=0.01,
        capital=300000
    )

    engine.add_strategy(FixedTradeTimeStrategy, {})
    engine.load_data()
    engine.run_backtesting()
    fig:go.Figure = engine.show_chart()