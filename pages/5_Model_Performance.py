import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, apply_plotly_theme, footer, kpi_card
from models.train_model import train_and_evaluate

st.set_page_config(page_title="Model Performance | Ocean Intel", page_icon=None, layout="wide")
load_css()

@st.cache_resource
def get_metrics():
    return train_and_evaluate()

metrics = get_metrics()
page_header("Model Performance", "Comparison of machine learning models trained to predict carbon concentration", "settings")

if not metrics.get("xgboost_available", True):
    st.info("XGBoost is not installed in this environment — the 'XGBoost' slot used a Gradient Boosting fallback with an equivalent API. Install `xgboost` (see requirements.txt) for the exact algorithm.")

lb = pd.DataFrame(metrics["leaderboard"])
best = metrics["best_model"]

k1, k2, k3, k4 = st.columns(4)
best_row = lb.iloc[0]
with k1:
    kpi_card("Best Model", best, "trophy", color="emerald")
with k2:
    kpi_card("R² Score", f"{best_row['r2']*100:.2f}%", "target", color="cyan")
with k3:
    kpi_card("RMSE", f"{best_row['rmse']:.3f} ppm", "ruler", color="blue")
with k4:
    kpi_card("MAE", f"{best_row['mae']:.3f} ppm", "ruler", color="purple")

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("Model Leaderboard", "Ranked by RMSE on held-out test data (lower is better)", "trophy")
lb_display = lb.rename(columns={"model": "Model", "mae": "MAE", "mse": "MSE", "rmse": "RMSE", "r2": "R² Score"})
st.dataframe(
    lb_display.style.background_gradient(subset=["RMSE"], cmap="RdYlGn_r").format({"MAE": "{:.3f}", "MSE": "{:.3f}", "RMSE": "{:.3f}", "R² Score": "{:.3f}"}),
    use_container_width=True, hide_index=True,
)
fig = px.bar(lb, x="model", y="rmse", color="rmse", color_continuous_scale="RdYlGn_r", text="rmse")
fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
st.plotly_chart(apply_plotly_theme(fig, 360), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Feature Importance", f"Drivers of carbon prediction ({best})", "star")
    fi = pd.DataFrame(list(metrics["feature_importance"].items()), columns=["feature", "importance"])
    fi = fi.sort_values("importance", ascending=True)
    fig = px.bar(fi, x="importance", y="feature", orientation="h", color="importance",
                 color_continuous_scale="Teal")
    st.plotly_chart(apply_plotly_theme(fig, 380), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Actual vs Predicted", "Test set predictions from the best model", "target")
    av = metrics["actual_vs_predicted"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=av["actual"], y=av["predicted"], mode="markers",
                              marker=dict(color="#22d3ee", size=6, opacity=0.55), name="Predictions"))
    lims = [min(av["actual"] + av["predicted"]), max(av["actual"] + av["predicted"])]
    fig.add_trace(go.Scatter(x=lims, y=lims, mode="lines", line=dict(color="#f59e0b", dash="dash"), name="Perfect Fit"))
    fig.update_xaxes(title="Actual (ppm)")
    fig.update_yaxes(title="Predicted (ppm)")
    st.plotly_chart(apply_plotly_theme(fig, 380), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Residual Plot", "Prediction errors across the test set", "trending-down")
    residuals = metrics["residuals_sample"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=residuals, mode="markers", marker=dict(color="#a855f7", size=6, opacity=0.55)))
    fig.add_hline(y=0, line_dash="dash", line_color="#f59e0b")
    fig.update_yaxes(title="Residual (ppm)")
    fig.update_xaxes(title="Test sample index")
    st.plotly_chart(apply_plotly_theme(fig, 380), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Learning Curve", "Training vs. validation R² as sample size grows", "trending-up")
    lc = metrics["learning_curve"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lc["train_sizes"], y=lc["train_scores_mean"], name="Training Score",
                              line=dict(color="#22d3ee", width=3)))
    fig.add_trace(go.Scatter(x=lc["train_sizes"], y=lc["val_scores_mean"], name="Validation Score",
                              line=dict(color="#f97316", width=3)))
    fig.update_xaxes(title="Training samples")
    fig.update_yaxes(title="R² Score")
    st.plotly_chart(apply_plotly_theme(fig, 380), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("Performance Summary", "", "clipboard")
st.markdown(f"""
- **Best performing model:** {best}, selected automatically based on lowest RMSE on the held-out test set.
- **Training set size:** {metrics['n_train']:,} records &nbsp;|&nbsp; **Test set size:** {metrics['n_test']:,} records
- **Features used:** {', '.join(metrics['features'])}
- The model is retrained automatically whenever `model_metrics.json` or `trained_model.pkl` are missing, and persisted with `joblib` for fast reuse across all pages.
""")
st.markdown('</div>', unsafe_allow_html=True)

footer()
