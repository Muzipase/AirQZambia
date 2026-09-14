"""Command Center — national overview for policymakers and officials.

A data-dense, real-time operational view: location, live AQI, pollutant
cards, real trend (24h / 7d / 30d), pollutant conditions, situation
awareness and system status. All figures come from the backend live feed
and Open-Meteo archive — nothing is fabricated.
"""

import streamlit as st

from style_assets import (
    _block,
    aqi_badge_html,
    aqi_command_card,
    banner,
    conditions_table,
    foot_note,
    hero,
    ico,
    live_pill,
    location_bar,
    panel_close,
    panel_open,
    pollutant_grid,
    section_label,
    situation_panel,
    status_list,
)
from state import (
    CITIES,
    POLLUTANTS,
    SOURCE_API_MAP,
    fetch_api_status,
    get_live_snapshot,
    get_model_names,
    get_trend_frame,
    pollutant_status,
    _minutes_ago,
)

TREND_COLORS = {
    "PM2.5": "#006a3d",
    "PM10": "#34d399",
    "NO₂": "#0a8a4e",
    "SO₂": "#fbbf24",
    "CO": "#94a3b8",
    "O₃": "#f59e0b",
}

PERIOD_LABEL = {"24h": "Last 24 hours", "7d": "Past 7 days", "30d": "Past 30 days"}


def _pollutant_items(readings):
    """Real pollutant cards (PM2.5 uses its EPA class, others WHO ratio)."""
    items = []
    for key, meta in POLLUTANTS.items():
        value = readings.get(key)
        if value is None:
            continue
        if key == "pm25":
            status, color = pollutant_status(value, meta["who_24h"], pm25_override=value)
        else:
            status, color = pollutant_status(value, meta["who_24h"])
        items.append({
            "label": meta["label"], "unit": meta["unit"], "desc": meta["desc"],
            "value": value, "status": status, "color": color,
        })
    return items


def _trend_direction(current, previous):
    if previous is None or previous == 0:
        return "flat"
    diff = current - previous
    if abs(diff) / abs(previous) < 0.02:
        return "flat"
    return "worse" if diff > 0 else "better"


def _conditions_rows(snapshot, period_df):
    rows = []
    for key, meta in POLLUTANTS.items():
        current = snapshot["readings"].get(key)
        if current is None:
            continue
        if key == "pm25":
            status, color = pollutant_status(current, meta["who_24h"],
                                                 pm25_override=current)
        else:
            status, color = pollutant_status(current, meta["who_24h"])
        prev = None
        if period_df is not None and not period_df.empty:
            col = "PM2.5" if key == "pm25" else meta["label"]
            if col not in period_df.columns and key in period_df.columns:
                col = key
            if col in period_df.columns:
                values = period_df[col].dropna()
                if len(values) >= 2:
                    prev = float(values.iloc[-2])
        trend = _trend_direction(current, prev)
        note = "vs prev. period" if prev is not None else ""
        rows.append({
            "label": meta["label"], "unit": meta["unit"], "value": current,
            "status": status, "color": color, "trend": trend, "trend_note": note,
        })
    return rows


def _trend_chart(period, df):
    import plotly.graph_objects as go

    if period == "24h":
        x = df["timestamp"]
        label = "hourly station feed"
    else:
        x = df["date"]
        label = "daily average"

    fig = go.Figure()
    aqi = df["pm25"] if "pm25" in df.columns else None
    if aqi is not None:
        fig.add_trace(go.Scatter(
            x=x, y=aqi.round(1), name="AQI (PM2.5)",
            mode="lines+markers", line=dict(color="#006a3d", width=2.4),
            marker=dict(size=5),
            hovertemplate="%{x|%d %b %H:%M}<br><b>AQI %{y:.1f}</b><extra></extra>",
        ))
    for col, color in (("pm25", "#16a34a"), ("pm10", "#94a3b8")):
        if col in df.columns:
            name = "PM2.5 µg/m³" if col == "pm25" else "PM10 µg/m³"
            fig.add_trace(go.Scatter(
                x=x, y=df[col].round(1), name=name,
                mode="lines", line=dict(color=color, width=1.4, dash="dot"),
                hovertemplate="%{x|%d %b %H:%M}<br>%{fullData.name}: %{y:.1f}<extra></extra>",
            ))

    fig.update_layout(
        margin=dict(l=8, r=8, t=18, b=8),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(15,23,42,0.06)", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="rgba(15,23,42,0.06)", title=None, tickfont=dict(size=11)),
        font=dict(family="Inter", color="#4b5563", size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=12)),
    )
    st.markdown(
        f"<p class='section-kicker'>{label} · real backend telemetry</p>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, width="stretch", key=f"trend_{period}")
    return fig


def render():
    stats = fetch_api_status()
    model_names = get_model_names(stats)
    source = SOURCE_API_MAP.get(st.session_state.get("data_source", ""), "auto")
    city = st.session_state.get("overview_city", CITIES[0])

    hero(
        "Situation · Command Center",
        "Zambia Air Quality Command Center",
        "Real-time monitoring, forecasting and decision support for urban Zambia.",
        chips=[
            ("Backend", "Online" if stats else "Offline", "good" if stats else "bad"),
            ("Models", ", ".join(model_names[:2]) if model_names else "No model loaded",
             "good" if model_names else "bad"),
            ("City", city, "good"),
        ],
        breadcrumb=False,
    )

    location_bar(city, CITIES, key="overview_city")

    if not stats:
        banner(
            "warn",
            "Backend API is not reachable — showing approved reference values. "
            "Start <b>localhost:8000</b> for live telemetry.",
        )

    snapshot = get_live_snapshot(city=city, source=source)
    snapshot["updated_min"] = _minutes_ago(snapshot.get("timestamp"))
    aqi_command_card(snapshot)

    # ---- Pollutant cards (six criteria pollutants) ---------------------
    section_label("Pollutant levels", "all six criteria pollutants")
    pollutant_grid(_pollutant_items(snapshot["readings"]))

    # ---- Live / historical trend ---------------------------------------
    section_label("Air quality trend", "select a period")
    period = st.segmented_control(
        "Trend period", options=["24h", "7d", "30d"], default="7d",
        key="trend_period", help="24h uses the live station feed; 7d/30d use the Open-Meteo archive.",
    ) or "7d"

    with st.spinner(f"Loading {PERIOD_LABEL.get(period, period)}..."):
        period, trend_df = get_trend_frame(period, city=city)

    if trend_df is None or trend_df.empty:
        panel_open(
            "Air quality trend",
            "trend",
            "Historical telemetry is temporarily unavailable.",
        )
        banner("info", "No trend records for this period yet. Live readings still power the cards above.")
        panel_close()
        conditions_df = None
    else:
        st.markdown(
            "<div class='panel'>"
            f"<div class='panel-head'><span class='panel-icon'>{ico('trend', 17)}</span>"
            "<div><div class='panel-title'>Air quality trend</div>"
            f"<p class='panel-sub'>{PERIOD_LABEL.get(period, period)} · {city}</p></div></div>",
            unsafe_allow_html=True,
        )
        _trend_chart(period, trend_df)
        st.markdown("</div>", unsafe_allow_html=True)
        conditions_df = trend_df

    # ---- Pollutant conditions table -------------------------------------
    section_label("Pollutant conditions", "current · status · trend")
    conditions_table(_conditions_rows(snapshot, conditions_df))

    # ---- Situation awareness --------------------------------------------
    section_label("Situation awareness")
    situation_panel(snapshot["label"], city, snapshot["message"])

    # ---- Air pollutants focus (WHO-policy detail) -----------------------
    section_label("WHO guideline perspective", "how today compares to guidance")
    pm25_meta = POLLUTANTS["pm25"]
    pm25 = snapshot["readings"].get("pm25", 0.0)
    pm25_fill = "#ef4444" if pm25 > 35.4 else ("#f97316" if pm25 > 12.0 else "#22c55e")
    st.markdown(
        _block(
            f"""
            <div class='pollutant-focus-card'>
              <div class='pollutant-focus-header'>
                <div>
                  <span class='pollutant-focus-name'>{pm25_meta['label']}</span>
                  <span class='pollutant-focus-desc'>{pm25_meta['desc']}</span>
                </div>
                <div class='pollutant-focus-value'>
                  <span class='pollutant-focus-number'>{pm25:g}</span>
                  <span class='pollutant-focus-unit'>µg/m³</span>
                </div>
              </div>
              <div class='pollutant-bar-container'>
                <div class='pollutant-bar-track'>
                  <div class='pollutant-bar-fill'
                       style='width:{min(pm25 / 150 * 100, 100):.1f}%;background:{pm25_fill};'/>
                </div>
                <div class='pollutant-bar-guidelines'>
                  <span class='pollutant-bar-guideline-line' style='left:{(5 / 150) * 100:.1f}%'/>
                  <span class='pollutant-bar-guideline-label' style='left:{(5 / 150) * 100:.1f}%'>WHO annual<br/>5 µg/m³</span>
                  <span class='pollutant-bar-guideline-line' style='left:{(15 / 150) * 100:.1f}%'/>
                  <span class='pollutant-bar-guideline-label' style='left:{(15 / 150) * 100:.1f}%'>WHO 24h<br/>15 µg/m³</span>
                </div>
                <div class='pollutant-bar-scale'><span>0</span><span>50</span><span>100</span><span>150 µg/m³</span></div>
              </div>
              <p class='pollutant-who-note'>
                PM2.5 is currently <strong>{pm25 / 5:.1f}×</strong> the WHO annual guideline
                and <strong>{pm25 / 15:.1f}×</strong> the WHO 24-hour guideline.
              </p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # ---- Data & model status + reports ----------------------------------
    col_status, col_report = st.columns([3, 2])

    with col_status:
        section_label("Data & model status")
        model_names_now = get_model_names(stats)
        if "optimized_svm" in model_names_now:
            model_label = "Bayesian-Optimized SVM"
        else:
            model_label = ", ".join(model_names_now[:2]) or "None"
        pool = (stats or {}).get("data", {}).get("raw_data")
        source_icon = "Open-Meteo active" if "openmeteo" in source else (
            "OpenAQ active" if "openaq" in source else "Auto · both feeds"
        )
        status_list(
            [
                ("Backend", "Online" if stats else "Offline", "good" if stats else "bad"),
                ("Telemetry pool", "Available" if pool else "N/A",
                 "good" if pool else "warn"),
                ("Data source", source_icon, "good"),
                ("Model", model_label, "good"),
                ("City", city, "neutral"),
            ]
        )
    with col_report:
        section_label("Reports & export")
        st.markdown(
            "<div class='panel report-panel'>"
            "<div><div class='r-t'>Trend report</div>"
            "<div class='r-s'>Download the current period as CSV</div></div>",
            unsafe_allow_html=True,
        )
        if trend_df is not None and not trend_df.empty:
            csv_name = f"{city.lower()}_{period}_air_quality_trend.csv"
            st.download_button(
                "Download CSV",
                data=trend_df.to_csv(index=False),
                file_name=csv_name,
                mime="text/csv",
            )
        else:
            st.download_button(
                "Download reference CSV",
                data=__import__("pandas").DataFrame(
                    snapshot["readings"].items(), columns=["pollutant", "value"]
                ).to_csv(index=False),
                file_name=f"{city.lower()}_reference_readings.csv",
                mime="text/csv",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Operational handoff ---------------------------------------------
    col_next, col_advice = st.columns([1, 1])

    with col_next:
        panel_open(
            "What's next",
            "layers",
            "Decision-support guidance for this session.",
        )
        outcome = snapshot.get("prediction")
        conf = snapshot.get("confidence")
        if outcome is not None:
            from style_assets import risk_chip

            st.markdown(
                "<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:12px;'>"
                f"{live_pill('Live monitoring')} {risk_chip(outcome)}"
                f"{f'<span style=font-size:.78rem;color:#4b5563>Model confidence {float(conf)*100:.1f}%</span>' if conf is not None else ''}"
                "</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            "<ul class='health-list'>"
            "<li>Review the <b>Forecast &amp; Scenarios</b> page for the model outlook.</li>"
            "<li>Open <b>Model Performance</b> to verify class-level reliability.</li>"
            "<li>Use <b>Explainability</b> to see which inputs drive the classification.</li>"
            "</ul>",
            unsafe_allow_html=True,
        )
        panel_close()

    with col_advice:
        panel_open(
            "Health advisory",
            "shield",
            "Immediate advice for at-risk groups.",
        )
        aqi_badge = aqi_badge_html(snapshot["label"])
        st.markdown(
            f"<div style='font-size:.88rem;line-height:1.7;color:#4b5563;'>"
            f"Current conditions in <b>{city}</b> are <b>{snapshot['label']}</b>. "
            f"{snapshot['message']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;'>"
            f"{aqi_badge}<span class='tag' style='background:#f0fdf4;color:#15803d;'>"
            f"{snapshot['model_label']}</span></div>",
            unsafe_allow_html=True,
        )
        panel_close()

    foot_note(
        f"Aggregate of station readings for {city} · Values refresh automatically.",
        "AQI follows the US-EPA quick index on PM2.5. Classification by the tuned hybrid SVM.",
        "Hybrid SMOTE-Tomek + Bayesian-Optimized SVM · Urban Zambia",
    )