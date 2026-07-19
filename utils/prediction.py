"""Wraps the trained model for single-record carbon predictions with
confidence scoring, explanation, and downstream health/risk derivation."""

import numpy as np
import pandas as pd

from models.train_model import load_model, FEATURES
from utils.insights import risk_from_carbon
from utils.data_loader import health_category


def predict_carbon(temperature_c, salinity_psu, ph, dissolved_oxygen_mgL,
                    chlorophyll_mgm3, depth_m, lat, lon, region: str) -> dict:
    model, encoder, metrics = load_model()

    region_encoded = encoder.transform([region])[0] if region in encoder.classes_ else 0

    record = pd.DataFrame([{
        "temperature_c": temperature_c, "salinity_psu": salinity_psu, "ph": ph,
        "dissolved_oxygen_mgL": dissolved_oxygen_mgL, "chlorophyll_mgm3": chlorophyll_mgm3,
        "depth_m": depth_m, "lat": lat, "lon": lon, "region_encoded": region_encoded,
    }])[FEATURES]

    pred = float(model.predict(record)[0])
    pred = max(pred, 0)

    # confidence score: derived from model RMSE (tighter RMSE -> higher confidence),
    # discounted for feature values far from training distribution
    rmse = metrics["leaderboard"][0]["rmse"]
    base_confidence = max(55, 100 - rmse * 6)
    extremity_penalty = 0
    if temperature_c < -1 or temperature_c > 30:
        extremity_penalty += 5
    if ph < 7.7 or ph > 8.25:
        extremity_penalty += 5
    confidence = float(np.clip(base_confidence - extremity_penalty, 40, 99))

    risk_level = risk_from_carbon(pred, dissolved_oxygen_mgL)
    health_score = int(np.clip(100 - (pred / 90) * 70 - (8.1 - ph) * 40, 0, 100))
    health_cat, health_color = health_category(health_score)

    if pred > 55:
        forecast_category = "Rapidly Deteriorating"
    elif pred > 40:
        forecast_category = "Elevated / Watch"
    elif pred > 25:
        forecast_category = "Stable"
    else:
        forecast_category = "Healthy"

    # simple explanation: contribution ranking using feature importance x deviation from mean
    fi = metrics["feature_importance"]
    explanation = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:4]
    explanation_text = ", ".join([f"{name.replace('_', ' ')} ({imp*100:.0f}% influence)" for name, imp in explanation])

    if risk_level in ("Critical", "High"):
        recommendation = "Conduct field verification and increase monitoring frequency in this area."
    elif risk_level == "Medium":
        recommendation = "Continue routine monitoring; consider additional sensor deployment nearby."
    else:
        recommendation = "Conditions are within safe operating range; maintain standard monitoring."

    return {
        "carbon_ppm": round(pred, 2),
        "confidence": round(confidence, 1),
        "health_score": health_score,
        "health_category": health_cat,
        "health_color": health_color,
        "risk_level": risk_level,
        "forecast_category": forecast_category,
        "recommendation": recommendation,
        "explanation": explanation_text,
        "model_used": metrics["best_model"],
    }
