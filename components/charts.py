"""
charts.py — All Plotly figure builders.

Design: Ultra-clean. Thin lines, muted palette. Data breathes.
Legend click highlights the selected trace (others dim).
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy.stats import norm

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

BENCHMARK_COLOR = "#3d4250"
BG_COLOR = "rgba(0,0,0,0)"
PAPER_COLOR = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.025)"
TEXT_COLOR = "#6a7080"

CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=PAPER_COLOR,
    plot_bgcolor=BG_COLOR,
    font=dict(family="Inter, -apple-system, sans-serif", color=TEXT_COLOR, size=11),
    margin=dict(l=48, r=16, t=36, b=32),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.12,
        xanchor="center",
        x=0.5,
        font=dict(size=10, color="#5a6270"),
        bgcolor="rgba(0,0,0,0)",
        itemsizing="constant",
        tracegroupgap=0,
        # Click to isolate: single-click dims others, double-click resets
        itemclick="toggleothers",
        itemdoubleclick="toggle",
    ),
    xaxis=dict(
        gridcolor=GRID_COLOR, showgrid=False, zeroline=False,
        showline=False, tickfont=dict(size=10, color="#4a5060"),
    ),
    yaxis=dict(
        gridcolor=GRID_COLOR, gridwidth=1, zeroline=False,
        showline=False, tickfont=dict(size=10, color="#4a5060"),
    ),
    hoverlabel=dict(
        bgcolor="rgba(18,20,26,0.95)",
        font_size=11,
        font_color="#c8cdd5",
        bordercolor="rgba(255,255,255,0.06)",
    ),
    hovermode="x unified",
)


def _apply_layout(fig, **kwargs):
    """Apply common layout. kwargs override defaults."""
    merged = {**CHART_LAYOUT, **kwargs}
    fig.update_layout(**merged)
    return fig


def _title(text):
    """Consistent minimal title config."""
    return dict(text=text, font=dict(size=12, color="#5a6270"), x=0.01, y=0.97, xanchor="left", yanchor="top")


# ─── Cumulative Returns ────────────────────────────────────────────────

def cumulative_returns_chart(
    returns: pd.DataFrame,
    portfolio_returns: pd.Series,
    benchmark_col: str = "SPY",
) -> go.Figure:
    fig = go.Figure()

    cum = (1 + returns).cumprod() - 1
    port_cum = (1 + portfolio_returns).cumprod() - 1

    # Individual holdings — whisper-thin, very faded
    for i, col in enumerate(returns.columns):
        if col == benchmark_col:
            continue
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum[col],
            name=col,
            mode="lines",
            line=dict(width=1.2, color=PALETTE[(i + 1) % len(PALETTE)]),
            opacity=0.25,
            hovertemplate="%{y:.1%}",
        ))

    # Benchmark — subtle dotted
    if benchmark_col in cum.columns:
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum[benchmark_col],
            name=benchmark_col,
            mode="lines",
            line=dict(width=1.2, color=BENCHMARK_COLOR, dash="dot"),
            hovertemplate="%{y:.1%}",
        ))

    # Portfolio — clean line, no fill
    fig.add_trace(go.Scatter(
        x=port_cum.index, y=port_cum.values,
        name="Portfolio",
        mode="lines",
        line=dict(width=2.5, color=PALETTE[0]),
        hovertemplate="%{y:.1%}",
    ))

    return _apply_layout(fig,
        yaxis_tickformat=".0%",
        title=_title("Cumulative Returns"),
        height=380,
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
            tickvals=[-1, 0, 1],
            ticktext=["-1", "0", "1"],
            len=0.6,
            thickness=6,
            outlinewidth=0,
            tickfont=dict(size=9, color="#4a5060"),
        ),
    ))

    return _apply_layout(fig,
        title=_title("Correlations"),
        height=370,
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

    # 90d as a soft background reference
    fig.add_trace(go.Scatter(
        x=portfolio_vol_90.index, y=portfolio_vol_90.values,
        name="90d",
        mode="lines",
        line=dict(width=1, color=PALETTE[1], dash="dot"),
        opacity=0.5,
        hovertemplate="%{y:.1%}",
    ))

    # Benchmark
    if benchmark_vol_30 is not None:
        fig.add_trace(go.Scatter(
            x=benchmark_vol_30.index, y=benchmark_vol_30.values,
            name="SPY",
            mode="lines",
            line=dict(width=0.8, color=BENCHMARK_COLOR, dash="dot"),
            opacity=0.4,
            hovertemplate="%{y:.1%}",
        ))

    # 30d portfolio — main event
    fig.add_trace(go.Scatter(
        x=portfolio_vol_30.index, y=portfolio_vol_30.values,
        name="30d",
        mode="lines",
        line=dict(width=2, color=PALETTE[0]),
        hovertemplate="%{y:.1%}",
    ))

    return _apply_layout(fig,
        yaxis_tickformat=".0%",
        title=_title("Rolling Volatility"),
        height=360,
    )


# ─── Return Distribution (VaR) ──────────────────────────────────────

def var_histogram(
    daily_returns: pd.Series,
    var_95: float,
    var_99: float,
) -> go.Figure:
    """
    Industry-standard return distribution with:
    - Histogram of daily returns
    - Normal distribution overlay (fitted)
    - Clearly labeled VaR thresholds with legend entries
    """
    fig = go.Figure()

    # Histogram
    fig.add_trace(go.Histogram(
        x=daily_returns.values,
        nbinsx=50,
        marker_color="rgba(0,212,170,0.35)",
        marker_line=dict(width=0.5, color="rgba(0,212,170,0.15)"),
        name="Daily Returns",
        hovertemplate="Return: %{x:.2%}<br>Count: %{y}<extra></extra>",
        histnorm="probability density",
    ))

    # Normal distribution overlay
    mu = daily_returns.mean()
    sigma = daily_returns.std()
    x_range = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 200)
    y_norm = norm.pdf(x_range, mu, sigma)
    fig.add_trace(go.Scatter(
        x=x_range, y=y_norm,
        name="Normal Fit",
        mode="lines",
        line=dict(width=1.5, color="#6c5ce7", dash="dot"),
        opacity=0.6,
        hoverinfo="skip",
    ))

    # VaR threshold lines as visible traces (so they appear in legend)
    y_max = norm.pdf(mu, mu, sigma)  # peak of the normal curve

    # 95% VaR line
    fig.add_trace(go.Scatter(
        x=[-var_95, -var_95],
        y=[0, y_max * 0.85],
        name=f"95% VaR ({var_95:.2%})",
        mode="lines",
        line=dict(width=2, color="#ff9f43", dash="dash"),
        hoverinfo="skip",
    ))

    # 99% VaR line
    fig.add_trace(go.Scatter(
        x=[-var_99, -var_99],
        y=[0, y_max * 0.7],
        name=f"99% VaR ({var_99:.2%})",
        mode="lines",
        line=dict(width=2, color="#ff6b6b", dash="dash"),
        hoverinfo="skip",
    ))

    # Shade the left tail beyond 95% VaR
    tail_x = np.linspace(mu - 4 * sigma, -var_95, 50)
    tail_y = norm.pdf(tail_x, mu, sigma)
    fig.add_trace(go.Scatter(
        x=np.concatenate([tail_x, [tail_x[-1], tail_x[0]]]),
        y=np.concatenate([tail_y, [0, 0]]),
        fill="toself",
        fillcolor="rgba(255,107,107,0.1)",
        line=dict(width=0),
        name="Tail Risk",
        hoverinfo="skip",
        showlegend=False,
    ))

    return _apply_layout(fig,
        title=_title("Return Distribution"),
        xaxis_tickformat=".1%",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        height=370,
        bargap=0.03,
        hovermode="closest",
        showlegend=True,
        margin=dict(l=48, r=16, t=36, b=50),
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
            marker=dict(
                size=9,
                color=PALETTE[(i + 1) % len(PALETTE)],
                opacity=0.6,
                line=dict(width=0),
            ),
            hovertemplate=(
                f"<b>{d['ticker']}</b><br>"
                f"Return: {d['return']:.1%}<br>"
                f"Vol: {d['vol']:.1%}<br>"
                f"Sharpe: {d['sharpe']:.2f}<extra></extra>"
            ),
        ))

    # Portfolio — standout
    fig.add_trace(go.Scatter(
        x=[portfolio_point["vol"]], y=[portfolio_point["return"]],
        name="Portfolio",
        mode="markers+text",
        text=["Portfolio"],
        textposition="bottom center",
        textfont=dict(size=10, color="#c8cdd5"),
        marker=dict(
            size=14, color=PALETTE[0],
            line=dict(width=1.5, color="rgba(255,255,255,0.2)"),
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
        title=_title("Risk vs Return"),
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        height=370,
        showlegend=False,
        hovermode="closest",
    )


# ─── Drawdown Chart ──────────────────────────────────────────────────

def drawdown_chart(
    dd_series: pd.Series,
    max_dd_window: tuple | None = None,
) -> go.Figure:
    """
    Industry-standard underwater chart:
    - Drawdown as filled area from zero (always negative)
    - Zero line clearly marked
    - Max drawdown period highlighted with clear labeled annotation
    - Peak-to-trough and recovery markers
    """
    fig = go.Figure()

    # Zero baseline
    fig.add_hline(
        y=0, line_width=1, line_color="rgba(255,255,255,0.1)",
    )

    # Drawdown area — gradient red fill
    fig.add_trace(go.Scatter(
        x=dd_series.index, y=dd_series.values,
        name="Drawdown",
        mode="lines",
        line=dict(width=1.5, color="#ff6b6b"),
        fill="tozeroy",
        fillcolor="rgba(255,107,107,0.08)",
        hovertemplate="Drawdown: %{y:.1%}<extra></extra>",
    ))

    if max_dd_window is not None:
        start, trough, end = max_dd_window

        # Highlight the max DD period
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="rgba(255,107,107,0.06)",
            line_width=0,
        )

        trough_val = dd_series.loc[trough] if trough in dd_series.index else dd_series.min()

        # Peak marker (start of drawdown)
        fig.add_trace(go.Scatter(
            x=[start], y=[0],
            mode="markers",
            marker=dict(size=7, color="#ffd93d", symbol="triangle-down", line=dict(width=1, color="#0b0d10")),
            name="Peak",
            hovertemplate=f"Peak: {start.strftime('%Y-%m-%d') if hasattr(start, 'strftime') else start}<extra></extra>",
            showlegend=True,
        ))

        # Trough marker (bottom of drawdown)
        fig.add_trace(go.Scatter(
            x=[trough], y=[trough_val],
            mode="markers",
            marker=dict(size=8, color="#ff6b6b", symbol="circle", line=dict(width=1.5, color="#0b0d10")),
            name=f"Trough ({trough_val:.1%})",
            hovertemplate=f"Trough: {trough_val:.1%}<br>{trough.strftime('%Y-%m-%d') if hasattr(trough, 'strftime') else trough}<extra></extra>",
            showlegend=True,
        ))

        # Recovery marker
        if end != dd_series.index[-1]:
            fig.add_trace(go.Scatter(
                x=[end], y=[0],
                mode="markers",
                marker=dict(size=7, color="#00d4aa", symbol="triangle-up", line=dict(width=1, color="#0b0d10")),
                name="Recovery",
                hovertemplate=f"Recovery: {end.strftime('%Y-%m-%d') if hasattr(end, 'strftime') else end}<extra></extra>",
                showlegend=True,
            ))

        # Duration annotation
        if hasattr(start, 'strftime') and hasattr(trough, 'strftime'):
            days_to_trough = (trough - start).days
            days_to_recovery = (end - start).days if end != dd_series.index[-1] else None
            duration_text = f"{days_to_trough}d to trough"
            if days_to_recovery:
                duration_text += f" · {days_to_recovery}d total"

            fig.add_annotation(
                x=trough, y=trough_val,
                text=duration_text,
                showarrow=True,
                arrowhead=0,
                arrowcolor="rgba(255,255,255,0.15)",
                arrowwidth=1,
                font=dict(size=9, color="#8a92a0"),
                bgcolor="rgba(18,20,26,0.8)",
                borderpad=4,
                ay=-35, ax=40,
            )

    return _apply_layout(fig,
        title=_title("Drawdown"),
        yaxis_tickformat=".0%",
        height=370,
        showlegend=True,
        margin=dict(l=48, r=16, t=36, b=50),
    )
