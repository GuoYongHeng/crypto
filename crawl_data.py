import ccxt
import pytz
from datetime import datetime
from vnpy.trader.database import get_database, BaseDatabase
from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange,Interval

def date_to_timestamp(date_str):
    # 将日期字符串转为datetime对象
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
    except:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    # 设置为UTC时区
    dt = pytz.timezone('UTC').localize(dt)
    # 转换为时间戳(毫秒)
    return int(dt.timestamp() * 1000)


def generate_datetime(timestamp : float):
    dt = datetime.fromtimestamp(timestamp / 1000)
    dt = pytz.timezone("Asia/Shanghai").localize(dt)
    return dt


def main():
    exchange = ccxt.binance()
    proxy = "http://127.0.0.1:7890"
    exchange.httpsProxy = proxy

    start_date = '2024-04-01'
    end_date = '2024-08-01'

    start_ts = date_to_timestamp(start_date)
    end_ts = date_to_timestamp(end_date)
    current_ts = start_ts
    symbol = "BTC/USDT"
    timeframe = "1m"

    db:BaseDatabase = get_database()

    while current_ts < end_ts:
        klines = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=current_ts,
            limit=1000
        )
        buf = []
        for row in klines:
            bar:BarData = BarData(
                gateway_name="BINANCE_SPOT",
                symbol=symbol,
                exchange=Exchange.BINANCE,
                datetime=generate_datetime(row[0]),
                interval=Interval.MINUTE,
                volume=row[5],
                open_price=row[1],
                high_price=row[2],
                low_price=row[3],
                close_price=row[4]
            )
            buf.append(bar)
        db.save_bar_data(buf)
        current_ts = klines[-1][0]
        print(generate_datetime(current_ts))



if __name__ == "__main__":
    main()