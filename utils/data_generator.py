"""
Ocean Intelligence Platform - Synthetic Data Generator
--------------------------------------------------------
Generates a realistic, internally-consistent ocean monitoring dataset
covering multiple regions, monitoring stations, and a multi-year daily
time series with correlated environmental variables.

This is NOT random noise: carbon concentration is modeled as a function
of temperature, depth, region baseline, seasonality and a slow warming
trend, so downstream ML models have real signal to learn.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

REGIONS = {
    "North Pacific":   {"lat": 40.0, "lon": -160.0, "base_carbon": 46, "base_temp": 14, "risk_bias": 0.35},
    "South Atlantic":   {"lat": -25.0, "lon": -20.0, "base_carbon": 34, "base_temp": 19, "risk_bias": 0.10},
    "Indian Ocean":     {"lat": -10.0, "lon": 75.0,  "base_carbon": 31, "base_temp": 22, "risk_bias": 0.05},
    "North Atlantic":   {"lat": 45.0, "lon": -35.0,  "base_carbon": 30, "base_temp": 12, "risk_bias": 0.05},
    "Southern Ocean":   {"lat": -60.0, "lon": 0.0,   "base_carbon": 22, "base_temp": 2,  "risk_bias": -0.10},
    "Arctic Ocean":     {"lat": 78.0, "lon": 20.0,   "base_carbon": 20, "base_temp": -1, "risk_bias": -0.05},
}

STATIONS_PER_REGION = 4


def _region_stations():
    """Generate fixed station coordinates scattered around each region centroid."""
    rng = np.random.default_rng(42)
    stations = []
    sid = 1000
    for region, meta in REGIONS.items():
        for i in range(STATIONS_PER_REGION):
            lat = np.clip(meta["lat"] + rng.normal(0, 6), -85, 85)
            lon = ((meta["lon"] + rng.normal(0, 10)) + 180) % 360 - 180
            stations.append({
                "station_id": f"STN-{sid}",
                "region": region,
                "lat": round(float(lat), 3),
                "lon": round(float(lon), 3),
                "depth_m": int(rng.uniform(20, 4500)),
            })
            sid += 1
    return pd.DataFrame(stations)


def generate_dataset(days: int = 730, seed: int = 7) -> pd.DataFrame:
    """Generate a daily multi-station ocean monitoring dataset.

    Parameters
    ----------
    days : number of days of history to simulate (ending today)
    seed : RNG seed for reproducibility

    Returns
    -------
    pd.DataFrame with one row per (station, date)
    """
    rng = np.random.default_rng(seed)
    stations = _region_stations()

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start_date, end_date, freq="D")

    rows = []
    for _, st in stations.iterrows():
        region_meta = REGIONS[st["region"]]
        base_carbon = region_meta["base_carbon"]
        base_temp = region_meta["base_temp"]
        risk_bias = region_meta["risk_bias"]

        # station-level idiosyncrasies
        station_offset = rng.normal(0, 2.5)
        warming_rate = rng.uniform(0.0025, 0.009)  # ppm/day upward drift
        noise_scale = rng.uniform(1.2, 2.6)

        for i, d in enumerate(dates):
            day_of_year = d.dayofyear
            season = np.sin(2 * np.pi * day_of_year / 365.25)

            temp = (base_temp + 4 * season + rng.normal(0, 1.1)
                    + 0.0015 * i)  # mild warming trend
            temp = float(np.clip(temp, -2, 33))

            trend_component = warming_rate * i
            carbon = (base_carbon + station_offset + trend_component
                      + 0.55 * (temp - base_temp)
                      + 2.2 * season
                      + rng.normal(0, noise_scale))
            carbon = float(np.clip(carbon, 5, 95))

            salinity = float(np.clip(34.7 + 0.4 * season + rng.normal(0, 0.4)
                                      - 0.02 * (st["region"] == "Arctic Ocean"), 30, 39))
            ph = float(np.clip(8.10 - 0.004 * carbon + rng.normal(0, 0.03), 7.55, 8.30))
            dissolved_o2 = float(np.clip(7.5 - 0.03 * (temp - 10) + rng.normal(0, 0.35), 2.0, 10.5))
            chlorophyll = float(np.clip(0.9 + 0.6 * season + rng.normal(0, 0.35)
                                         + (1.2 if st["region"] in ("Southern Ocean", "North Atlantic") else 0), 0.05, 6.0))

            # occasional sensor anomalies
            sensor_status = "Online"
            if rng.random() < 0.012:
                sensor_status = "Offline"

            risk_score = (carbon / 90) * 0.55 + (1 - dissolved_o2 / 10.5) * 0.25 + risk_bias * 0.2
            if risk_score > 0.62:
                risk_level = "Critical"
            elif risk_score > 0.45:
                risk_level = "High"
            elif risk_score > 0.28:
                risk_level = "Medium"
            else:
                risk_level = "Low"

            rows.append({
                "date": d,
                "station_id": st["station_id"],
                "region": st["region"],
                "lat": st["lat"],
                "lon": st["lon"],
                "depth_m": st["depth_m"],
                "temperature_c": round(temp, 2),
                "salinity_psu": round(salinity, 2),
                "ph": round(ph, 3),
                "dissolved_oxygen_mgL": round(dissolved_o2, 2),
                "chlorophyll_mgm3": round(chlorophyll, 2),
                "carbon_ppm": round(carbon, 2),
                "risk_level": risk_level,
                "sensor_status": sensor_status,
            })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "region", "station_id"]).reset_index(drop=True)
    return df


def get_or_create_dataset(path: str = "data/ocean_data.csv", force: bool = False) -> pd.DataFrame:
    import os
    if os.path.exists(path) and not force:
        df = pd.read_csv(path, parse_dates=["date"])
        return df
    df = generate_dataset()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return df


if __name__ == "__main__":
    d = get_or_create_dataset(force=True)
    print(d.shape)
    print(d.head())
