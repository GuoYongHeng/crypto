import multiprocessing
import sys
import os
from time import sleep
from datetime import datetime, time
from logging import INFO

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine

from vnpy.trader.setting import SETTINGS

from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctastrategy.base import EVENT_CTA_LOG
from vnpy_ctastrategy.engine import CtaEngine
from vnpy_binance import BinanceSpotGateway

from pathlib import Path


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True


binance_settings = {
    "API Key": "*",
    "API Secret": "*",
    "Server": "TESTNET",
    "Kline Stream": "False",
    "Proxy Host": "127.0.0.1",
    "Proxy Port": 7890
}

def main():

    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(BinanceSpotGateway)
    cta_engine : CtaEngine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    main_engine.connect(binance_settings, "BINANCE_SPOT")
    main_engine.write_log("连接BINANCE接口")

    sleep(10)
    cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    sleep(30)   # Leave enough time to complete strategy initialization
    main_engine.write_log("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")

    while True:
        sleep(10)



if __name__ == "__main__":
    main()