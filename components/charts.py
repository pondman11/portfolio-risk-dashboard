"""
charts.py — All Plotly figure builders.

Design: Minimal, dark, generous whitespace. Data-forward.
Tooltips use hovermode="x unified" where appropriate.
Title inside the top margin, legend below chart area.
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ─── Color palette ───────────────────────────────────────────────────
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

BENCHMARK_COLOR = "#4a5060"
BG_COLOR = "rgba(0,0,0,0)"
PAPER_COLOR = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.03)"
TEXT_COLOR = "#8a92a0"

CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=PAPER_COLOR,
    plot_bgcolor=BG_COLOR,
    font=dict(family="Inter, -apple-system, sans-serif", color=TEXT_COLOR, size=11),
    margin=dict(l=50, r=20, t=70, b=35),
    title=dict(
        font=dict(size=13, color="#6a7080"),
        x=0.01,
        y=0.98,
        xanchor="left",
        yanchor="top",
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.08,
        xanchor="left",
        x=0,
        font=dict(size=10, color="#5a6270"),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(gridcolor=GRID_COLOR, showgrid=False, zeroline=False, showline=False),
    yaxis=dict(gridcolor=GRID_COLOR, gridwidth=1, zeroline=False, showline=False),
    hoverlabel=dict(
        bgcolor="rgba(22,25,32,0.95)",
        font_size=12,
        font_color="#e0e4ea",
        bordercolor="rgba(255,255,255,0.1)",
    ),
    hovermode="x unified",
)


def _apply_layout(fig, **kwargs):
    """Apply common layout to a figure. kwargs override CHART_LAYOUT defaults."""
    merged = {**CHART_LAYOUT, **kwargs}
    fig.update_layout(**merged)
    return fig


# ─── Cumulative Returns ────────────────────────────────────────────────

def cumulative_returns_chart(
    returns: pd.DataFrame,
    portfolio_returns: pd.Series,
    benchmark_col: str = "SPY",
) -> go.Figure:
    fig = go.Figure()

    cum = (1 + returns).cumprod() - 1
    port_cum = (1 + portfolio_returns).cumprod() - 1

    # Individual holdings — thin, subtle
    for i, col in enumerate(returns.columns):
        if col == benchmark_col:
            continue
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum[col],
            name=col,
            mode="lines",
            line=dict(width=1, color=PALETTE[(i + 1) % len(PALETTE)]),
            opacity=0.3,
            hovertemplate="%{y:.1%}",
        ))

    # Benchmark
    if benchmark_col in cum.columns:
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum[benchmark_col],
            name=benchmark_col,
            mode="lines",
            line=dict(width=1.5, color=BENCHMARK_COLOR, dash="dot"),
            hovertemplate="%{y:.1%}",
        ))

    # Portfolio — hero
    fig.add_trace(go.Scatter(
        x=port_cum.index, y=port_cum.values,
        name="Portfolio",
        mode="lines",
        line=dict(width=2.5, color=PALETTE[0]),
        fill="tozeroy",
        fillcolor="rgba(0,212,170,0.06)",
        hovertemplate="%{y:.1%}",
    ))

    return _apply_layout(fig,
        yaxis_tickformat=".0%",
        title_text="Cumulative Returns",
        height=400,
    )


# ─── Correlation Heatmap ──────────────────────────────────────────────

def correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
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
        textfont=dict(size=11, color="#c8cdd5"),
        hovertemplate="%{x} × %{y}: %{z:.2f}<extra></extra>",
        colorbar=dict(
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1", "-.5", "0", ".5", "1"],
            len=0.8,
            thickness=8,
            outlinewidth=0,
        ),
    ))

    return _apply_layout(fig,
        title_text="Correlations",
        height=380,
        xaxis=dict(side="bottom"),
        yaxis=dict(autorange="reversed"),
        hovermode="closest",
        showlegend=False,
    )


# ─── Rolling Volatility ──────────────────────────────────────────────

def rolling_vol_chart(
    portfolio_vol_30: pd.Series,
    portfolio_vol_90: pd.Series,
    benchmark_vol_30: pd.Series | None = None,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=portfolio_vol_30.index, y=portfolio_vol_30.values,
        name="30d",
        mode="lines",
        line=dict(width=1.5, color=PALETTE[0]),
        fill="tozeroy",
        fillcolor="rgba(0,212,170,0.06)",
        hovertemplate="%{y:.1%}",
    ))

    fig.add_trace(go.Scatter(
        x=portfolio_vol_90.index, y=portfolio_vol_90.values,
        name="90d",
        mode="lines",
        line=dict(width=1.5, color=PALETTE[1]),
        hovertemplate="%{y:.1%}",
    ))

    if benchmark_vol_30 is not None:
        fig.add_trace(go.Scatter(
            x=benchmark_vol_30.index, y=benchmark_vol_30.values,
            name="SPY 30d",
            mode="lines",
            line=dict(width=1, color=BENCHMARK_COLOR, dash="dot"),
            hovertemplate="%{y:.1%}",
        ))

    return _apply_layout(fig,
        yaxis_tickformat=".0%",
        title_text="Rolling Volatility",
        height=380,
    )


# ─── VaR Histogram ──────────────────────────────────────────────────

def var_histogram(
    daily_returns: pd.Series,
    var_95: float,
    var_99: float,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=daily_returns.values,
        nbinsx=60,
        marker_color="rgba(0,212,170,0.5)",
        marker_line=dict(width=0),
        name="Daily Returns",
        hovertemplate="Return: %{x:.2%}<br>Count: %{y}<extra></extra>",
    ))

    for val, label, color in [
        (-var_95, "95% VaR", "#ff9f43"),
        (-var_99, "99% VaR", "#ff6b6b"),
    ]:
        fig.add_vline(
            x=val, line_width=1.5, line_dash="dash", line_color=color,
            annotation_text=f"{label}: {abs(val):.2%}",
            annotation_position="top left",
            annotation_font=dict(size=10, color=color),
        )

    return _apply_layout(fig,
        title_text="Return Distribution",
        xaxis_tickformat=".1%",
        xaxis_title=None,
        yaxis_title=None,
        height=380,
        bargap=0.02,
        hovermode="closest",
        showlegend=False,
    )


# ─── Risk-Return Scatter ─────────────────────────────────────────────

def risk_return_scatter(
    ticker_data: list[dict],
    portfolio_point: dict,
) -> go.Figure:
    fig = go.Figure()

    for i, d in enumerate(ticker_data):
        fig.add_trace(go.Scatter(
            x=[d["vol"]], y=[d["return"]],
            name=d["ticker"],
            mode="markers+text",
            text=[d["ticker"]],
            textposition="top center",
            textfont=dict(size=10, color=PALETTE[(i + 1) % len(PALETTE)]),
            marker=dict(size=10, color=PALETTE[(i + 1) % len(PALETTE)], opacity=0.7),
            hovertemplate=(
                f"<b>{d['ticker']}</b><br>"
                f"Return: {d['return']:.1%}<br>"
                f"Vol: {d['vol']:.1%}<br>"
                f"Sharpe: {d['sharpe']:.2f}<extra></extra>"
            ),
        ))

    # Portfolio
    fig.add_trace(go.Scatter(
        x=[portfolio_point["vol"]], y=[portfolio_point["return"]],
        name="Portfolio",
        mode="markers+text",
        text=["Portfolio"],
        textposition="bottom center",
        textfont=dict(size=11, color="#e0e4ea"),
        marker=dict(
            size=16, color=PALETTE[0],
            line=dict(width=2, color="rgba(255,255,255,0.3)"),
            symbol="diamond",
        ),
        hovertemplate=(
            f"<b>Portfolio</b><br>"
            f"Return: {portfolio_point['return']:.1%}<br>"
            f"Vol: {portfolio_point['vol']:.1%}<br>"
            f"Sharpe: {portfolio_point['sharpe']:.2f}<extra></extra>"
        ),
    ))

    return _apply_layout(fig,
        title_text="Risk vs Return",
        xaxis_title="Volatility",
        yaxis_title="Return",
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        height=380,
        showlegend=False,
        hovermode="closest",
    )


# ─── Drawdown Chart ──────────────────────────────────────────────────

def drawdown_chart(
    dd_series: pd.Series,
    max_dd_window: tuple | None = None,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dd_series.index, y=dd_series.values,
        name="Drawdown",
        mode="lines",
        line=dict(width=1.5, color="#ff6b6b"),
        fill="tozeroy",
        fillcolor="rgba(255,107,107,0.08)",
        hovertemplate="%{y:.1%}",
    ))

    if max_dd_window is not None:
        start, trough, end = max_dd_window
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="rgba(238,90,36,0.08)",
            line_width=0,
            annotation_text="Max DD",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#ee5a24"),
        )

    return _apply_layout(fig,
        title_text="Drawdown",
        yaxis_tickformat=".0%",
        height=360,
        showlegend=False,
    )
