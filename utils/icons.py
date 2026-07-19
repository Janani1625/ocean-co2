"""
Lightweight, dependency-free line-icon set for the Ocean Intelligence Platform.

Every icon is a small hand-authored SVG (24x24 viewBox, stroke-based,
`currentColor`) rendered inline as HTML — no external font, no CDN, no
extra package, so it always renders identically regardless of environment.

Usage:
    from utils.icons import icon
    st.markdown(f"{icon('bar-chart')} Analytics", unsafe_allow_html=True)
"""

_ICONS = {
    "waves": '<path d="M2 8c1.5-2 3.5-2 5 0s3.5 2 5 0 3.5-2 5 0 3.5 2 5 0"/><path d="M2 15c1.5-2 3.5-2 5 0s3.5 2 5 0 3.5-2 5 0 3.5 2 5 0"/>',
    "bar-chart": '<line x1="5" y1="20" x2="5" y2="11"/><line x1="12" y1="20" x2="12" y2="5"/><line x1="19" y1="20" x2="19" y2="14"/>',
    "alert-triangle": '<path d="M12 3.5 2.5 20h19L12 3.5z"/><line x1="12" y1="10" x2="12" y2="14.5"/><circle cx="12" cy="17.3" r="0.6" fill="currentColor" stroke="none"/>',
    "trending-up": '<polyline points="3,17 9,11 13,15 21,6"/><polyline points="15,6 21,6 21,12"/>',
    "trending-down": '<polyline points="3,7 9,13 13,9 21,18"/><polyline points="15,18 21,18 21,12"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.8"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/>',
    "file-text": '<path d="M6 2.5h8l4 4V21a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1z"/><line x1="14" y1="2.5" x2="14" y2="7" /><line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="16" y2="16"/>',
    "radio": '<circle cx="12" cy="12" r="1.6" fill="currentColor" stroke="none"/><path d="M8.5 8.5a5 5 0 0 0 0 7"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M5.5 5.5a9.5 9.5 0 0 0 0 13"/><path d="M18.5 5.5a9.5 9.5 0 0 1 0 13"/>',
    "radar": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5.2"/><circle cx="12" cy="12" r="1.3" fill="currentColor" stroke="none"/><path d="M12 12 19 6"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="18" rx="1.6"/><rect x="8.5" y="2.2" width="7" height="3.4" rx="1"/><line x1="8" y1="11" x2="16" y2="11"/><line x1="8" y1="15" x2="16" y2="15"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M19.4 13.5a1.7 1.7 0 0 0 .35 1.9l.06.06a2.05 2.05 0 1 1-2.9 2.9l-.06-.06a1.7 1.7 0 0 0-1.9-.35 1.7 1.7 0 0 0-1 1.55V19.6a2.05 2.05 0 1 1-4.1 0v-.1a1.7 1.7 0 0 0-1.1-1.55 1.7 1.7 0 0 0-1.9.35l-.06.06a2.05 2.05 0 1 1-2.9-2.9l.06-.06a1.7 1.7 0 0 0 .35-1.9 1.7 1.7 0 0 0-1.55-1H2.4a2.05 2.05 0 1 1 0-4.1h.1a1.7 1.7 0 0 0 1.55-1.1 1.7 1.7 0 0 0-.35-1.9l-.06-.06a2.05 2.05 0 1 1 2.9-2.9l.06.06a1.7 1.7 0 0 0 1.9.35H8.5a1.7 1.7 0 0 0 1-1.55V2.4a2.05 2.05 0 1 1 4.1 0v.1a1.7 1.7 0 0 0 1 1.55 1.7 1.7 0 0 0 1.9-.35l.06-.06a2.05 2.05 0 1 1 2.9 2.9l-.06.06a1.7 1.7 0 0 0-.35 1.9V8.5a1.7 1.7 0 0 0 1.55 1h.1a2.05 2.05 0 1 1 0 4.1h-.1a1.7 1.7 0 0 0-1.55 1z"/>',
    "download": '<path d="M12 3v12.5"/><polyline points="7,11.5 12,16.5 17,11.5"/><path d="M4.5 18.5V20a1 1 0 0 0 1 1h13a1 1 0 0 0 1-1v-1.5"/>',
    "upload": '<path d="M12 21V8.5"/><polyline points="7,13 12,8 17,13"/><path d="M4.5 18.5V20a1 1 0 0 0 1 1h13a1 1 0 0 0 1-1v-1.5"/>',
    "thermometer": '<path d="M12 14.5V4.5a2 2 0 1 0-4 0v10a4 4 0 1 0 4 0z"/><line x1="10" y1="7" x2="10" y2="13.5"/>',
    "bell": '<path d="M6 10a6 6 0 0 1 12 0c0 4 1.5 5.5 2 6.2H4c.5-.7 2-2.2 2-6.2z"/><path d="M9.7 19.5a2.3 2.3 0 0 0 4.6 0"/>',
    "map": '<path d="M9 4 4 6v14l5-2 6 2 5-2V4l-5 2-6-2z"/><line x1="9" y1="4" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="20"/>',
    "map-pin": '<path d="M12 21s7-6.6 7-11.5A7 7 0 0 0 5 9.5C5 14.4 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.4"/>',
    "trophy": '<path d="M7 4h10v5a5 5 0 0 1-10 0V4z"/><path d="M7 5H4a3 3 0 0 0 3.5 5.5"/><path d="M17 5h3a3 3 0 0 1-3.5 5.5"/><line x1="12" y1="14" x2="12" y2="17.5"/><path d="M8.5 21h7"/><path d="M9.5 17.5h5l1 3.5h-7z"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><polyline points="7.5,12.5 10.5,15.5 16.5,9"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><line x1="3" y1="12" x2="21" y2="12"/>',
    "circle": '<circle cx="12" cy="12" r="6.5" fill="currentColor" stroke="none"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.3" y1="15.3" x2="20.5" y2="20.5"/>',
    "cloud": '<path d="M7 18.5a4.5 4.5 0 0 1-1-8.9 5.5 5.5 0 0 1 10.6-2 4.5 4.5 0 0 1-.6 10.9H7z"/>',
    "gauge": '<path d="M4 15.5a8 8 0 1 1 16 0"/><line x1="12" y1="15.5" x2="15.5" y2="10.8"/><circle cx="12" cy="15.5" r="1.1" fill="currentColor" stroke="none"/>',
    "cpu": '<rect x="7" y="7" width="10" height="10" rx="1.4"/><rect x="10" y="10" width="4" height="4"/><line x1="12" y1="2.5" x2="12" y2="7"/><line x1="12" y1="17" x2="12" y2="21.5"/><line x1="2.5" y1="12" x2="7" y2="12"/><line x1="17" y1="12" x2="21.5" y2="12"/>',
    "satellite": '<rect x="9.5" y="9.5" width="5" height="5" rx="0.8" transform="rotate(45 12 12)"/><line x1="14.5" y1="9.5" x2="19" y2="5"/><line x1="17" y1="7.5" x2="21" y2="3.5"/><line x1="9.5" y1="14.5" x2="6" y2="18"/><path d="M4 20c2-3.5 5-3.5 7 0"/>',
    "wind": '<path d="M3 8h11.5a2.5 2.5 0 1 0-2.4-3.2"/><path d="M3 12.5h15a2.5 2.5 0 1 1-2.4 3.2"/><path d="M3 17h9.5a2.2 2.2 0 1 1-2.1 2.8"/>',
    "arrow-up": '<line x1="12" y1="20" x2="12" y2="5"/><polyline points="6,11 12,5 18,11"/>',
    "refresh-cw": '<path d="M4 12a8 8 0 0 1 13.8-5.6L20 8.5"/><polyline points="20,3.5 20,8.5 15,8.5"/><path d="M20 12a8 8 0 0 1-13.8 5.6L4 15.5"/><polyline points="4,20.5 4,15.5 9,15.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><polyline points="12,6.5 12,12 16,14.5"/>',
    "leaf": '<path d="M20 4C10 4 4 10 4 18c0 .8 2 1 3 .5C9 12 14 8 20 4z"/><path d="M8.5 19.5C10 15 13.5 11 18 8"/>',
    "pie-chart": '<path d="M12 3v9l7.8 4.4A9 9 0 1 1 12 3z"/><path d="M12 3a9 9 0 0 1 7.8 13.4L12 12V3z" fill="rgba(255,255,255,0.08)"/>',
    "brain": '<path d="M9.5 3.5a3 3 0 0 0-3 3v.3A3 3 0 0 0 5 12a3 3 0 0 0 1.5 5.4A3 3 0 0 0 9.5 20.5a3 3 0 0 0 3-3v-11a3 3 0 0 0-3-3z"/><path d="M14.5 3.5a3 3 0 0 1 3 3v.3A3 3 0 0 1 19 12a3 3 0 0 1-1.5 5.4 3 3 0 0 1-3 3.1 3 3 0 0 1-3-3v-11a3 3 0 0 1 3-3z"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="1.4"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/>',
    "flask": '<path d="M10 3h4"/><path d="M10.5 3v6.5L5.8 18a2 2 0 0 0 1.8 3h8.8a2 2 0 0 0 1.8-3l-4.7-8.5V3"/><line x1="7.5" y1="14.5" x2="16.5" y2="14.5"/>',
    "fish": '<path d="M3 12c3-4.5 8-6.5 12.5-4.5 2 .9 3.5 2.6 4.5 4.5-1 1.9-2.5 3.6-4.5 4.5C11 18.5 6 16.5 3 12z"/><circle cx="16" cy="10.5" r="0.7" fill="currentColor" stroke="none"/><path d="M3 12 1 9m2 3-2 3"/>',
    "factory": '<path d="M4 20V11l4.5 3V11l4.5 3V11l4.5 3V6h2.5v14z"/><line x1="4" y1="20" x2="20" y2="20"/>',
    "tool": '<path d="M17.5 9.5 20 7a4 4 0 0 1-5.5 5.5l-8 8a1.8 1.8 0 0 1-2.5-2.5l8-8A4 4 0 0 1 17.5 4l-2.5 2.5z"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5 13.2 13.2 8.5 15.5l2.3-4.7z"/>',
    "ruler": '<rect x="3" y="8" width="18" height="8" rx="1.2" transform="rotate(0 12 12)"/><line x1="7" y1="8" x2="7" y2="11"/><line x1="11" y1="8" x2="11" y2="11"/><line x1="15" y1="8" x2="15" y2="11"/><line x1="19" y1="8" x2="19" y2="11"/>',
    "star": '<path d="M12 3.5 14.6 9 20.5 9.9 16.3 14 17.3 20 12 17.1 6.7 20 7.7 14 3.5 9.9 9.4 9z"/>',
    "palette": '<path d="M12 3a9 8.5 0 1 0 0 17c1.4 0 2-1 2-2s-1-1.5-1-2.5 1-1.5 2-1.5h2.5a3 3 0 0 0 3-3C20.5 6.2 16.7 3 12 3z"/><circle cx="7.5" cy="11" r="1.1" fill="currentColor" stroke="none"/><circle cx="9.5" cy="7.2" r="1.1" fill="currentColor" stroke="none"/><circle cx="14.5" cy="7.2" r="1.1" fill="currentColor" stroke="none"/>',
    "help-circle": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.2a2.5 2.5 0 1 1 3.7 2.2c-.9.55-1.2 1-1.2 2.1"/><circle cx="12" cy="17" r="0.6" fill="currentColor" stroke="none"/>',
    "shuffle": '<polyline points="17,3 21,3 21,7"/><line x1="3" y1="20" x2="21" y2="3"/><polyline points="17,20 21,20 21,16"/><line x1="3" y1="4" x2="9" y2="10"/><line x1="15" y1="14" x2="21" y2="20"/>',
    "calculator": '<rect x="5" y="3" width="14" height="18" rx="1.4"/><line x1="7.5" y1="6.5" x2="16.5" y2="6.5"/><line x1="7.5" y1="11" x2="7.5" y2="11"/><line x1="12" y1="11" x2="12" y2="11"/><line x1="16.5" y1="11" x2="16.5" y2="11"/><line x1="7.5" y1="14.5" x2="7.5" y2="14.5"/><line x1="12" y1="14.5" x2="12" y2="14.5"/><line x1="16.5" y1="11" x2="16.5" y2="17.5"/><line x1="7.5" y1="18" x2="12.5" y2="18"/>',
    "edit": '<path d="M4 20 4.6 16.2 15 5.8a1.8 1.8 0 0 1 2.5 0l0.7 0.7a1.8 1.8 0 0 1 0 2.5L7.8 19.4 4 20z"/><line x1="13.3" y1="7.5" x2="16.5" y2="10.7"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="7.5" ry="3"/><path d="M4.5 5.5v13c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-13"/><path d="M4.5 12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3"/>',
    "layers": '<polygon points="12,3 21,8 12,13 3,8"/><polyline points="3,13 12,18 21,13"/><polyline points="3,17.5 12,22.5 21,17.5"/>',
    "sparkles": '<path d="M11 3 12.3 8 17 9.3 12.3 10.6 11 15.5 9.7 10.6 5 9.3 9.7 8z"/><path d="M18 14 18.7 16.5 21 17.3 18.7 18 18 20.5 17.3 18 15 17.3 17.3 16.5z"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="16" rx="1.6"/><line x1="3.5" y1="10" x2="20.5" y2="10"/><line x1="8" y1="2.5" x2="8" y2="6.5"/><line x1="16" y1="2.5" x2="16" y2="6.5"/>',
}


def icon(name: str, size: int = 16, stroke_width: float = 1.8, color: str = "currentColor",
         style: str = "vertical-align:-3px; margin-right:5px;") -> str:
    """Return an inline <svg> string for the given icon name.

    Falls back to a plain circle glyph if the name is unknown, so a typo
    never crashes a page — it just renders a small dot.
    """
    body = _ICONS.get(name, _ICONS["circle"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" style="{style}">{body}</svg>'
    )


def icon_only(name: str, size: int = 20, stroke_width: float = 1.8, color: str = "currentColor") -> str:
    """Icon with no inline margin — used inside icon boxes (e.g. kpi-icon) that
    already handle their own centering/spacing via CSS."""
    return icon(name, size=size, stroke_width=stroke_width, color=color, style="display:block;")
