"""
cards.py — Summary metric cards for the bottom row.

Each card shows a single KPI with a label and formatted value.
Uses dash-bootstrap-components Card for consistent styling.
"""

import dash_bootstrap_components as dbc
from dash import html


def metric_card(title: str, value: str, color: str = "light") -> dbc.Card:
    """
    Build a single summary metric card.

    Parameters
    ----------
    title : str
        Label shown above the number (e.g. "Annualised Return").
    value : str
        Pre-formatted string (e.g. "12.3%").
    color : str
        Bootstrap colour token (light, success, danger, …).
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.P(title, className="card-title text-muted mb-1 small"),
                html.H4(value, className="card-text fw-bold"),
            ]
        ),
        color=color,
        inverse=True if color not in ("light", "white") else False,
        className="shadow-sm text-center",
    )


def summary_cards(metrics: dict[str, str]) -> dbc.Row:
    """
    Build a responsive row of metric cards.

    Parameters
    ----------
    metrics : dict
        Mapping of label → formatted value, e.g.
        {"Annualised Return": "12.3%", "Sharpe Ratio": "0.87", …}
    """
    cols = [
        dbc.Col(metric_card(k, v, "dark"), xs=6, md=4, lg=2, className="mb-2")
        for k, v in metrics.items()
    ]
    return dbc.Row(cols)
