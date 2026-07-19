"""
Ocean Intelligence Platform - Model Training Pipeline
--------------------------------------------------------
Trains Linear Regression, Decision Tree, Random Forest and XGBoost
regressors to predict carbon_ppm from environmental features, evaluates
them with MAE / MSE / RMSE / R2, and persists the best model + a full
metrics/leaderboard JSON for the Model Performance page.
"""

import json
import os
import sys
import numpy as np
import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor
    XGBOOST_AVAILABLE = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_generator import get_or_create_dataset

FEATURES = [
    "temperature_c", "salinity_psu", "ph", "dissolved_oxygen_mgL",
    "chlorophyll_mgm3", "depth_m", "lat", "lon", "region_encoded",
]
TARGET = "carbon_ppm"

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "region_encoder.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "model_metrics.json")


def _prepare_features(df: pd.DataFrame, encoder: LabelEncoder = None):
    df = df.copy()
    if encoder is None:
        encoder = LabelEncoder()
        df["region_encoded"] = encoder.fit_transform(df["region"])
    else:
        df["region_encoded"] = encoder.transform(df["region"])
    X = df[FEATURES]
    y = df[TARGET]
    return X, y, encoder


def train_and_evaluate(force: bool = False):
    if os.path.exists(MODEL_PATH) and os.path.exists(METRICS_PATH) and not force:
        with open(METRICS_PATH) as f:
            metrics = json.load(f)
        return metrics

    df = get_or_create_dataset()
    X, y, encoder = _prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    candidates = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=10, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=150, max_depth=14, random_state=42, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.08, random_state=42)
                   if XGBOOST_AVAILABLE else
                   XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.08, random_state=42),
    }

    leaderboard = []
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        mse = mean_squared_error(y_test, preds)
        rmse = float(np.sqrt(mse))
        r2 = r2_score(y_test, preds)
        leaderboard.append({
            "model": name, "mae": round(mae, 4), "mse": round(mse, 4),
            "rmse": round(rmse, 4), "r2": round(r2, 4),
        })
        fitted[name] = model

    leaderboard.sort(key=lambda r: r["rmse"])
    best_name = leaderboard[0]["model"]
    best_model = fitted[best_name]

    # feature importance (best model, fallback to permutation-free coef for linear)
    if hasattr(best_model, "feature_importances_"):
        importances = dict(zip(FEATURES, [round(float(v), 4) for v in best_model.feature_importances_]))
    elif hasattr(best_model, "coef_"):
        coefs = np.abs(best_model.coef_)
        coefs = coefs / coefs.sum()
        importances = dict(zip(FEATURES, [round(float(v), 4) for v in coefs]))
    else:
        importances = {f: 0 for f in FEATURES}

    # learning curve for the best model
    train_sizes, train_scores, val_scores = learning_curve(
        best_model.__class__(**best_model.get_params()) if hasattr(best_model, "get_params") else best_model,
        X, y, cv=3, train_sizes=np.linspace(0.2, 1.0, 5), scoring="r2", n_jobs=-1,
    )

    preds_best = best_model.predict(X_test)
    residuals = (y_test.values - preds_best).tolist()

    metrics = {
        "leaderboard": leaderboard,
        "best_model": best_name,
        "xgboost_available": XGBOOST_AVAILABLE,
        "feature_importance": importances,
        "learning_curve": {
            "train_sizes": train_sizes.tolist(),
            "train_scores_mean": train_scores.mean(axis=1).tolist(),
            "val_scores_mean": val_scores.mean(axis=1).tolist(),
        },
        "actual_vs_predicted": {
            "actual": y_test.values[:400].tolist(),
            "predicted": preds_best[:400].tolist(),
        },
        "residuals_sample": residuals[:400],
        "n_train": len(X_train),
        "n_test": len(X_test),
        "features": FEATURES,
    }

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f)

    return metrics


def load_model():
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    with open(METRICS_PATH) as f:
        metrics = json.load(f)
    return model, encoder, metrics


if __name__ == "__main__":
    m = train_and_evaluate(force=True)
    print(json.dumps(m["leaderboard"], indent=2))
    print("Best model:", m["best_model"], "| XGBoost available:", m["xgboost_available"])
