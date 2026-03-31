"""
portfolio_input.py — Sidebar portfolio construction panel.

Design: Holdings as editable rows with inline weight inputs.
Add stock = dropdown only, auto-rebalances equally.
Remove = ×, auto-rebalances remaining equally.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from data_loader import DEFAULT_TICKERS, AVAILABLE_TICKERS, PERIOD_MAP

# Default equal weights
DEFAULT_WEIGHTS = {t: round(1.0 / len(DEFAULT_TICKERS), 2) for t in DEFAULT_TICKERS}
_remainder = 1.0 - sum(DEFAULT_WEIGHTS.values())
DEFAULT_WEIGHTS[DEFAULT_TICKERS[0]] += _remainder


def build_sidebar() -> html.Div:
    """Sidebar with holdings list, add-stock dropdown, period selector, recalc button."""

    return html.Div(
        [
            # ── Logo ──────────────────────────────────────────
            html.Div(
                [
                    html.H4(
                        "Portfolio Risk",
                        className="mb-0",
                        style={"color": "#e8eaed", "fontWeight": "700", "fontSize": "1.15rem"},
                    ),
                    html.P(
                        "analytics",
                        className="mb-0",
                        style={"fontSize": "0.72rem", "color": "#4a5060", "letterSpacing": "0.15em"},
                    ),
                ],
                className="mb-4 pb-3",
                style={"borderBottom": "1px solid rgba(255,255,255,0.05)"},
            ),

            # ── Holdings section ──────────────────────────────
            html.Label(
                "HOLDINGS",
                style={
                    "fontSize": "0.65rem",
                    "color": "#4a5060",
                    "letterSpacing": "0.12em",
                    "fontWeight": "600",
                },
                className="mb-2",
            ),

            # Dynamic holdings list (populated by callback)
            html.Div(id="holdings-list"),

            # Add stock — just a dropdown, adding auto-rebalances
            html.Div(
                dcc.Dropdown(
                    id="add-ticker-dropdown",
                    options=[{"label": t, "value": t} for t in AVAILABLE_TICKERS],
                    placeholder="+ Add stock…",
                    className="dash-dropdown",
                    value=None,
                ),
                className="mt-2 mb-2",
            ),

            # Weight validation
            html.Div(id="weight-validation", className="mb-3"),

            # ── Lookback period ───────────────────────────────
            html.Label(
                "PERIOD",
                style={
                    "fontSize": "0.65rem",
                    "color": "#4a5060",
                    "letterSpacing": "0.12em",
                    "fontWeight": "600",
                },
                className="mb-2",
            ),
            html.Div(
                dbc.RadioItems(
                    id="period-select",
                    options=[{"label": k, "value": k} for k in PERIOD_MAP],
                    value="3Y",
                    inline=True,
                    className="period-btn",
                    input_class_name="btn-check",
                    label_class_name="btn btn-outline-secondary btn-sm me-1",
                    label_checked_class_name="btn btn-sm me-1",
                    label_checked_style={
                        "backgroundColor": "#00d4aa",
                        "borderColor": "#00d4aa",
                        "color": "#0b0d10",
                    },
                ),
                style={"whiteSpace": "nowrap", "display": "flex", "flexWrap": "nowrap"},
                className="mb-4",
            ),

            # Spacer
            html.Div(style={"flex": "1"}),

            # ── Recalculate ───────────────────────────────────
            dbc.Button(
                "Recalculate",
                id="recalc-btn",
                className="w-100 recalc-btn",
                size="lg",
            ),
        ],
        className="sidebar d-flex flex-column",
        style={
            "padding": "24px 20px",
            "height": "100vh",
            "position": "sticky",
            "top": 0,
            "overflowY": "auto",
        },
    )
