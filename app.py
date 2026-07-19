"""
Ocean Intelligence Platform
AI-Powered Marine Carbon Monitoring & Environmental Analytics

Entry point — Executive Dashboard
"""

import os
import sys
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ui import (load_css, page_header, section_title, kpi_card,
                       apply_plotly_theme, insight_card, recommendation_card, footer, risk_pill)
from utils.icons import icon, icon_only
from utils.data_loader import load_data, kpi_summary, regional_summary, health_category, station_snapshot
from utils.alerts import generate_alerts, SEVERITY_COLOR
from utils.insights import generate_insights, generate_recommendations
from utils.forecasting import forecast_carbon
from models.train_model import train_and_evaluate

st.set_page_config(
    page_title="Ocean Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# ---------------------------------------------------------------- Sidebar
with st.sidebar:
    st.markdown(
        f"""<div style="display:flex; align-items:center; gap:10px; padding:6px 0 18px 0;">
        <div class="oi-page-icon" style="width:38px; height:38px;">{icon_only('waves', size=19)}</div>
        <div>
            <div style="font-weight:800; font-size:17px; line-height:1.1;">OCEAN INTEL</div>
            <div style="font-size:10.5px; letter-spacing:0.08em; color:#93a7c0;">CARBON MONITORING</div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.caption("Navigate using the pages above")
    st.markdown("---")
    st.markdown("**Quick Actions**")
    if st.button("Refresh Data", use_container_width=True, icon=":material/refresh:"):
        st.cache_data.clear()
        st.rerun()
    st.page_link("pages/6_Alert_Center.py", label="View Alerts", icon=":material/warning:")
    st.page_link("pages/7_Reports.py", label="Generate Report", icon=":material/description:")
    st.markdown("---")
    st.markdown(
        f"""<div style="font-size:12px; color:#93a7c0; display:flex; align-items:center;">
        {icon('clock', size=13)} {datetime.now().strftime('%d %b %Y, %H:%M:%S')}
        </div>""",
        unsafe_allow_html=True,
    )
    st.caption("Auto-refresh: 60s (manual)")

# ---------------------------------------------------------------- Data
@st.cache_data(ttl=3600)
def get_data():
    return load_data()

@st.cache_resource
def get_model_metrics():
    return train_and_evaluate()

df = get_data()
metrics = get_model_metrics()
kpis = kpi_summary(df)
reg_summary = regional_summary(df)
alerts_df = generate_alerts(df)
insights = generate_insights(df)
stations = station_snapshot(df)

# ---------------------------------------------------------------- Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(
        f"""<div style="margin-bottom: 18px;">
        <h1 style="margin-bottom:2px;">Monitoring System</h1>
        <p style="color:#93a7c0; font-size:14.5px;">Real-time AI-powered ocean carbon monitoring and prediction system</p>
        </div>""",
        unsafe_allow_html=True,
    )
with col_h2:
    st.markdown(
        f"""<div style="text-align:right; padding-top:18px;">
        <div style="font-size:13px; color:#93a7c0;">{datetime.now().strftime('%A, %d %B %Y')}</div>
        <div style="font-size:22px; font-weight:700;">{datetime.now().strftime('%H:%M:%S')}</div>
        </div>""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- KPI Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Average Carbon Level", f"{kpis['avg_carbon']} ppm", "cloud", kpis["avg_carbon_change"], color="cyan")
with c2:
    kpi_card("Highest Carbon Level", f"{kpis['max_carbon']} ppm", "bar-chart", sub=f"Region: {kpis['max_carbon_region']}", color="red")
with c3:
    kpi_card("Lowest Carbon Level", f"{kpis['min_carbon']} ppm", "leaf", sub=f"Region: {kpis['min_carbon_region']}", color="emerald")
with c4:
    kpi_card("Average Ocean Temperature", f"{kpis['avg_temp']} °C", "thermometer", kpis["avg_temp_change"], color="blue")

c5, c6, c7, c8 = st.columns(4)
with c5:
    cat, _ = health_category(kpis["health_score"])
    kpi_card("Ocean Health Score", f"{kpis['health_score']} / 100", "gauge", sub=f"Status: {cat}", color="purple")
with c6:
    best_r2 = metrics["leaderboard"][0]["r2"] * 100
    kpi_card("Prediction Accuracy", f"{best_r2:.1f}%", "target", sub=f"Model: {metrics['best_model']}", color="emerald")
with c7:
    kpi_card("Monitoring Stations", f"{kpis['stations']}", "radio", sub="Across 6 ocean regions", color="cyan")
with c8:
    kpi_card("Active Alerts", f"{kpis['active_alerts']}", "bell", sub="Requires attention" if kpis['active_alerts'] > 0 else "All clear", color="amber" if kpis['active_alerts'] > 0 else "emerald")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------- Carbon Trend + Regional Ranking
col_map, col_side = st.columns([2.1, 1])

with col_map:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Carbon Trend (Last 12 Months)", "Global monthly average carbon concentration", "trending-up")
    trend_df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=365)]
    trend_daily = trend_df.groupby(trend_df["date"].dt.to_period("M"))["carbon_ppm"].mean().reset_index()
    trend_daily["date"] = trend_daily["date"].dt.to_timestamp()
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_daily["date"], y=trend_daily["carbon_ppm"], mode="lines+markers",
        line=dict(color="#22d3ee", width=3), marker=dict(size=7, color="#0891b2"),
        fill="tozeroy", fillcolor="rgba(34,211,238,0.08)",
    ))
    fig_trend = apply_plotly_theme(fig_trend, height=300)
    fig_trend.update_yaxes(title="ppm")
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Regional Carbon Levels", "Average concentration across all monitored ocean regions", "bar-chart")
    reg_sorted = reg_summary.sort_values("avg_carbon", ascending=True)
    fig_reg = px.bar(
        reg_sorted, x="avg_carbon", y="region", orientation="h", text="avg_carbon",
        color="avg_carbon", color_continuous_scale=["#10b981", "#eab308", "#f97316", "#ef4444"],
    )
    fig_reg.update_traces(texttemplate="%{text:.1f} ppm", textposition="outside")
    fig_reg.update_layout(coloraxis_showscale=False)
    fig_reg.update_xaxes(title="Avg Carbon (ppm)")
    fig_reg.update_yaxes(title="")
    st.plotly_chart(apply_plotly_theme(fig_reg, 300), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Top 5 Highest-Risk Regions", "", "alert-triangle")
    top5 = reg_summary.head(5)
    for _, r in top5.iterrows():
        risk = "Critical" if r["avg_carbon"] > 55 else ("High" if r["avg_carbon"] > 40 else ("Medium" if r["avg_carbon"] > 28 else "Low"))
        st.markdown(
            f"""<div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid rgba(148,163,184,0.08);">
            <span style="font-size:13px;">{r['region']}</span>
            <span style="font-size:13px; font-weight:700;">{r['avg_carbon']} ppm {risk_pill(risk)}</span>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Top 5 Safest Regions", "", "check-circle")
    safest5 = reg_summary.sort_values("avg_carbon", ascending=True).head(5)
    for _, r in safest5.iterrows():
        risk = "Critical" if r["avg_carbon"] > 55 else ("High" if r["avg_carbon"] > 40 else ("Medium" if r["avg_carbon"] > 28 else "Low"))
        st.markdown(
            f"""<div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid rgba(148,163,184,0.08);">
            <span style="font-size:13px;">{r['region']}</span>
            <span style="font-size:13px; font-weight:700;">{r['avg_carbon']} ppm {risk_pill(risk)}</span>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Recent Monitoring Timeline", "Latest station updates", "clock")
    recent_updates = stations.sort_values("date", ascending=False).head(5)
    for _, r in recent_updates.iterrows():
        st.markdown(
            f"""<div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid rgba(148,163,184,0.08); font-size:12px;">
            <span>{r['station_id']} · {r['region']}</span>
            <span style="color:#93a7c0;">{pd.to_datetime(r['date']).strftime('%d %b')}</span>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------- Insights + Recommendations + Alerts
col_i, col_r, col_a = st.columns(3)

with col_i:
    st.markdown('<div class="oi-card" style="min-height:380px;">', unsafe_allow_html=True)
    section_title("Environmental Intelligence", "Automatically generated insights", "brain")
    for ins in insights[:4]:
        insight_card(ins["icon"], ins["title"], ins["text"], ins["type"])
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="oi-card" style="min-height:380px;">', unsafe_allow_html=True)
    section_title("AI Recommendations", "Actions based on current conditions", "cpu")
    recs = generate_recommendations(df)
    for r in recs[:4]:
        recommendation_card(r["icon"], r["title"], r["text"])
    st.markdown('</div>', unsafe_allow_html=True)

with col_a:
    st.markdown('<div class="oi-card" style="min-height:380px;">', unsafe_allow_html=True)
    section_title("Recent Alerts", f"{len(alerts_df)} in the last 7 days", "alert-triangle")
    if len(alerts_df) == 0:
        st.success("No active alerts — all systems nominal.")
    for _, a in alerts_df.head(5).iterrows():
        color = SEVERITY_COLOR.get(a["severity"], "#3b82f6")
        st.markdown(
            f"""<div class="oi-card" style="padding:12px 14px; margin-bottom:8px; border-left:3px solid {color};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="font-size:13px; display:flex; align-items:center;">{icon(a['icon'], size=14)}{a['label']}</b>
                <span style="font-size:11px; color:#93a7c0;">{pd.to_datetime(a['timestamp']).strftime('%d %b')}</span>
            </div>
            <div style="font-size:12px; color:#93a7c0; margin-top:3px;">{a['region']} · {a['message']}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- Quick forecast strip
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("30-Day Carbon Forecast Preview", "Full forecast controls available in the Forecast Center page", "radar")
fc = forecast_carbon(df, region=None, horizon_days=30)
fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(x=fc["history_dates"], y=fc["history_values"], name="Historical",
                             line=dict(color="#93a7c0", width=2)))
fig_fc.add_trace(go.Scatter(x=fc["forecast_dates"], y=fc["forecast_values"], name="Forecast",
                             line=dict(color="#22d3ee", width=3, dash="dash")))
fig_fc.add_trace(go.Scatter(
    x=list(fc["forecast_dates"]) + list(fc["forecast_dates"])[::-1],
    y=list(fc["upper"]) + list(fc["lower"])[::-1],
    fill="toself", fillcolor="rgba(34,211,238,0.12)", line=dict(color="rgba(0,0,0,0)"),
    name="90% Confidence", showlegend=True,
))
fig_fc = apply_plotly_theme(fig_fc, height=320)
st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False})
fcol1, fcol2, fcol3 = st.columns(3)
fcol1.metric("Trend Direction", fc["trend_direction"])
fcol2.metric("Expected Change", f"{fc['expected_change_pct']:+.2f}%")
fcol3.metric("30-Day Projection", f"{fc['forecast_end_value']} ppm")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- Feature strip
st.markdown("<br>", unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
feats = [
    ("check-circle", "Real-time Monitoring", "24/7 ocean data tracking"),
    ("cpu", "AI Powered Predictions", "Advanced ML algorithms"),
    ("satellite", "Multi-Source Data", "Satellite, Buoy & Sensor data"),
    ("lock", "Secure & Reliable", "Enterprise grade security"),
]
for col, (icon_name, title, sub) in zip([f1, f2, f3, f4], feats):
    with col:
        st.markdown(
            f"""<div class="oi-card" style="text-align:center; padding:16px;">
            <div style="display:flex; justify-content:center;">{icon(icon_name, size=24, style="margin:0;")}</div>
            <div style="font-weight:700; font-size:13.5px; margin-top:6px;">{title}</div>
            <div style="font-size:11.5px; color:#93a7c0;">{sub}</div>
            </div>""", unsafe_allow_html=True)

footer()
