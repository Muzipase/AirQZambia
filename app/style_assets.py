"""AirQ Zambia — design system and reusable UI primitives.

A restrained, data-dense "environmental intelligence" language: Zambia-green
accents on a light neutral canvas, flat white cards with thin borders, a
narrow dark command sidebar, and semantic AQI colour coding. Every helper
renders plain HTML via st.markdown so the look stays consistent, fast and
easy to extend. Widget styling is centralised here rather than scattered
across views.
"""

import html as _html
from datetime import datetime

import streamlit as st

ZAMBIA = "#006a3d"
ZAMBIA_LIGHT = "#0a8a4e"
SIDEBAR = "#131a2b"
SIDEBAR_HOVER = "#1e2940"
ACTIVE_TEXT = "#4ade80"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#4b5563"
TEXT_MUTED = "#8a94a6"
BORDER = "rgba(15, 23, 42, 0.07)"
BORDER_STRONG = "rgba(15, 23, 42, 0.16)"
BG_TOP = "#f7f8fa"
BG_BOTTOM = "#eef1f4"

# ---- Semantic AQI palette: color / bg / text / border pairs ----------------
AQI_STYLES = {
    "Good": ("#16a34a", "#f0fdf4", "#15803d", "#bbf7d0"),
    "Moderate": ("#eab308", "#fefce8", "#a16207", "#fef08a"),
    "Sensitive": ("#f97316", "#fff7ed", "#c2410c", "#fed7aa"),
    "Unhealthy": ("#ef4444", "#fef2f2", "#dc2626", "#fecaca"),
    "Very Unhealthy": ("#7c2d92", "#faf5ff", "#6b21a8", "#e9d5ff"),
    "Hazardous": ("#5f0f0f", "#450a0a", "#fca5a5", "#991b1b"),
}

AQI_COLORS = {k: v[0] for k, v in AQI_STYLES.items()}

# ---- EPA AQI bands used by the gauge (value ranges => colour) ----
AQI_BANDS = [
    (0, 50, "#22c55e", "Good"),
    (50, 100, "#eab308", "Moderate"),
    (100, 150, "#f97316", "Unhealthy"),
    (150, 200, "#ef4444", "Very Unhealthy"),
    (200, 300, "#7c2d92", "Very Unhealthy"),
    (300, 500, "#450a0a", "Hazardous"),
]

# ---------------------------------------------------------------------------
# Inline SVG icon set (monochrome, inherits currentColor)
# ---------------------------------------------------------------------------

_ICON_PATHS = {
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.1-6"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.7" fill="currentColor" stroke="none"/>',
    "chart": '<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-8"/><path d="M22 20V8"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="10" y="10" width="4" height="4" fill="currentColor" stroke="none"/><path d="M9 2v2M15 2v2M9 20v2M15 20v2M2 9h2M2 15h2M20 9h2M20 15h2"/>',
    "wrench": '<path d="M14.7 6.3a4.5 4.5 0 0 0-6.1 6.1L3 18l3 3 5.6-5.6a4.5 4.5 0 0 0 6.1-6.1L14 13l-3-3 3.7-3.7Z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>',
    "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h16.9a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0Z"/><circle cx="12" cy="10" r="3"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.7-4 3-9 3s-9-1.3-9-3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "layers": '<path d="m12 2-10 5 10 5 10-5-10-5z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "check": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "wind": '<path d="M9.6 4.6A2 2 0 1 1 11 8H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/><path d="M17.7 7.7A2.5 2.5 0 1 1 19.5 12H2"/>',
    "scale": '<path d="M12 3v18"/><path d="M8 21h8"/><path d="M3 7h18"/><path d="M6 7l-3-4h6l-3 4Z"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
    "sparkles": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><path d="M12 8l1.5 2.5L16 12l-2.5 1.5L12 16l-1.5-2.5L8 12l2.5-1.5L12 8Z"/>',
    "flask": '<path d="M9 4h6M10 4v6l-5 8a2 2 0 0 0 1.8 3h10.4a2 2 0 0 0 1.8-3l-5-8V4"/><path d="M7.5 15h9"/>',
}


def ico(name, size=18, cls=""):
    """Inline SVG icon. Falls back to a neutral dot for unknown names."""
    path = _ICON_PATHS.get(name)
    if path is None:
        return f'<span class="dot-ico">●</span>'
    return (
        f'<svg class="icon {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'
    )


STYLE_SHEET = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {{
  --zambia-green: {ZAMBIA};
  --zambia-green-light: {ZAMBIA_LIGHT};
  --bg-primary: #f5f6f8;
  --bg-secondary: #ffffff;
  --text-primary: {TEXT_PRIMARY};
  --text-secondary: {TEXT_SECONDARY};
  --text-muted: {TEXT_MUTED};
  --line: {BORDER};
  --line-strong: {BORDER_STRONG};
  --radius: 12px;
}}

html, body, .stApp {{
  background: linear-gradient(170deg, {BG_TOP} 0%, {BG_BOTTOM} 100%) !important;
  color: var(--text-primary) !important;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}}

.stApp {{
  padding: 1.25rem 2.25rem 2.5rem !important;
  max-width: 1280px;
  margin: 0 auto 0 0;
}}

::selection {{ background: rgba(0, 106, 61, 0.16); }}
h1, h2, h3, h4 {{ font-family: 'Inter', 'Segoe UI', sans-serif !important; letter-spacing: -0.02em; }}
.icon {{ vertical-align: -0.22em; flex: 0 0 auto; }}

/* thin Zambia-green top accent */
.stApp::before {{
  content: ""; position: fixed; top: 0; left: 0; right: 0; height: 3px; z-index: 1000;
  background: {ZAMBIA};
}}

/* ---------- Global top command bar ---------- */
.topbar {{
  display: flex; align-items: center; justify-content: space-between;
  gap: 1rem; flex-wrap: wrap; padding: 0.15rem 0 1.1rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1.5rem;
}}
.topbar-left {{ display: flex; align-items: center; gap: 0.8rem; min-width: 0; }}
.topbar-logo {{
  width: 42px; height: 42px; flex: 0 0 auto; border-radius: 11px;
  display: grid; place-items: center; color: #ffffff;
  background: linear-gradient(135deg, {ZAMBIA} 0%, {ZAMBIA_LIGHT} 100%);
  box-shadow: 0 5px 14px rgba(0, 106, 61, 0.30);
}}
.topbar-brand {{ font-size: 1.15rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1.1; }}
.topbar-brand span {{ color: var(--zambia-green); }}
.topbar-sub {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 2px; font-weight: 500; }}
.topbar-right {{ display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }}
.system-pill {{
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.45rem 0.9rem; border-radius: 999px;
  background: var(--bg-secondary); border: 1px solid var(--line);
  font-size: 0.72rem; font-weight: 700; color: var(--text-secondary);
}}
.system-pill .ts {{ color: var(--text-muted); font-weight: 600; }}
.system-pill.ok {{ border-color: #bbf7d0; }}
.system-pill.ok .pv {{ color: #15803d; }}
.system-pill.err {{ border-color: #fecaca; }}
.system-pill.err .pv {{ color: #dc2626; }}
.dot {{
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  background: rgba(120, 130, 145, 0.5);
}}
.dot.on {{ background: #22c55e; box-shadow: 0 0 6px rgba(34, 197, 94, 0.55); }}
.dot.off {{ background: #ef4444; box-shadow: 0 0 6px rgba(239, 68, 68, 0.55); }}
.dot.amber {{ background: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.55); }}
.pulse {{ animation: pulse 2s infinite; }}
@keyframes pulse {{
  0% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.45); }}
  70% {{ box-shadow: 0 0 0 7px rgba(34, 197, 94, 0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
}}

/* ---------- Sidebar: narrow dark command rail ---------- */
[data-testid="stSidebar"] {{
  background: {SIDEBAR} !important;
  border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
  width: 252px !important; min-width: 240px !important; max-width: 262px !important;
}}
[data-testid="stSidebar"] * {{ color: #b8bfd4 !important; }}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{ color: #FFFFFF !important; }}
[data-testid="stSidebarCollapsedButton"] {{ color: #b8bfd4 !important; }}

[data-testid="stSidebar"] [data-testid="stExpander"] {{
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 10px !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {{ font-weight: 600; }}
[data-testid="stSidebar"] label {{
  color: rgba(184, 191, 212, 0.6) !important;
  font-size: 0.66rem !important; letter-spacing: 0.09em;
  text-transform: uppercase; font-weight: 700 !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div,
[data-testid="stSidebar"] input {{
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #FFFFFF !important; border-radius: 8px !important;
}}

/* grouped nav — compact items, uppercase groups */
[data-testid="stSidebarNavItems"] ul {{ gap: 1px !important; }}
[data-testid="stSidebarNavItems"] a {{
  color: #b8bfd4 !important; font-weight: 500; font-size: 0.8125rem;
  border-radius: 7px; margin: 1px -6px; padding: 4px 8px !important;
  transition: background 0.15s ease, color 0.15s ease;
}}
[data-testid="stSidebarNavItems"] a:hover {{
  background: {SIDEBAR_HOVER} !important; color: #FFFFFF !important;
}}
[data-testid="stSidebarNavItems"] a[aria-current="page"] {{
  background: rgba(0, 106, 61, 0.28) !important;
  color: {ACTIVE_TEXT} !important; font-weight: 600;
}}
[data-testid="stSidebarNavItems"] a[aria-current="page"] * {{ color: {ACTIVE_TEXT} !important; }}
[data-testid="stSidebarNavItems"] p {{ font-size: 0.66rem !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; color: rgba(184,191,212,0.45) !important; font-weight: 700 !important; margin-top: 0.4rem !important; }}

[data-testid="stSidebarHeader"] {{ padding-top: 0.3rem !important; }}
[data-testid="stSidebarNav"] {{ background: transparent !important; padding: 0.4rem 0.4rem 1rem !important; }}

.side-brand {{ display: flex; align-items: center; gap: 12px; padding: 0.7rem 0.2rem 1rem; }}
.side-logo {{
  width: 38px; height: 38px; flex: 0 0 auto; border-radius: 10px;
  display: grid; place-items: center; color: #FFFFFF;
  background: linear-gradient(135deg, {ZAMBIA} 0%, {ZAMBIA_LIGHT} 100%);
  box-shadow: 0 4px 12px rgba(0, 106, 61, 0.35);
}}
.side-brand .mark {{ font-size: 0.95rem; font-weight: 800; color: #FFFFFF !important; letter-spacing: 0.02em; line-height: 1.15; }}
.side-brand .mark span {{ color: {ACTIVE_TEXT}; }}
.side-brand .sub {{ color: rgba(184, 191, 212, 0.5); font-size: 0.66rem; letter-spacing: 0.04em; margin-top: 3px; line-height: 1.4; }}

.side-status {{
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px; padding: 12px 14px; margin-top: 2px;
}}
.side-status .h {{
  font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase;
  color: rgba(184, 191, 212, 0.5); font-weight: 700; margin-bottom: 8px;
}}
.side-status .row {{
  display: flex; justify-content: space-between; align-items: center; gap: 10px;
  margin: 5px 0; font-size: 0.74rem; font-weight: 500;
}}
.side-status .row strong {{ color: #e8eaf3; font-weight: 600; }}
.side-foot {{
  margin-top: 14px; padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  color: rgba(184, 191, 212, 0.4); font-size: 0.62rem; line-height: 1.7;
}}

/* ---------- Breadcrumb + page header (compact) ---------- */
.breadcrumb {{ display: flex; align-items: center; gap: 0.45rem; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.9rem; }}
.breadcrumb-item {{ color: var(--text-muted); }}
.breadcrumb-sep {{ color: var(--line-strong); font-size: 0.72rem; }}
.breadcrumb-current {{ color: var(--text-primary); font-weight: 700; }}

.page-header {{ margin-bottom: 1.15rem; }}
.page-label {{
  font-size: 0.66rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.09em; color: var(--zambia-green); margin-bottom: 0.25rem;
}}
.page-title {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -0.025em; color: var(--text-primary); margin: 0; line-height: 1.2; }}
.page-subtitle {{ font-size: 0.85rem; color: var(--text-muted); margin-top: 0.3rem; line-height: 1.6; max-width: 62ch; }}

.page-chips {{ display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.9rem; }}
.page-pill {{
  display: inline-flex; align-items: center; gap: 0.45rem;
  padding: 0.34rem 0.75rem; border-radius: 999px; font-size: 0.72rem;
  background: var(--bg-secondary); border: 1px solid var(--line);
  color: var(--text-secondary);
}}
.page-pill .pl {{ font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 700; }}
.page-pill .pv {{ font-weight: 700; color: var(--text-primary); }}
.page-pill.good .pv {{ color: #15803d; }}
.page-pill.bad .pv {{ color: #dc2626; }}

/* ---------- Location bar (Command Center) ---------- */
.location-bar {{
  display: flex; align-items: stretch; gap: 0.85rem; margin: 0 0 1.5rem;
}}
.location-bread {{ display: flex; align-items: center; gap: 0.45rem; font-size: 0.78rem; color: var(--text-muted); }}
.location-bread b {{ color: var(--zambia-green); font-weight: 700; }}
.loc-box {{ flex: 1; min-width: 0; }}
.loc-box [data-testid="stSelectbox"] label {{ display: inline-flex !important; }}
.loc-box label p {{ font-size: 0.64rem !important; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-muted) !important; font-weight: 700 !important; margin-bottom: 0.25rem !important; }}

/* ---------- AQI command card ---------- */
.aqi-command {{
  display: grid; grid-template-columns: minmax(230px, 320px) auto 1fr;
  gap: 0; background: var(--bg-secondary);
  border: 1px solid var(--line); border-radius: 16px;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
  margin-bottom: 1.25rem; overflow: hidden;
}}
.aqi-command-main {{ padding: 1.6rem 1.9rem; display: flex; flex-direction: column; justify-content: center; }}
.aqi-city {{ font-size: 1.05rem; font-weight: 800; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem; }}
.aqi-eyebrow {{ font-size: 0.64rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-top: 0.35rem; }}
.aqi-numbers {{ display: flex; align-items: baseline; gap: 0.55rem; margin: 0.9rem 0 0.65rem; }}
.aqi-big {{ font-size: 4rem; font-weight: 800; line-height: 1; letter-spacing: -0.04em; font-variant-numeric: tabular-nums; }}
.aqi-us {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: var(--text-muted); }}
.aqi-message {{ font-size: 0.85rem; color: var(--text-secondary); line-height: 1.55; max-width: 34ch; }}
.aqi-command-side {{ padding: 1.6rem 1.9rem; border-left: 1px solid var(--line); display: flex; flex-direction: column; justify-content: center; gap: 1rem; min-width: 0; }}
.aqi-meta-row {{ display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; font-size: 0.78rem; color: var(--text-secondary); }}
.aqi-meta-row .mk {{ font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.09em; color: var(--text-muted); font-weight: 700; }}
.aqi-meta-row .mv {{ font-weight: 700; color: var(--text-primary); text-align: right; }}

/* segmented AQI gauge */
.aqi-gauge {{ width: 100%; margin-top: 0.35rem; }}
.aqi-gauge-track {{ position: relative; display: flex; height: 9px; min-height: 9px; border-radius: 999px; overflow: visible; }}
.aqi-gauge-seg {{ height: 9px; min-height: 9px; flex: 0 0 auto; }}
.aqi-gauge-seg:first-child {{ border-radius: 999px 0 0 999px; }}
.aqi-gauge-seg:last-child {{ border-radius: 0 999px 999px 0; }}
.aqi-gauge-marker {{
  position: absolute; top: -4px; width: 4px; height: 17px;
  background: var(--text-primary); border-radius: 2px;
  transform: translateX(-50%); box-shadow: 0 0 0 3px rgba(255,255,255,0.85);
}}
.aqi-gauge-scale {{ display: flex; justify-content: space-between; font-size: 0.6rem; color: var(--text-muted); margin-top: 0.35rem; font-weight: 600; }}

/* ---------- Pollutant cards ---------- */
.pollutant-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(178px, 1fr)); gap: 0.7rem; margin: 0.4rem 0 1.5rem; }}
.pollutant-card {{
  position: relative; background: var(--bg-secondary);
  border: 1px solid var(--line); border-radius: var(--radius);
  padding: 0.9rem 1rem 0.85rem;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
  overflow: hidden;
}}
.pollutant-card::before {{
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--pc, var(--zambia-green));
}}
.pollutant-card .top-c {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }}
.pollutant-card .lbl {{ font-size: 0.78rem; font-weight: 800; color: var(--text-primary); }}
.pollutant-card .status-chip {{
  font-size: 0.6rem; font-weight: 700; letter-spacing: 0.03em;
  padding: 0.16rem 0.5rem; border-radius: 999px; white-space: nowrap;
}}
.pollutant-card .val {{ display: flex; align-items: baseline; gap: 0.25rem; margin-top: 0.55rem; }}
.pollutant-card .num {{ font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; line-height: 1; }}
.pollutant-card .unit {{ font-size: 0.72rem; color: var(--text-muted); font-weight: 600; }}
.pollutant-card .desc {{ font-size: 0.68rem; color: var(--text-muted); margin-top: 0.4rem; }}

/* ---------- Panels ---------- */
.panel {{
  position: relative; background: var(--bg-secondary);
  border: 1px solid var(--line); border-radius: 14px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
  padding: 1.2rem 1.4rem; margin-bottom: 1.25rem;
}}
.panel-head {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }}
.panel-icon {{
  width: 34px; height: 34px; flex: 0 0 auto; border-radius: 9px;
  display: grid; place-items: center; color: var(--zambia-green);
  background: rgba(0, 106, 61, 0.07);
  box-shadow: inset 0 0 0 1px rgba(0, 106, 61, 0.12);
}}
.panel-title {{ font-size: 1rem; font-weight: 800; color: var(--text-primary); margin: 0; }}
.panel-sub {{ color: var(--text-muted); font-size: 0.78rem; margin: 2px 0 0; line-height: 1.5; }}

/* ---------------- KPI grid ---------- */
.kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.7rem; margin: 0.4rem 0 1.5rem; }}
.kpi {{
  position: relative; background: var(--bg-secondary);
  border: 1px solid var(--line); border-radius: var(--radius);
  padding: 1rem 1.1rem; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}}
.kpi .top {{ display: flex; justify-content: space-between; align-items: center; }}
.kpi .label {{ font-size: 0.66rem; letter-spacing: 0.09em; text-transform: uppercase; color: var(--text-muted); font-weight: 700; }}
.kpi .ico {{ color: var(--zambia-green); opacity: 0.85; }}
.kpi .value {{ font-size: 1.75rem; font-weight: 800; color: var(--text-primary); line-height: 1.25; margin-top: 6px; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }}
.kpi .delta {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; font-weight: 600; }}
.kpi .delta.up {{ color: #dc2626; }}
.kpi .delta.warn {{ color: #c2410c; }}
.kpi .delta.ok {{ color: #15803d; }}

.tag {{ display: inline-block; padding: 0.28rem 0.72rem; border-radius: 999px; font-size: 0.7rem; font-weight: 700; font-family: 'Inter', sans-serif; }}

/* ---------- Conditions table ---------- */
.conditions-card {{ background: var(--bg-secondary); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; margin: 0.4rem 0 1.5rem; }}
table.conditions {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
table.conditions th {{
  text-align: left; padding: 0.7rem 1.1rem; font-size: 0.62rem;
  text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted);
  font-weight: 700; background: #f7f8fa; border-bottom: 1px solid var(--line);
}}
table.conditions td {{ padding: 0.85rem 1.1rem; border-bottom: 1px solid var(--line); vertical-align: middle; }}
table.conditions tr:last-child td {{ border-bottom: 0; }}
table.conditions .c-name {{ font-weight: 700; color: var(--text-primary); }}
table.conditions .c-unit {{ color: var(--text-muted); font-size: 0.7rem; font-weight: 600; }}
.trend-arrow {{ font-size: 1rem; font-weight: 800; }}
.trend-arrow.worse {{ color: #dc2626; }}
.trend-arrow.better {{ color: #16a34a; }}
.trend-arrow.flat {{ color: #94a3b8; }}

/* ---------- Situation awareness ---------- */
.situation {{
  display: flex; align-items: flex-start; gap: 14px;
  border-radius: 14px; border: 1px solid var(--line);
  background: var(--bg-secondary); padding: 1.1rem 1.3rem; margin: 0.4rem 0 1.5rem;
}}
.situation .s-ico {{
  width: 38px; height: 38px; flex: 0 0 auto; border-radius: 10px;
  display: grid; place-items: center; color: #ffffff;
}}
.situation.ok .s-ico {{ background: #16a34a; }}
.situation.warn .s-ico {{ background: #f59e0b; }}
.situation.alert .s-ico {{ background: #dc2626; }}
.situation .s-title {{ font-size: 0.98rem; font-weight: 800; color: var(--text-primary); }}
.situation .s-body {{ font-size: 0.83rem; color: var(--text-secondary); line-height: 1.6; margin-top: 3px; }}
.situation.ok .s-line {{ border-left: 3px solid #16a34a; }}
.situation.warn .s-line {{ border-left: 3px solid #f59e0b; }}
.situation.alert .s-line {{ border-left: 3px solid #dc2626; }}

/* ---------- Status list (Data & model status) ---------- */
.status-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 0.65rem; }}
.status-item {{
  display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;
  background: var(--bg-secondary); border: 1px solid var(--line);
  border-radius: 10px; padding: 0.65rem 0.9rem; font-size: 0.78rem;
}}
.status-item .k {{ font-weight: 600; color: var(--text-muted); }}
.status-item .v {{ display: inline-flex; align-items: center; gap: 0.5rem; font-weight: 700; color: var(--text-primary); }}
.status-item .v.bad {{ color: #dc2626; }}
.status-item .v.amber {{ color: #b45309; }}
.status-item .v.good {{ color: #15803d; }}

/* ---------- Spotlight (model performance) ---------- */
.spotlight {{
  display: flex; align-items: center; justify-content: space-between; gap: 1.2rem;
  background: linear-gradient(120deg, rgba(0,106,61,0.05), rgba(124,45,146,0.05));
  border: 1px solid var(--line); border-radius: 14px;
  padding: 1.15rem 1.4rem; margin: 0.4rem 0 1.5rem;
}}
.spotlight .s-val {{ font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }}
.spotlight .s-label {{ font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); font-weight: 700; margin-top: 2px; }}
.spotlight .s-sub {{ font-size: 0.8rem; color: var(--text-secondary); line-height: 1.55; flex: 1; max-width: 56ch; }}
.spotlight .s-badge {{ font-size: 0.68rem; font-weight: 800; padding: 0.3rem 0.8rem; border-radius: 999px; white-space: nowrap; }}

/* ---------- Report / export panel ---------- */
.report-panel {{ display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }}
.report-panel .r-t {{ font-size: 0.95rem; font-weight: 800; color: var(--text-primary); }}
.report-panel .r-s {{ font-size: 0.76rem; color: var(--text-muted); margin-top: 2px; }}

/* ---------- Live pill ---------- */
.live-pill {{
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 0.66rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase;
  color: #15803d; background: #f0fdf4; border: 1px solid #bbf7d0;
  border-radius: 999px; padding: 0.24rem 0.8rem 0.24rem 0.6rem;
}}
.live-pill .p {{ width: 7px; height: 7px; border-radius: 50%; background: #22c55e; animation: livepulse 1.6s infinite; }}
@keyframes livepulse {{
  0% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5); }}
  70% {{ box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
}}

/* banners */
.banner {{ display: flex; align-items: flex-start; gap: 12px; border-radius: 12px; padding: 0.85rem 1.05rem; margin-bottom: 1.2rem; font-size: 0.84rem; font-weight: 500; line-height: 1.6; }}
.banner .ico {{ color: inherit; flex: 0 0 auto; }}
.banner.info {{ background: #eff6ff; color: #1e3a8a; border: 1px solid #dbeafe; }}
.banner.warn {{ background: #fffbeb; color: #92400e; border: 1px solid #fef3c7; }}
.banner.err {{ background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }}

.divider {{ border: 0; border-top: 1px solid var(--line-strong); margin: 1.6rem 0; }}
.section-label {{ display: flex; align-items: center; gap: 10px; font-size: 0.7rem; letter-spacing: 0.13em; text-transform: uppercase; color: var(--zambia-green); font-weight: 800; margin: 4px 0 14px; }}
.section-label::after {{ content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0,106,61,0.28), transparent); }}
.section-label .sub {{ color: var(--text-muted); text-transform: none; letter-spacing: 0; font-weight: 600; font-size: 0.72rem; }}
.section-kicker {{ font-size: 0.66rem; color: var(--text-muted); margin: -8px 0 1rem; font-weight: 600; }}

.flag-accent {{
  height: 3px;
  background: linear-gradient(90deg, var(--zambia-green) 0%, var(--zambia-green) 72%, #ef4444 72%, #ef4444 80%, #131a2b 80%, #131a2b 85%, #f97316 85%, #f97316 100%);
  border-radius: 999px; margin: 0 auto 1rem; max-width: 220px;
}}
.foot-note {{ color: var(--text-muted); font-size: 0.74rem; text-align: center; margin-top: 2.4rem; line-height: 1.8; border-top: 1px solid var(--line); padding-top: 1.4rem; }}

/* ---------- AQI situational block (compat) ---------- */
.aqi-flex {{ display: grid; grid-template-columns: 220px 1fr; gap: 26px; align-items: center; }}
.aqi-dial {{ border-radius: 14px; padding: 26px 18px; text-align: center; background: var(--bg-secondary); border: 1px solid var(--line); box-shadow: 0 1px 3px rgba(0,0,0,0.03); }}
.aqi-dial .num {{ font-size: 4rem; font-weight: 800; line-height: 1; color: var(--text-primary); letter-spacing: -0.03em; }}
.aqi-dial .unit {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 6px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600; }}
.aqi-dial .label {{ display: inline-block; margin-top: 14px; padding: 0.3rem 0.9rem; border-radius: 999px; background: rgba(0,0,0,0.05); color: var(--text-primary); font-weight: 700; font-size: 0.8125rem; }}
.aqi-side h3 {{ margin: 0 0 9px; font-size: 1.05rem; font-weight: 800; }}
.aqi-side p {{ color: var(--text-secondary); line-height: 1.75; margin: 0 0 16px; font-size: 0.875rem; }}
.health-list {{ list-style: none; margin: 0; padding: 0; }}
.health-list li {{ display: flex; gap: 11px; align-items: flex-start; padding: 8px 0; border-bottom: 1px dashed var(--line-strong); color: #3f3f4e; font-size: 0.85rem; line-height: 1.55; }}
.health-list li:last-child {{ border-bottom: 0; }}
.health-list li::before {{ content: "✓"; color: var(--zambia-green); font-weight: 900; }}

/* mini bars */
.mini-bars {{ display: flex; align-items: flex-end; gap: 6px; height: 46px; margin-top: 12px; }}
.mini-bars .bar {{ flex: 1; border-radius: 5px 5px 2px 2px; min-height: 4px; opacity: 0.9; }}

/* forecast cards */
.forecast {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }}
.forecast .t {{ border: 1px solid var(--line); border-radius: 12px; padding: 1.1rem 0.875rem; text-align: center; background: var(--bg-secondary); }}
.forecast .t .d {{ font-size: 0.66rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); font-weight: 700; }}
.forecast .t .i {{ font-size: 1.3rem; margin-top: 10px; }} 
.forecast .t .s {{ font-size: 0.95rem; font-weight: 800; margin-top: 8px; }}

/* pollutant focus + mini grid (compat with Next.js section) */
.pollutant-focus-card {{ background: var(--bg-secondary); border: 1px solid var(--line); border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }}
.pollutant-focus-header {{ display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 1rem; }}
.pollutant-focus-name {{ font-size: 1rem; font-weight: 800; color: var(--text-primary); display: block; }}
.pollutant-focus-desc {{ font-size: 0.75rem; color: var(--text-muted); display: block; margin-top: 0.125rem; }}
.pollutant-focus-value {{ text-align: right; }}
.pollutant-focus-number {{ font-size: 2rem; font-weight: 800; color: var(--text-primary); }}
.pollutant-focus-unit {{ font-size: 0.75rem; color: var(--text-muted); margin-left: 0.25rem; }}
.pollutant-bar-container {{ margin-bottom: 1rem; }}
.pollutant-bar-track {{ position: relative; width: 100%; height: 8px; background: var(--line-strong); border-radius: 999px; overflow: visible; }}
.pollutant-bar-fill {{ height: 100%; border-radius: 999px; }}
.pollutant-bar-guidelines {{ position: relative; width: 100%; height: 40px; margin-top: 6px; }}
.pollutant-bar-guideline {{ position: absolute; top: 0; left: 0; right: 0; }}
.pollutant-bar-guideline-line {{ position: absolute; top: 0; width: 2px; height: 10px; background: var(--text-muted); border-radius: 1px; opacity: 0.5; }}
.pollutant-bar-guideline-label {{ position: absolute; top: 12px; transform: translateX(-50%); font-size: 0.65rem; font-weight: 600; color: var(--text-muted); text-align: center; line-height: 1.3; white-space: nowrap; }}
.pollutant-bar-scale {{ display: flex; justify-content: space-between; font-size: 0.625rem; color: var(--text-muted); margin-top: 2px; }}
.pollutant-who-note {{ font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5; }}
.pollutant-who-note strong {{ color: var(--text-primary); }}
.pollutant-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.7rem; }}
.pollutant-mini-card {{ background: var(--bg-secondary); border: 1px solid var(--line); border-radius: 12px; padding: 0.95rem 1rem; }}
.pollutant-mini-header {{ display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 0.5rem; }}
.pollutant-mini-name {{ font-size: 0.8rem; font-weight: 700; color: var(--text-primary); }}
.pollutant-mini-value {{ font-size: 0.85rem; font-weight: 800; color: var(--text-primary); }}
.pollutant-mini-unit {{ font-size: 0.68rem; font-weight: 500; color: var(--text-muted); }}
.pollutant-mini-bar {{ width: 100%; height: 4px; background: var(--line-strong); border-radius: 999px; overflow: hidden; margin-bottom: 0.375rem; }}
.pollutant-mini-bar-fill {{ height: 100%; border-radius: 999px; }}
.pollutant-mini-who {{ font-size: 0.62rem; color: var(--text-muted); }}

.legend {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }}
.legend .item {{ display: inline-flex; align-items: center; gap: 8px; font-size: 0.73rem; color: var(--text-secondary); font-weight: 600; }}
.legend .sw {{ width: 13px; height: 13px; border-radius: 999px; display: inline-block; }}

.stat-strip {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.7rem; }}
.stat-strip .ss {{ border: 1px solid var(--line); border-radius: 10px; padding: 0.7rem 0.85rem; background: var(--bg-secondary); }}
.stat-strip .ss .k {{ font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 700; }}
.stat-strip .ss .v {{ font-size: 1.05rem; font-weight: 800; margin-top: 4px; color: var(--text-primary); }}

.chart-wrap {{ margin-top: 6px; }}

/* ---------- Widgets ---------- */
.stButton>button, .stFormSubmitButton>button {{
  background: var(--zambia-green) !important; color: #FFFFFF !important;
  border: 1.5px solid var(--zambia-green) !important; border-radius: 9px !important;
  font-weight: 600 !important; font-family: 'Inter', sans-serif !important;
  font-size: 0.8rem !important; padding: 0.45rem 0.95rem !important;
  transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
}}
.stButton>button:hover, .stFormSubmitButton>button:hover {{
  background: var(--zambia-green-light) !important;
  border-color: var(--zambia-green-light) !important;
  box-shadow: 0 2px 8px rgba(0, 106, 61, 0.25) !important;
  transform: translateY(-1px) !important;
}}
.stButton>button:active {{ transform: translateY(0) !important; }}

[data-testid="stDownloadButton"]>button {{
  background: var(--bg-secondary) !important; color: var(--text-primary) !important;
  border: 1.5px solid var(--line-strong) !important; border-radius: 9px !important;
  font-weight: 600 !important; font-size: 0.8rem !important;
  padding: 0.45rem 0.95rem !important; box-shadow: none !important;
}}
[data-testid="stDownloadButton"]>button:hover {{
  border-color: var(--zambia-green) !important; color: var(--zambia-green) !important;
  background: #f9fbfa !important;
}}

.stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: rgba(15, 23, 42, 0.045); border-radius: 10px; padding: 4px; }}
.stTabs [data-baseweb="tab"] {{ background: transparent; border-radius: 8px; padding: 8px 16px; font-weight: 600; color: var(--text-secondary); }}
.stTabs [aria-selected="true"] {{ background: #FFFFFF !important; color: var(--text-primary) !important; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}

.stNumberInput input, .stTextInput input, .stTextArea textarea {{
  border-radius: 10px !important; border: 1px solid var(--line-strong) !important; background: #FFFFFF !important;
}}
.stNumberInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"] > div {{
  border-radius: 10px !important; border: 1px solid var(--line-strong) !important; background: #FFFFFF !important;
}}
.stSelectbox [data-baseweb="select"] > div:hover {{ border-color: var(--zambia-green) !important; }}

[data-testid="stMetric"] {{
  background: var(--bg-secondary); border: 1px solid var(--line);
  border-radius: 12px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}}

.stCodeBlock {{ border-radius: 12px !important; border: 1px solid var(--line); }}
[data-testid="stDataFrame"] {{ border-radius: 12px; border: 1px solid var(--line); overflow: hidden; }}
[data-testid="stDataFrame"] thead tr th {{ background: #f7f8fa !important; font-weight: 700; color: var(--text-primary); }}
footer {{
  visibility: hidden;
}}
#MainMenu {{ visibility: hidden; }}
footer:after {{
  content: "AirQ Zambia - National Air Quality Intelligence Platform";
  visibility: visible; display: block;
  color: var(--text-muted); font-size: 0.72rem; text-align: center; padding: 14px;
}}

/* ---------- ML pipeline progress rail ---------- */
.pipe-overview {{
  display: flex; align-items: center; justify-content: space-between; gap: 1.4rem; flex-wrap: wrap;
  background: var(--bg-secondary); border: 1px solid var(--line); border-radius: 16px;
  padding: 1.25rem 1.5rem; box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06); margin: 0.4rem 0 1.5rem;
}}
.pipe-ov-left {{ min-width: 0; }}
.pipe-ov-label {{ font-size: 0.66rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-muted); font-weight: 800; }}
.pipe-ov-title {{ font-size: 1.25rem; font-weight: 800; color: var(--text-primary); margin-top: 4px; letter-spacing: -0.02em; }}
.pipe-ov-sub {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 3px; line-height: 1.55; }}
.pipe-ov-meter {{ flex: 1; min-width: 240px; max-width: 460px; }}
.overall-bar {{ height: 13px; border-radius: 999px; background: rgba(15, 23, 42, 0.07); overflow: hidden; margin: 0.3rem 0 0.45rem; }}
.overall-fill {{ height: 100%; border-radius: 999px; transition: width 0.4s ease; }}
.overall-scale {{ display: flex; justify-content: space-between; font-size: 0.66rem; color: var(--text-muted); font-weight: 700; letter-spacing: 0.04em; }}
.pipe-ov-big {{ font-size: 2rem; font-weight: 800; color: var(--text-primary); font-variant-numeric: tabular-nums; line-height: 1; }}
.pipe-ov-big small {{ font-size: 0.78rem; color: var(--text-muted); font-weight: 700; }}

.pipe-rail {{ position: relative; margin: 0.4rem 0 1.5rem; }}
.pipe-stage {{ display: grid; grid-template-columns: 54px 1fr; gap: 1rem; position: relative; }}
.pipe-stage + .pipe-stage {{ margin-top: 1.15rem; }}
.pipe-track {{ position: absolute; left: 26px; top: 56px; bottom: -1.15rem; width: 2px; background: var(--line-strong); }}
.pipe-stage:last-child .pipe-track {{ display: none; }}
.pipe-col {{ display: flex; flex-direction: column; align-items: center; }}
.pipe-marker {{
  width: 52px; height: 52px; flex: 0 0 auto; border-radius: 14px;
  display: grid; place-items: center; z-index: 1;
}}
.pipe-marker.completed {{ background: rgba(22, 163, 74, 0.12); color: #15803d; box-shadow: inset 0 0 0 1.5px #16a34a; }}
.pipe-marker.partial {{ background: rgba(245, 158, 11, 0.10); color: #b45309; box-shadow: inset 0 0 0 1.5px #f59e0b; }}
.pipe-marker.pending {{ background: rgba(148, 163, 184, 0.12); color: #64748b; box-shadow: inset 0 0 0 1.5px #94a3b8; }}
.pipe-marker.offline {{ background: rgba(239, 68, 68, 0.08); color: #dc2626; box-shadow: inset 0 0 0 1.5px #fca5a5; }}
.pipe-marker .n {{ font-size: 0.6rem; font-weight: 800; letter-spacing: 0.06em; }}

.pipe-body {{
  background: var(--bg-secondary); border: 1px solid var(--line); border-radius: 14px;
  padding: 1rem 1.25rem; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}}
.pipe-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap; }}
.pipe-title {{ font-size: 0.97rem; font-weight: 800; color: var(--text-primary); }}
.pipe-eyebrow {{ font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--zambia-green); font-weight: 800; margin-bottom: 3px; }}
.pipe-desc {{ font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; line-height: 1.55; max-width: 66ch; }}
.pipe-chip {{
  font-size: 0.64rem; font-weight: 800; letter-spacing: 0.07em; text-transform: uppercase;
  padding: 0.24rem 0.7rem; border-radius: 999px; white-space: nowrap;
}}
.pipe-chip.completed {{ background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }}
.pipe-chip.partial {{ background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }}
.pipe-chip.pending {{ background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }}
.pipe-chip.offline {{ background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }}
.pipe-kpis {{ display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 0.8rem; }}
.pipe-kpi {{
  font-size: 0.72rem; color: var(--text-secondary); background: #f7f8fa;
  border: 1px solid var(--line); border-radius: 8px; padding: 0.35rem 0.7rem; font-weight: 600;
}}
.pipe-kpi b {{ color: var(--text-primary); font-weight: 800; }}

.pipe-detail {{ margin-top: 0.9rem; padding-top: 0.8rem; border-top: 1px dashed var(--line-strong); }}
.pipe-note {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 0.7rem; line-height: 1.6; }}

@media (max-width: 1120px) {{
  .stApp {{ padding: 1rem !important; }}
  .aqi-command {{ grid-template-columns: 1fr; }}
  .aqi-command-side {{ border-left: 0; border-top: 1px solid var(--line); }}
  .kpi-grid, .pollutant-grid {{ grid-template-columns: 1fr 1fr; }}
  .aqi-flex, .forecast {{ grid-template-columns: 1fr; }}
  .spotlight {{ flex-direction: column; align-items: flex-start; }}
  .pipe-ov-meter {{ max-width: none; }}
}}
@media (max-width: 640px) {{
  .kpi-grid, .pollutant-grid, .status-list {{ grid-template-columns: 1fr; }}
  .topbar {{ flex-direction: column; align-items: flex-start; }}
}}
</style>
"""

# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

def insert_style():
    """Inject the global stylesheet into the app via st.markdown."""
    st.markdown(STYLE_SHEET, unsafe_allow_html=True)


def live_pill(text="Live"):
    """Pulsing "Live" badge pill as an HTML fragment."""
    return f"<span class='live-pill'><span class='p'></span>{text}</span>"


def _block(frag: str) -> str:
    """Collapse a multi-line HTML fragment to a single line so Markdown can
    never re-interpret indented lines (e.g. indented code blocks escape them
    as literal text)."""
    return " ".join(line.strip() for line in frag.splitlines() if line.strip())


def badge_html(label, style=None):
    """Soft AQI pill: color / bg / text / border per category."""
    color, bg, text, border = AQI_STYLES.get(label, AQI_STYLES["Moderate"])
    return (
        f"<span class='tag' style='background:{bg};color:{text};border:1px solid {border};"
        f"{(style or '')}'>{label}</span>"
    )


def aqi_badge_html(label):
    """Soft AQI pill for a category, as an HTML fragment (alias of badge_html)."""
    return badge_html(label)


def topbar(online=True, updated=None, sources="Open-Meteo + OpenAQ"):
    """Compact global header: brand left, system status right."""
    if updated is None:
        updated = datetime.now().strftime("%H:%M")
    state = "Online" if online else "Offline"
    dot = "on pulse" if online else "off"
    pill = "ok" if online else "err"
    updated_html = (
        f"<span class='ts'>updated {updated}</span>" if online
        else "<span class='ts'>backend unreachable</span>"
    )
    st.markdown(
        _block(
            f"""
            <div class='topbar'>
              <div class='topbar-left'>
                <div class='topbar-logo'>{ico('leaf', 22)}</div>
                <div>
                  <div class='topbar-brand'>Air<span>Q</span> Zambia</div>
                  <div class='topbar-sub'>Air quality intelligence platform</div>
                </div>
              </div>
              <div class='topbar-right'>
                <span class='system-pill {pill}'>
                  <span class='dot {dot}'></span><span class='pv'>SYSTEM {state.upper()}</span>
                </span>
                <span class='system-pill'><span class='ts'>{updated_html}</span></span>
                <span class='system-pill'>{ico('wind', 15)} <span class='ts'>{sources}</span></span>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def hero(eyebrow, title, subtitle, chips=None, snapshot=None, breadcrumb=True):
    """Compact page header. chips: [(label, value, kind)]. snapshot:
    dict with value/unit/label/color/city for a legacy hero card."""
    crumb_html = ""
    if breadcrumb:
        crumb_html = (
            "<nav class='breadcrumb'>"
            "<span class='breadcrumb-item'>World</span>"
            "<span class='breadcrumb-sep'>/</span>"
            "<span class='breadcrumb-item'>Zambia</span>"
            "</nav>"
        )

    chips_html = ""
    if chips:
        pills = "".join(
            f"<span class='page-pill {kind}'>"
            f"<span class='pl'>{label}</span>"
            f"<span class='pv'>{value}</span></span>"
            for label, value, kind in chips
        )
        chips_html = f"<div class='page-chips'>{pills}</div>"

    snap_html = ""
    if snapshot:
        color = snapshot.get("color", "#eab308")
        value = snapshot.get("value", "—")
        unit = snapshot.get("unit", "AQI")
        label = snapshot.get("label", "")
        extras = snapshot.get("extras") or []
        extras_html = "".join(
            f"<span class='extra-pill'>{e}</span>" for e in extras
        )
        snap_html = (
            "<div class='aqi-hero-card'>"
            "<div class='aqi-hero-left'>"
            f"<div class='aqi-hero-big-number' style='color:{color}'>{value}</div>"
            f"<div class='aqi-hero-badge' style='background:{color}'>{label} · {unit}</div>"
            "</div>"
            "<div class='aqi-hero-divider'></div>"
            "<div class='aqi-hero-right'>"
            f"<div class='aqi-hero-advice'>{label} air quality</div>"
            f"<div class='aqi-hero-extras'>{extras_html}</div>"
            "</div>"
            "</div>"
        )

    st.markdown(
        _block(
            f"""
            {crumb_html}
            <header class='page-header'>
              <div class='page-label'>{eyebrow}</div>
              <h1 class='page-title'>{title}</h1>
              <p class='page-subtitle'>{subtitle}</p>
              {chips_html}
            </header>
            {snap_html}
            """
        ),
        unsafe_allow_html=True,
    )


def location_bar(city, cities, key, source_label=None):
    """Breadcrumb (World / Zambia / city) beside a polished Location selector."""
    col_crumb, col_pick = st.columns([3, 2])
    with col_crumb:
        st.markdown(
            _block(
                f"""
                <div class='location-bread' style='height:100%;align-items:center;'>
                  <span>World</span><span class='breadcrumb-sep'>/</span>
                  <span>Zambia</span><span class='breadcrumb-sep'>/</span>
                  <b>{_html.escape(city)}</b>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )
    with col_pick:
        st.selectbox(
            "Location", cities, index=cities.index(city) if city in cities else 0,
            key=key, label_visibility="collapsed",
        )


def aqi_gauge_html(value):
    """Segmented EPA AQI gauge with a marker at the current value."""
    segments = []
    for lo, hi, color, label in AQI_BANDS:
        width = (hi - lo) / 500 * 100
        segments.append(
            f"<div class='aqi-gauge-seg' title='{label} ({lo}-{hi})' "
            f"style='width:{width:.1f}%;background:{color};'></div>"
        )
    pct = max(0.0, min(100.0, float(value) / 500 * 100))
    return (
        f"<div class='aqi-gauge'>"
        f"<div class='aqi-gauge-track'>"
        f"{''.join(segments)}"
        f"<div class='aqi-gauge-marker' style='left:{pct:.1f}%'></div>"
        f"</div>"
        f"<div class='aqi-gauge-scale'><span>0</span><span>100</span>"
        f"<span>200</span><span>300</span><span>500</span></div>"
        f"</div>"
    )


def aqi_command_card(snapshot):
    """Premium AQI command card. Snapshot keys: city, value, unit, label,
    color, message, model_label, confidence (0-1 or None), model_outcome,
    updated_min, source_note."""
    city = snapshot.get("city", "Zambia")
    value = snapshot.get("value", "—")
    unit = snapshot.get("unit", "AQI")
    label = snapshot.get("label", "")
    color = snapshot.get("color", "#eab308")
    message = snapshot.get("message", "")
    model_label = snapshot.get("model_label", "Hybrid SVM")
    confidence = snapshot.get("confidence")
    outcome = snapshot.get("model_outcome")
    updated_min = snapshot.get("updated_min")

    conf_row = ""
    if confidence is not None:
        pct = max(0.0, min(1.0, float(confidence))) * 100
        conf_row = (
            "<div class='aqi-meta-row'>"
            "<span class='mk'>Model confidence</span>"
            f"<span class='mv'>{pct:.1f}%</span>"
            "</div>"
        )
    elif outcome:
        conf_row = (
            "<div class='aqi-meta-row'>"
            "<span class='mk'>Model output</span>"
            f"<span class='mv'>{_html.escape(str(outcome))}</span>"
            "</div>"
        )

    outcome_row = ""
    if outcome:
        out_badge = badge_html(outcome) if outcome in AQI_STYLES else (
            f"<span class='mv'>{_html.escape(str(outcome))}</span>"
        )
        outcome_row = (
            "<div class='aqi-meta-row'>"
            "<span class='mk'>SVM classification</span>"
            f"<span class='mv'>{out_badge}</span>"
            "</div>"
        )

    driver_row = ""
    if snapshot.get("dominant"):
        driver_row = (
            "<div class='aqi-meta-row'>"
            "<span class='mk'>AQI driven by</span>"
            f"<span class='mv'>{_html.escape(str(snapshot['dominant']))}</span>"
            "</div>"
        )

    updated_row = (
        "<div class='aqi-meta-row'>"
        "<span class='mk'>Updated</span>"
        f"<span class='mv'>{updated_min} min ago</span>"
        "</div>"
    ) if updated_min is not None else ""

    source_row = (
        "<div class='aqi-meta-row'>"
        "<span class='mk'>Inputs</span>"
        f"<span class='mv'>{_html.escape(snapshot.get('source_note', 'Open-Meteo + OpenAQ'))}</span>"
        "</div>"
    )

    st.markdown(
        _block(
            f"""
            <div class='aqi-command'>
              <div class='aqi-command-main'>
                <div class='aqi-city'>{ico('pin', 17)} {_html.escape(city)}</div>
                <div class='aqi-eyebrow'>Live Air Quality Index · {unit}</div>
                <div class='aqi-numbers'>
                  <span class='aqi-big' style='color:{color}'>{value}</span>
                  <span class='aqi-us'>US AQI⁺</span>
                </div>
                <div style='margin-bottom:0.6rem'>{badge_html(label)}</div>
                <div class='aqi-message'>{message}</div>
              </div>
              <div class='aqi-command-side'>
                {aqi_gauge_html(float(value) if str(value).replace('.','').isdigit() else 0.0)}
                {driver_row}
                {outcome_row}
                {conf_row}
                {updated_row}
                {source_row}
                <div class='aqi-meta-row'>
                  <span class='mk'>Model</span>
                  <span class='mv'>{_html.escape(model_label)}</span>
                </div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def pollutant_grid(items):
    """items: list of dicts {label, unit, desc, value, status, color}."""
    cards = ""
    for it in items:
        status_color = it.get("color", ZAMBIA)
        status_text = it.get("status", "")
        status_bg = f"{status_color}1a"
        cards += (
            f"<div class='pollutant-card' style='--pc:{status_color}'>"
            f"<div class='top-c'>"
            f"<span class='lbl'>{_html.escape(it['label'])}</span>"
            f"<span class='status-chip' style='color:{status_color};background:{status_bg};'>{status_text}</span>"
            f"</div>"
            f"<div class='val'><span class='num'>{it['value']:g}</span>"
            f"<span class='unit'>{_html.escape(it['unit'])}</span></div>"
            f"<div class='desc'>{_html.escape(it['desc'])}</div>"
            f"</div>"
        )
    st.markdown(f"<div class='pollutant-grid'>{cards}</div>", unsafe_allow_html=True)


def conditions_table(rows):
    """rows: list of dicts {label, unit, value, status, color, trend, trend_note}."""
    body = ""
    for r in rows:
        trend = r.get("trend", "flat")
        arrow = {"worse": "↑", "better": "↓", "flat": "→"}.get(trend, "→")
        note = r.get("trend_note") or ""
        body += (
            "<tr>"
            f"<td class='c-name'>{_html.escape(r['label'])}</td>"
            f"<td>{r['value']:g} <span class='c-unit'>{_html.escape(r['unit'])}</span></td>"
            f"<td><span style='color:{r['color']};font-weight:700'>{_html.escape(r['status'])}</span></td>"
            f"<td><span class='trend-arrow {trend}'>{arrow}</span> "
            f"<span style='color:var(--text-muted);font-size:0.72rem'>{note}</span></td>"
            "</tr>"
        )
    st.markdown(
        _block(
            f"""
            <div class='conditions-card'>
              <table class='conditions'>
                <thead><tr><th>Pollutant</th><th>Current</th><th>Status</th><th>Trend</th></tr></thead>
                <tbody>{body}</tbody>
              </table>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def situation_panel(status, city, message):
    """Dynamically graded situation-awareness panel from the real AQI class."""
    status = status or "Good"
    if status in ("Good", "Moderate"):
        tone, icon, title = "ok", "check", "No significant air-quality alerts detected"
        body = (
            f"Conditions in {city} are {status.lower()}. Routine monitoring continues; "
            "no protective action required for the general population."
        )
    elif status in ("Unhealthy",):
        tone, icon, title = "warn", "alert", "Elevated pollution detected"
        body = (
            f"Levels in {city} are {status.lower()} — children, the elderly and people "
            "with respiratory conditions should limit prolonged outdoor exertion."
        )
    else:
        tone, icon, title = "alert", "alert", "HEALTH ALERT · Increased attention required"
        body = (
            f"Air quality conditions in {city} are {status.lower()} ({message}). "
            "Everyone is advised to reduce outdoor activity and the public "
            "should monitor updates."
        )
    st.markdown(
        _block(
            f"""
            <div class='situation {tone}'>
              <div class='s-ico'>{ico(icon, 20)}</div>
              <div class='s-line'>
                <div class='s-title'>{title}</div>
                <div class='s-body'>{body}</div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def status_list(rows):
    """rows: list of (label, value, tone) with tone in good/warn/bad/neutral."""
    cells = ""
    for label, value, tone in rows:
        cls = f" {tone}" if tone in ("good", "warn", "bad") else ""
        dot = "on" if tone == "good" else ("off" if tone == "bad" else (
            "amber" if tone == "warn" else ""))
        cells += (
            f"<div class='status-item'>"
            f"<span class='k'>{label}</span>"
            f"<span class='v{cls}'>{f'<span class=dot {dot}></span>' if dot else ''}{value}</span>"
            f"</div>"
        )
    st.markdown(f"<div class='status-list'>{cells}</div>", unsafe_allow_html=True)


def spotlight(value, label, sub, badge_text=None, badge_style="background:#f0fdf4;color:#15803d;"):
    """Highlight card for a headline metric with an optional status badge."""
    st.markdown(
        _block(
            f"""
            <div class='spotlight'>
              <div>
                <div class='s-val'>{value}</div>
                <div class='s-label'>{label}</div>
              </div>
              <div class='s-sub'>{sub}</div>
              <span class='s-badge' style='{badge_style}'>{badge_text or ""}</span>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def risk_chip(level):
    """Coloured "Low/Moderate/High risk" chip for an AQI category, as HTML."""
    mapping = {
        "Good": ("#f0fdf4", "#15803d", "Low"),
        "Moderate": ("#fefce8", "#a16207", "Moderate"),
        "Sensitive": ("#fff7ed", "#c2410c", "Elevated"),
        "Unhealthy": ("#fef2f2", "#dc2626", "High"),
        "Very Unhealthy": ("#faf5ff", "#6b21a8", "Very high"),
        "Hazardous": ("#450a0a", "#fca5a5", "Extreme"),
    }
    bg, text, label = mapping.get(level, ("#f0fdf4", "#15803d", "Low"))
    return f"<span class='tag' style='background:{bg};color:{text};'>{label} risk</span>"


def banner(kind, message):
    """Full-width info/warn/err banner; ``message`` may contain HTML."""
    ico_map = {"info": "check", "warn": "alert", "err": "alert"}
    st.markdown(
        f"<div class='banner {kind}'><span class='ico'>{ico(ico_map.get(kind, 'check'), 18)}</span>"
        f"{message}</div>",
        unsafe_allow_html=True,
    )


def panel_open(title, icon=None, subtitle=""):
    """Open a white panel card with an optional icon and subtitle."""
    icon_html = f"<span class='panel-icon'>{ico(icon) if icon and icon not in ('', None) else ''}</span>"
    sub = f"<p class='panel-sub'>{subtitle}</p>" if subtitle else ""
    st.markdown(
        _block(
            f"""
            <div class='panel'>
              <div class='panel-head'>
                {icon_html}
                <div>
                  <div class='panel-title'>{title}</div>
                  {sub}
                </div>
              </div>
            """
        ),
        unsafe_allow_html=True,
    )


def panel_close():
    """Close a panel opened with panel_open (emits a closing div tag)."""
    st.markdown("</div>", unsafe_allow_html=True)


def kpi_grid(items):
    """items: list of (label, value, delta, direction, icon_name)."""
    cells = ""
    for item in items:
        label, value, delta, direction = item[0], item[1], item[2], item[3]
        icon = item[4] if len(item) > 4 and item[4] else ""
        ico_html = f"<span class='ico'>{ico(icon) if icon else ''}</span>" if icon else ""
        cls = {"up": "up", "warn": "warn", "ok": "ok"}.get(direction, "")
        delta_html = f"<div class='delta {cls}'>{delta}</div>" if delta else ""
        cells += (
            f"<div class='kpi'>"
            f"<div class='top'><div class='label'>{label}</div>{ico_html}</div>"
            f"<div class='value'>{value}</div>{delta_html}</div>"
        )
    st.markdown(f"<div class='kpi-grid'>{cells}</div>", unsafe_allow_html=True)


def stat_strip(items):
    """Inline key-value statistic strip; items: list of (label, value)."""
    cells = "".join(
        f"<div class='ss'><div class='k'>{k}</div><div class='v'>{v}</div></div>"
        for k, v in items
    )
    st.markdown(f"<div class='stat-strip'>{cells}</div>", unsafe_allow_html=True)


def mini_bars(values, color="#0a8a4e"):
    """Tiny vertical bar sparkline scaled to the max input value."""
    max_v = max(values) or 1
    bars = "".join(
        f"<div class='bar' style='height:{max(6, int(v / max_v * 46))}px;"
        f"background:linear-gradient(180deg,{color},{color}88)' title='{v}'></div>"
        for v in values
    )
    st.markdown(f"<div class='mini-bars'>{bars}</div>", unsafe_allow_html=True)


def current_time_badge():
    """Current timestamp formatted for "Updated …" pills."""
    stamp = datetime.now().strftime("%d %b %Y · %H:%M")
    return f"<span class='extra-pill'>Updated {stamp}</span>"


def chart_card(fig, key=None):
    """Render a plotly figure full-width inside the app."""
    st.plotly_chart(fig, width="stretch", key=key)


def section_label(text, sub=None):
    """Zambia-green section heading with an optional muted subtitle."""
    sub_html = f"<span class='sub'>· {_html.escape(sub)}</span>" if sub else ""
    st.markdown(
        f"<div class='section-label'>{text}{sub_html}</div>", unsafe_allow_html=True
    )


def legend(items):
    """Colour-key legend; items: list of (label, hex color)."""
    swatches = "".join(
        f"<span class='item'><span class='sw' style='background:{color}'></span>{label}</span>"
        for label, color in items
    )
    st.markdown(f"<div class='legend'>{swatches}</div>", unsafe_allow_html=True)


def pollutant_mini_grid(items):
    """Compact pollutant cards showing value vs WHO 24-hour guideline."""
    cards = ""
    for it in items:
        label = it["label"]
        value = it["value"]
        unit = it["unit"]
        who = it.get("who_24h", 100)
        ratio = it.get("ratio_override")
        if ratio is None:
            ratio = value / who if who else 0
        fill = "#ef4444" if ratio > 1 else ("#f97316" if ratio > 0.7 else "#22c55e")
        pct = max(0, min(100, ratio * 100))
        cards += (
            f"<div class='pollutant-mini-card'>"
            f"<div class='pollutant-mini-header'>"
            f"<span class='pollutant-mini-name'>{label}</span>"
            f"<span class='pollutant-mini-value'>{value:g} "
            f"<span class='pollutant-mini-unit'>{unit}</span></span></div>"
            f"<div class='pollutant-mini-bar'>"
            f"<div class='pollutant-mini-bar-fill' style='width:{pct:.1f}%;background:{fill}'></div>"
            f"</div>"
            f"<span class='pollutant-mini-who'>WHO: {who} {unit}</span>"
            f"</div>"
        )
    st.markdown(f"<div class='pollutant-grid'>{cards}</div>", unsafe_allow_html=True)


def foot_note(*lines):
    """Standardised footer block listing one or more note lines."""
    st.markdown(
        "<div class='foot-note'><div class='flag-accent'></div>"
        + "<br/>".join(lines)
        + "</div>",
        unsafe_allow_html=True,
    )


def AQI_ANGLE(value):
    """Map an AQI value to a 0-360° gauge angle (capped)."""
    return max(0, min(360, int(value / 300 * 360)))