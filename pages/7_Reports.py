import os
import sys
from datetime import datetime
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, footer
from utils.data_loader import load_data, kpi_summary, regional_summary
from utils.alerts import generate_alerts
from utils.insights import generate_insights
from utils.reports import build_pdf_report, build_csv, build_excel

st.set_page_config(page_title="Reports | Ocean Intel", page_icon=None, layout="wide")
load_css()

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()
kpis = kpi_summary(df)
reg = regional_summary(df)
alerts_df = generate_alerts(df)
insights = generate_insights(df)

page_header("Reports", "Generate downloadable executive, regional, and monitoring reports", "file-text")

report_types = {
    "Executive Report": "High-level summary of ocean health, KPIs, and top insights for leadership.",
    "Carbon Monitoring Report": "Detailed carbon concentration statistics across all monitoring stations.",
    "Monthly Report": "Month-over-month trend summary with regional breakdown.",
    "Regional Report": "Deep dive into a single ocean region's environmental status.",
    "Prediction Report": "Model performance summary and recent prediction accuracy.",
}

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("Select a Report", "Choose a report type, then export in your preferred format", "edit")
report_type = st.selectbox("Report Type", list(report_types.keys()))
st.caption(report_types[report_type])

region_scope = None
if report_type == "Regional Report":
    region_scope = st.selectbox("Region", sorted(df["region"].unique().tolist()))

scoped_df = df if region_scope is None else df[df["region"] == region_scope]
scoped_kpis = kpi_summary(scoped_df) if region_scope else kpis
scoped_reg = regional_summary(scoped_df)
scoped_alerts = generate_alerts(scoped_df)
scoped_insights = generate_insights(scoped_df)

colp1, colp2, colp3 = st.columns(3)
with colp1:
    pdf_bytes = build_pdf_report(report_type, scoped_kpis, scoped_reg, scoped_insights, scoped_alerts)
    st.download_button(
        "Download as PDF", data=pdf_bytes,
        file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf", use_container_width=True, icon=":material/download:",
    )
with colp2:
    csv_bytes = build_csv(scoped_df)
    st.download_button(
        "Download as CSV", data=csv_bytes,
        file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv", use_container_width=True, icon=":material/download:",
    )
with colp3:
    xlsx_bytes = build_excel({"Raw Data": scoped_df.head(20000), "Regional Summary": scoped_reg, "Alerts": scoped_alerts})
    st.download_button(
        "Download as Excel", data=xlsx_bytes,
        file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, icon=":material/download:",
    )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("Report Preview", "Executive summary that will appear in the exported report", "eye")
p1, p2, p3, p4 = st.columns(4)
p1.metric("Avg Carbon", f"{scoped_kpis['avg_carbon']} ppm")
p2.metric("Ocean Health", f"{scoped_kpis['health_score']} / 100")
p3.metric("Stations", scoped_kpis["stations"])
p4.metric("Active Alerts", scoped_kpis["active_alerts"])
st.dataframe(scoped_reg, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

footer()
