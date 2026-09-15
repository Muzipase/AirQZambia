"""Historical Data — browse the daily-averaged air-quality archive.

Daily averages come from the Open-Meteo archive via the backend
(/public/city/{city}/historical) for Lusaka, Ndola and Kitwe. The page offers
a full period overview, per-pollutant conditions, configurable trend charts,
archive statistics and CSV export.
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from style_assets import (
    banner,
    foot_note,
    hero,
    legend,
    panel_close,
    panel_open,
    section_label,
    stat_strip,
)
from state import (
    CITIES,
    POLLUTANTS,
    classify_pm25,
    fetch_api_status,
    fetch_historical_payload,
    get_model_names,
)

TREND_COLORS = {
    "pm25": "#006a3d",
    "pm10": "#94a3b8",
    "no2": "#f97316",
    "so2": "#eab308",
    "co": "#6366f1",
    "o3": "#f59e0b",
}

ARCHIVE_START = date(2023, 1, 1)
MAX_RANGE_DAYS = 366


def _worst_day(df):
    """Return (date, aqi_level, pm25) for the highest-PM2.5 day in the frame."""
    pm = df["pm25"].dropna() if "pm25" in df.columns else pd.Series(dtype=float)
    if pm.empty:
        return None
    idx = pm.idxmax()
    value = float(pm.loc[idx])
    level = classify_pm25(value)[0]
    the_date = df.loc[idx, "date"]
    return the_date.date(), level, value


def _conditions_rows(payload):
    """Mean-per-pollutant conditions for the selected archive period."""
    stats = payload["stats"]
    rows = []
    for key, meta in POLLUTANTS.items():
        info = stats.get(key) or {}
        mean = info.get("mean")
        if mean is None:
            continue
        rows.append({
            "label": meta["label"],
            "unit": meta["unit"],
            "value": float(mean),
            "who_24h": meta["who_24h"],
        })
    return rows


def _trend_chart(payload, selected):
    """Build a Plotly multi-line figure of daily pollutant averages for the selected columns."""
    import plotly.express as px
    import plotly.graph_objects as go

    df = payload["df"]
    shown = [c for c in selected if c in df.columns and df[c].notna().any()]
    if not shown:
        return None

    fig = go.Figure()
    for key in shown:
        meta = POLLUTANTS[key]
        sub = df[df[key].notna()][["date", key]]
        fig.add_trace(go.Scatter(
            x=sub["date"], y=sub[key].round(2), name=meta["label"],
            mode="lines", line=dict(color=TREND_COLORS.get(key, "#0a8a4e"), width=2.2),
            hovertemplate="%{x|%d %b %Y}<br><b>%{y:.1f}</b> µg/m³<extra>%{fullData.name}</extra>",
        ))

    fig.update_layout(
        margin=dict(l=8, r=8, t=24, b=8),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(15,23,42,0.06)", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="rgba(15,23,42,0.06)", title=None, tickfont=dict(size=11)),
        font=dict(family="Inter", color="#4b5563", size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=12)),
    )
    return fig


def _stats_table(payload):
    """Return a per-pollutant summary DataFrame with days covered, min/max/mean and trend."""
    rows = []
    for key, meta in POLLUTANTS.items():
        info = payload["stats"].get(key) or {}
        if not info or info.get("count", 0) == 0:
            continue
        rows.append({
            "Pollutant": meta["label"],
            "Days": int(info.get("count", 0)),
            "Min (µg/m³)": round(float(info.get("min") or 0), 1),
            "Max (µg/m³)": round(float(info.get("max") or 0), 1),
            "Mean (µg/m³)": round(float(info.get("mean") or 0), 1),
            "Trend": info.get("trend", "stable"),
        })
    return pd.DataFrame(rows)


def render():
    """Render the Historical Data page: date range explorer, archive conditions and CSV export."""
    stats = fetch_api_status()
    model_names = get_model_names(stats)

    hero(
        "Decision Support · History",
        "Historical Air Quality",
        "Daily-averaged archive for urban Zambia from the Open-Meteo record. "
        "Explore pollutant levels, long-range trends and download the raw series.",
        chips=[
            ("Backend", "Online" if stats else "Offline", "good" if stats else "bad"),
            ("Archive", "Open-Meteo", "good"),
            ("Coverage", "2023 → today", "good"),
        ],
        breadcrumb=True,
    )

    if not stats:
        banner(
            "warn",
            "Backend API is not reachable — historical records will be unavailable. "
            "Start <b>localhost:8000</b> to load the archive.",
        )

    panel_open(
        "Archive selection",
        "database",
        "Choose a city and period. Daily values are averaged from hourly station telemetry.",
    )
    c_city, c_start, c_end = st.columns([1, 1, 1])
    with c_city:
        city = st.selectbox("City", CITIES, index=0, key="hist_city")
    with c_start:
        default_start = date.today() - timedelta(days=120)
        start_raw = st.date_input(
            "Start date", value=min(default_start, date.today() - timedelta(days=1)),
            min_value=ARCHIVE_START, max_value=date.today() - timedelta(days=1),
            key="hist_start",
        )
    with c_end:
        default_end = date.today() - timedelta(days=1)
        end_raw = st.date_input(
            "End date", value=default_end,
            min_value=ARCHIVE_START, max_value=default_end,
            key="hist_end",
        )
    panel_close()

    start_date = start_raw.strftime("%Y-%m-%d")
    end_date = end_raw.strftime("%Y-%m-%d")

    if start_raw > end_raw:
        banner("err", "Start date must be on or before the end date.")
        foot_note("Values are daily means of the Open-Meteo hourly archive for each city.")
        return

    range_days = (end_raw - start_raw).days + 1
    if range_days > MAX_RANGE_DAYS:
        banner("info", "Requested period exceeds one year — showing daily means, which grow "
                       "slower than hourly loads but still require a connection.")

    with st.spinner(f"Loading historical archive for {city}..."):
        payload = fetch_historical_payload(city, start_date, end_date)

    if payload is None:
        panel_open(
            "Historical archive",
            "database",
            "No records matched the selected period.",
        )
        banner("info", "No daily records are available for this range yet. "
                       "Try a narrower window or confirm the backend is running.")
        panel_close()
        foot_note("Values are daily means of the Open-Meteo hourly archive for each city.")
        return

    df = payload["df"]
    span_days = (df["date"].max() - df["date"].min()).days + 1
    worst = _worst_day(df)

    stat_strip(
        [
            ("City", payload["city"]),
            ("Period", f"{df['date'].min().strftime('%d %b %Y')} → "
                       f"{df['date'].max().strftime('%d %b %Y')}"),
            ("Days recorded", f"{len(df)} / {span_days}"),
            ("PM2.5 mean", f"{(payload['stats'].get('pm25', {}) or {}).get('mean', '—')} µg/m³"
             if (payload['stats'].get('pm25', {}) or {}).get('mean') is not None else "PM2.5 mean —"),
        ]
    )

    section_label("Archive conditions", f"period means vs WHO 24-hour guidance · {city}")
    from style_assets import pollutant_mini_grid

    condition_rows = _conditions_rows(payload)
    if condition_rows:
        pollutant_mini_grid(condition_rows)
    else:
        banner("info", "No pollutant means were reported for this period.")

    if worst is not None:
        st.markdown(
            f"<div style='background:#fff;border:1px solid rgba(15,23,42,0.07);border-radius:14px;"
            f"padding:12px 16px;margin-top:10px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;'>"
            f"<span style='font-weight:800;color:#111827'>Worst day</span> "
            f"<span style='font-size:.84rem;color:#4b5563'>{worst[0]} · "
            f"PM2.5 {worst[2]:.1f} µg/m³</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    section_label("Daily trend", "select pollutants to compare")
    default_selected = ["pm25"]
    available = [k for k in POLLUTANTS if k in df.columns and df[k].notna().any()]
    selected = st.multiselect(
        "Pollutants", options=available, default=[k for k in default_selected if k in available],
        key="hist_pollutants",
    ) or available

    fig = _trend_chart(payload, selected)
    if fig is not None:
        st.plotly_chart(fig, width="stretch", key="history_trend")
    else:
        banner("info", "No values recorded for the selected pollutants.")

    legend(
        [
            ("PM2.5", TREND_COLORS["pm25"]),
            ("PM10", TREND_COLORS["pm10"]),
            ("NO₂", TREND_COLORS["no2"]),
            ("SO₂", TREND_COLORS["so2"]),
            ("CO", TREND_COLORS["co"]),
            ("O₃", TREND_COLORS["o3"]),
        ]
    )

    section_label("Archive statistics", "min · max · mean per pollutant")
    stats_table = _stats_table(payload)
    if not stats_table.empty:
        st.dataframe(stats_table, width="stretch", hide_index=True)
    else:
        banner("info", "No statistics are available for this period.")

    section_label("Daily records", "raw series for inspection and export")
    display_df = df.copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    max_cols = display_df.columns.tolist()
    st.dataframe(display_df, width="stretch", hide_index=True, column_order=max_cols)

    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False),
        file_name=f"{city.lower()}_historical_{start_date}_{end_date}.csv",
        mime="text/csv",
    )

    foot_note(
        "Daily values are arithmetic means of hourly Open-Meteo archive readings.",
        "Coverage starts 2023 and extends to yesterday; empty days are gaps in the archive.",
        "AQI wording follows the US-EPA quick index applied to daily PM2.5 means.",
    )