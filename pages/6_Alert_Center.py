import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, apply_plotly_theme, footer, kpi_card, risk_pill
from utils.icons import icon
from utils.data_loader import load_data
from utils.alerts import generate_alerts, SEVERITY_COLOR

st.set_page_config(page_title="Alert Center | Ocean Intel", page_icon=None, layout="wide")
load_css()

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()
page_header("Alert Center", "Automatically generated environmental and system alerts", "alert-triangle")

lookback = st.slider("Lookback window (days)", 1, 30, 7)
alerts_df = generate_alerts(df, lookback_days=lookback)

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Total Alerts", f"{len(alerts_df)}", "bell", color="cyan")
with k2:
    critical_n = (alerts_df["severity"] == "Critical").sum() if len(alerts_df) else 0
    kpi_card("Critical", f"{critical_n}", "alert-triangle", color="red")
with k3:
    high_n = (alerts_df["severity"] == "High").sum() if len(alerts_df) else 0
    kpi_card("High", f"{high_n}", "alert-triangle", color="amber")
with k4:
    regions_affected = alerts_df["region"].nunique() if len(alerts_df) else 0
    kpi_card("Regions Affected", f"{regions_affected}", "globe", color="purple")

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Alerts by Type", "", "bar-chart")
    if len(alerts_df):
        counts = alerts_df["label"].value_counts().reset_index()
        counts.columns = ["Alert Type", "Count"]
        fig = px.bar(counts, x="Count", y="Alert Type", orientation="h", color="Count",
                     color_continuous_scale="OrRd")
        st.plotly_chart(apply_plotly_theme(fig, 320), use_container_width=True)
    else:
        st.success("No alerts in the selected window.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Alerts by Region", "", "globe")
    if len(alerts_df):
        counts = alerts_df["region"].value_counts().reset_index()
        counts.columns = ["Region", "Count"]
        fig = px.pie(counts, names="Region", values="Count", hole=0.5,
                     color_discrete_sequence=px.colors.sequential.Sunset)
        st.plotly_chart(apply_plotly_theme(fig, 320), use_container_width=True)
    else:
        st.success("No alerts in the selected window.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("Alert History", f"{len(alerts_df)} alerts in the last {lookback} days", "clipboard")

fcol1, fcol2 = st.columns(2)
with fcol1:
    sev_filter = st.multiselect("Filter by Severity", ["Critical", "High", "Medium", "Low"],
                                 default=["Critical", "High", "Medium", "Low"])
with fcol2:
    region_filter = st.multiselect("Filter by Region", sorted(df["region"].unique().tolist()),
                                    default=sorted(df["region"].unique().tolist()))

if len(alerts_df):
    view = alerts_df[alerts_df["severity"].isin(sev_filter) & alerts_df["region"].isin(region_filter)]
    for _, a in view.iterrows():
        color = SEVERITY_COLOR.get(a["severity"], "#3b82f6")
        st.markdown(
            f"""<div class="oi-card" style="padding:12px 16px; margin-bottom:8px; border-left:4px solid {color};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="font-size:14px; display:flex; align-items:center;">{icon(a['icon'], size=15)}{a['label']}</b>
                <span style="font-size:11.5px; color:#93a7c0;">{pd.to_datetime(a['timestamp']).strftime('%d %b %Y, %H:%M')}</span>
            </div>
            <div style="font-size:12.5px; color:#93a7c0; margin-top:4px;">
                {a['region']} · Station {a['station_id']} · {a['message']}
            </div>
            <div style="margin-top:6px;">{risk_pill(a['severity'])}</div>
            </div>""", unsafe_allow_html=True)
    if len(view) == 0:
        st.info("No alerts match the current filters.")
else:
    st.success("No active alerts — all monitoring stations report normal conditions.")
st.markdown('</div>', unsafe_allow_html=True)

footer()
