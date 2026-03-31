"""
cards.py — KPI summary cards with at-a-glance good/bad indicators.

Each card shows the portfolio metric, a delta vs benchmark (where applicable),
and a color-coded background tint so you can glance and know: am I winning?

Green = good, Red = bad, Amber = neutral/caution.
"""

import dash_bootstrap_components as dbc
from dash import html

# ─── Sentiment colors ────────────────────────────────────────────────
GOOD = "#00d4aa"
BAD = "#ff6b6b"
NEUTRAL = "#ffd93d"
GOOD_BG = "rgba(0,212,170,0.07)"
BAD_BG = "rgba(255,107,107,0.07)"
NEUTRAL_BG = "rgba(255,217,61,0.06)"


def _sentiment(is_good: bool | None):
    """Return (accent_color, bg_tint) based on sentiment."""
    if is_good is None:
        return NEUTRAL, NEUTRAL_BG
    return (GOOD, GOOD_BG) if is_good else (BAD, BAD_BG)


def _delta_badge(delta: float | None, fmt: str = "+.1%", flip: bool = False):
    """
    Small inline badge showing the delta.
    flip=True means lower is better (e.g. volatility, drawdown).
    """
    if delta is None:
        return None

    is_good = delta > 0 if not flip else delta < 0
    color = GOOD if is_good else BAD
    arrow = "▲" if delta > 0 else "▼" if delta < 0 else "–"

    formatted = f"{delta:{fmt}}" if "%" in fmt else f"{delta:+.2f}"

    return html.Span(
        f"{arrow} {formatted}",
        style={
            "fontSize": "0.68rem",
            "fontWeight": "600",
            "color": color,
            "backgroundColor": f"rgba({','.join(str(int(color[i:i+2], 16)) for i in (1,3,5))},0.12)",
            "padding": "2px 8px",
            "borderRadius": "6px",
            "marginLeft": "8px",
            "verticalAlign": "middle",
        },
    )


def _kpi_card(
    title: str,
    value: str,
    is_good: bool | None = None,
    delta: float | None = None,
    delta_fmt: str = "+.1%",
    delta_flip: bool = False,
    subtitle: str = "",
):
    """
    Single KPI card with sentiment coloring.

    is_good: True=green tint, False=red tint, None=amber
    delta: numeric delta vs benchmark (shown as badge)
    delta_flip: True if lower delta = better (vol, drawdown)
    """
    accent, bg_tint = _sentiment(is_good)

    return dbc.Card(
        dbc.CardBody(
            [
                html.P(
                    title,
                    className="mb-1",
                    style={
                        "fontSize": "0.65rem",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.08em",
                        "color": "#5a6270",
                        "fontWeight": "500",
                    },
                ),
                html.Div(
                    [
                        html.Span(
                            value,
                            style={"fontWeight": "700", "color": "#e8eaed", "fontSize": "1.5rem"},
                        ),
                        _delta_badge(delta, delta_fmt, delta_flip),
                    ],
                    style={"display": "flex", "alignItems": "baseline"},
                ),
                html.Small(subtitle, style={"color": "#4a5060", "fontSize": "0.68rem"}) if subtitle else None,
            ],
            style={"padding": "18px 20px"},
        ),
        className="kpi-card h-100",
        style={
            "borderLeft": f"3px solid {accent}",
            "borderLeftColor": accent,
            "background": f"linear-gradient(135deg, {bg_tint}, rgba(18,20,26,0.9))",
        },
    )


def build_kpi_row(metrics: dict, bench: dict | None = None) -> dbc.Row:
    """
    Build a row of 4 KPI cards with sentiment indicators.

    metrics: ann_return, ann_vol, sharpe, max_dd
    bench: same keys for benchmark (SPY). If provided, deltas are shown.
    """
    ann_ret = metrics.get("ann_return", 0)
    ann_vol = metrics.get("ann_vol", 0)
    sharpe = metrics.get("sharpe", 0)
    max_dd = metrics.get("max_dd", 0)

    b_ret = bench.get("ann_return", 0) if bench else None
    b_vol = bench.get("ann_vol", 0) if bench else None
    b_sharpe = bench.get("sharpe", 0) if bench else None
    b_dd = bench.get("max_dd", 0) if bench else None

    # Return: higher is better, compare vs benchmark
    ret_delta = (ann_ret - b_ret) if b_ret is not None else None
    ret_good = ann_ret > (b_ret or 0) if b_ret is not None else ann_ret > 0

    # Volatility: lower is better vs benchmark
    vol_delta = (ann_vol - b_vol) if b_vol is not None else None
    vol_good = ann_vol < (b_vol or 999) if b_vol is not None else ann_vol < 0.20

    # Sharpe: higher is better
    sharpe_delta = (sharpe - b_sharpe) if b_sharpe is not None else None
    sharpe_good = True if sharpe >= 0.5 else None if sharpe >= 0 else False

    # Max DD: lower is better
    dd_delta = (max_dd - b_dd) if b_dd is not None else None
    dd_good = max_dd < (b_dd or 999) if b_dd is not None else max_dd < 0.20

    cards = [
        dbc.Col(
            _kpi_card(
                "Return",
                f"{ann_ret:+.1%}",
                is_good=ret_good,
                delta=ret_delta,
                delta_fmt="+.1%",
                subtitle=f"vs SPY {b_ret:+.1%}" if b_ret is not None else "",
            ),
            xs=6, md=3,
        ),
        dbc.Col(
            _kpi_card(
                "Volatility",
                f"{ann_vol:.1%}",
                is_good=vol_good,
                delta=vol_delta,
                delta_fmt="+.1%",
                delta_flip=True,
                subtitle=f"vs SPY {b_vol:.1%}" if b_vol is not None else "",
            ),
            xs=6, md=3,
        ),
        dbc.Col(
            _kpi_card(
                "Sharpe",
                f"{sharpe:.2f}",
                is_good=sharpe_good,
                delta=sharpe_delta,
                delta_fmt="+.2f",
                subtitle=f"vs SPY {b_sharpe:.2f}" if b_sharpe is not None else "",
            ),
            xs=6, md=3,
        ),
        dbc.Col(
            _kpi_card(
                "Max Drawdown",
                f"{max_dd:.1%}",
                is_good=dd_good,
                delta=dd_delta,
                delta_fmt="+.1%",
                delta_flip=True,
                subtitle=f"vs SPY {b_dd:.1%}" if b_dd is not None else "",
            ),
            xs=6, md=3,
        ),
    ]
    return dbc.Row(cards, className="g-3 mb-4")
