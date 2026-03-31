"""
charts.py — Plotly chart-building functions.

Each function returns a plotly.graph_objects.Figure ready for a dcc.Graph.
All charts use the "plotly_dark" template for visual consistency.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from risk_metrics import (
    drawdown_series,
    max_drawdown_window,
    rolling_volatility,
    annualised_return,
    annualised_vol,
    sharpe_ratio,
    parametric_var,
    historical_var,
)
from data_loader import BENCHMARK

# Consistent colour palette.
PALETTE = px.colors.qualitative.Plotly
TEMPLATE = "plotly_dark"


def cumulative_returns_chart(
    returns: pd.DataFrame, port_returns: pd.Series
) -> go.Figure:
    """
    Line chart: cumulative return of each holding, the portfolio, and
    the benchmark over the selected window.
    """
    cum = returns.cumsum().apply(np.exp) - 1  # log cumret → simple cumret
    port_cum = port_returns.cumsum().apply(np.exp) - 1

    fig = go.Figure()

    # Individual holdings (muted lines).
    for i, col in enumerate(returns.columns):
        if col == BENCHMARK:
            continue
        fig.add_trace(
            go.Scatter(
                x=cum.index,
                y=cum[col],
                name=col,
                mode="lines",
                line=dict(width=1, color=PALETTE[i % len(PALETTE)]),
                opacity=0.5,
            )
        )

    # Benchmark — dashed.
    if BENCHMARK in cum.columns:
        fig.add_trace(
            go.Scatter(
                x=cum.index,
                y=cum[BENCHMARK],
                name=BENCHMARK,
                mode="lines",
                line=dict(width=2, dash="dash", color="gray"),
            )
        )

    # Portfolio — bold.
    fig.add_trace(
        go.Scatter(
            x=port_cum.index,
            y=port_cum,
            name="Portfolio",
            mode="lines",
            line=dict(width=3, color="#00cc96"),
        )
    )

    fig.update_layout(
        template=TEMPLATE,
        title="Cumulative Returns",
        yaxis_tickformat=".0%",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(t=40, b=60),
    )
    return fig


def correlation_heatmap(corr: pd.DataFrame) -> go.Figure:
    """Heatmap of pairwise return correlations."""
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu_r",
            zmin=-1,
            zmax=1,
            text=corr.round(2).values,
            texttemplate="%{text}",
        )
    )
    fig.update_layout(
        template=TEMPLATE,
        title="Correlation Matrix",
        margin=dict(t=40, b=20),
    )
    return fig


def rolling_vol_chart(
    port_returns: pd.Series, bench_returns: pd.Series
) -> go.Figure:
    """Rolling 30-day and 90-day annualised volatility for portfolio and benchmark."""
    fig = go.Figure()

    for window, dash in [(30, "solid"), (90, "dot")]:
        rv_port = rolling_volatility(port_returns, window)
        rv_bench = rolling_volatility(bench_returns, window)
        fig.add_trace(
            go.Scatter(
                x=rv_port.index,
                y=rv_port,
                name=f"Portfolio {window}d",
                mode="lines",
                line=dict(width=2, dash=dash, color="#00cc96"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=rv_bench.index,
                y=rv_bench,
                name=f"{BENCHMARK} {window}d",
                mode="lines",
                line=dict(width=2, dash=dash, color="gray"),
            )
        )

    fig.update_layout(
        template=TEMPLATE,
        title="Rolling Volatility",
        yaxis_tickformat=".0%",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(t=40, b=60),
    )
    return fig


def risk_return_scatter(
    returns: pd.DataFrame, weights: dict[str, float]
) -> go.Figure:
    """
    Scatter plot: annualised return vs. vol per holding. Portfolio shown
    as a highlighted diamond. Sharpe ratio in hover text.
    """
    data = []
    for col in returns.columns:
        ar = annualised_return(returns[col])
        av = annualised_vol(returns[col])
        sr = sharpe_ratio(returns[col])
        data.append(dict(ticker=col, ret=ar, vol=av, sharpe=sr))

    fig = go.Figure()
    for d in data:
        fig.add_trace(
            go.Scatter(
                x=[d["vol"]],
                y=[d["ret"]],
                mode="markers+text",
                marker=dict(size=10),
                text=[d["ticker"]],
                textposition="top center",
                hovertemplate=(
                    f"<b>{d['ticker']}</b><br>"
                    f"Return: {d['ret']:.1%}<br>"
                    f"Vol: {d['vol']:.1%}<br>"
                    f"Sharpe: {d['sharpe']:.2f}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    # Portfolio point.
    from risk_metrics import portfolio_returns as _pr

    port = _pr(returns, weights)
    par = annualised_return(port)
    pav = annualised_vol(port)
    psr = sharpe_ratio(port)
    fig.add_trace(
        go.Scatter(
            x=[pav],
            y=[par],
            mode="markers+text",
            marker=dict(size=16, symbol="diamond", color="#00cc96"),
            text=["Portfolio"],
            textposition="top center",
            hovertemplate=(
                f"<b>Portfolio</b><br>"
                f"Return: {par:.1%}<br>"
                f"Vol: {pav:.1%}<br>"
                f"Sharpe: {psr:.2f}<extra></extra>"
            ),
            showlegend=False,
        )
    )

    fig.update_layout(
        template=TEMPLATE,
        title="Risk–Return",
        xaxis_title="Annualised Volatility",
        yaxis_title="Annualised Return",
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        margin=dict(t=40, b=40),
    )
    return fig


def return_histogram(port_returns: pd.Series) -> go.Figure:
    """
    Histogram of daily portfolio returns with VaR threshold lines at
    95% and 99% (both parametric and historical).
    """
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=port_returns,
            nbinsx=80,
            marker_color="#636efa",
            opacity=0.75,
            name="Daily Returns",
        )
    )

    # VaR lines.
    var95_p = -parametric_var(port_returns, 0.95)
    var99_p = -parametric_var(port_returns, 0.99)
    var95_h = -historical_var(port_returns, 0.95)
    var99_h = -historical_var(port_returns, 0.99)

    for val, label, color, dash in [
        (var95_p, "Param 95%", "#EF553B", "solid"),
        (var99_p, "Param 99%", "#EF553B", "dash"),
        (var95_h, "Hist 95%", "#FFA15A", "solid"),
        (var99_h, "Hist 99%", "#FFA15A", "dash"),
    ]:
        fig.add_vline(
            x=val,
            line_dash=dash,
            line_color=color,
            annotation_text=label,
            annotation_font_color=color,
        )

    fig.update_layout(
        template=TEMPLATE,
        title="Daily Return Distribution & VaR",
        xaxis_title="Log Return",
        xaxis_tickformat=".1%",
        margin=dict(t=40, b=40),
    )
    return fig


def drawdown_chart(port_returns: pd.Series) -> go.Figure:
    """
    Drawdown curve over time.  The worst drawdown window is highlighted
    with a shaded rectangle.
    """
    cum = port_returns.cumsum().apply(np.exp) - 1
    dd = drawdown_series(cum)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dd.index,
            y=dd,
            fill="tozeroy",
            mode="lines",
            line=dict(color="#EF553B", width=1),
            name="Drawdown",
        )
    )

    # Highlight the max-drawdown window.
    try:
        start, trough, end = max_drawdown_window(cum)
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor="red",
            opacity=0.15,
            line_width=0,
            annotation_text="Max DD",
            annotation_position="top left",
        )
    except Exception:
        pass  # graceful degradation

    fig.update_layout(
        template=TEMPLATE,
        title="Portfolio Drawdown",
        yaxis_tickformat=".0%",
        margin=dict(t=40, b=20),
    )
    return fig
