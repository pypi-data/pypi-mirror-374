# -*- coding: utf-8 -*-
import asyncio
import json
import logging
from datetime import datetime, timezone

from xecution.common.enums import KlineType, Mode
from xecution.models.config import RuntimeConfig
from xecution.models.topic import KlineTopic
from xecution.services.connection.base_websockets import WebSocketService
from xecution.services.exchange.coinbase_helper import CoinbaseHelper


class CoinbaseService:
    """
    Coinbase Spot listener: WebSocket is a signal, REST is the source of truth.
    - WS (advanced-trade) "candles" channel used only as heartbeat.
    - On each local bucket close (based on timeframe), confirm via REST, then refresh self.data_map.
    """

    # timeframe -> milliseconds
    INTERVAL_TO_MS = {
        "1m": 60_000,
        "5m": 5 * 60_000,
        "15m": 15 * 60_000,
        "30m": 30 * 60_000,
        "1h": 60 * 60_000,
        "2h": 2 * 60 * 60_000,
        "4h": 4 * 60 * 60_000,
        "6h": 6 * 60 * 60_000,
        "1d": 24 * 60 * 60_000,
    }

    def __init__(self, config: RuntimeConfig, data_map: dict):
        """
        config: RuntimeConfig
        data_map: external dict to store kline arrays per topic (like your Binance service)
        """
        self.config = config
        self.coinbaseHelper = CoinbaseHelper(config)
        self.ws_service = WebSocketService()
        self.data_map = data_map
        self._last_bucket_end = {}

    @staticmethod
    def _ws_url() -> str:
        # Advanced Trade Market Data WS for spot
        return "wss://advanced-trade-ws.coinbase.com"

    @staticmethod
    def _subscription_message(kline_topic: KlineTopic) -> dict:
        """
        Advanced Trade spot candles channel.
        Normalize product_id so you can pass 'BTCUSDT' but subscribe to 'BTC-USD'.
        """
        product_id = CoinbaseHelper._normalize_product_id(kline_topic.symbol.value)  # e.g., "BTC-USD"
        return {
            "type": "subscribe",
            "channel": "candles",
            "product_ids": [product_id],
        }

    def _bucket_end_ms(self, now_ms: int, tf_key: str) -> int:
        size = self.INTERVAL_TO_MS.get(tf_key, 60_000)
        return (now_ms // size) * size

    async def get_klines(self, kline_topic: KlineTopic, on_candle_closed):
        """
        Retrieve klines depending on mode:
          - Backtest: one-shot REST pull into data_map and trigger callback
          - Live/Testnet: run the WS listener that confirms each closed candle via REST
        """
        if self.config.mode == Mode.Backtest:
            candles = await self.coinbaseHelper.getKlineRestAPI(kline_topic)
            self.data_map[kline_topic] = candles
            await on_candle_closed(kline_topic)
        elif self.config.mode in (Mode.Live, Mode.Testnet):
            await self.listen_kline(on_candle_closed, kline_topic)

    async def listen_kline(self, on_candle_closed, kline_topic: KlineTopic):
        """
        Subscribe to Coinbase SPOT WS and, on each timeframe boundary,
        confirm via REST and refresh data_map[kline_topic], then fire on_candle_closed.
        """
        try:
            if kline_topic.klineType != KlineType.Coinbase_Spot:
                logging.error("[CoinbaseService] kline_topic.klineType must be Coinbase_Spot")
                return

            tf = kline_topic.timeframe.lower()
            if tf not in self.INTERVAL_TO_MS:
                logging.error(f"[CoinbaseService] Unsupported timeframe: {tf}")
                return

            ws_url = self._ws_url()
            sub_msg = self._subscription_message(kline_topic)
            norm_prod = CoinbaseHelper._normalize_product_id(kline_topic.symbol.value)

            # init per-topic state
            self.data_map[kline_topic] = []
            self._last_bucket_end[kline_topic] = None

            # Preload a window so consumers aren’t empty before first close
            try:
                now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
                preload_bucket_end = self._bucket_end_ms(now_ms, tf)
                self.data_map[kline_topic] = await self.coinbaseHelper.getKlineRestAPI(
                    kline_topic, end_time=preload_bucket_end
                )
                self._last_bucket_end[kline_topic] = preload_bucket_end
                logging.info(
                    f"[CoinbaseService] Preloaded candles for {norm_prod} {tf} up to {preload_bucket_end}"
                )
            except Exception as e:
                logging.warning(f"[CoinbaseService] Preload failed: {e}")

            async def message_handler(exchange_name, message: dict):
                """
                Any WS tick is used as a heartbeat.
                On new bucket close: poll REST for latest 2 bars until the closed bar appears,
                then backfill a full window (getKlineRestAPI) ending exactly at bucket_end.
                """
                try:
                    interval_ms = self.INTERVAL_TO_MS.get(tf, 60_000)

                    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
                    bucket_end = self._bucket_end_ms(now_ms, tf)

                    # Only once per bucket
                    last_end = self._last_bucket_end.get(kline_topic)
                    if last_end is not None and bucket_end <= last_end:
                        return

                    # Grace so Coinbase finalizes the bar
                    await asyncio.sleep(0.15)  # 100–300 ms typical

                    expected_start = bucket_end - interval_ms

                    # Poll REST until the closed candle appears (bounded)
                    retries, max_retries = 0, 12
                    poll_sleep = 0.20  # seconds

                    while retries < max_retries:
                        recent = await self.coinbaseHelper.getLatestKline(kline_topic)
                        if recent and any(c["start_time"] == expected_start for c in recent):
                            # Refresh full window ending exactly at this bucket end
                            self.data_map[kline_topic] = await self.coinbaseHelper.getKlineRestAPI(
                                kline_topic, end_time=bucket_end
                            )
                            self._last_bucket_end[kline_topic] = bucket_end

                            logging.debug(
                                f"[{exchange_name}] Candle closed | "
                                f"{kline_topic.klineType.name}-{norm_prod}-{kline_topic.timeframe}"
                            )
                            await on_candle_closed(kline_topic)
                            break

                        retries += 1
                        await asyncio.sleep(poll_sleep)

                    if retries >= max_retries:
                        logging.warning(
                            f"[{exchange_name}] Timed out waiting for closed {norm_prod} {kline_topic.timeframe} candle (spot)"
                        )

                except Exception as e:
                    logging.error(f"[CoinbaseService] on_candle_closed failed: {e}")

            # Use your shared WebSocketService
            exchange_name = f"COINBASE-SPOT-{norm_prod}-{kline_topic.timeframe}"
            logging.debug(f"[CoinbaseService] Connecting to WebSocket: {ws_url}")
            await self.ws_service.subscribe(exchange_name, ws_url, sub_msg, message_handler)
            logging.info(
                f"[CoinbaseService] Subscribed to {kline_topic.klineType.name}-{norm_prod}-{kline_topic.timeframe}"
            )

        except Exception as e:
            logging.error(f"[CoinbaseService] listen_kline failed: {e}")
