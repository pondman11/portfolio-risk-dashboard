# Portfolio Risk Analytics Dashboard

Interactive Plotly Dash application for portfolio-level risk analytics. Pull historical equity prices from Yahoo Finance, construct a weighted portfolio, and visualise key risk metrics used by asset managers and risk analysts.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Dash](https://img.shields.io/badge/dash-2.14%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

| Feature | Description |
|---|---|
| **Portfolio Construction** | Pick up to 10 tickers, assign weights, choose 1/3/5-year lookback |
| **Cumulative Returns** | Portfolio vs. individual holdings vs. SPY benchmark |
| **Correlation Heatmap** | Pairwise return correlations for diversification analysis |
| **Rolling Volatility** | 30-day and 90-day annualised vol for portfolio and benchmark |
| **Risk–Return Scatter** | Annualised return vs. vol per holding, Sharpe on hover |
| **VaR Analysis** | Daily return histogram with parametric & historical VaR lines |
| **Drawdown Chart** | Drawdown curve with worst drawdown period highlighted |
| **Summary Cards** | Ann. return, vol, Sharpe, max drawdown, 95% & 99% VaR |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/pondman11/portfolio-risk-dashboard.git
cd portfolio-risk-dashboard

# Create a virtual environment (recommended)
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open **http://localhost:8050** in your browser.

## Project Structure

```
portfolio-risk-dashboard/
├── app.py                  # Dash entry point, layout, and callbacks
├── data_loader.py          # yfinance data retrieval and caching
├── risk_metrics.py         # VaR, Sharpe, drawdown, rolling vol calculations
├── components/
│   ├── portfolio_input.py  # Ticker/weight input panel
│   ├── charts.py           # Chart-building functions
│   └── cards.py            # Summary metric cards
├── requirements.txt
└── README.md
```

## Calculation Notes

- All calculations use **log returns** (`np.log(price / price.shift(1))`), standard in quantitative finance.
- Annualisation assumes **252 trading days** per year.
- **Parametric VaR** assumes normally distributed returns; **Historical VaR** uses empirical percentiles.
- Default risk-free rate: **5%** (configurable in `risk_metrics.py`).

## Tech Stack

- **Data:** `yfinance`
- **Processing:** `pandas`, `numpy`
- **Visualisation:** `plotly`, `dash`
- **Styling:** `dash-bootstrap-components` (DARKLY theme)

## License

MIT
