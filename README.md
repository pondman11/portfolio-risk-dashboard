# ⚡ Portfolio Risk Analytics Dashboard

Interactive portfolio risk analytics built with Plotly Dash. Dark-themed, narrative-driven layout.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://localhost:8050](http://localhost:8050)

## Features

- **Portfolio Construction** — sidebar with ticker/weight inputs, lookback period selector
- **KPI Cards** — annualised return, volatility, Sharpe, max drawdown, VaR at a glance
- **Cumulative Returns** — portfolio vs benchmark vs individual holdings
- **Rolling Volatility** — 30d/90d annualised vol with benchmark overlay
- **VaR Distribution** — daily return histogram with 95%/99% VaR thresholds
- **Correlation Heatmap** — pairwise return correlations
- **Risk-Return Scatter** — vol vs return per holding with portfolio highlighted
- **Drawdown Chart** — worst drawdown period highlighted

## Project Structure

```
├── app.py                     # Dash entry point, layout, callbacks
├── data_loader.py             # yfinance data retrieval + caching
├── risk_metrics.py            # VaR, Sharpe, drawdown, rolling vol
├── components/
│   ├── portfolio_input.py     # Sidebar panel
│   ├── charts.py              # All Plotly figure builders
│   └── cards.py               # KPI summary cards
├── requirements.txt
└── README.md
```

## Tech Stack

| Layer | Tool |
|---|---|
| Data | yfinance |
| Processing | pandas, numpy, scipy |
| Visualization | plotly, dash |
| Styling | dash-bootstrap-components (DARKLY) |
