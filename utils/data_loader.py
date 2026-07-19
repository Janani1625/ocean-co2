"""Central data access & aggregation helpers used across all pages."""

import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_generator import get_or_create_dataset, REGIONS

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ocean_data.csv")


def load_data() -> pd.DataFrame:
    df = get_or_create_dataset(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df


def kpi_summary(df: pd.DataFrame) -> dict:
    latest_month = df["date"].max().to_period("M")
    prev_month = latest_month - 1
    cur = df[df["date"].dt.to_period("M") == latest_month]
    prev = df[df["date"].dt.to_period("M") == prev_month]

    def pct_change(cur_val, prev_val):
        if prev_val in (0, None) or pd.isna(prev_val):
            return 0.0
        return round(((cur_val - prev_val) / prev_val) * 100, 2)

    avg_carbon = cur["carbon_ppm"].mean()
    max_row = df.loc[df["carbon_ppm"].idxmax()]
    min_row = df.loc[df["carbon_ppm"].idxmin()]
    avg_temp = cur["temperature_c"].mean()

    prev_avg_carbon = prev["carbon_ppm"].mean() if len(prev) else avg_carbon
    prev_avg_temp = prev["temperature_c"].mean() if len(prev) else avg_temp

    health_score = ocean_health_score(df)
    active_alerts = estimate_active_alerts(df)

    return {
        "avg_carbon": round(avg_carbon, 2),
        "avg_carbon_change": pct_change(avg_carbon, prev_avg_carbon),
        "max_carbon": round(float(max_row["carbon_ppm"]), 2),
        "max_carbon_region": max_row["region"],
        "min_carbon": round(float(min_row["carbon_ppm"]), 2),
        "min_carbon_region": min_row["region"],
        "avg_temp": round(avg_temp, 2),
        "avg_temp_change": pct_change(avg_temp, prev_avg_temp),
        "health_score": health_score,
        "stations": df["station_id"].nunique(),
        "active_alerts": active_alerts,
        "records": len(df),
    }


def ocean_health_score(df: pd.DataFrame) -> int:
    """0-100 composite health score. Higher carbon/lower O2/lower pH -> lower score."""
    recent = df[df["date"] >= df["date"].max() - pd.Timedelta(days=30)]
    carbon_penalty = np.clip((recent["carbon_ppm"].mean() - 15) / (80 - 15), 0, 1)
    o2_bonus = np.clip((recent["dissolved_oxygen_mgL"].mean() - 2) / (9 - 2), 0, 1)
    ph_bonus = np.clip((recent["ph"].mean() - 7.6) / (8.2 - 7.6), 0, 1)
    score = 100 * (0.5 * (1 - carbon_penalty) + 0.25 * o2_bonus + 0.25 * ph_bonus)
    return int(round(score))


def health_category(score: int) -> tuple:
    if score >= 85:
        return "Excellent", "#10b981"
    if score >= 70:
        return "Good", "#22c55e"
    if score >= 50:
        return "Moderate", "#eab308"
    if score >= 30:
        return "Poor", "#f97316"
    return "Critical", "#ef4444"


def estimate_active_alerts(df: pd.DataFrame) -> int:
    recent = df[df["date"] >= df["date"].max() - pd.Timedelta(days=3)]
    n = 0
    n += (recent["carbon_ppm"] > 55).sum()
    n += (recent["dissolved_oxygen_mgL"] < 4.5).sum()
    n += (recent["ph"] < 7.85).sum()
    n += (recent["sensor_status"] == "Offline").sum()
    return int(min(n, 999))


def regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("region").agg(
        avg_carbon=("carbon_ppm", "mean"),
        max_carbon=("carbon_ppm", "max"),
        avg_temp=("temperature_c", "mean"),
        avg_o2=("dissolved_oxygen_mgL", "mean"),
        avg_ph=("ph", "mean"),
        stations=("station_id", "nunique"),
    ).reset_index()
    g["avg_carbon"] = g["avg_carbon"].round(2)
    g["max_carbon"] = g["max_carbon"].round(2)
    g["avg_temp"] = g["avg_temp"].round(2)
    g["avg_o2"] = g["avg_o2"].round(2)
    g["avg_ph"] = g["avg_ph"].round(3)
    g = g.sort_values("avg_carbon", ascending=False)
    return g


def station_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Latest reading per station, used for the map."""
    latest = df.sort_values("date").groupby("station_id").tail(1).reset_index(drop=True)
    return latest
