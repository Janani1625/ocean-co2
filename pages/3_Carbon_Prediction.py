import os
import sys
import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, footer, risk_pill, kpi_card
from utils.icons import icon
from utils.data_loader import load_data
from utils.prediction import predict_carbon
from utils.data_generator import REGIONS

st.set_page_config(page_title="Carbon Prediction | Ocean Intel", page_icon=None, layout="wide")
load_css()

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()
page_header("Carbon Prediction", "Enter environmental parameters to predict carbon concentration using the trained AI model", "target")

col_form, col_result = st.columns([1, 1.3])

with col_form:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Input Parameters", "Provide station environmental readings", "flask")

    region = st.selectbox("Ocean Region", list(REGIONS.keys()))
    region_meta = REGIONS[region]

    c1, c2 = st.columns(2)
    with c1:
        temperature_c = st.slider("Temperature (°C)", -2.0, 33.0, float(region_meta["base_temp"]), 0.1)
        salinity_psu = st.slider("Salinity (PSU)", 30.0, 39.0, 34.7, 0.1)
        ph = st.slider("pH", 7.5, 8.3, 8.05, 0.01)
        dissolved_oxygen = st.slider("Dissolved Oxygen (mg/L)", 2.0, 10.5, 6.5, 0.1)
    with c2:
        chlorophyll = st.slider("Chlorophyll (mg/m³)", 0.05, 6.0, 1.0, 0.05)
        depth_m = st.slider("Ocean Depth (m)", 20, 4500, 500, 10)
        lat = st.number_input("Latitude", -90.0, 90.0, float(region_meta["lat"]), 0.1)
        lon = st.number_input("Longitude", -180.0, 180.0, float(region_meta["lon"]), 0.1)

    predict_btn = st.button("Predict Carbon Concentration", use_container_width=True, icon=":material/insights:")
    st.markdown('</div>', unsafe_allow_html=True)

with col_result:
    if predict_btn:
        result = predict_carbon(temperature_c, salinity_psu, ph, dissolved_oxygen,
                                 chlorophyll, depth_m, lat, lon, region)
        st.session_state["last_prediction"] = result

    result = st.session_state.get("last_prediction")

    if result is None:
        st.markdown('<div class="oi-card" style="text-align:center; padding:60px 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex; justify-content:center; color:#22d3ee;">{icon("target", size=44, style="margin:0;")}</div>', unsafe_allow_html=True)
        st.markdown("Configure parameters and click **Predict Carbon Concentration** to generate an AI-powered prediction.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="oi-card">', unsafe_allow_html=True)
        section_title("Prediction Result", f"Model used: {result['model_used']}", "trending-up")
        pc1, pc2 = st.columns(2)
        with pc1:
            kpi_card("Predicted Carbon Concentration", f"{result['carbon_ppm']} ppm", "cloud", color="cyan")
        with pc2:
            kpi_card("Confidence Score", f"{result['confidence']}%", "target", color="emerald")

        pc3, pc4 = st.columns(2)
        with pc3:
            kpi_card("Ocean Health Score", f"{result['health_score']} / 100", "gauge", sub=f"Status: {result['health_category']}", color="purple")
        with pc4:
            kpi_card("Forecast Category", result["forecast_category"], "bar-chart", color="blue")

        st.markdown(f"**Risk Level:** {risk_pill(result['risk_level'])}", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"**{icon('compass', size=15)}Environmental Recommendation**", unsafe_allow_html=True)
        st.info(result["recommendation"])

        st.markdown(f"**{icon('search', size=15)}Prediction Explanation**", unsafe_allow_html=True)
        st.caption(f"Top contributing factors: {result['explanation']}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="oi-card">', unsafe_allow_html=True)
        section_title("Input Summary", "", "clipboard")
        summary = pd.DataFrame([{
            "Region": region, "Temperature (°C)": temperature_c, "Salinity (PSU)": salinity_psu,
            "pH": ph, "Dissolved O2 (mg/L)": dissolved_oxygen, "Chlorophyll (mg/m³)": chlorophyll,
            "Depth (m)": depth_m, "Latitude": lat, "Longitude": lon,
        }])
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

footer()
