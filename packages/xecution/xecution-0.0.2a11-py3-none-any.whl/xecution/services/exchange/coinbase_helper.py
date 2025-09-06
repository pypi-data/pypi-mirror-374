# -*- coding: utf-8 -*-
import logging
import aiohttp
from typing import Optional, List, Dict
from datetime import datetime, timezone

from xecution.common.enums import KlineType, Mode
from xecution.common.exchange.live_constants import LiveConstants
from xecution.common.exchange.testnet_constants import TestnetConstants
from xecution.models.topic import KlineTopic
from xecution.models.config import RuntimeConfig

# Import your downloader
from .safe_kline_downloader import SafeKlineDownloader


class CoinbaseHelper:
    """
    Coinbase spot (Advanced Trade) candles helper — optimized with SafeKlineDownloader.

    Public REST endpoint (no auth required):
      GET {base}/api/v3/brokerage/market/products/{product_id}/candles
      params:
        start (UNIX seconds), end (UNIX seconds),
        granularity ∈ {ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, THIRTY_MINUTE,
                       ONE_HOUR, TWO_HOUR, FOUR_HOUR, SIX_HOUR, ONE_DAY},
        limit ≤ 350

    We adapt downloader params (Binance-like: endTime/startTime, interval, limit)
    to Coinbase query, then return **Binance-style arrays** so the downloader’s
    reverse-paging logic works unchanged:

      [openTime(ms), open, high, low, close, volume, closeTime(ms)]
    """

    def __init__(self, config: RuntimeConfig):
        self.config = config

    # ───────────────────────── intervals ─────────────────────────

    interval_to_ms: Dict[str, int] = {
        "1m": 60 * 1000,
        "5m": 5 * 60 * 1000,
        "15m": 15 * 60 * 1000,
        "30m": 30 * 60 * 1000,
        "1h": 60 * 60 * 1000,
        "2h": 2 * 60 * 60 * 1000,
        "4h": 4 * 60 * 60 * 1000,
        "6h": 6 * 60 * 60 * 1000,
        "1d": 24 * 60 * 60 * 1000,
    }

    interval_to_cb_enum: Dict[str, str] = {
        "1m": "ONE_MINUTE",
        "5m": "FIVE_MINUTE",
        "15m": "FIFTEEN_MINUTE",
        "30m": "THIRTY_MINUTE",
        "1h": "ONE_HOUR",
        "2h": "TWO_HOUR",
        "4h": "FOUR_HOUR",
        "6h": "SIX_HOUR",
        "1d": "ONE_DAY",
    }

    # ───────────────────────── URLs & product IDs ─────────────────────────

    @staticmethod
    def get_restapi_base_url(kline_topic: KlineTopic, mode: Mode) -> str:
        """Spot only; fallback protects if constants missing."""
        try:
            base = TestnetConstants.Coinbase if mode == Mode.Testnet else LiveConstants.Coinbase
            return getattr(base, "RESTAPI_SPOT_URL", "https://api.coinbase.com")
        except Exception:
            return "https://api.coinbase.com"

    @staticmethod
    def _normalize_product_id(symbol_value: str) -> str:
        """
        Map common Binance-like symbols to Coinbase product_id format.
        'BTCUSDT' -> 'BTC-USD', 'ETHUSD' -> 'ETH-USD'. Keep dashed as-is.
        """
        s = symbol_value.upper()
        if "-" in s:
            return s
        QUOTES = ("USD", "USDC", "EUR", "GBP")
        for q in QUOTES:
            if s.endswith(q):
                base = s[:-len(q)]
                return f"{base}-{q}"
        return s

    # ───────────────────────── converters ─────────────────────────

    @staticmethod
    def _safe_f(x) -> float:
        try:
            return float(x)
        except Exception:
            return float("nan")

    @staticmethod
    def convert_rest_kline(row: list) -> dict:
        """
        Convert a Binance-like array row into unified dict.
        row = [openTime, open, high, low, close, volume, closeTime]
        """
        try:
            return {
                "start_time": int(row[0]),
                "end_time":   int(row[6]),
                "open":       float(row[1]),
                "high":       float(row[2]),
                "low":        float(row[3]),
                "close":      float(row[4]),
                "volume":     float(row[5]),
            }
        except Exception:
            logging.exception(f"Failed to convert REST kline array: {row}")
            return {}

    # ───────────────────────── downloader fetch wrapper ─────────────────────────

    async def fetch_kline(self, session, endpoint: str, dl_params: dict):
        """
        Adapter for SafeKlineDownloader:
          dl_params includes: 'interval', 'limit', and either 'endTime' or 'startTime' (ms)
        We convert to Coinbase query, call REST, then return **array rows**.
        """
        try:
            interval = dl_params.get("interval", "1m")
            limit = int(dl_params.get("limit", 100))
            limit = max(1, min(350, limit))  # Coinbase hard cap

            gran = self.interval_to_cb_enum.get(interval, "ONE_MINUTE")
            step_ms = self.interval_to_ms.get(interval, 60_000)

            # Determine start/end in ms
            if "endTime" in dl_params:
                end_ms = int(dl_params["endTime"])
                start_ms = end_ms - limit * step_ms
            elif "startTime" in dl_params:
                start_ms = int(dl_params["startTime"])
                end_ms = start_ms + limit * step_ms
            else:
                # fallback: last 'limit' bars ending now
                end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
                start_ms = end_ms - limit * step_ms

            params = {
                "granularity": gran,
                "start": str(start_ms // 1000),
                "end": str(end_ms // 1000),
                "limit": str(limit),
            }

            async with session.get(endpoint, params=params) as resp:
                if resp.status != 200:
                    txt = await resp.text()
                    logging.error(f"[CoinbaseHelper.fetch_kline] HTTP {resp.status}: {txt}")
                    return []

                data = await resp.json()
                candles = data.get("candles", []) or []
                # Ensure oldest→newest
                candles.sort(key=lambda r: int(r.get("start", "0")))

                # Convert to Binance-like array rows for the downloader
                rows = []
                for c in candles:
                    start_s = int(c["start"])
                    start_ms = start_s * 1000
                    close_ms = start_ms + step_ms
                    rows.append([
                        start_ms,
                        self._safe_f(c.get("open")),
                        self._safe_f(c.get("high")),
                        self._safe_f(c.get("low")),
                        self._safe_f(c.get("close")),
                        self._safe_f(c.get("volume")),
                        close_ms
                    ])
                return rows

        except Exception as e:
            logging.exception(f"[CoinbaseHelper.fetch_kline] unexpected error: {e}")
            return []

    # ───────────────────────── public APIs ─────────────────────────

    async def getKlineRestAPI(self, kline_topic: KlineType, end_time: Optional[int] = None) -> List[dict]:
        """
        Use SafeKlineDownloader.download_reverse to fetch fast, then convert to unified dicts.
        Drops the first 5 bars as warm-up (to mirror your Binance behavior).
        """
        try:
            if kline_topic.klineType != KlineType.Coinbase_Spot:
                logging.error("[CoinbaseHelper] getKlineRestAPI called with non-spot KlineType.")
                return []

            base_url = self.get_restapi_base_url(kline_topic, self.config.mode)
            product_id = self._normalize_product_id(kline_topic.symbol.value)  # e.g., BTC-USD
            interval = kline_topic.timeframe.lower()
            time_increment = self.interval_to_ms.get(interval, 60_000)
            total_needed = int(getattr(self.config, "data_count", 500))

            endpoint = f"{base_url}/api/v3/brokerage/market/products/{product_id}/candles"

            # default end_time: now (ms)
            if end_time is None:
                end_time = int(datetime.now(timezone.utc).timestamp() * 1000)

            # public market endpoint → no auth header needed
            async with aiohttp.ClientSession() as session:
                downloader = SafeKlineDownloader(
                    session=session,
                    fetch_func=self.fetch_kline,        # <— our adapter
                    endpoint=endpoint,
                    symbol=product_id,                  # ignored by adapter (but kept for logs)
                    interval=interval,                  # "1m", "5m", ...
                    max_limit=350,                      # Coinbase cap
                    time_increment_ms=time_increment,
                    max_concurrent_requests=10,
                    chunk_sleep=0
                )

                bins_rows = await downloader.download_reverse(end_time=end_time, total_needed=total_needed)
                # Convert Binance-like rows to unified dicts
                converted = [self.convert_rest_kline(r) for r in bins_rows]
                # Drop first 5 as warm-up
                return converted[5:]

        except Exception as e:
            logging.error(f"[CoinbaseHelper] getKlineRestAPI failed: {e}")
            return []

    async def getLatestKline(self, kline_topic: KlineType):
        """
        Fetch the latest 2 spot candles for confirmation logic (WS → REST), no downloader needed.
        """
        try:
            if kline_topic.klineType != KlineType.Coinbase_Spot:
                logging.error("[CoinbaseHelper] getLatestKline called with non-spot KlineType.")
                return None

            base_url = self.get_restapi_base_url(kline_topic, self.config.mode)
            product_id = self._normalize_product_id(kline_topic.symbol.value)
            interval = kline_topic.timeframe.lower()
            gran = self.interval_to_cb_enum.get(interval, "ONE_MINUTE")
            step_ms = self.interval_to_ms.get(interval, 60_000)

            endpoint = f"{base_url}/api/v3/brokerage/market/products/{product_id}/candles"

            now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
            start_ms = now_ms - 2 * step_ms

            params = {
                "granularity": gran,
                "start": str(start_ms // 1000),
                "end": str(now_ms // 1000),
                "limit": "2",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params) as resp:
                    if resp.status != 200:
                        txt = await resp.text()
                        logging.error(f"[CoinbaseHelper] HTTP {resp.status}: {txt}")
                        return None
                    data = await resp.json()
                    candles = data.get("candles", []) or []
                    if not candles:
                        logging.warning(f"[CoinbaseHelper] No latest kline for {product_id}")
                        return None

                    candles.sort(key=lambda r: int(r.get("start", "0")))
                    # Convert to unified dicts directly
                    latest = []
                    for c in candles[-2:]:
                        s_ms = int(c["start"]) * 1000
                        latest.append({
                            "start_time": s_ms,
                            "end_time":   s_ms + step_ms,
                            "open":       self._safe_f(c.get("open")),
                            "high":       self._safe_f(c.get("high")),
                            "low":        self._safe_f(c.get("low")),
                            "close":      self._safe_f(c.get("close")),
                            "volume":     self._safe_f(c.get("volume")),
                        })
                    return latest

        except Exception as e:
            logging.error(f"[CoinbaseHelper] getLatestKline failed: {e}")
            return None
