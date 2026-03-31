# Portfolio Risk Analytics Dashboard

## Project Summary

A Plotly Dash application that pulls historical equity price data from Yahoo Finance (`yfinance`) and provides interactive portfolio-level risk analytics. The dashboard lets users construct a portfolio from a configurable list of tickers and weights, then visualizes key risk metrics that an asset management or wealth management team would use in practice.

### Data Source

- **Yahoo Finance** via the `yfinance` Python library (free, no API key required)
- Historical adjusted close prices, configurable lookback window (1Y, 3Y, 5Y)

### Target Audience

Portfolio managers, risk analysts, and investment operations teams at asset managers, wealth managers, or fund administrators.

### Key Features

1. **Portfolio Construction Panel** — Users select tickers (from a predefined universe or free-text input) and assign weights. Weights are validated to sum to 100%.
2. **Cumulative Returns Chart** — Line chart showing cumulative portfolio return vs. individual holdings and a benchmark (e.g., SPY) over the selected time window.
3. **Correlation Heatmap** — Plotly heatmap of pairwise return correlations across portfolio holdings. Useful for diversification analysis.
4. **Rolling Volatility** — Line chart of rolling 30-day and 90-day annualized volatility for the portfolio and benchmark.
5. **Value at Risk (VaR) Summary** — Cards displaying 1-day parametric VaR at 95% and 99% confidence, plus historical VaR. Optionally a histogram of daily returns with VaR thresholds drawn as vertical lines.
6. **Risk-Return Scatter** — Scatter plot of annualized return vs. annualized volatility for each holding, with the portfolio plotted as a highlighted point. Sharpe ratios displayed on hover.
7. **Max Drawdown Chart** — Drawdown curve over time for the portfolio, with the maximum drawdown period highlighted.

### Tech Stack

| Layer | Tool |
|---|---|
| Data retrieval | `yfinance` |
| Data processing | `pandas`, `numpy` |
| Visualization | `plotly`, `dash` |
| Layout/styling | `dash-bootstrap-components` |

### Project Structure

```
portfolio-risk-dashboard/
├── app.py                  # Dash app entry point, layout, and callbacks
├── data_loader.py          # yfinance data retrieval and caching
├── risk_metrics.py         # VaR, Sharpe, drawdown, rolling vol calculations
├── components/
│   ├── portfolio_input.py  # Ticker/weight input panel
│   ├── charts.py           # Chart-building functions
│   └── cards.py            # Summary metric cards
├── requirements.txt
└── README.md
```

### Calculation Notes

All calculations use **log returns** (`np.log(price / price.shift(1))`), which are additive across time and standard in quantitative finance. Annualization assumes 252 trading days. Parametric VaR assumes normally distributed returns; historical VaR uses the empirical percentile of the return distribution.

---

## AI Agent Build Prompt

```
You are building a Plotly Dash dashboard called "Portfolio Risk Analytics."

CONSTRAINTS:
- Python only. Use yfinance for data, pandas/numpy for calculations, plotly/dash
  for visualization, and dash-bootstrap-components for layout.
- All code must be well-commented explaining WHAT each section does and WHY.
- Separate concerns: data loading, risk metric calculations, and UI components
  should live in separate modules, not one monolithic file.
- Use log returns (np.log(price / price.shift(1))) for all return calculations.
  Annualize using 252 trading days.

DATA:
- Use yfinance to pull adjusted close prices for a configurable list of tickers.
- Default tickers: AAPL, MSFT, JNJ, JPM, XOM, SPY (SPY as benchmark).
- Default lookback: 3 years from today.
- Cache the downloaded data in memory so callbacks don't re-fetch on every
  interaction. Use a simple module-level dict or dcc.Store.

LAYOUT (use dash-bootstrap-components grid):
- Top row: Portfolio construction panel. Dropdowns or text inputs for up to
  10 tickers with weight sliders or numeric inputs. A "Recalculate" button.
  Show a validation message if weights don't sum to 100%.
- Second row, left: Cumulative returns line chart (portfolio vs. benchmark).
  Second row, right: Correlation heatmap of daily returns.
- Third row, left: Rolling volatility chart (30-day and 90-day windows,
  portfolio and benchmark). Third row, right: Risk-return scatter plot
  (annualized return vs. annualized vol per holding, Sharpe on hover).
- Fourth row, left: Daily return histogram with VaR threshold lines.
  Fourth row, right: Max drawdown chart with worst drawdown highlighted.
- Bottom row: Summary cards — annualized return, annualized vol, Sharpe ratio,
  max drawdown, 95% parametric VaR, 99% parametric VaR.

RISK METRIC IMPLEMENTATIONS:
- Sharpe Ratio: (annualized_return - risk_free_rate) / annualized_vol.
  Use 0.05 as the risk-free rate (or make it configurable).
- Parametric VaR: mean - z_score * std (z=1.645 for 95%, z=2.326 for 99%),
  scaled to 1-day horizon.
- Historical VaR: 5th and 1st percentile of empirical daily return distribution.
- Max Drawdown: max peak-to-trough decline in cumulative returns.
- Rolling Volatility: std of log returns over a rolling window, annualized.

STYLING:
- Use a dark theme (DARKLY or CYBORG bootstrap theme).
- Plotly chart template: "plotly_dark".
- Consistent color palette across all charts.

OUTPUT: Deliver all files in the project structure, with a requirements.txt
and a README.md explaining how to run the app locally.
```
