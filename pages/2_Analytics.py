import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, apply_plotly_theme, footer
from utils.data_loader import load_data

st.set_page_config(page_title="Analytics | Ocean Intel", page_icon=None, layout="wide")
load_css()

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()
page_header("Analytics", "Deep-dive interactive analysis across every environmental dimension", "bar-chart")

regions = ["All Regions"] + sorted(df["region"].unique().tolist())
sel_region = st.selectbox("Region", regions)
data = df if sel_region == "All Regions" else df[df["region"] == sel_region]

tabs = st.tabs([
    "Carbon Trend", "Temperature Trend", "Seasonal Analysis", "Monthly Comparison",
    "Regional Comparison", "Correlation Heatmap", "Carbon Distribution",
    "Scatter Analysis", "Depth Analysis", "Time Series",
])

# ---------------- Carbon Trend ----------------
with tabs[0]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Carbon Concentration Trend", "Daily average with 7-day rolling smoothing", "trending-up")
    daily = data.groupby("date")["carbon_ppm"].mean().reset_index()
    daily["rolling"] = daily["carbon_ppm"].rolling(7).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["carbon_ppm"], name="Daily Avg",
                              line=dict(color="rgba(34,211,238,0.3)", width=1)))
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["rolling"], name="7-Day Trend",
                              line=dict(color="#22d3ee", width=3)))
    st.plotly_chart(apply_plotly_theme(fig, 420), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Temperature Trend ----------------
with tabs[1]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Ocean Temperature Trend", "Daily average with 7-day rolling smoothing", "thermometer")
    daily = data.groupby("date")["temperature_c"].mean().reset_index()
    daily["rolling"] = daily["temperature_c"].rolling(7).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["temperature_c"], name="Daily Avg",
                              line=dict(color="rgba(249,115,22,0.3)", width=1)))
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["rolling"], name="7-Day Trend",
                              line=dict(color="#f97316", width=3)))
    st.plotly_chart(apply_plotly_theme(fig, 420), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Seasonal Analysis ----------------
with tabs[2]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Seasonal Analysis", "Average carbon concentration by month across all years", "calendar")
    seasonal = data.copy()
    seasonal["month"] = seasonal["date"].dt.strftime("%b")
    seasonal["month_num"] = seasonal["date"].dt.month
    seasonal_agg = seasonal.groupby(["month", "month_num"])["carbon_ppm"].mean().reset_index().sort_values("month_num")
    fig = px.bar(seasonal_agg, x="month", y="carbon_ppm", color="carbon_ppm",
                 color_continuous_scale=["#10b981", "#eab308", "#ef4444"])
    st.plotly_chart(apply_plotly_theme(fig, 420), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Monthly Comparison ----------------
with tabs[3]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Monthly Comparison", "Month-over-month average carbon & temperature", "calendar")
    mc = data.copy()
    mc["ym"] = mc["date"].dt.to_period("M").dt.to_timestamp()
    mc_agg = mc.groupby("ym").agg(carbon=("carbon_ppm", "mean"), temp=("temperature_c", "mean")).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mc_agg["ym"], y=mc_agg["carbon"], name="Avg Carbon (ppm)", marker_color="#22d3ee", yaxis="y1"))
    fig.add_trace(go.Scatter(x=mc_agg["ym"], y=mc_agg["temp"], name="Avg Temp (°C)", line=dict(color="#f97316", width=3), yaxis="y2"))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, title="°C"))
    st.plotly_chart(apply_plotly_theme(fig, 420), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Regional Comparison ----------------
with tabs[4]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Regional Comparison", "Carbon concentration distribution by region", "globe")
    fig = px.box(df, x="region", y="carbon_ppm", color="region",
                 color_discrete_sequence=px.colors.sequential.Teal)
    fig.update_layout(showlegend=False)
    st.plotly_chart(apply_plotly_theme(fig, 420), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Correlation Heatmap ----------------
with tabs[5]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Correlation Heatmap", "Relationships between environmental variables", "layers")
    numeric_cols = ["temperature_c", "salinity_psu", "ph", "dissolved_oxygen_mgL", "chlorophyll_mgm3", "carbon_ppm", "depth_m"]
    corr = data[numeric_cols].corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="Tealrose", aspect="auto")
    st.plotly_chart(apply_plotly_theme(fig, 460), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Carbon Distribution ----------------
with tabs[6]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Carbon Distribution", "Frequency histogram of carbon readings", "bar-chart")
    fig = px.histogram(data, x="carbon_ppm", nbins=40, color_discrete_sequence=["#22d3ee"])
    st.plotly_chart(apply_plotly_theme(fig, 420), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Scatter Analysis ----------------
with tabs[7]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Scatter Analysis", "Carbon vs. any environmental variable", "target")
    x_var = st.selectbox("X-Axis Variable", ["temperature_c", "salinity_psu", "ph", "dissolved_oxygen_mgL", "chlorophyll_mgm3", "depth_m"], key="scatter_x")
    sample = data.sample(min(2000, len(data)), random_state=1)
    fig = px.scatter(sample, x=x_var, y="carbon_ppm", color="region", trendline="ols",
                      color_discrete_sequence=px.colors.sequential.Teal + px.colors.sequential.Blues)
    st.plotly_chart(apply_plotly_theme(fig, 440), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Depth Analysis ----------------
with tabs[8]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Ocean Depth Analysis", "Carbon concentration vs. depth", "ruler")
    sample = data.sample(min(2000, len(data)), random_state=1)
    fig = px.scatter(sample, x="depth_m", y="carbon_ppm", color="carbon_ppm",
                      color_continuous_scale=["#10b981", "#eab308", "#ef4444"], trendline="ols")
    st.plotly_chart(apply_plotly_theme(fig, 440), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Time Series (per region) ----------------
with tabs[9]:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Time Series Analysis", "Compare carbon trends across all regions", "trending-up")
    ts = df.groupby([df["date"].dt.to_period("M").dt.to_timestamp(), "region"])["carbon_ppm"].mean().reset_index()
    fig = px.line(ts, x="date", y="carbon_ppm", color="region",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(apply_plotly_theme(fig, 460), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

footer()
