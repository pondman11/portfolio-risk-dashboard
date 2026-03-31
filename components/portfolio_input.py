"""
portfolio_input.py — Sidebar portfolio construction panel.

Design: Clean sidebar with ticker/weight rows, period selector, and a CTA button.
Minimal chrome, clear labels, instant visual feedback on weight validation.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from data_loader import DEFAULT_TICKERS, PERIOD_MAP

# Default equal weights
DEFAULT_WEIGHTS = {t: round(1.0 / len(DEFAULT_TICKERS), 2) for t in DEFAULT_TICKERS}
# Fix rounding so it sums to 1.0
_remainder = 1.0 - sum(DEFAULT_WEIGHTS.values())
DEFAULT_WEIGHTS[DEFAULT_TICKERS[0]] += _remainder


def _ticker_row(ticker: str, weight: float, idx: int) -> dbc.Row:
    """Single ticker + weight input row."""
    return dbc.Row(
        [
            dbc.Col(
                dbc.Input(
                    id={"type": "ticker-input", "index": idx},
                    value=ticker,
                    placeholder="TICKER",
                    size="sm",
                    style={
                        "backgroundColor": "#1a1d23",
                        "border": "1px solid #2a2d35",
                        "color": "#e8eaed",
                        "fontFamily": "monospace",
                    },
                ),
                width=6,
            ),
            dbc.Col(
                dbc.Input(
                    id={"type": "weight-input", "index": idx},
                    type="number",
                    value=round(weight * 100, 1),
                    min=0, max=100, step=0.1,
                    size="sm",
                    style={
                        "backgroundColor": "#1a1d23",
                        "border": "1px solid #2a2d35",
                        "color": "#e8eaed",
                        "textAlign": "right",
                    },
                ),
                width=4,
            ),
            dbc.Col(
                html.Span("%", className="text-muted", style={"lineHeight": "31px"}),
                width=2,
                className="ps-0",
            ),
        ],
        className="g-2 mb-2",
    )


def build_sidebar() -> html.Div:
    """
    Build the sidebar portfolio construction panel.

    Contains: ticker/weight inputs, lookback selector, recalculate button,
    and a weight validation badge.
    """
    ticker_rows = [
        _ticker_row(t, w, i)
        for i, (t, w) in enumerate(DEFAULT_WEIGHTS.items())
    ]

    # Extra empty rows for adding tickers
    for i in range(len(DEFAULT_WEIGHTS), 10):
        ticker_rows.append(_ticker_row("", 0, i))

    return html.Div(
        [
            # Logo / title
            html.Div(
                [
                    html.H4(
                        "⚡ Portfolio Risk",
                        className="mb-0",
                        style={"color": "#e8eaed", "fontWeight": "700"},
                    ),
                    html.P(
                        "Analytics Dashboard",
                        className="text-muted mb-0",
                        style={"fontSize": "0.8rem"},
                    ),
                ],
                className="mb-4 pb-3",
                style={"borderBottom": "1px solid #2a2d35"},
            ),

            # Section label
            html.Label(
                "HOLDINGS",
                style={
                    "fontSize": "0.7rem",
                    "color": "#636e72",
                    "letterSpacing": "0.1em",
                    "textTransform": "uppercase",
                },
                className="mb-2",
            ),

            # Column headers
            dbc.Row(
                [
                    dbc.Col(html.Small("Ticker", className="text-muted"), width=6),
                    dbc.Col(html.Small("Weight", className="text-muted"), width=4),
                    dbc.Col(width=2),
                ],
                className="g-2 mb-1",
            ),

            # Ticker rows
            html.Div(ticker_rows, style={"maxHeight": "360px", "overflowY": "auto"}),

            # Weight validation
            html.Div(id="weight-validation", className="mt-2 mb-3"),

            # Lookback period
            html.Label(
                "LOOKBACK",
                style={
                    "fontSize": "0.7rem",
                    "color": "#636e72",
                    "letterSpacing": "0.1em",
                    "textTransform": "uppercase",
                },
                className="mb-2",
            ),
            dbc.RadioItems(
                id="period-select",
                options=[{"label": k, "value": k} for k in PERIOD_MAP],
                value="3Y",
                inline=True,
                className="mb-4",
                input_class_name="btn-check",
                label_class_name="btn btn-outline-secondary btn-sm me-1",
                label_checked_class_name="btn btn-sm me-1",
                label_checked_style={"backgroundColor": "#00d4aa", "borderColor": "#00d4aa", "color": "#12141a"},
            ),

            # Recalculate button
            dbc.Button(
                "Recalculate",
                id="recalc-btn",
                color="light",
                className="w-100",
                size="lg",
                style={
                    "backgroundColor": "#00d4aa",
                    "border": "none",
                    "color": "#12141a",
                    "fontWeight": "600",
                    "letterSpacing": "0.02em",
                },
            ),
        ],
        style={
            "backgroundColor": "#12141a",
            "padding": "24px",
            "height": "100vh",
            "position": "sticky",
            "top": 0,
            "overflowY": "auto",
        },
    )
