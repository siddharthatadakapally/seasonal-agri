# Seasonal Agriculture Performance Analysis — Streamlit App

An interactive Streamlit dashboard built from the `Seasonal_Agriculture_Performance_Analysis`
notebook. It explores how farming performance (yield, cost, profit, water use) varies across
India's three growing seasons — **Kharif**, **Rabi**, and **Zaid**.

## Project layout

```
agri_app/
├── app.py                 # Streamlit app (entry point)
├── data/
│   └── seasonal_agriculture_performance_dataset.csv
├── pyproject.toml         # uv-managed project & dependencies
├── uv.lock                # locked dependency versions
└── README.md
```

## Run it (using uv)

1. Install [uv](https://docs.astral.sh/uv/) if you don't have it:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. From inside the `agri_app` folder, just run:
   ```bash
   uv run streamlit run app.py
   ```
   `uv` will automatically create a virtual environment and install the exact
   dependency versions from `uv.lock` on first run — no manual `pip install` needed.
3. Streamlit will open the app at `http://localhost:8501`.

## What's inside the app

- **Overview** — dataset shape, sample rows, summary statistics
- **Data Cleaning** — missing values found, median-fill strategy, duplicate check
- **Categorical Exploration** — record counts by season, crop, state, irrigation method
- **Season-wise Comparison** — average rainfall/temperature/yield/etc. per season, yield & weather boxplots
- **Profit & Loss** — % of loss-making farms overall and per season, profit distribution
- **Crop Yield** — average yield per crop, drill-down into a single crop's season performance
- **Irrigation & Water Efficiency** — water efficiency by irrigation method, water-used vs. yield scatter
- **Correlation with Yield** — correlation heatmap of key numeric drivers, seed quality by season
- **Key Insights** — summary takeaways from the analysis

Every chart page respects the **Season / State / Crop filters** in the sidebar, so you can
slice the whole dashboard interactively instead of just reading static notebook output.

## Data

`data/seasonal_agriculture_performance_dataset.csv` — 4,000 farm records across 8 states,
8 crops, and 3 seasons, with weather, soil, resource-use, and financial columns.
