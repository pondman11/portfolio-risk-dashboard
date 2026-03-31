"""
app.py — Portfolio Risk Analytics Dashboard

Entry point. Layout and callbacks.

NARRATIVE FLOW (top → bottom):
  1. KPI Cards — instant snapshot of portfolio health
  2. Cumulative Returns — how is the portfolio performing?
  3. Rolling Volatility + VaR — how risky is it right now?
  4. Correlation Heatmap + Risk-Return Scatter — is it diversified?
  5. Drawdown — what's the worst-case scenario?

Design: Dark theme, sidebar for controls, main area for analysis.
"""

import dash
from dash import html, dcc, Input, Output, State, ALL, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

import data_loader
import risk_metrics as rm
from components.portfolio_input import build_sidebar
from components.cards import build_kpi_row
from components import charts

# ─── App init ────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    title="Portfolio Risk Analytics",
    suppress_callback_exceptions=True,
)

server = app.server  # for gunicorn / deployment


# ─── Custom CSS ──────────────────────────────────────────────────────



# ─── Layout ──────────────────────────────────────────────────────────

def _chart_card(children, **kwargs):
    """Wrap a chart in a styled card."""
    return dbc.Card(
        dbc.CardBody(children, style={"padding": "12px"}),
        style={
            "backgroundColor": "#12141a",
            "border": "1px solid #1e2028",
            "borderRadius": "8px",
        },
        **kwargs,
    )


app.layout = html.Div(
    [
        

        dbc.Row(
            [
                # ── Sidebar ──────────────────────────────────────
                dbc.Col(
                    build_sidebar(),
                    width=2,
                    style={"padding": 0, "borderRight": "1px solid #1e2028"},
                ),

                # ── Main content ─────────────────────────────────
                dbc.Col(
                    html.Div(
                        [
                            # Section 1: KPI cards
                            html.P("PORTFOLIO OVERVIEW", className="section-header mt-2"),
                            html.Div(id="kpi-cards"),

                            # Section 2: Hero chart — cumulative returns
                            html.P("PERFORMANCE", className="section-header"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        _chart_card(dcc.Graph(id="cum-returns-chart", config={"displayModeBar": False})),
                                        md=12,
                                    ),
                                ],
                                className="g-3 mb-4",
                            ),

                            # Section 3: Risk analysis
                            html.P("RISK ANALYSIS", className="section-header"),
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
                                className="g-3 mb-4",
                            ),

                            # Section 4: Diversification
                            html.P("DIVERSIFICATION", className="section-header"),
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
                                className="g-3 mb-4",
                            ),

                            # Section 5: Worst case
                            html.P("WORST CASE", className="section-header"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        _chart_card(dcc.Graph(id="drawdown-chart", config={"displayModeBar": False})),
                                        md=12,
                                    ),
                                ],
                                className="g-3 mb-4",
                            ),
                        ],
                        style={"padding": "24px 32px"},
                    ),
                    width=10,
                    style={"backgroundColor": "#0d0f13", "minHeight": "100vh"},
                ),
            ],
            className="g-0",
        ),
    ]
)


# ─── Callbacks ───────────────────────────────────────────────────────

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
        State({"type": "ticker-input", "index": ALL}, "value"),
        State({"type": "weight-input", "index": ALL}, "value"),
        State("period-select", "value"),
    ],
    prevent_initial_call=False,
)
def update_dashboard(n_clicks, tickers, weights_pct, period):
    """Master callback — recalculates everything on button click or initial load."""

    # ── Parse inputs ─────────────────────────────────────────────
    portfolio = {}
    for t, w in zip(tickers, weights_pct):
        if t and w and float(w) > 0:
            portfolio[t.strip().upper()] = float(w) / 100.0

    if not portfolio:
        portfolio = {"AAPL": 0.2, "MSFT": 0.2, "JNJ": 0.2, "JPM": 0.2, "XOM": 0.2}

    total_weight = sum(portfolio.values())

    # Validation badge
    if abs(total_weight - 1.0) < 0.001:
        validation = dbc.Badge("✓ Weights sum to 100%", color="success", className="p-2")
    else:
        validation = dbc.Badge(
            f"⚠ Weights sum to {total_weight:.1%}",
            color="warning",
            className="p-2",
        )

    # ── Fetch data ───────────────────────────────────────────────
    ticker_list = list(portfolio.keys())
    prices = data_loader.fetch_prices(ticker_list, period=period or "3Y")

    # Ensure all requested tickers are in the dataframe
    available = [t for t in ticker_list if t in prices.columns]
    if not available:
        empty = _empty_figures()
        return (html.Div("No data found for the given tickers."), *empty, validation)

    # Re-normalise weights to available tickers
    w_sum = sum(portfolio[t] for t in available)
    weights = {t: portfolio[t] / w_sum for t in available}

    returns = rm.log_returns(prices)
    port_ret = rm.portfolio_returns(returns, weights)

    # ── KPI metrics ──────────────────────────────────────────────
    ann_ret = rm.annualised_return(port_ret)
    ann_vol = rm.annualised_vol(port_ret)
    sharpe = rm.sharpe_ratio(port_ret)
    cum_ret = (1 + port_ret).cumprod() - 1
    mdd = rm.max_drawdown(cum_ret)
    var_95 = rm.parametric_var(port_ret, 0.95)
    var_99 = rm.parametric_var(port_ret, 0.99)

    kpi = build_kpi_row({
        "ann_return": ann_ret,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_dd": mdd,
        "var_95": var_95,
        "var_99": var_99,
    })

    # ── Charts ───────────────────────────────────────────────────

    # 1) Cumulative returns
    fig_cum = charts.cumulative_returns_chart(returns, port_ret, "SPY")

    # 2) Rolling volatility
    vol30 = rm.rolling_volatility(port_ret, 30)
    vol90 = rm.rolling_volatility(port_ret, 90)
    bench_vol30 = rm.rolling_volatility(returns["SPY"], 30) if "SPY" in returns.columns else None
    fig_vol = charts.rolling_vol_chart(vol30, vol90, bench_vol30)

    # 3) VaR histogram
    fig_var = charts.var_histogram(port_ret, var_95, var_99)

    # 4) Correlation heatmap (holdings only, no benchmark)
    holding_cols = [t for t in available if t != "SPY"]
    corr = rm.correlation_matrix(returns[holding_cols]) if len(holding_cols) > 1 else rm.correlation_matrix(returns[available])
    fig_corr = charts.correlation_heatmap(corr)

    # 5) Risk-return scatter
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

    # 6) Drawdown
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
        paper_bgcolor="#12141a",
        plot_bgcolor="#12141a",
        annotations=[dict(text="No data", showarrow=False, font=dict(size=20, color="#636e72"))],
    )
    return (empty,) * 6


# ─── Run ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
