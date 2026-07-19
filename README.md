# 🌊 Ocean Intelligence Platform

**AI-Powered Marine Carbon Monitoring & Environmental Analytics**

An enterprise-grade Streamlit application for monitoring ocean environmental
conditions, forecasting carbon concentration with machine learning, detecting
anomalies, and generating actionable environmental insights.


## Features

- **Executive Dashboard** — animated KPI cards, global map snapshot, carbon trend, ocean health gauge, live insights, alerts, and a 30-day forecast preview.
- **Global Ocean Intelligence Map** — fully interactive Folium world map with heatmap overlay, marker clustering, risk color gradients, and region/date/carbon filters.
- **Analytics** — 10 interactive Plotly views: trends, seasonality, monthly & regional comparisons, correlation heatmap, distribution, scatter analysis, depth analysis, time series.
- **Carbon Prediction** — input environmental parameters and get an ML-predicted carbon level, confidence score, ocean health score, risk level, and recommendation.
- **Forecast Center** — 7 / 30 / 90 / 180-day carbon forecasts with confidence intervals and forecast-driven recommendations.
- **Model Performance** — leaderboard across Linear Regression, Decision Tree, Random Forest, and XGBoost with MAE/MSE/RMSE/R², feature importance, actual-vs-predicted, residuals, and learning curves.
- **Alert Center** — automatically generated alerts (rapid carbon increase, high carbon, temperature spikes, low oxygen, low pH, sensor offline) with full filterable history.
- **Reports** — Executive / Carbon Monitoring / Monthly / Regional / Prediction reports, exportable as PDF, CSV, or Excel.
- **Data Explorer** — search, sort, filter, descriptive statistics, IQR-based outlier detection, CSV upload/download.
- **Settings** — theme, notification thresholds, auto-refresh interval, map and export preferences.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + custom glassmorphism CSS |
| Data Science | Pandas, NumPy, Scikit-learn, XGBoost, Joblib |
| Visualization | Plotly, Folium |
| Reports | ReportLab (PDF), OpenPyXL (Excel) |

---

## Project Structure

```
ocean_intel/
├── app.py                          # Main entry point — Executive Dashboard
├── requirements.txt
├── .streamlit/config.toml          # Theme configuration
├── assets/css/style.css            # Glassmorphism enterprise theme
├── data/ocean_data.csv             # Generated on first run
├── models/
│   ├── train_model.py              # Training pipeline (4 models compared)
│   ├── trained_model.pkl           # Best model (generated on first run)
│   ├── region_encoder.pkl
│   └── model_metrics.json
├── utils/
│   ├── data_generator.py           # Synthetic multi-station ocean dataset
│   ├── data_loader.py              # KPI & aggregation helpers
│   ├── forecasting.py              # Trend + seasonal forecasting engine
│   ├── alerts.py                   # Rule-based alert generation
│   ├── insights.py                 # Environmental insights & AI recommendations
│   ├── prediction.py               # Single-record prediction wrapper
│   ├── map_builder.py              # Folium interactive map builder
│   ├── reports.py                  # PDF / CSV / Excel report generation
│   └── ui.py                       # Reusable UI components (KPI cards, gauges…)
└── pages/
    ├── 1_Global_Ocean_Intelligence.py
    ├── 2_Analytics.py
    ├── 3_Carbon_Prediction.py
    ├── 4_Forecast_Center.py
    ├── 5_Model_Performance.py
    ├── 6_Alert_Center.py
    ├── 7_Reports.py
    ├── 8_Data_Explorer.py
    └── 9_Settings.py
```

---

## Getting Started

```bash
pip install -r requirements.txt
streamlit run app.py
```

On first launch the app will:
1. Generate a realistic 2-year synthetic ocean monitoring dataset (24 stations across 6 regions) and cache it to `data/ocean_data.csv`.
2. Train and compare four regression models, save the best one to `models/trained_model.pkl`, and cache evaluation metrics to `models/model_metrics.json`.

Subsequent runs reuse the cached dataset and model instantly. Delete `data/ocean_data.csv` or `models/trained_model.pkl` to force regeneration.

> **Note:** if `xgboost` is not installed in your environment, the training pipeline automatically falls back to `GradientBoostingRegressor` (same API) so the app still runs end-to-end — install `xgboost` per `requirements.txt` for the exact algorithm requested.

---

## Data Notes

The dataset is synthetically generated but internally consistent: carbon
concentration is modeled as a function of regional baseline, temperature,
seasonality, and a slow warming trend, so the ML models learn genuine signal
rather than noise. Swap in real monitoring data by replacing
`data/ocean_data.csv` with the same schema (see `utils/data_generator.py`
for column definitions) and deleting `models/trained_model.pkl` to retrain.
