"""Rule-based environmental intelligence: narrative insights + recommendations.

These are deterministic, explainable rules driven by real statistics computed
from the dataset (trend slopes, regional comparisons, correlations) rather
than a black box, which keeps the "AI insight" cards accurate and auditable.
"""

import numpy as np
import pandas as pd


def generate_insights(df: pd.DataFrame, max_items: int = 6) -> list:
    insights = []
    recent = df[df["date"] >= df["date"].max() - pd.Timedelta(days=60)]

    # 1) Region with fastest carbon growth
    growth = {}
    for region, g in recent.groupby("region"):
        daily = g.groupby("date")["carbon_ppm"].mean().sort_index()
        if len(daily) >= 5:
            t = np.arange(len(daily))
            slope = np.polyfit(t, daily.values, 1)[0]
            growth[region] = slope
    if growth:
        fastest = max(growth, key=growth.get)
        slowest = min(growth, key=growth.get)
        if growth[fastest] > 0.01:
            insights.append({
                "icon": "trending-up", "type": "warning",
                "title": f"Carbon concentration rising in {fastest}",
                "text": f"Trend analysis shows carbon levels increasing at roughly "
                        f"{growth[fastest]*30:.2f} ppm/month over the last 60 days.",
            })
        if growth[slowest] < -0.005:
            insights.append({
                "icon": "check-circle", "type": "positive",
                "title": f"{slowest} remains environmentally stable",
                "text": f"Carbon levels have trended downward "
                        f"({growth[slowest]*30:.2f} ppm/month), indicating stable conditions.",
            })

    # 2) Temperature-carbon correlation
    corr = df[["temperature_c", "carbon_ppm"]].corr().iloc[0, 1]
    if corr > 0.4:
        insights.append({
            "icon": "thermometer", "type": "info",
            "title": "Temperature increase strongly correlated with carbon concentration",
            "text": f"Pearson correlation of {corr:.2f} across all monitoring stations "
                    f"confirms a consistent warming-carbon relationship.",
        })

    # 3) Highest risk region right now
    reg_avg = recent.groupby("region")["carbon_ppm"].mean().sort_values(ascending=False)
    if len(reg_avg):
        top_region = reg_avg.index[0]
        insights.append({
            "icon": "alert-triangle", "type": "warning",
            "title": f"{top_region} shows the highest average carbon concentration",
            "text": f"Averaging {reg_avg.iloc[0]:.1f} ppm over the last 60 days, "
                    f"well above the global mean of {recent['carbon_ppm'].mean():.1f} ppm.",
        })

    # 4) Dissolved oxygen concern
    low_o2 = recent[recent["dissolved_oxygen_mgL"] < 4.5]
    if len(low_o2) > 0:
        pct = len(low_o2) / len(recent) * 100
        if pct > 3:
            worst_region = low_o2.groupby("region").size().idxmax()
            insights.append({
                "icon": "wind", "type": "warning",
                "title": "Localized oxygen depletion detected",
                "text": f"{pct:.1f}% of recent readings fall below the 4.5 mg/L threshold, "
                        f"concentrated near {worst_region}.",
            })

    # 5) Sensor uptime
    offline_pct = (recent["sensor_status"] == "Offline").mean() * 100
    if offline_pct > 0.5:
        insights.append({
            "icon": "radio", "type": "info",
            "title": "Sensor network uptime slightly degraded",
            "text": f"{offline_pct:.1f}% of readings in the last 60 days came from offline "
                    f"or non-reporting sensors.",
        })

    # 6) Overall trend
    global_daily = recent.groupby("date")["carbon_ppm"].mean().sort_index()
    if len(global_daily) >= 5:
        slope = np.polyfit(np.arange(len(global_daily)), global_daily.values, 1)[0]
        direction = "accelerating" if slope > 0.02 else ("easing" if slope < -0.005 else "holding steady")
        insights.append({
            "icon": "globe", "type": "info",
            "title": f"Global average carbon trend is {direction}",
            "text": f"Across all monitored regions, average carbon concentration is "
                    f"changing at {slope*30:+.2f} ppm/month.",
        })

    return insights[:max_items]


def generate_recommendations(df: pd.DataFrame, region: str = None, carbon_level: float = None,
                              risk_level: str = None, max_items: int = 5) -> list:
    """Dynamic recommendations that respond to current conditions."""
    recs = []
    data = df if region in (None, "All Regions") else df[df["region"] == region]
    recent = data[data["date"] >= data["date"].max() - pd.Timedelta(days=30)]

    avg_carbon = carbon_level if carbon_level is not None else recent["carbon_ppm"].mean()
    avg_o2 = recent["dissolved_oxygen_mgL"].mean() if len(recent) else 6.5
    avg_ph = recent["ph"].mean() if len(recent) else 8.05
    offline_rate = (recent["sensor_status"] == "Offline").mean() if len(recent) else 0

    if avg_carbon > 55 or risk_level in ("Critical", "High"):
        recs.append({"icon": "search", "title": "Conduct field verification",
                      "text": "Elevated carbon readings warrant on-site sample collection to confirm sensor accuracy."})
        recs.append({"icon": "alert-triangle", "title": "Initiate environmental investigation",
                      "text": "Escalate to the environmental response team for root-cause analysis."})
    elif avg_carbon > 40:
        recs.append({"icon": "radio", "title": "Increase monitoring frequency",
                      "text": "Shorten the sampling interval in this region to catch developing trends earlier."})
        recs.append({"icon": "satellite", "title": "Deploy additional underwater sensors",
                      "text": "Improve spatial resolution around the highest-reading stations."})
    else:
        recs.append({"icon": "bar-chart", "title": "Maintain standard monitoring cadence",
                      "text": "Conditions are within normal range; continue routine surveillance."})

    if avg_o2 < 5:
        recs.append({"icon": "fish", "title": "Protect coral reef & marine ecosystems",
                      "text": "Low dissolved oxygen threatens sensitive species; prioritize habitat protection measures."})

    if avg_ph < 7.95:
        recs.append({"icon": "factory", "title": "Reduce industrial discharge",
                      "text": "Declining pH suggests acidification pressure; review nearby discharge permits."})

    if offline_rate > 0.02:
        recs.append({"icon": "tool", "title": "Schedule sensor maintenance",
                      "text": f"{offline_rate*100:.1f}% sensor downtime detected; dispatch a maintenance crew."})

    recs.append({"icon": "trending-up", "title": "Increase sampling density",
                  "text": "Add supplementary buoys along the carbon gradient for higher-confidence forecasting."})

    return recs[:max_items]


def risk_from_carbon(carbon_ppm: float, dissolved_o2: float = 6.5) -> str:
    risk_score = (carbon_ppm / 90) * 0.75 + (1 - min(dissolved_o2, 10) / 10.5) * 0.25
    if risk_score > 0.62:
        return "Critical"
    if risk_score > 0.45:
        return "High"
    if risk_score > 0.28:
        return "Medium"
    return "Low"
