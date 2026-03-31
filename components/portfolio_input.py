"""
portfolio_input.py — Sidebar portfolio construction panel.

Design: Clean, minimal. Default holdings shown as removable pills.
"+ Add Stock" button reveals a dropdown + weight input inline.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from data_loader import DEFAULT_TICKERS, AVAILABLE_TICKERS, PERIOD_MAP

# Default equal weights
DEFAULT_WEIGHTS = {t: round(1.0 / len(DEFAULT_TICKERS), 2) for t in DEFAULT_TICKERS}
_remainder = 1.0 - sum(DEFAULT_WEIGHTS.values())
DEFAULT_WEIGHTS[DEFAULT_TICKERS[0]] += _remainder


def build_sidebar() -> html.Div:
    """Sidebar with holdings list, add-stock form, period selector, and recalc button."""

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

            # Add stock button
            html.Button(
                "+ Add Stock",
                id="add-stock-btn",
                className="add-stock-btn w-100 mt-1 mb-2",
                n_clicks=0,
            ),

            # Add stock form (hidden by default)
            html.Div(
                id="add-stock-form",
                children=[
                    dcc.Dropdown(
                        id="new-ticker-dropdown",
                        options=[{"label": t, "value": t} for t in AVAILABLE_TICKERS],
                        placeholder="Select ticker…",
                        style={"marginBottom": "6px"},
                        className="dash-dropdown",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.Input(
                                id="new-weight-input",
                                type="number",
                                placeholder="Weight",
                                min=0, max=100, step=0.1,
                                size="sm",
                                style={
                                    "backgroundColor": "#1a1d23",
                                    "border": "1px solid #2a2d35",
                                    "color": "#e0e4ea",
                                    "borderRadius": "8px 0 0 8px",
                                    "fontSize": "0.8rem",
                                },
                            ),
                            dbc.InputGroupText(
                                "%",
                                style={
                                    "backgroundColor": "#1a1d23",
                                    "border": "1px solid #2a2d35",
                                    "color": "#5a6270",
                                    "borderRadius": "0 8px 8px 0",
                                    "fontSize": "0.8rem",
                                },
                            ),
                        ],
                        size="sm",
                        className="mb-2",
                    ),
                    dbc.Button(
                        "Add",
                        id="confirm-add-btn",
                        size="sm",
                        className="w-100",
                        style={
                            "backgroundColor": "rgba(0,212,170,0.15)",
                            "border": "1px solid rgba(0,212,170,0.3)",
                            "color": "#00d4aa",
                            "borderRadius": "8px",
                            "fontSize": "0.8rem",
                            "fontWeight": "500",
                        },
                        n_clicks=0,
                    ),
                ],
                style={"display": "none"},
            ),

            # Weight validation
            html.Div(id="weight-validation", className="mt-2 mb-3"),

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
            dbc.RadioItems(
                id="period-select",
                options=[{"label": k, "value": k} for k in PERIOD_MAP],
                value="3Y",
                inline=True,
                className="mb-4 period-btn",
                input_class_name="btn-check",
                label_class_name="btn btn-outline-secondary btn-sm me-1",
                label_checked_class_name="btn btn-sm me-1",
                label_checked_style={
                    "backgroundColor": "#00d4aa",
                    "borderColor": "#00d4aa",
                    "color": "#0b0d10",
                },
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
