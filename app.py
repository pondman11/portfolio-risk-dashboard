"""
app.py — Dash application entry point, layout, and callbacks.

Launches the Portfolio Risk Analytics dashboard on http://localhost:8050.
"""

import json
import numpy as np
import pandas as pd

import dash
from dash import html, dcc, callback, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc

# Local modules.
from data_loader import fetch_prices, BENCHMARK, DEFAULT_TICKERS
from risk_metrics import (
    log_returns,
    portfolio_returns,
    annualised_return,
    annualised_vol,
    sharpe_ratio,
    parametric_var,
    historical_var,
    max_drawdown,
    correlation_matrix,
)
from components.portfolio_input import portfolio_panel, DEFAULT_WEIGHTS
from components.charts import (
    cumulative_returns_chart,
    correlation_heatmap,
    rolling_vol_chart,
    risk_return_scatter,
    return_histogram,
    drawdown_chart,
)
from components.cards import summary_cards

# ---------------------------------------------------------------------------
# App initialisation — DARKLY theme for a sleek dark look.
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Portfolio Risk Analytics",
    suppress_callback_exceptions=True,
)

server = app.server  # Expose for WSGI / gunicorn deployment.

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            dbc.Col(
                html.H2(
                    "⚡ Portfolio Risk Analytics",
                    className="text-center my-3",
                ),
            )
        ),
        # Row 1: Portfolio construction panel
        dbc.Row(
            dbc.Col(portfolio_panel(), lg=12),
            className="mb-3",
        ),
        # Graphs rendered inside this div by the callback.
        html.Div(id="dashboard-content"),
    ],
    fluid=True,
    className="px-4 pb-4",
)


# ---------------------------------------------------------------------------
# Main callback — fires on Recalculate click.
# ---------------------------------------------------------------------------
@callback(
    Output("dashboard-content", "children"),
    Output("weight-validation", "children"),
    Input("recalc-btn", "n_clicks"),
    State({"type": "ticker-dd", "index": ALL}, "value"),
    State({"type": "weight-input", "index": ALL}, "value"),
    State("lookback-select", "value"),
    prevent_initial_call=False,  # render default view on load
)
def update_dashboard(n_clicks, tickers_raw, weights_raw, lookback):
    """
    Core callback: gather inputs, validate weights, fetch data, compute
    all risk metrics, and return the full dashboard layout.
    """

    # --- Parse & validate inputs -----------------------------------------
    pairs = [
        (t, float(w))
        for t, w in zip(tickers_raw, weights_raw)
        if t and w and float(w) > 0
    ]

    if not pairs:
        # Fall back to defaults on first load or empty input.
        pairs = list(DEFAULT_WEIGHTS.items())

    tickers = [p[0] for p in pairs]
    raw_weights = {p[0]: p[1] for p in pairs}
    total_weight = sum(raw_weights.values())

    # Validation badge.
    if abs(total_weight - 100) > 0.1:
        validation = dbc.Alert(
            f"Weights sum to {total_weight:.1f}% — must equal 100%. "
            "Results use normalised weights.",
            color="warning",
            className="py-1 px-2 mb-0",
        )
    else:
        validation = dbc.Alert(
            "✓ Weights valid", color="success", className="py-1 px-2 mb-0"
        )

    # Normalise weights to 0-1 scale.
    weights = {t: w / total_weight for t, w in raw_weights.items()}

    # --- Fetch data & compute returns ------------------------------------
    lookback_years = int(lookback) if lookback else 3
    all_tickers = list(set(tickers + [BENCHMARK]))
    prices = fetch_prices(all_tickers, lookback_years)

    # Ensure columns match requested tickers (handles case sensitivity).
    available = [c for c in all_tickers if c in prices.columns]
    prices = prices[available]
    returns = log_returns(prices)

    # Portfolio return series.
    # Only include tickers that are actually in the returns DataFrame.
    valid_weights = {t: weights[t] for t in weights if t in returns.columns}
    if not valid_weights:
        return html.P("No valid tickers found.", className="text-danger"), validation

    # Re-normalise after dropping missing tickers.
    w_sum = sum(valid_weights.values())
    valid_weights = {t: v / w_sum for t, v in valid_weights.items()}

    port_ret = portfolio_returns(returns, valid_weights)
    bench_ret = returns[BENCHMARK] if BENCHMARK in returns.columns else port_ret

    # --- Build charts ----------------------------------------------------
    fig_cum = cumulative_returns_chart(returns, port_ret)
    fig_corr = correlation_heatmap(correlation_matrix(returns))
    fig_rvol = rolling_vol_chart(port_ret, bench_ret)
    fig_scatter = risk_return_scatter(returns, valid_weights)
    fig_hist = return_histogram(port_ret)
    fig_dd = drawdown_chart(port_ret)

    # --- Summary metrics -------------------------------------------------
    cum_port = port_ret.cumsum().apply(np.exp) - 1
    metrics = {
        "Ann. Return": f"{annualised_return(port_ret):.1%}",
        "Ann. Vol": f"{annualised_vol(port_ret):.1%}",
        "Sharpe": f"{sharpe_ratio(port_ret):.2f}",
        "Max DD": f"{max_drawdown(cum_port):.1%}",
        "VaR 95%": f"{parametric_var(port_ret, 0.95):.2%}",
        "VaR 99%": f"{parametric_var(port_ret, 0.99):.2%}",
    }

    cards = summary_cards(metrics)

    # --- Assemble layout -------------------------------------------------
    content = html.Div(
        [
            # Row 2: cumulative returns + correlation
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_cum), lg=7),
                    dbc.Col(dcc.Graph(figure=fig_corr), lg=5),
                ],
                className="mb-3",
            ),
            # Row 3: rolling vol + risk-return scatter
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_rvol), lg=6),
                    dbc.Col(dcc.Graph(figure=fig_scatter), lg=6),
                ],
                className="mb-3",
            ),
            # Row 4: histogram + drawdown
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig_hist), lg=6),
                    dbc.Col(dcc.Graph(figure=fig_dd), lg=6),
                ],
                className="mb-3",
            ),
            # Row 5: summary cards
            cards,
        ]
    )

    return content, validation


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
