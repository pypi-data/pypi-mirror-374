import asyncio
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    sys.path.append("/Users/kaihock/Desktop/All In/Xecution")
import asyncio
from pathlib import Path
from urllib.parse import parse_qs
import pandas as pd
import logging
from xecution.core.engine import BaseEngine
from xecution.common.enums import DataProvider, Exchange, KlineType, Mode, Symbol
from xecution.models.config import RuntimeConfig
from xecution.models.topic import DataTopic, KlineTopic
from xecution.utils.logger import Logger
from xecution.utils.utility import (
    to_camel,
    split_exchange_category,
    symbol_str,
    write_csv_overwrite,
    append_rows_csv,
    extract_first_key,
    OPEN_TIME_KEYS,
    last_closed_log_line,
)
import numpy as np

# --------------------------------------------------------------------
candle_path1 = Path("data/candle/binance_kline_btc_1h.csv") # candle data file path
# --------------------------------------------------------------------

DATASOURCE_PATH = Path("data/datasource")
CANDLE_PATH = Path("data/candle")
KLINE_FUTURES = KlineTopic(klineType=KlineType.Coinbase_Spot, symbol=Symbol.BTCUSD, timeframe="1h")
KLINE_SPOT = KlineTopic(klineType=KlineType.Binance_Spot, symbol=Symbol.BTCUSDT, timeframe="1h")
BINANCE_FUTURES = KlineTopic(klineType=KlineType.Binance_Futures, symbol=Symbol.BTCUSDT, timeframe="1h")

Data1  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/market-data/coinbase-premium-index?window=hour&exchange=binance')
Data2  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/market-data/funding-rates?window=hour&exchange=binance')
Data3  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/exchange-flows/reserve?exchange=binance&window=hour')
Data4  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/exchange-flows/netflow?window=hour&exchange=binance')
Data5  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/exchange-flows/transactions-count?window=hour&exchange=binance')
Data6  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/exchange-flows/in-house-flow?exchange=binance&window=hour')
Data7  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/flow-indicator/exchange-shutdown-index?exchange=binance&window=hour')
Data8  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/flow-indicator/exchange-inflow-age-distribution?exchange=binance&window=hour')
Data9  = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/flow-indicator/exchange-inflow-cdd?window=hour&exchange=binance')
Data10 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/flow-indicator/exchange-supply-ratio?window=hour&exchange=binance')
Data11 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/flow-indicator/miner-supply-ratio?miner=f2pool&window=hour')
Data12 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/market-indicator/utxo-realized-price-age-distribution?window=hour&exchange=binance')
Data13 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/stock-to-flow?window=hour')
Data14 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/nrpl?window=hour')
Data15 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/utxo-age-distribution?window=hour')
Data16 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/spent-output-age-distribution?window=hour')
Data17 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/utxo-supply-distribution?window=hour')
Data18 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/utxo-realized-supply-distribution?window=hour')
Data19 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/utxo-count-supply-distribution?window=hour')
Data20 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-indicator/spent-output-supply-distribution?window=hour')
Data21 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/miner-flows/reserve?miner=f2pool&window=hour')
Data22 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/miner-flows/netflow?miner=f2pool&window=hour')
Data23 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/miner-flows/transactions-count?miner=f2pool&window=hour')
Data24 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/miner-flows/addresses-count?miner=f2pool&window=hour')
Data25 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/miner-flows/in-house-flow?miner=f2pool&window=hour')
Data26 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/inter-entity-flows/exchange-to-exchange?from_exchange=binance&to_exchange=bithumb&window=hour')
Data27 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/inter-entity-flows/miner-to-exchange?from_miner=f2pool&to_exchange=binance&window=hour')
Data28 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/inter-entity-flows/bank-to-exchange?from_bank=blockfi&to_exchange=binance&window=hour')
Data29 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/inter-entity-flows/exchange-to-miner?from_exchange=binance&to_miner=f2pool&window=hour')
Data30 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/inter-entity-flows/miner-to-miner?from_miner=f2pool&to_miner=antpool&window=hour')
Data31 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/inter-entity-flows/bank-to-miner?from_bank=blockfi&to_miner=f2pool&window=hour')
Data32 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/inter-entity-flows/exchange-to-bank?from_exchange=binance&to_bank=blockfi&window=hour')
Data33 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/market-data/taker-buy-sell-stats?window=hour&exchange=binance')
Data34 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/market-data/liquidations?window=hour&exchange=binance')
Data35 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/supply?window=hour')
Data36 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/velocity?window=hour')
Data37 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/transactions-count?window=hour')
Data38 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/addresses-count?window=hour')
Data39 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/tokens-transferred?window=hour')
Data40 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/block-bytes?window=hour')
Data41 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/block-count?window=hour')
Data42 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/block-interval?window=hour')
Data43 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/utxo-count?window=hour')
Data44 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/fees?window=hour')
Data45 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/fees-transaction?window=hour')
Data46 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/blockreward?window=hour')
Data47 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/difficulty?window=hour')
Data48 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/network-data/hashrate?window=hour')
Data49 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/flow-indicator/stablecoins-ratio?exchange=binance&window=hour')
Data50 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/flow-indicator/exchange-whale-ratio?exchange=binance&window=hour')

# Enable logging to see real-time data
class Engine(BaseEngine):
    """Base engine that initializes BinanceService and processes on_candle_closed and on_datasource_update."""
    def __init__(self, config):
        Logger(log_file="data_retrieval.log", log_level=logging.INFO)
        super().__init__(config)

    async def on_datasource_update(self, datasource_topic):
        """
        Saves CryptoQuant (or similar) datasource to CSV:
          {SYMBOL}_Cryptoquant-{CategoryCamel}-{EndpointCamel}-{interval}.csv
        Example: BTC_Cryptoquant-MarketData-CoinbasePremiumIndex-1h.csv
        """
        data = self.data_map.get(datasource_topic, [])
        logging.info(f"Data Incoming: {datasource_topic} (len={len(data)})")

        # strip any leading slash, split off params
        path, _, query = datasource_topic.url.lstrip("/").partition("?")

        # 1) symbol is the first segment of the path
        symbol = path.split("/", 1)[0].upper()  # e.g. "BTC"

        # 2) endpoint slug is the last segment
        endpoint = path.rsplit("/", 1)[-1]  # e.g. "coinbase-premium-index"
        camel_endpoint = to_camel(endpoint)

        # 3) category is the middle segment
        #    path looks like "btc/market-data/coinbase-premium-index"
        category_slug = path.split("/", 2)[1]  # e.g. "market-data"
        category_camel = to_camel(category_slug)

        # 4) derive interval (e.g. "hour" → "1h")
        params = parse_qs(query)
        window = params.get("window", ["hour"])[0]
        interval = {"hour": "1h", "day": "1d"}.get(window, window)

        filename = f"{symbol}_Cryptoquant-{category_camel}-{camel_endpoint}-{interval}.csv"
        out_path = DATASOURCE_PATH / filename

        try:
            write_csv_overwrite(out_path, data)
            logging.info(f"Saved {datasource_topic.url} → {out_path}")
        except Exception as e:
            logging.exception(f"Failed to save datasource to {out_path}: {e}")

    # ───────────────────────── candle saver ─────────────────────────

    async def on_candle_closed(self, kline_topic):
        """
        Handles closed candle data and auto-saves to:
          {Exchange}-{Category}_{SYMBOL}_Kline-{timeframe}.csv
        Examples:
          Coinbase-Spot_BTCUSD_Kline-1m.csv
          Binance-Spot_BTCUSDT_Kline-1h.csv
        Behavior: appends ONLY the last closed bar.
        """
        candles = self.data_map.get(kline_topic, [])
        if not candles:
            logging.warning(f"No candles for {kline_topic}")
            return

        last = candles[-1]

        # Try to get the bar's open/start time (ms) for human-readable logging
        start_ms = extract_first_key(last, OPEN_TIME_KEYS)
        try:
            # If you have your own ms→datetime util, call it here.
            # Falling back to pandas for robust conversion without extra deps.
            human_time = str(pd.to_datetime(start_ms, unit="ms", utc=True)) if start_ms is not None else "N/A"
        except Exception:
            human_time = str(start_ms)

        symbol = symbol_str(kline_topic.symbol)
        exchange, category = split_exchange_category(kline_topic.klineType)
        interval = kline_topic.timeframe  # e.g. "1m", "1h", "1d"

        # Filename with EXCHANGE first (as requested)
        filename = f"{exchange}-{category}_{symbol}_Kline-{interval}.csv"
        out_path = CANDLE_PATH / filename

        logging.info(last_closed_log_line(symbol, interval, last, human_time))

        # Append just the last closed candle
        try:
            append_rows_csv(out_path, candles)
            logging.info(f"Saved kline → {out_path}")
        except Exception as e:
            logging.exception(f"Failed to save kline to {out_path}: {e}")

engine = Engine(
    RuntimeConfig(
        mode= Mode.Backtest,
        kline_topic=[
            KLINE_FUTURES,
            KLINE_SPOT,
            BINANCE_FUTURES
        ],
        datasource_topic=[
        Data1,Data2,Data3,Data4,Data5,Data6,Data7,Data8,Data9,Data10,
        # Data11,Data12,Data13,Data14,Data15,Data16,Data17,Data18,Data19,Data20,
        # Data21,Data22,Data23,Data24,Data25,Data26,Data27,Data28,Data29,Data30,
        # Data31,Data32,Data33,Data34,Data35,Data36,Data37,Data38,Data39,Data40,       
        # Data41,Data42,Data43,Data44,Data45,Data46,Data47,Data48,Data49,Data50,
        ],
        data_count=2000,
        exchange=Exchange.Binance,
        API_Key="ge5t5e7PyJNPxeYXSjDaEKv3ZedDgKANPONdqg7uiqqw94Yqrpv46A57UbMP6BST",
        API_Secret="jLavX4rfnhXNoo0jVECUsPEOZFy0nPIE2VOgGSzas3KFXLSHEmLYWoFzpkTxurYr",
        cryptoquant_api_key="iG48lac3kRFcFq0q5WMm0BpnTt1XYMvRB6yz63OP"
    )
)

asyncio.run(engine.start())

