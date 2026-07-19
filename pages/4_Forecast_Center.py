import os
import sys
import streamlit as st
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, apply_plotly_theme, footer, kpi_card
from utils.icons import icon
from utils.data_loader import load_data
from utils.forecasting import forecast_carbon
from utils.insights import generate_recommendations

st.set_page_config(page_title="Forecast Center | Ocean Intel", page_icon=None, layout="wide")
load_css()

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()
page_header("Carbon Forecast Center", "Machine-learning based projections of future carbon concentration", "radar")

fc1, fc2 = st.columns([1, 1])
with fc1:
    region = st.selectbox("Region", ["All Regions"] + sorted(df["region"].unique().tolist()))
with fc2:
    horizon_label = st.radio("Forecast Horizon", ["7 Days", "30 Days", "90 Days", "180 Days"], horizontal=True)
horizon_map = {"7 Days": 7, "30 Days": 30, "90 Days": 90, "180 Days": 180}
horizon = horizon_map[horizon_label]

fc = forecast_carbon(df, region=region, horizon_days=horizon)

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Current Carbon Level", f"{fc['current_value']:.2f} ppm", "map-pin", color="cyan")
with k2:
    kpi_card("Trend Direction", fc["trend_direction"], "trending-up" if fc["trend_direction"] == "Increasing" else "trending-down", color="amber" if fc["trend_direction"] == "Increasing" else "emerald")
with k3:
    kpi_card("Expected Change", f"{fc['expected_change_pct']:+.2f}%", "shuffle", color="purple")
with k4:
    kpi_card(f"{horizon_label} Projection", f"{fc['forecast_end_value']} ppm", "target", color="blue")

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title(f"{horizon_label} Carbon Forecast — {region}", "Shaded band represents the 90% confidence interval", "bar-chart")
fig = go.Figure()
fig.add_trace(go.Scatter(x=fc["history_dates"], y=fc["history_values"], name="Historical",
                          line=dict(color="#93a7c0", width=2)))
fig.add_trace(go.Scatter(x=fc["forecast_dates"], y=fc["forecast_values"], name="Forecast",
                          line=dict(color="#22d3ee", width=3, dash="dash")))
fig.add_trace(go.Scatter(
    x=list(fc["forecast_dates"]) + list(fc["forecast_dates"])[::-1],
    y=list(fc["upper"]) + list(fc["lower"])[::-1],
    fill="toself", fillcolor="rgba(34,211,238,0.14)", line=dict(color="rgba(0,0,0,0)"),
    name="90% Confidence Interval",
))
fig.add_vline(x=fc["history_dates"].max(), line_dash="dot", line_color="#f59e0b")
st.plotly_chart(apply_plotly_theme(fig, 460), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1, 1])
with col_a:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Forecast Confidence Meter", "Model uncertainty for this horizon", "calculator")
    conf = max(50, 95 - horizon * 0.18)
    st.progress(int(conf), text=f"{conf:.0f}% confidence at {horizon}-day horizon")
    st.caption("Confidence naturally decreases for longer horizons as uncertainty compounds over time.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Forecast-Driven Recommendations", "", "cpu")
    recs = generate_recommendations(df, region=region, carbon_level=fc["forecast_end_value"])
    for r in recs[:3]:
        st.markdown(f"**{icon(r['icon'], size=15)}{r['title']}**", unsafe_allow_html=True)
        st.caption(r["text"])
    st.markdown('</div>', unsafe_allow_html=True)

footer()
