"""
data_loader.py — Yahoo Finance data retrieval and caching.

Pulls adjusted close prices via yfinance and caches them in a module-level
dictionary so repeated Dash callbacks don't trigger redundant API calls.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Module-level cache: keyed by a frozenset of (tickers, lookback_years) so
# the same request is never fetched twice in a single server process.
# ---------------------------------------------------------------------------
_cache: dict[str, pd.DataFrame] = {}

# Default universe — SPY serves double duty as a holding *and* benchmark.
DEFAULT_TICKERS = ["AAPL", "MSFT", "JNJ", "JPM", "XOM", "SPY"]
DEFAULT_LOOKBACK_YEARS = 3
BENCHMARK = "SPY"


def _cache_key(tickers: list[str], lookback_years: int) -> str:
    """Build a deterministic cache key from tickers + lookback."""
    return f"{','.join(sorted(tickers))}|{lookback_years}"


def fetch_prices(
    tickers: list[str] | None = None,
    lookback_years: int = DEFAULT_LOOKBACK_YEARS,
    force: bool = False,
) -> pd.DataFrame:
    """
    Return a DataFrame of adjusted close prices (columns = tickers, index = date).

    Parameters
    ----------
    tickers : list[str]
        Symbols to download. Defaults to DEFAULT_TICKERS.
    lookback_years : int
        How many years of history to pull. Defaults to 3.
    force : bool
        If True, bypass the cache and re-download.

    Returns
    -------
    pd.DataFrame
        Adjusted close prices, forward-filled then back-filled to handle
        minor gaps (holidays across exchanges).
    """
    tickers = tickers or DEFAULT_TICKERS
    # Always include the benchmark so we can compare against it.
    if BENCHMARK not in tickers:
        tickers = tickers + [BENCHMARK]

    key = _cache_key(tickers, lookback_years)

    if not force and key in _cache:
        return _cache[key]

    end = datetime.today()
    start = end - timedelta(days=lookback_years * 365)

    # yfinance returns a MultiIndex DataFrame when >1 ticker is requested.
    raw = yf.download(
        tickers,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        auto_adjust=True,   # gives adjusted prices directly in "Close"
        progress=False,
    )

    # Extract the Close column(s). For a single ticker yf returns flat cols.
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})

    # Fill minor gaps, drop rows where everything is NaN.
    prices = prices.ffill().bfill().dropna(how="all")

    _cache[key] = prices
    return prices
