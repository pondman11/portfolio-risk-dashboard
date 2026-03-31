"""
charts.py — All Plotly figure builders.

Design principles:
- Consistent dark theme (plotly_dark base, customized)
- Clean, minimal gridlines — data speaks
- Cohesive color palette across all charts
- Generous margins, readable axis labels
- Smooth lines, no chart junk
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from scipy.stats import norm

# ─── Color palette ───────────────────────────────────────────────────────
PALETTE = [
    "#00d4aa",  # teal-green (portfolio)
    "#6c5ce7",  # purple
    "#ffd93d",  # gold
    "#ff6b6b",  # coral-red
    "#74b9ff",  # sky-blue
    "#fd79a8",  # pink
    "#a29bfe",  # lavender
    "#00cec9",  # cyan
    "#ff9f43",  # orange
    "#55efc4",  # mint
]

BENCHMARK_COLOR = "#636e72"  # muted grey for benchmark
BG_COLOR = "#12141a"
PAPER_COLOR = "#12141a"
GRID_COLOR = "#1e2028"
TEXT_COLOR = "#b2b9c4"

CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=PAPER_COLOR,
    plot_bgcolor=BG_COLOR,
    font=dict(family="Inter, -apple-system, sans-serif", color=TEXT_COLOR, size=12),
    margin=dict(l=50, r=30, t=50, b=40),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(gridcolor=GRID_COLOR, showgrid=False, zeroline=False),
    yaxis=dict(gridcolor=GRID_COLOR, gridwidth=1, zeroline=False),
    hoverlabel=dict(bgcolor="#1a1d23", font_size=12, bordercolor="rgba(0,0,0,0)"),
)


def _apply_layout(fig, **kwargs):
    """Apply common layout to a figure."""
    fig.update_layout(**CHART_LAYOUT, **kwargs)
    return fig


# ─── Cumulative Returns ────────────────────────────────────────────────

def cumulative_returns_chart(
    returns: pd.DataFrame,
    portfolio_returns: pd.Series,
    benchmark_col: str = "SPY",
) -> go.Figure:
    """
    Hero chart: cumulative performance of portfolio vs benchmark vs holdings.

    Portfolio line is thick and prominent. Holdings are thin and translucent.
    Benchmark is dashed grey.
    """
    fig = go.Figure()

    cum = (1 + returns).cumprod() - 1
    port_cum = (1 + portfolio_returns).cumprod() - 1

    # Individual holdings — thin, translucent
    for i, col in enumerate(returns.columns):
        if col == benchmark_col:
            continue
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum[col],
            name=col,
            mode="lines",
            line=dict(width=1.5, color=PALETTE[i % len(PALETTE)]),
            opacity=0.4,
            hovertemplate=f"{col}: %{{y:.1%}}<extra></extra>",
        ))

    # Benchmark — dashed grey
    if benchmark_col in cum.columns:
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum[benchmark_col],
            name=benchmark_col,
            mode="lines",
            line=dict(width=2, color=BENCHMARK_COLOR, dash="dot"),
            hovertemplate=f"{benchmark_col}: %{{y:.1%}}<extra></extra>",
        ))

    # Portfolio — hero line, thick
    fig.add_trace(go.Scatter(
        x=port_cum.index, y=port_cum.values,
        name="Portfolio",
        mode="lines",
        line=dict(width=3, color=PALETTE[0]),
        hovertemplate="Portfolio: %{y:.1%}<extra></extra>",
    ))

    fig.update_layout(
        yaxis_tickformat=".0%",
        title=dict(text="Cumulative Returns", font=dict(size=16, color="#e8eaed")),
        height=400,
    )
    return _apply_layout(fig)


# ─── Correlation Heatmap ──────────────────────────────────────────────

def correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """
    Clean heatmap with annotated values.
    Uses a teal-to-coral diverging scale centered on 0.
    """
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale=[
            [0.0, "#ff6b6b"],
            [0.5, "#1a1d23"],
            [1.0, "#00d4aa"],
        ],
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=12, color="#e8eaed"),
        hovertemplate="%{x} × %{y}: %{z:.2f}<extra></extra>",
        colorbar=dict(
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1.0", "-0.5", "0", "0.5", "1.0"],
            len=0.8,
        ),
    ))

    fig.update_layout(
        title=dict(text="Return Correlations", font=dict(size=16, color="#e8eaed")),
        height=400,
        xaxis=dict(side="bottom"),
        yaxis=dict(autorange="reversed"),
    )
    return _apply_layout(fig)


# ─── Rolling Volatility ──────────────────────────────────────────────

def rolling_vol_chart(
    portfolio_vol_30: pd.Series,
    portfolio_vol_90: pd.Series,
    benchmark_vol_30: pd.Series | None = None,
) -> go.Figure:
    """
    Rolling annualised volatility — 30d and 90d windows.
    Fill area under the 30d line for visual weight.
    """
    fig = go.Figure()

    # 30-day portfolio vol — filled area
    fig.add_trace(go.Scatter(
        x=portfolio_vol_30.index, y=portfolio_vol_30.values,
        name="Portfolio 30d",
        mode="lines",
        line=dict(width=2, color=PALETTE[0]),
        fill="tozeroy",
        fillcolor="rgba(0,212,170,0.1)",
        hovertemplate="30d vol: %{y:.1%}<extra></extra>",
    ))

    # 90-day portfolio vol
    fig.add_trace(go.Scatter(
        x=portfolio_vol_90.index, y=portfolio_vol_90.values,
        name="Portfolio 90d",
        mode="lines",
        line=dict(width=2, color=PALETTE[1]),
        hovertemplate="90d vol: %{y:.1%}<extra></extra>",
    ))

    # Benchmark 30-day
    if benchmark_vol_30 is not None:
        fig.add_trace(go.Scatter(
            x=benchmark_vol_30.index, y=benchmark_vol_30.values,
            name="SPY 30d",
            mode="lines",
            line=dict(width=1.5, color=BENCHMARK_COLOR, dash="dot"),
            hovertemplate="SPY 30d vol: %{y:.1%}<extra></extra>",
        ))

    fig.update_layout(
        yaxis_tickformat=".0%",
        title=dict(text="Rolling Volatility", font=dict(size=16, color="#e8eaed")),
        height=380,
    )
    return _apply_layout(fig)


# ─── VaR Histogram ──────────────────────────────────────────────────

def var_histogram(
    daily_returns: pd.Series,
    var_95: float,
    var_99: float,
) -> go.Figure:
    """
    Histogram of daily portfolio returns with VaR thresholds as vertical lines.
    Left tail is highlighted red for visual impact.
    """
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=daily_returns.values,
        nbinsx=80,
        marker_color=PALETTE[0],
        opacity=0.7,
        name="Daily Returns",
        hovertemplate="Return: %{x:.2%}<br>Count: %{y}<extra></extra>",
    ))

    # VaR lines
    for val, label, color in [
        (-var_95, "95% VaR", "#ff9f43"),
        (-var_99, "99% VaR", "#ee5a24"),
    ]:
        fig.add_vline(
            x=val, line_width=2, line_dash="dash", line_color=color,
            annotation_text=f" {label}: {abs(val):.2%}",
            annotation_position="top left",
            annotation_font=dict(size=11, color=color),
        )

    fig.update_layout(
        title=dict(text="Return Distribution & VaR", font=dict(size=16, color="#e8eaed")),
        xaxis_tickformat=".1%",
        xaxis_title="Daily Return",
        yaxis_title="Frequency",
        height=380,
    )
    return _apply_layout(fig)


# ─── Risk-Return Scatter ─────────────────────────────────────────────

def risk_return_scatter(
    ticker_data: list[dict],
    portfolio_point: dict,
) -> go.Figure:
    """
    Scatter: annualised vol (x) vs annualised return (y) per holding.
    Portfolio is a large highlighted marker. Sharpe on hover.

    ticker_data: list of {"ticker", "vol", "return", "sharpe"}
    portfolio_point: {"vol", "return", "sharpe"}
    """
    fig = go.Figure()

    # Individual holdings
    for i, d in enumerate(ticker_data):
        fig.add_trace(go.Scatter(
            x=[d["vol"]], y=[d["return"]],
            name=d["ticker"],
            mode="markers+text",
            text=[d["ticker"]],
            textposition="top center",
            textfont=dict(size=11, color=PALETTE[i % len(PALETTE)]),
            marker=dict(size=12, color=PALETTE[i % len(PALETTE)], opacity=0.8),
            hovertemplate=(
                f"<b>{d['ticker']}</b><br>"
                f"Return: {d['return']:.1%}<br>"
                f"Vol: {d['vol']:.1%}<br>"
                f"Sharpe: {d['sharpe']:.2f}<extra></extra>"
            ),
        ))

    # Portfolio — highlighted
    fig.add_trace(go.Scatter(
        x=[portfolio_point["vol"]], y=[portfolio_point["return"]],
        name="Portfolio",
        mode="markers+text",
        text=["Portfolio"],
        textposition="bottom center",
        textfont=dict(size=12, color="#fff", weight="bold"),
        marker=dict(
            size=18, color=PALETTE[0],
            line=dict(width=3, color="#fff"),
            symbol="diamond",
        ),
        hovertemplate=(
            f"<b>Portfolio</b><br>"
            f"Return: {portfolio_point['return']:.1%}<br>"
            f"Vol: {portfolio_point['vol']:.1%}<br>"
            f"Sharpe: {portfolio_point['sharpe']:.2f}<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(text="Risk vs Return", font=dict(size=16, color="#e8eaed")),
        xaxis_title="Annualised Volatility",
        yaxis_title="Annualised Return",
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        height=380,
        showlegend=False,
    )
    return _apply_layout(fig)


# ─── Drawdown Chart ──────────────────────────────────────────────────

def drawdown_chart(
    dd_series: pd.Series,
    max_dd_window: tuple | None = None,
) -> go.Figure:
    """
    Drawdown curve with the worst drawdown period highlighted.
    Uses red fill for visual gravity.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dd_series.index, y=dd_series.values,
        name="Drawdown",
        mode="lines",
        line=dict(width=1.5, color="#ff6b6b"),
        fill="tozeroy",
        fillcolor="rgba(255,107,107,0.15)",
        hovertemplate="Drawdown: %{y:.1%}<extra></extra>",
    ))

    # Highlight worst drawdown window
    if max_dd_window is not None:
        start, trough, end = max_dd_window
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="rgba(238,90,36,0.15)",
            line_width=0,
            annotation_text="Max DD",
            annotation_position="top left",
            annotation_font=dict(size=11, color="#ee5a24"),
        )

    fig.update_layout(
        title=dict(text="Portfolio Drawdown", font=dict(size=16, color="#e8eaed")),
        yaxis_tickformat=".0%",
        height=380,
    )
    return _apply_layout(fig)
