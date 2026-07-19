"""Reusable Streamlit UI component builders for a consistent enterprise look.

All icon parameters throughout this module take an icon *name* (see
utils/icons.py) rather than an emoji character, and are rendered as
professional inline SVGs.
"""

import os
import streamlit as st
import plotly.graph_objects as go

from utils.icons import icon, icon_only

CSS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "css", "style.css")

ICON_COLORS = {
    "cyan": "background: rgba(34,211,238,0.15); color:#22d3ee;",
    "emerald": "background: rgba(16,185,129,0.15); color:#10b981;",
    "purple": "background: rgba(168,85,247,0.15); color:#a855f7;",
    "amber": "background: rgba(245,158,11,0.15); color:#f59e0b;",
    "red": "background: rgba(239,68,68,0.15); color:#ef4444;",
    "blue": "background: rgba(59,130,246,0.15); color:#3b82f6;",
}


def load_css():
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon_name: str = ""):
    icon_html = ""
    if icon_name:
        icon_html = f'<span class="oi-page-icon">{icon_only(icon_name, size=22)}</span>'
    st.markdown(
        f"""<div style="margin-bottom: 18px; display:flex; align-items:center; gap:12px;">
        {icon_html}
        <div>
            <h1 style="margin-bottom:2px;">{title}</h1>
            <p style="color:#93a7c0; font-size:14.5px; margin:0;">{subtitle}</p>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = "", icon_name: str = ""):
    icon_html = icon(icon_name, size=17) if icon_name else ""
    st.markdown(
        f"""<div class="oi-section-title">{icon_html}{title}</div>
        <div class="oi-section-sub">{subtitle}</div>""",
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, icon_name: str, change: float = None,
             sub: str = "", color: str = "cyan"):
    change_html = ""
    if change is not None:
        cls = "badge-up" if change >= 0 else "badge-down"
        arrow_icon = icon("trending-up", size=12, style="vertical-align:-1px;") if change >= 0 else icon("trending-down", size=12, style="vertical-align:-1px;")
        change_html = f'<span class="{cls}">{arrow_icon} {abs(change):.2f}%</span> <span style="color:#93a7c0;">vs last month</span>'

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="{ICON_COLORS.get(color, ICON_COLORS['cyan'])}">{icon_only(icon_name, size=20)}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{change_html}{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_pill(level: str) -> str:
    mapping = {
        "Critical": "pill-critical", "High": "pill-high",
        "Medium": "pill-medium", "Low": "pill-low", "Good": "pill-good",
    }
    cls = mapping.get(level, "pill-low")
    return f'<span class="pill {cls}">{level}</span>'


def risk_pill_html(level: str):
    st.markdown(risk_pill(level), unsafe_allow_html=True)


def insight_card(icon_name: str, title: str, text: str, kind: str = "info"):
    st.markdown(
        f"""<div class="insight-card {kind}">
            <div class="insight-title">{icon(icon_name, size=15)}{title}</div>
            <div class="insight-text">{text}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def recommendation_card(icon_name: str, title: str, text: str):
    st.markdown(
        f"""<div class="oi-card" style="padding:14px 16px; margin-bottom:10px;">
            <div style="font-weight:700; font-size:14px; margin-bottom:3px; display:flex; align-items:center;">{icon(icon_name, size=15)}{title}</div>
            <div style="font-size:12.5px; color:#93a7c0; line-height:1.5;">{text}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def gauge_chart(value: float, title: str = "Ocean Health Score", color: str = "#22d3ee") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 15, "color": "#e6f1f8"}},
        number={"font": {"size": 36, "color": "#e6f1f8"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#93a7c0", "tickfont": {"color": "#93a7c0"}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "rgba(239,68,68,0.25)"},
                {"range": [30, 50], "color": "rgba(249,115,22,0.25)"},
                {"range": [50, 70], "color": "rgba(234,179,8,0.25)"},
                {"range": [70, 85], "color": "rgba(34,197,94,0.25)"},
                {"range": [85, 100], "color": "rgba(16,185,129,0.3)"},
            ],
        },
    ))
    fig.update_layout(
        height=260, margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e6f1f8"},
    )
    return fig


def apply_plotly_theme(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#cbd8e8", "family": "Segoe UI, sans-serif"},
        legend={"bgcolor": "rgba(0,0,0,0)"},
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis={"gridcolor": "rgba(148,163,184,0.10)", "zerolinecolor": "rgba(148,163,184,0.10)"},
        yaxis={"gridcolor": "rgba(148,163,184,0.10)", "zerolinecolor": "rgba(148,163,184,0.10)"},
    )
    return fig


def footer():
    st.markdown(
        f"""<div class="oi-footer">
        {icon('waves', size=14)} <b>Ocean Intelligence Platform</b> &nbsp;|&nbsp; AI-Powered Marine Carbon Monitoring & Environmental Analytics
        &nbsp;|&nbsp; Enterprise Edition v1.0
        </div>""",
        unsafe_allow_html=True,
    )
