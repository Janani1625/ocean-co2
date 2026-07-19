"""Builds the interactive Global Ocean Intelligence map using Folium."""

import folium
from folium.plugins import HeatMap, MarkerCluster, Fullscreen
import pandas as pd

RISK_COLOR = {
    "Critical": "#ef4444",
    "High": "#f97316",
    "Medium": "#eab308",
    "Low": "#22c55e",
}


def build_ocean_map(stations_df: pd.DataFrame, show_heatmap: bool = True,
                     show_clusters: bool = True, zoom_start: int = 2) -> folium.Map:
    m = folium.Map(
        location=[15, 0], zoom_start=zoom_start, tiles=None,
        control_scale=True, world_copy_jump=False,
    )
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="CartoDB dark_all", name="Dark Ocean", subdomains="abcd", max_zoom=19,
    ).add_to(m)

    Fullscreen(position="topleft").add_to(m)

    if show_heatmap and len(stations_df):
        heat_data = [
            [row["lat"], row["lon"], min(row["carbon_ppm"] / 70, 1.0)]
            for _, row in stations_df.iterrows()
        ]
        HeatMap(heat_data, radius=32, blur=28, min_opacity=0.25,
                gradient={"0.2": "#22c55e", "0.4": "#eab308", "0.6": "#f97316", "0.85": "#ef4444"}
                ).add_to(folium.FeatureGroup(name="Carbon Heatmap").add_to(m))

    marker_layer = MarkerCluster(name="Monitoring Stations", disableClusteringAtZoom=5) if show_clusters else folium.FeatureGroup(name="Monitoring Stations")
    marker_layer.add_to(m)

    for _, row in stations_df.iterrows():
        color = RISK_COLOR.get(row["risk_level"], "#3b82f6")
        popup_html = f"""
        <div style="font-family:Segoe UI, sans-serif; min-width:220px;">
            <div style="font-weight:700; font-size:14px; color:#0a1628; margin-bottom:6px;">
                {row['region']} — {row['station_id']}
            </div>
            <table style="font-size:12px; color:#1e293b; border-collapse:collapse;">
                <tr><td style="padding:2px 8px 2px 0;">Carbon Level</td><td><b>{row['carbon_ppm']:.2f} ppm</b></td></tr>
                <tr><td style="padding:2px 8px 2px 0;">Temperature</td><td>{row['temperature_c']:.1f} °C</td></tr>
                <tr><td style="padding:2px 8px 2px 0;">Salinity</td><td>{row['salinity_psu']:.1f} PSU</td></tr>
                <tr><td style="padding:2px 8px 2px 0;">Dissolved O2</td><td>{row['dissolved_oxygen_mgL']:.2f} mg/L</td></tr>
                <tr><td style="padding:2px 8px 2px 0;">Depth</td><td>{row['depth_m']} m</td></tr>
                <tr><td style="padding:2px 8px 2px 0;">Risk Level</td><td><b style="color:{color};">{row['risk_level']}</b></td></tr>
                <tr><td style="padding:2px 8px 2px 0;">Status</td><td>{row['sensor_status']}</td></tr>
            </table>
        </div>
        """
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=7 + min(row["carbon_ppm"] / 12, 6),
            color=color, fill=True, fill_color=color, fill_opacity=0.85, weight=1.5,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{row['station_id']} · {row['region']} · {row['carbon_ppm']:.1f} ppm",
        ).add_to(marker_layer)

    folium.LayerControl(collapsed=True).add_to(m)
    return m
