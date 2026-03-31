"""
data_loader.py — Fetch and cache historical price data from Yahoo Finance.

Uses a module-level dict to avoid re-fetching on every callback.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Module-level cache: key = frozenset(tickers) + period → DataFrame
_cache: dict[str, pd.DataFrame] = {}

DEFAULT_TICKERS = ["AAPL", "MSFT", "JNJ", "JPM", "XOM"]
BENCHMARK = "SPY"

PERIOD_MAP = {
    "1Y": 365,
    "3Y": 365 * 3,
    "5Y": 365 * 5,
}


def fetch_prices(
    tickers: list[str],
    period: str = "3Y",
    include_benchmark: bool = True,
) -> pd.DataFrame:
    """
    Download adjusted close prices for the given tickers (+ benchmark).

    Returns a DataFrame indexed by date with one column per ticker.
    Results are cached in memory.
    """
    all_tickers = list(tickers)
    if include_benchmark and BENCHMARK not in all_tickers:
        all_tickers.append(BENCHMARK)

    cache_key = f"{sorted(all_tickers)}_{period}"
    if cache_key in _cache:
        return _cache[cache_key]

    days = PERIOD_MAP.get(period, 365 * 3)
    end = datetime.today()
    start = end - timedelta(days=days)

    df = yf.download(
        all_tickers,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
    )

    # yf.download returns MultiIndex columns when >1 ticker
    if isinstance(df.columns, pd.MultiIndex):
        prices = df["Close"]
    else:
        prices = df[["Close"]].rename(columns={"Close": all_tickers[0]})

    prices = prices.dropna()
    _cache[cache_key] = prices
    return prices


def clear_cache():
    """Clear the in-memory price cache."""
    _cache.clear()
