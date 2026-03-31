"""
cards.py — KPI summary cards for the dashboard header.

Design: Large metric number with a subtle label underneath.
Each card gets a contextual accent color via left border.
"""

import dash_bootstrap_components as dbc
from dash import html


def _kpi_card(title: str, value: str, color: str = "#00d4aa", subtitle: str = ""):
    """
    Single KPI card with accent left-border, large value, small label.

    Parameters
    ----------
    title : str   — Label (e.g. "Annualised Return")
    value : str   — Formatted value (e.g. "+12.4%")
    color : str   — Left-border accent color
    subtitle : str — Optional secondary info line
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.P(
                    title,
                    className="text-muted mb-1",
                    style={"fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "0.05em"},
                ),
                html.H3(
                    value,
                    className="mb-0",
                    style={"fontWeight": "700", "color": "#e8eaed"},
                ),
                html.Small(subtitle, className="text-muted") if subtitle else None,
            ]
        ),
        style={
            "borderLeft": f"4px solid {color}",
            "backgroundColor": "#1a1d23",
            "border": f"1px solid #2a2d35",
            "borderLeftWidth": "4px",
            "borderLeftColor": color,
        },
        className="h-100",
    )


def build_kpi_row(metrics: dict) -> dbc.Row:
    """
    Build a row of KPI cards from a dict of metric values.

    Expected keys:
        ann_return, ann_vol, sharpe, max_dd, var_95, var_99
    """
    ann_ret = metrics.get("ann_return", 0)
    ann_vol = metrics.get("ann_vol", 0)
    sharpe = metrics.get("sharpe", 0)
    max_dd = metrics.get("max_dd", 0)
    var_95 = metrics.get("var_95", 0)
    var_99 = metrics.get("var_99", 0)

    # Color logic: green for positive, red for negative
    ret_color = "#00d4aa" if ann_ret >= 0 else "#ff6b6b"
    sharpe_color = "#00d4aa" if sharpe >= 0 else "#ff6b6b"

    cards = [
        dbc.Col(
            _kpi_card(
                "Annualised Return",
                f"{ann_ret:+.1%}",
                color=ret_color,
            ),
            xs=6, sm=4, md=2,
        ),
        dbc.Col(
            _kpi_card(
                "Annualised Vol",
                f"{ann_vol:.1%}",
                color="#ffd93d",
            ),
            xs=6, sm=4, md=2,
        ),
        dbc.Col(
            _kpi_card(
                "Sharpe Ratio",
                f"{sharpe:.2f}",
                color=sharpe_color,
            ),
            xs=6, sm=4, md=2,
        ),
        dbc.Col(
            _kpi_card(
                "Max Drawdown",
                f"-{max_dd:.1%}",
                color="#ff6b6b",
            ),
            xs=6, sm=4, md=2,
        ),
        dbc.Col(
            _kpi_card(
                "VaR 95%",
                f"{var_95:.2%}",
                color="#ff9f43",
                subtitle="1-day parametric",
            ),
            xs=6, sm=4, md=2,
        ),
        dbc.Col(
            _kpi_card(
                "VaR 99%",
                f"{var_99:.2%}",
                color="#ee5a24",
                subtitle="1-day parametric",
            ),
            xs=6, sm=4, md=2,
        ),
    ]
    return dbc.Row(cards, className="g-3 mb-4")
