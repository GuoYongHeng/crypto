from datetime import datetime
from time import sleep
from zoneinfo import ZoneInfo

from vnpy.trader.database import get_database

from vnpy.event import EventEngine
from vnpy.trader.object import HistoryRequest
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.event import EVENT_LOG

from vnpy_binance import BinanceSpotGateway

def output_log(event):
    log = event.data
    print(log.time, log.msg)


if __name__ == "__main__":
    ee = EventEngine()
    ee.register(EVENT_LOG, output_log)
    ee.start()

    setting = {
        "API Key": "",
        "API Secret": "",
        "Server": "REAL",
        "Kline Stream": "True",
        "Proxy Host": "127.0.0.1",
        "Proxy Port": 7890
    }

    gateway = BinanceSpotGateway(ee, BinanceSpotGateway.default_name)
    gateway.connect(setting)

    sleep(10)

    req = HistoryRequest(
        symbol="BTCUSDT",
        exchange=Exchange.BINANCE,
        interval=Interval.MINUTE,
        start=datetime(2022, 1, 1, tzinfo=ZoneInfo('Asia/Shanghai')),
        end=datetime(2023, 1, 1, tzinfo=ZoneInfo('Asia/Shanghai'))
    )
    bars = gateway.query_history(req)
    
    for bar in bars:
        del bar.extra

    print(bars[0])
    print(bars[-1])

    db = get_database()
    db.save_bar_data(bars)
    print("Saved", len(bars))

    gateway.close()
    ee.stop()

#reference:https://github.com/veighna-global/vnpy_novastrategy/blob/main/examples/sma_strategy/download_data.py