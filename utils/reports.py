"""Report generation: Executive / Regional / Monitoring PDF reports, plus
CSV and Excel export helpers."""

import io
from datetime import datetime
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


NAVY = colors.HexColor("#0a1628")
CYAN = colors.HexColor("#0891b2")
LIGHT = colors.HexColor("#f0f9ff")
GREY = colors.HexColor("#475569")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="OITitle", fontSize=22, textColor=NAVY, spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="OISubtitle", fontSize=11, textColor=GREY, spaceAfter=16))
    styles.add(ParagraphStyle(name="OIHeading", fontSize=14, textColor=CYAN, spaceBefore=14, spaceAfter=8, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="OIBody", fontSize=10, textColor=colors.black, leading=14))
    return styles


def _table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build_pdf_report(report_type: str, kpis: dict, regional_df: pd.DataFrame,
                      insights: list, alerts_df: pd.DataFrame = None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    styles = _styles()
    story = []

    story.append(Paragraph("Ocean Intelligence Platform", styles["OITitle"]))
    story.append(Paragraph(f"{report_type} — Generated {datetime.now().strftime('%d %B %Y, %H:%M')}", styles["OISubtitle"]))

    story.append(Paragraph("Executive Summary", styles["OIHeading"]))
    summary_data = [
        ["Metric", "Value"],
        ["Average Carbon Level", f"{kpis.get('avg_carbon', '-')} ppm"],
        ["Highest Carbon Level", f"{kpis.get('max_carbon', '-')} ppm ({kpis.get('max_carbon_region', '-')})"],
        ["Lowest Carbon Level", f"{kpis.get('min_carbon', '-')} ppm ({kpis.get('min_carbon_region', '-')})"],
        ["Average Ocean Temperature", f"{kpis.get('avg_temp', '-')} °C"],
        ["Ocean Health Score", f"{kpis.get('health_score', '-')} / 100"],
        ["Monitoring Stations", f"{kpis.get('stations', '-')}"],
        ["Active Alerts", f"{kpis.get('active_alerts', '-')}"],
        ["Total Records Analyzed", f"{kpis.get('records', '-')}"],
    ]
    story.append(_table(summary_data, col_widths=[8 * cm, 8 * cm]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Regional Breakdown", styles["OIHeading"]))
    reg_data = [["Region", "Avg Carbon (ppm)", "Max Carbon", "Avg Temp (°C)", "Avg O2 (mg/L)", "Stations"]]
    for _, r in regional_df.iterrows():
        reg_data.append([r["region"], r["avg_carbon"], r["max_carbon"], r["avg_temp"], r["avg_o2"], r["stations"]])
    story.append(_table(reg_data))
    story.append(Spacer(1, 10))

    if insights:
        story.append(Paragraph("Environmental Intelligence Highlights", styles["OIHeading"]))
        for ins in insights:
            story.append(Paragraph(f"<b>{ins['title']}</b> — {ins['text']}", styles["OIBody"]))
            story.append(Spacer(1, 4))

    if alerts_df is not None and len(alerts_df):
        story.append(Paragraph("Recent Alerts", styles["OIHeading"]))
        alert_data = [["Time", "Region", "Alert", "Severity"]]
        for _, a in alerts_df.head(15).iterrows():
            alert_data.append([str(a["timestamp"])[:16], a["region"], a["label"], a["severity"]])
        story.append(_table(alert_data))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "This report was generated automatically by the Ocean Intelligence Platform's "
        "environmental analytics engine. Figures are derived from monitoring station "
        "telemetry and machine-learning based forecasting models.",
        styles["OIBody"]))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def build_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def build_excel(sheets: dict) -> bytes:
    """sheets: {sheet_name: dataframe}"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, sheet_df in sheets.items():
            sheet_df.to_excel(writer, sheet_name=name[:31], index=False)
    buf.seek(0)
    return buf.getvalue()
