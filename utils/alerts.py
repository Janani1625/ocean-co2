"""Automatic environmental alert generation."""

import pandas as pd

ALERT_RULES = [
    {"code": "RAPID_CARBON_INCREASE", "label": "Rapid Carbon Increase", "severity": "High", "icon": "trending-up"},
    {"code": "HIGH_CARBON", "label": "High Carbon Concentration", "severity": "Critical", "icon": "alert-triangle"},
    {"code": "TEMP_SPIKE", "label": "Temperature Spike", "severity": "High", "icon": "thermometer"},
    {"code": "LOW_OXYGEN", "label": "Low Dissolved Oxygen", "severity": "High", "icon": "wind"},
    {"code": "LOW_PH", "label": "Low pH (Acidification)", "severity": "Medium", "icon": "flask"},
    {"code": "SENSOR_OFFLINE", "label": "Sensor Offline", "severity": "Medium", "icon": "radio"},
    {"code": "DATA_QUALITY", "label": "Data Quality Issue", "severity": "Low", "icon": "help-circle"},
]

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
SEVERITY_COLOR = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#eab308", "Low": "#3b82f6"}


def generate_alerts(df: pd.DataFrame, lookback_days: int = 7) -> pd.DataFrame:
    recent = df[df["date"] >= df["date"].max() - pd.Timedelta(days=lookback_days)].copy()
    recent = recent.sort_values("date")
    alerts = []

    for station_id, g in recent.groupby("station_id"):
        g = g.sort_values("date")
        region = g["region"].iloc[-1]
        last = g.iloc[-1]

        if len(g) >= 3:
            delta = g["carbon_ppm"].iloc[-1] - g["carbon_ppm"].iloc[0]
            span_days = max((g["date"].iloc[-1] - g["date"].iloc[0]).days, 1)
            rate = delta / span_days
            if rate > 1.1:
                alerts.append(_mk(last, "RAPID_CARBON_INCREASE",
                                   f"Carbon rising {rate:.2f} ppm/day at {station_id}"))

        if last["carbon_ppm"] > 58:
            alerts.append(_mk(last, "HIGH_CARBON", f"{last['carbon_ppm']:.2f} ppm recorded"))

        if len(g) >= 3:
            t_delta = g["temperature_c"].iloc[-1] - g["temperature_c"].mean()
            if t_delta > 3.5:
                alerts.append(_mk(last, "TEMP_SPIKE", f"{t_delta:+.1f}°C above local baseline"))

        if last["dissolved_oxygen_mgL"] < 4.2:
            alerts.append(_mk(last, "LOW_OXYGEN", f"{last['dissolved_oxygen_mgL']:.2f} mg/L"))

        if last["ph"] < 7.85:
            alerts.append(_mk(last, "LOW_PH", f"pH {last['ph']:.2f}"))

        if last["sensor_status"] == "Offline":
            alerts.append(_mk(last, "SENSOR_OFFLINE", "No data received in latest cycle"))

    if not alerts:
        return pd.DataFrame(columns=["timestamp", "station_id", "region", "code", "label",
                                      "severity", "icon", "message"])

    out = pd.DataFrame(alerts)
    out["severity_rank"] = out["severity"].map(SEVERITY_ORDER)
    out = out.sort_values(["severity_rank", "timestamp"], ascending=[True, False]).drop(columns="severity_rank")
    return out.reset_index(drop=True)


def _mk(row, code, message):
    rule = next(r for r in ALERT_RULES if r["code"] == code)
    return {
        "timestamp": row["date"],
        "station_id": row["station_id"],
        "region": row["region"],
        "code": code,
        "label": rule["label"],
        "severity": rule["severity"],
        "icon": rule["icon"],
        "message": message,
    }
