"""
app.py — Portfolio Risk Analytics Dashboard

Entry point. Layout and callbacks.

Design: Sleek, minimal, premium dark UI. Data-forward, no clutter.
"""

import json
import dash
from dash import html, dcc, Input, Output, State, callback_context, no_update, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

import data_loader
import risk_metrics as rm
from components.portfolio_input import build_sidebar, DEFAULT_WEIGHTS
from components.cards import build_kpi_row
from components import charts

# ─── App init ────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
    title="Portfolio Risk",
    suppress_callback_exceptions=True,
)

server = app.server


# ─── Layout helpers ──────────────────────────────────────────────────

def _chart_card(children, **kwargs):
    """Wrap a chart in a glass-style card."""
    return dbc.Card(
        dbc.CardBody(children, style={"padding": "8px 4px"}),
        className="chart-card",
        **kwargs,
    )


# ─── Layout ──────────────────────────────────────────────────────────

app.layout = html.Div(
    [
        # Store for portfolio holdings: list of {"ticker": "AAPL", "weight": 20.0}
        dcc.Store(
            id="portfolio-store",
            data=[{"ticker": t, "weight": round(w * 100, 1)} for t, w in DEFAULT_WEIGHTS.items()],
        ),

        dbc.Row(
            [
                # ── Sidebar ──────────────────────────────────────
                dbc.Col(
                    build_sidebar(),
                    width=2,
                    style={"padding": 0},
                ),

                # ── Main content ─────────────────────────────────
                dbc.Col(
                    html.Div(
                        [
                            # KPI cards
                            html.Div(id="kpi-cards", className="mb-4"),

                            # Hero chart
                            dbc.Row(
                                dbc.Col(
                                    _chart_card(dcc.Graph(id="cum-returns-chart", config={"displayModeBar": False})),
                                    md=12,
                                ),
                                className="g-3 mb-3",
                            ),

                            # Risk row
                            dbc.Row(
                                [
                                    dbc.Col(
                                        _chart_card(dcc.Graph(id="rolling-vol-chart", config={"displayModeBar": False})),
                                        md=6,
                                    ),
                                    dbc.Col(
                                        _chart_card(dcc.Graph(id="var-histogram", config={"displayModeBar": False})),
                                        md=6,
                                    ),
                                ],
                                className="g-3 mb-3",
                            ),

                            # Diversification row
                            dbc.Row(
                                [
                                    dbc.Col(
                                        _chart_card(dcc.Graph(id="corr-heatmap", config={"displayModeBar": False})),
                                        md=6,
                                    ),
                                    dbc.Col(
                                        _chart_card(dcc.Graph(id="risk-return-scatter", config={"displayModeBar": False})),
                                        md=6,
                                    ),
                                ],
                                className="g-3 mb-3",
                            ),

                            # Drawdown
                            dbc.Row(
                                dbc.Col(
                                    _chart_card(dcc.Graph(id="drawdown-chart", config={"displayModeBar": False})),
                                    md=12,
                                ),
                                className="g-3 mb-4",
                            ),
                        ],
                        style={"padding": "28px 36px"},
                    ),
                    width=10,
                    style={"backgroundColor": "#0b0d10", "minHeight": "100vh"},
                ),
            ],
            className="g-0",
        ),
    ]
)


# ─── Helper: equal rebalance ─────────────────────────────────────────

def _equal_rebalance(holdings):
    """Set all holdings to equal weight summing to 100%."""
    n = len(holdings)
    if n == 0:
        return holdings
    w = round(100.0 / n, 1)
    for h in holdings:
        h["weight"] = w
    remainder = round(100.0 - w * n, 1)
    if holdings:
        holdings[0]["weight"] = round(holdings[0]["weight"] + remainder, 1)
    return holdings


# ─── Callbacks: Portfolio management ─────────────────────────────────

@app.callback(
    [
        Output("portfolio-store", "data"),
        Output("add-ticker-dropdown", "value"),
    ],
    [
        Input("add-ticker-dropdown", "value"),
        Input({"type": "remove-btn", "index": ALL}, "n_clicks"),
        Input({"type": "weight-input", "index": ALL}, "value"),
    ],
    [
        State("portfolio-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_portfolio_store(new_ticker, remove_clicks, weight_values, current_data):
    """Add, remove, or edit holdings. Add/remove auto-rebalance equally."""
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update

    trigger_id = ctx.triggered[0]["prop_id"]

    # ── Add stock
    if trigger_id == "add-ticker-dropdown.value":
        if not new_ticker:
            return no_update, no_update
        existing = {h["ticker"] for h in current_data}
        if new_ticker not in existing:
            current_data.append({"ticker": new_ticker, "weight": 0})
            current_data = _equal_rebalance(current_data)
        return current_data, None

    # ── Remove stock
    if "remove-btn" in trigger_id:
        btn_id = json.loads(trigger_id.split(".")[0])
        idx = btn_id["index"]
        if 0 <= idx < len(current_data):
            current_data.pop(idx)
            current_data = _equal_rebalance(current_data)
        return current_data, no_update

    # ── Edit weight
    if "weight-input" in trigger_id:
        btn_id = json.loads(trigger_id.split(".")[0])
        idx = btn_id["index"]
        if 0 <= idx < len(current_data):
            val = weight_values[idx]
            if val is not None and val >= 0:
                current_data[idx]["weight"] = round(float(val), 1)
        return current_data, no_update

    return no_update, no_update


@app.callback(
    Output("holdings-list", "children"),
    Input("portfolio-store", "data"),
)
def render_holdings(holdings):
    """Render the holdings list with inline editable weights."""
    if not holdings:
        return html.P("No holdings", style={"color": "#4a5060", "fontSize": "0.8rem", "textAlign": "center"})

    rows = []
    for i, h in enumerate(holdings):
        color = charts.PALETTE[(i + 1) % len(charts.PALETTE)]
        row = html.Div(
            [
                html.Div(
                    "",
                    style={
                        "width": "3px",
                        "height": "24px",
                        "backgroundColor": color,
                        "borderRadius": "2px",
                        "marginRight": "10px",
                        "flexShrink": "0",
                    },
                ),
                html.Span(h["ticker"], className="holding-ticker"),
                dbc.Input(
                    id={"type": "weight-input", "index": i},
                    type="number",
                    value=h["weight"],
                    min=0, max=100, step=0.1,
                    size="sm",
                    debounce=True,
                    style={
                        "width": "52px",
                        "backgroundColor": "transparent",
                        "border": "1px solid rgba(255,255,255,0.06)",
                        "color": "#8a92a0",
                        "textAlign": "right",
                        "fontSize": "0.78rem",
                        "padding": "2px 6px",
                        "borderRadius": "6px",
                        "marginRight": "2px",
                    },
                ),
                html.Span("%", style={"color": "#4a5060", "fontSize": "0.72rem", "marginRight": "8px"}),
                html.Button(
                    "×",
                    id={"type": "remove-btn", "index": i},
                    className="remove-btn",
                    n_clicks=0,
                ),
            ],
            className="holding-row",
        )
        rows.append(row)
    return rows


# ─── Callbacks: Dashboard update ─────────────────────────────────────

@app.callback(
    [
        Output("kpi-cards", "children"),
        Output("cum-returns-chart", "figure"),
        Output("rolling-vol-chart", "figure"),
        Output("var-histogram", "figure"),
        Output("corr-heatmap", "figure"),
        Output("risk-return-scatter", "figure"),
        Output("drawdown-chart", "figure"),
        Output("weight-validation", "children"),
    ],
    [Input("recalc-btn", "n_clicks")],
    [
        State("portfolio-store", "data"),
        State("period-select", "value"),
    ],
    prevent_initial_call=False,
)
def update_dashboard(n_clicks, holdings_data, period):
    """Master callback — recalculates everything."""

    # Parse portfolio from store
    portfolio = {}
    for h in (holdings_data or []):
        t = h.get("ticker", "").strip().upper()
        w = float(h.get("weight", 0))
        if t and w > 0:
            portfolio[t] = w / 100.0

    if not portfolio:
        portfolio = {"AAPL": 0.2, "MSFT": 0.2, "JNJ": 0.2, "JPM": 0.2, "XOM": 0.2}

    total_weight = sum(portfolio.values())

    # Validation
    if abs(total_weight - 1.0) < 0.01:
        validation = html.Div(
            "✓ 100%",
            className="weight-badge",
            style={"color": "#00d4aa", "backgroundColor": "rgba(0,212,170,0.1)"},
        )
    else:
        validation = html.Div(
            f"⚠ {total_weight:.0%}",
            className="weight-badge",
            style={"color": "#ffd93d", "backgroundColor": "rgba(255,217,61,0.1)"},
        )

    # Fetch data
    ticker_list = list(portfolio.keys())
    prices = data_loader.fetch_prices(ticker_list, period=period or "3Y")

    available = [t for t in ticker_list if t in prices.columns]
    if not available:
        empty = _empty_figures()
        return (html.Div("No data found.", style={"color": "#5a6270"}), *empty, validation)

    # Re-normalise weights
    w_sum = sum(portfolio[t] for t in available)
    weights = {t: portfolio[t] / w_sum for t in available}

    returns = rm.log_returns(prices)
    port_ret = rm.portfolio_returns(returns, weights)

    # ── Portfolio metrics ─────────────────────────────────────
    ann_ret = rm.annualised_return(port_ret)
    ann_vol = rm.annualised_vol(port_ret)
    sharpe = rm.sharpe_ratio(port_ret)
    cum_ret = (1 + port_ret).cumprod() - 1
    mdd = rm.max_drawdown(cum_ret)
    var_95 = rm.parametric_var(port_ret, 0.95)
    var_99 = rm.parametric_var(port_ret, 0.99)

    # ── Benchmark metrics (SPY) ───────────────────────────────
    bench = None
    if "SPY" in returns.columns:
        spy_ret = returns["SPY"]
        b_ann_ret = rm.annualised_return(spy_ret)
        b_ann_vol = rm.annualised_vol(spy_ret)
        b_sharpe = rm.sharpe_ratio(spy_ret)
        b_cum = (1 + spy_ret).cumprod() - 1
        b_mdd = rm.max_drawdown(b_cum)
        bench = {
            "ann_return": b_ann_ret,
            "ann_vol": b_ann_vol,
            "sharpe": b_sharpe,
            "max_dd": b_mdd,
        }

    kpi = build_kpi_row(
        {
            "ann_return": ann_ret,
            "ann_vol": ann_vol,
            "sharpe": sharpe,
            "max_dd": mdd,
        },
        bench=bench,
    )

    # ── Charts ────────────────────────────────────────────────
    fig_cum = charts.cumulative_returns_chart(returns, port_ret, "SPY")

    vol30 = rm.rolling_volatility(port_ret, 30)
    vol90 = rm.rolling_volatility(port_ret, 90)
    bench_vol30 = rm.rolling_volatility(returns["SPY"], 30) if "SPY" in returns.columns else None
    fig_vol = charts.rolling_vol_chart(vol30, vol90, bench_vol30)

    fig_var = charts.var_histogram(port_ret, var_95, var_99)

    holding_cols = [t for t in available if t != "SPY"]
    corr = rm.correlation_matrix(returns[holding_cols]) if len(holding_cols) > 1 else rm.correlation_matrix(returns[available])
    fig_corr = charts.correlation_heatmap(corr)

    ticker_data = []
    for t in available:
        if t == "SPY":
            continue
        t_ret = rm.annualised_return(returns[t])
        t_vol = rm.annualised_vol(returns[t])
        t_sharpe = rm.sharpe_ratio(returns[t])
        ticker_data.append({"ticker": t, "return": t_ret, "vol": t_vol, "sharpe": t_sharpe})

    portfolio_point = {"return": ann_ret, "vol": ann_vol, "sharpe": sharpe}
    fig_scatter = charts.risk_return_scatter(ticker_data, portfolio_point)

    dd = rm.drawdown_series(cum_ret)
    try:
        dd_window = rm.max_drawdown_window(cum_ret)
    except Exception:
        dd_window = None
    fig_dd = charts.drawdown_chart(dd, dd_window)

    return (kpi, fig_cum, fig_vol, fig_var, fig_corr, fig_scatter, fig_dd, validation)


def _empty_figures():
    """Return 6 empty figures for error states."""
    import plotly.graph_objects as go
    empty = go.Figure()
    empty.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text="No data", showarrow=False, font=dict(size=16, color="#4a5060"))],
    )
    return (empty,) * 6


# ─── Run ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
