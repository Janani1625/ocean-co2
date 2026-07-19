import os
import sys
import pandas as pd
import numpy as np
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import load_css, page_header, section_title, footer, kpi_card
from utils.data_loader import load_data
from utils.reports import build_csv

st.set_page_config(page_title="Data Explorer | Ocean Intel", page_icon=None, layout="wide")
load_css()

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()
page_header("Data Explorer", "Browse, search, filter, and export raw monitoring data", "search")

st.markdown('<div class="oi-card">', unsafe_allow_html=True)
section_title("Upload Custom Dataset", "Optionally upload your own CSV to explore instead of the default dataset", "upload")
uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded is not None:
    try:
        working_df = pd.read_csv(uploaded)
        st.success(f"Loaded uploaded file with {len(working_df):,} rows and {len(working_df.columns)} columns.")
    except Exception as e:
        st.error(f"Could not read file: {e}")
        working_df = df
else:
    working_df = df
st.markdown('</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Total Records", f"{len(working_df):,}", "bar-chart", color="cyan")
with k2:
    kpi_card("Columns", f"{len(working_df.columns)}", "clipboard", color="blue")
with k3:
    missing = int(working_df.isna().sum().sum())
    kpi_card("Missing Values", f"{missing:,}", "help-circle", color="amber" if missing else "emerald")
with k4:
    numeric_cols = working_df.select_dtypes(include=[np.number]).columns
    outliers = 0
    for c in numeric_cols:
        q1, q3 = working_df[c].quantile(0.25), working_df[c].quantile(0.75)
        iqr = q3 - q1
        outliers += int(((working_df[c] < q1 - 1.5 * iqr) | (working_df[c] > q3 + 1.5 * iqr)).sum())
    kpi_card("Detected Outliers", f"{outliers:,}", "alert-triangle", color="red" if outliers else "emerald")

tab1, tab2, tab3 = st.tabs(["Data Preview", "Statistics", "Outlier Detection"])

with tab1:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Search, Sort & Filter", "", "search")
    search = st.text_input("Search (matches any text column)")
    view = working_df.copy()
    if search:
        text_cols = view.select_dtypes(include="object").columns
        mask = pd.Series(False, index=view.index)
        for c in text_cols:
            mask |= view[c].astype(str).str.contains(search, case=False, na=False)
        view = view[mask]

    sort_col = st.selectbox("Sort by column", view.columns.tolist())
    sort_dir = st.radio("Sort direction", ["Ascending", "Descending"], horizontal=True)
    view = view.sort_values(sort_col, ascending=(sort_dir == "Ascending"))

    st.dataframe(view.head(1000), use_container_width=True, height=420)
    st.caption(f"Showing up to 1,000 of {len(view):,} filtered rows.")

    csv_bytes = build_csv(view)
    st.download_button("Download Filtered Data as CSV", data=csv_bytes,
                        file_name="ocean_data_filtered.csv", mime="text/csv", icon=":material/download:")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Descriptive Statistics", "", "bar-chart")
    st.dataframe(working_df.describe().T, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Missing Values by Column", "", "help-circle")
    miss = working_df.isna().sum().reset_index()
    miss.columns = ["Column", "Missing Count"]
    miss["Missing %"] = (miss["Missing Count"] / len(working_df) * 100).round(2)
    st.dataframe(miss, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="oi-card">', unsafe_allow_html=True)
    section_title("Outlier Detection (IQR Method)", "Values outside 1.5×IQR from Q1/Q3 flagged per numeric column", "alert-triangle")
    outlier_rows = []
    for c in numeric_cols:
        q1, q3 = working_df[c].quantile(0.25), working_df[c].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        cnt = int(((working_df[c] < lower) | (working_df[c] > upper)).sum())
        outlier_rows.append({"Column": c, "Lower Bound": round(lower, 3), "Upper Bound": round(upper, 3), "Outlier Count": cnt})
    st.dataframe(pd.DataFrame(outlier_rows), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

footer()
