"""
risk_metrics.py — Core risk and return calculations.

All calculations use **log returns** which are additive over time and standard
in quantitative finance.  Annualisation assumes 252 trading days per year.
"""

import numpy as np
import pandas as pd

TRADING_DAYS = 252
DEFAULT_RISK_FREE = 0.05  # annualised risk-free rate


# ---------------------------------------------------------------------------
# Return helpers
# ---------------------------------------------------------------------------

def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute daily log returns from a price DataFrame."""
    return np.log(prices / prices.shift(1)).dropna()


def portfolio_returns(
    returns: pd.DataFrame, weights: dict[str, float]
) -> pd.Series:
    """
    Weighted portfolio return series.

    Parameters
    ----------
    returns : pd.DataFrame
        Daily log returns per ticker.
    weights : dict[str, float]
        Ticker → weight (0-1 scale, must sum to ~1.0).
    """
    tickers = list(weights.keys())
    w = np.array([weights[t] for t in tickers])
    return returns[tickers].dot(w).rename("Portfolio")


# ---------------------------------------------------------------------------
# Annualised metrics
# ---------------------------------------------------------------------------

def annualised_return(returns: pd.Series) -> float:
    """Annualised mean log return → simple return equivalent."""
    return float(np.exp(returns.mean() * TRADING_DAYS) - 1)


def annualised_vol(returns: pd.Series) -> float:
    """Annualised standard deviation of log returns."""
    return float(returns.std() * np.sqrt(TRADING_DAYS))


def sharpe_ratio(
    returns: pd.Series, risk_free: float = DEFAULT_RISK_FREE
) -> float:
    """Sharpe ratio using annualised return and vol."""
    ann_ret = annualised_return(returns)
    ann_v = annualised_vol(returns)
    if ann_v == 0:
        return 0.0
    return float((ann_ret - risk_free) / ann_v)


# ---------------------------------------------------------------------------
# Value at Risk
# ---------------------------------------------------------------------------

def parametric_var(
    returns: pd.Series, confidence: float = 0.95
) -> float:
    """
    1-day parametric VaR assuming normal distribution.

    VaR = -(mean - z * std)
    Returned as a positive number representing the loss threshold.
    """
    from scipy.stats import norm

    z = norm.ppf(1 - confidence)  # negative z for left tail
    mu = returns.mean()
    sigma = returns.std()
    return float(-(mu + z * sigma))


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    1-day historical VaR — empirical percentile of daily returns.

    Returns a positive loss threshold.
    """
    percentile = (1 - confidence) * 100  # e.g. 5 for 95%
    return float(-np.percentile(returns.dropna(), percentile))


# ---------------------------------------------------------------------------
# Drawdown
# ---------------------------------------------------------------------------

def drawdown_series(cumulative_returns: pd.Series) -> pd.Series:
    """
    Compute the drawdown curve from a cumulative wealth index (1 + cumret).

    Returns a Series of non-positive values (0 = at peak).
    """
    wealth = (1 + cumulative_returns)
    peak = wealth.cummax()
    dd = (wealth - peak) / peak
    return dd


def max_drawdown(cumulative_returns: pd.Series) -> float:
    """Maximum drawdown (returned as a positive fraction, e.g. 0.25 = -25%)."""
    dd = drawdown_series(cumulative_returns)
    return float(-dd.min())


def max_drawdown_window(cumulative_returns: pd.Series):
    """
    Return (start, trough, end) dates of the worst drawdown period.

    start  — date of the pre-drawdown peak
    trough — date of the maximum drawdown
    end    — date the portfolio recovered (or last date if not yet recovered)
    """
    dd = drawdown_series(cumulative_returns)
    trough_idx = dd.idxmin()
    # Peak is the last date where wealth was at its cummax before trough
    wealth = (1 + cumulative_returns)
    peak_val = wealth.loc[:trough_idx].cummax().iloc[-1]
    start_idx = wealth.loc[:trough_idx][wealth.loc[:trough_idx] == peak_val].index[-1]
    # Recovery: first date after trough where wealth >= peak again
    post = wealth.loc[trough_idx:]
    recovered = post[post >= peak_val]
    end_idx = recovered.index[0] if len(recovered) > 0 else wealth.index[-1]
    return start_idx, trough_idx, end_idx


# ---------------------------------------------------------------------------
# Rolling volatility
# ---------------------------------------------------------------------------

def rolling_volatility(
    returns: pd.Series, window: int = 30
) -> pd.Series:
    """Annualised rolling volatility over *window* trading days."""
    return returns.rolling(window).std() * np.sqrt(TRADING_DAYS)


# ---------------------------------------------------------------------------
# Correlation matrix
# ---------------------------------------------------------------------------

def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Pairwise Pearson correlation of daily log returns."""
    return returns.corr()
