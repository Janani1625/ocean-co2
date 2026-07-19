"""
Carbon forecasting utilities.

Uses a per-region polynomial trend + seasonal decomposition fit on daily
aggregated history to project carbon_ppm forward, with a widening
confidence interval based on residual standard deviation.
"""

import numpy as np
import pandas as pd


def _daily_region_series(df: pd.DataFrame, region: str = None) -> pd.Series:
    data = df if region in (None, "All Regions") else df[df["region"] == region]
    daily = data.groupby("date")["carbon_ppm"].mean().sort_index()
    return daily


def forecast_carbon(df: pd.DataFrame, region: str = None, horizon_days: int = 30) -> dict:
    """Fit a trend+seasonal model and project `horizon_days` into the future.

    Returns dict with history (last 120 days), forecast dates/values, and
    upper/lower 90% confidence bounds.
    """
    daily = _daily_region_series(df, region)
    daily = daily.asfreq("D").interpolate()

    n = len(daily)
    t = np.arange(n)
    season = np.sin(2 * np.pi * t / 365.25)

    # design matrix: intercept, linear trend, seasonal component
    X = np.column_stack([np.ones(n), t, season])
    y = daily.values
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)

    fitted = X @ coef
    residual_std = float(np.std(y - fitted))

    future_t = np.arange(n, n + horizon_days)
    future_season = np.sin(2 * np.pi * future_t / 365.25)
    X_future = np.column_stack([np.ones(horizon_days), future_t, future_season])
    forecast_vals = X_future @ coef

    # widening interval with sqrt(time) growth, capped
    growth = np.sqrt(np.arange(1, horizon_days + 1))
    ci_width = 1.645 * residual_std * (1 + growth / 8)  # ~90% CI
    upper = forecast_vals + ci_width
    lower = forecast_vals - ci_width

    last_date = daily.index.max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon_days, freq="D")

    trend_slope = coef[1]
    start_val = float(forecast_vals[0])
    end_val = float(forecast_vals[-1])
    pct_change = ((end_val - float(daily.iloc[-1])) / float(daily.iloc[-1])) * 100 if daily.iloc[-1] else 0

    history_window = daily.tail(120)

    return {
        "history_dates": history_window.index,
        "history_values": history_window.values,
        "forecast_dates": future_dates,
        "forecast_values": np.clip(forecast_vals, 0, None),
        "upper": np.clip(upper, 0, None),
        "lower": np.clip(lower, 0, None),
        "trend_slope_per_day": float(trend_slope),
        "trend_direction": "Increasing" if trend_slope > 0.001 else ("Decreasing" if trend_slope < -0.001 else "Stable"),
        "expected_change_pct": round(float(pct_change), 2),
        "current_value": float(daily.iloc[-1]),
        "forecast_end_value": round(end_val, 2),
        "residual_std": residual_std,
    }
