"""
cards.py — KPI summary cards. Clean, minimal, with accent glow.
"""

import dash_bootstrap_components as dbc
from dash import html


def _kpi_card(title: str, value: str, color: str = "#00d4aa", subtitle: str = ""):
    """Single KPI card — large value, small label, subtle accent glow."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.P(
                    title,
                    className="mb-1",
                    style={
                        "fontSize": "0.68rem",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.08em",
                        "color": "#5a6270",
                        "fontWeight": "500",
                    },
                ),
                html.H3(
                    value,
                    className="mb-0",
                    style={"fontWeight": "700", "color": "#e8eaed", "fontSize": "1.6rem"},
                ),
                html.Small(subtitle, style={"color": "#4a5060", "fontSize": "0.7rem"}) if subtitle else None,
            ],
            style={"padding": "20px"},
        ),
        className="kpi-card h-100",
        style={
            "borderLeft": f"3px solid {color}",
            "borderLeftColor": color,
        },
    )


def build_kpi_row(metrics: dict) -> dbc.Row:
    """Build a row of 4 key KPI cards — the essentials only."""
    ann_ret = metrics.get("ann_return", 0)
    ann_vol = metrics.get("ann_vol", 0)
    sharpe = metrics.get("sharpe", 0)
    max_dd = metrics.get("max_dd", 0)

    ret_color = "#00d4aa" if ann_ret >= 0 else "#ff6b6b"
    sharpe_color = "#00d4aa" if sharpe >= 0.5 else "#ffd93d" if sharpe >= 0 else "#ff6b6b"

    cards = [
        dbc.Col(
            _kpi_card("Return", f"{ann_ret:+.1%}", color=ret_color),
            xs=6, md=3,
        ),
        dbc.Col(
            _kpi_card("Volatility", f"{ann_vol:.1%}", color="#6c5ce7"),
            xs=6, md=3,
        ),
        dbc.Col(
            _kpi_card("Sharpe", f"{sharpe:.2f}", color=sharpe_color),
            xs=6, md=3,
        ),
        dbc.Col(
            _kpi_card("Max Drawdown", f"{max_dd:.1%}", color="#ff6b6b"),
            xs=6, md=3,
        ),
    ]
    return dbc.Row(cards, className="g-3 mb-4")
