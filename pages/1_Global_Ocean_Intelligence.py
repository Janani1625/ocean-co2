import os
import sys
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, footer, risk_pill
from utils.icons import icon
from utils.data_loader import load_data, station_snapshot, regional_summary
from utils.map_builder import build_ocean_map

st.set_page_config(page_title="Global Ocean Intelligence | Ocean Intel", page_icon=None, layout="wide")
load_css()

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()
page_header("Global Ocean Intelligence Map", "Interactive real-time monitoring network across all ocean regions", "globe")

# ---------------- Filters ----------------
fc1, fc2, fc3, fc4 = st.columns(4)
with fc1:
    region_filter = st.selectbox("Filter by Region", ["All Regions"] + sorted(df["region"].unique().tolist()))
with fc2:
    carbon_range = st.slider("Filter by Carbon Level (ppm)", 0, 90, (0, 90))
with fc3:
    date_range = st.date_input(
        "Filter by Date",
        value=(df["date"].max() - pd.Timedelta(days=30), df["date"].max()),
        min_value=df["date"].min(), max_value=df["date"].max(),
    )
with fc4:
    view_options = st.multiselect("Map Layers", ["Heatmap", "Station Clusters"], default=["Heatmap", "Station Clusters"])

filtered = df.copy()
if region_filter != "All Regions":
    filtered = filtered[filtered["region"] == region_filter]
if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered = filtered[(filtered["date"] >= pd.Timestamp(date_range[0])) & (filtered["date"] <= pd.Timestamp(date_range[1]))]
filtered = filtered[(filtered["carbon_ppm"] >= carbon_range[0]) & (filtered["carbon_ppm"] <= carbon_range[1])]

stations = station_snapshot(filtered) if len(filtered) else station_snapshot(df).iloc[0:0]

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title(f"Monitoring Network — {len(stations)} stations shown", "Click any marker for detailed station telemetry · use the layer control (top-right) to toggle overlays", "map")

if len(stations) == 0:
    st.warning("No stations match the current filters.")
else:
    fmap = build_ocean_map(
        stations,
        show_heatmap="Heatmap" in view_options,
        show_clusters="Station Clusters" in view_options,
    )
    st_folium(fmap, use_container_width=True, height=560, returned_objects=[])

st.markdown(f"""
<div style="display:flex; gap:18px; margin-top:10px; font-size:12.5px; flex-wrap:wrap; align-items:center;">
<span style="color:#22c55e;">{icon("circle", size=10)}</span><span>Low Risk (&lt;28 ppm)</span>
<span style="color:#eab308;">{icon("circle", size=10)}</span><span>Medium Risk (28-45 ppm)</span>
<span style="color:#f97316;">{icon("circle", size=10)}</span><span>High Risk (45-58 ppm)</span>
<span style="color:#ef4444;">{icon("circle", size=10)}</span><span>Critical Risk (&gt;58 ppm)</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Regional statistics ----------------
st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("Regional Statistics", "Aggregated across the filtered date range", "bar-chart")
reg = regional_summary(filtered) if len(filtered) else regional_summary(df).iloc[0:0]
if len(reg):
    display_reg = reg.rename(columns={
        "region": "Region", "avg_carbon": "Avg Carbon (ppm)", "max_carbon": "Max Carbon (ppm)",
        "avg_temp": "Avg Temp (°C)", "avg_o2": "Avg O2 (mg/L)", "avg_ph": "Avg pH", "stations": "Stations",
    })
    st.dataframe(display_reg, use_container_width=True, hide_index=True)
else:
    st.info("No data available for the current filter selection.")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Station detail explorer ----------------
st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("Station Detail Lookup", "Select a station to view its full latest reading and recommended action", "map-pin")
if len(stations):
    sel_station = st.selectbox("Monitoring Station", stations["station_id"].tolist())
    row = stations[stations["station_id"] == sel_station].iloc[0]

    d1, d2, d3, d4, d5, d6 = st.columns(6)
    d1.metric("Region", row["region"])
    d2.metric("Carbon", f"{row['carbon_ppm']:.2f} ppm")
    d3.metric("Temperature", f"{row['temperature_c']:.1f} °C")
    d4.metric("Salinity", f"{row['salinity_psu']:.1f} PSU")
    d5.metric("Dissolved O2", f"{row['dissolved_oxygen_mgL']:.2f} mg/L")
    d6.metric("Depth", f"{row['depth_m']} m")

    st.markdown(f"**Risk Level:** {risk_pill(row['risk_level'])}", unsafe_allow_html=True)

    action = "Conduct field verification and increase monitoring frequency" if row["risk_level"] in ("Critical", "High") \
        else ("Continue routine monitoring" if row["risk_level"] == "Medium" else "No action required — conditions nominal")
    st.info(f"**Recommended Action:** {action}")
else:
    st.info("No stations to display.")
st.markdown('</div>', unsafe_allow_html=True)

footer()
