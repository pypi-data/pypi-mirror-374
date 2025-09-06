# Lightweight helpers for kline/datasource saving.
from __future__ import annotations
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import pandas as pd


# ───────────────────────── name helpers ─────────────────────────

def to_camel(slug: str) -> str:
    """'coinbase-premium-index' -> 'CoinbasePremiumIndex' (safe for -, _, .)."""
    return "".join(part.title() for part in str(slug).replace(".", "_").replace("-", "_").split("_") if part)

def enum_name(x: Any) -> str:
    """Return Enum.name if present; otherwise a reasonable short string."""
    if hasattr(x, "name"):
        return x.name
    s = str(x)
    if "." in s and not s.endswith(">"):
        # e.g. 'KlineType.Binance_Spot'
        return s.split(".", 1)[1]
    if s.startswith("<") and ":" in s:
        # e.g. '<KlineType.Binance_Spot: 1>'
        core = s.split(":", 1)[0].rstrip(">").rsplit(".", 1)[-1]
        return core
    return s

def split_exchange_category(kline_type: Any) -> tuple[str, str]:
    """
    From KlineType like 'Binance_Spot' -> ('Binance', 'Spot').
    Falls back gracefully if underscore not present.
    """
    raw = enum_name(kline_type)
    left, _, right = raw.partition("_")
    exchange = to_camel(left or "Unknown")
    category = to_camel(right or "Spot")
    return exchange, category

def symbol_str(symbol: Any) -> str:
    """Enum Symbol.BTCUSDT -> 'BTCUSDT', else str cleaned of module prefix."""
    if hasattr(symbol, "name"):
        return symbol.name
    s = str(symbol)
    return s.split(".", 1)[-1] if "." in s else s


# ───────────────────────── file helpers ─────────────────────────

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def write_csv_overwrite(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    """Overwrite CSV with given rows."""
    ensure_parent(path)
    pd.DataFrame(rows).to_csv(path, index=False)

def append_rows_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    """
    Append rows to CSV, writing a header only when file does not exist.
    Accepts any mappable row objects.
    """
    ensure_parent(path)
    df = pd.DataFrame(rows)
    write_header = not path.exists()
    df.to_csv(path, index=False, mode="a", header=write_header)


# ───────────────────────── candle helpers ─────────────────────────

# Common vendor key aliases for candles (be tolerant)
CLOSE_KEYS = ("close", "c", "Close")
OPEN_TIME_KEYS = ("start_time", "t", "open_time", "T")

def extract_first_key(d: Mapping[str, Any], keys: Iterable[str]) -> Any:
    for k in keys:
        if k in d:
            return d[k]
    return None

def last_closed_log_line(symbol: str, timeframe: str, last_bar: Mapping[str, Any], human_time: str) -> str:
    close_val = extract_first_key(last_bar, CLOSE_KEYS)
    return f"Last Kline Closed | {symbol}-{timeframe} | Close: {close_val} | Time: {human_time}"

