"""
portfolio_input.py — Ticker/weight input panel.

Provides a top-row card where users pick up to 10 tickers, assign percentage
weights, choose a lookback window, and hit Recalculate.  A validation badge
turns red when weights don't sum to 100%.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from data_loader import DEFAULT_TICKERS, BENCHMARK

# Tickers available in the dropdown (users can also type free-text).
TICKER_OPTIONS = [
    {"label": t, "value": t}
    for t in [
        "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA",
        "JNJ", "JPM", "XOM", "V", "PG", "UNH", "HD", "BAC",
    ]
]

# Default weights — equal-weight across non-benchmark tickers.
_non_bench = [t for t in DEFAULT_TICKERS if t != BENCHMARK]
DEFAULT_WEIGHTS = {t: round(100 / len(_non_bench), 2) for t in _non_bench}


def build_ticker_row(idx: int, ticker: str = "", weight: float = 0.0):
    """One row: ticker dropdown + weight input."""
    return dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id={"type": "ticker-dd", "index": idx},
                    options=TICKER_OPTIONS,
                    value=ticker or None,
                    placeholder="Ticker…",
                    clearable=True,
                    style={"color": "#000"},
                ),
                width=6,
            ),
            dbc.Col(
                dbc.Input(
                    id={"type": "weight-input", "index": idx},
                    type="number",
                    min=0,
                    max=100,
                    step=0.01,
                    value=weight if weight else None,
                    placeholder="%",
                ),
                width=6,
            ),
        ],
        className="mb-1",
    )


def portfolio_panel() -> dbc.Card:
    """Build the full portfolio construction card."""
    # Pre-populate rows for default tickers.
    rows = []
    for i, t in enumerate(_non_bench):
        rows.append(build_ticker_row(i, t, DEFAULT_WEIGHTS[t]))
    # Fill remaining slots up to 10.
    for i in range(len(_non_bench), 10):
        rows.append(build_ticker_row(i))

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Portfolio Construction", className="card-title"),
                html.P(
                    f"Benchmark: {BENCHMARK} (included automatically)",
                    className="text-muted small",
                ),
                # Lookback selector
                dbc.Row(
                    [
                        dbc.Col(html.Label("Lookback"), width=3),
                        dbc.Col(
                            dbc.Select(
                                id="lookback-select",
                                options=[
                                    {"label": "1 Year", "value": "1"},
                                    {"label": "3 Years", "value": "3"},
                                    {"label": "5 Years", "value": "5"},
                                ],
                                value="3",
                            ),
                            width=9,
                        ),
                    ],
                    className="mb-2",
                ),
                # Ticker / weight grid
                html.Div(rows, id="ticker-rows"),
                # Weight validation badge
                html.Div(
                    id="weight-validation",
                    className="mt-2",
                ),
                # Recalculate button
                dbc.Button(
                    "Recalculate",
                    id="recalc-btn",
                    color="primary",
                    className="mt-3 w-100",
                ),
            ]
        ),
        className="shadow-sm",
    )
