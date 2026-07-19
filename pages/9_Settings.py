import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, footer

st.set_page_config(page_title="Settings | Ocean Intel", page_icon=None, layout="wide")
load_css()

page_header("Settings", "Configure platform appearance, notifications, and preferences", "settings")

if "settings" not in st.session_state:
    st.session_state.settings = {
        "theme": "Dark Mode",
        "notify_critical": True,
        "notify_high": True,
        "notify_medium": False,
        "refresh_interval": 60,
        "map_style": "Dark Ocean",
        "default_export": "PDF",
    }

s = st.session_state.settings

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Theme", "Visual appearance of the platform", "palette")
    s["theme"] = st.radio("Interface Theme", ["Dark Mode", "Light Mode"],
                           index=0 if s["theme"] == "Dark Mode" else 1)
    if s["theme"] == "Light Mode":
        st.info("Light Mode is in preview — the enterprise dashboard is optimized for Dark Mode, which offers the best contrast for map visualizations and risk indicators.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Map Preferences", "", "map")
    s["map_style"] = st.selectbox("Base Map Style", ["Dark Ocean", "Satellite", "Terrain"],
                                   index=["Dark Ocean", "Satellite", "Terrain"].index(s["map_style"]) if s["map_style"] in ["Dark Ocean", "Satellite", "Terrain"] else 0)
    st.checkbox("Show heatmap layer by default", value=True, key="map_heatmap_default")
    st.checkbox("Cluster station markers by default", value=True, key="map_cluster_default")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Notification Settings", "Choose which alert severities trigger notifications", "bell")
    s["notify_critical"] = st.checkbox("Notify on Critical alerts", value=s["notify_critical"])
    s["notify_high"] = st.checkbox("Notify on High severity alerts", value=s["notify_high"])
    s["notify_medium"] = st.checkbox("Notify on Medium severity alerts", value=s["notify_medium"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Auto Refresh", "", "clock")
    s["refresh_interval"] = st.slider("Auto-refresh interval (seconds)", 15, 300, s["refresh_interval"], 15)
    st.caption(f"Dashboard data will refresh every {s['refresh_interval']} seconds when auto-refresh is enabled.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Export Preferences", "", "download")
    s["default_export"] = st.selectbox("Default report format", ["PDF", "CSV", "Excel"],
                                        index=["PDF", "CSV", "Excel"].index(s["default_export"]))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
st.success("Settings are saved for this session. They apply immediately across the platform.")
st.markdown('</div>', unsafe_allow_html=True)

footer()
