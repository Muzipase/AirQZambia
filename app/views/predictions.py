"""Predictions — live city forecasting and manual scenario scoring.

Decision-support framing: CURRENT condition → FORECAST outcome → RISK LEVEL.
All outputs come from the tuned hybrid SVM over real live/input data.
"""

import streamlit as st

from style_assets import (
    _block,
    aqi_badge_html,
    banner,
    foot_note,
    hero,
    ico,
    kpi_grid,
    legend,
    panel_close,
    panel_open,
    risk_chip,
)
from state import (
    CITIES,
    fetch_api_status,
    fetch_predict_live,
    get_model_names,
    post_prediction,
)


def _result_card(city, prediction, confidence, readings=None):
    color = {"Good": "#16a34a", "Moderate": "#eab308",
             "Unhealthy": "#f97316", "Very Unhealthy": "#ef4444",
             "Hazardous": "#5f0f0f"}.get(prediction, "#006a3d")
    conf_safe = max(0.0, min(1.0, float(confidence or 0)))

    cur_val = "—"
    if readings and readings.get("pm25") is not None:
        cur_val = f"{float(readings['pm25']):.1f} µg/m³"
    if readings:
        cur_txt = (
            f"Ingested live signals for <b>{city}</b> and classified the current "
            "air-quality state with the tuned hybrid SVM."
        )
    else:
        cur_txt = (
            f"Classified the entered <b>{city}</b> scenario with the tuned hybrid SVM."
        )
    for_label = "Forecast classification"
    if readings:
        pm_items = [k for k in ("pm25", "pm10", "no2", "so2", "co", "o3") if readings.get(k) is not None][:6]
        kpis = [
            (
                meta,
                f"{float(readings[k]):.1f}" if k not in ("co",) else f"{float(readings[k]):.0f}",
                "live input",
                "ok",
                "wind",
            )
            for k, meta in zip(pm_items, ["PM2.5 (µg/m³)", "PM10 (µg/m³)", "NO₂ (µg/m³)",
                                           "SO₂ (µg/m³)", "CO (µg/m³)", "O₃ (µg/m³)"])
        ]
        kpi_grid(kpis)

    st.markdown(
        _block(
            f"""
            <div class='panel' style='border-left:5px solid {color};'>
              <div class='panel-head'>
                <span class='panel-icon'>{ico('target', 17)}</span>
                <div>
                  <div class='panel-title'>{for_label} · {city}</div>
                  <p class='panel-sub'>{cur_txt}</p>
                </div>
              </div>
              <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-top:0.5rem;'>
                <div>
                  <div style='font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#8a94a6;font-weight:700'>Current condition</div>
                  <div style='font-size:1.4rem;font-weight:800;color:#111827;margin-top:4px'>{cur_val}</div>
                </div>
                <div>
                  <div style='font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#8a94a6;font-weight:700'>Forecast</div>
                  <div style='margin-top:4px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;'>
                    <span style='font-size:1.4rem;font-weight:800;color:{color}'>{prediction}</span>
                    {aqi_badge_html(prediction)}
                  </div>
                </div>
                <div>
                  <div style='font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#8a94a6;font-weight:700'>Risk level</div>
                  <div style='margin-top:6px'>{risk_chip(prediction)}</div>
                </div>
              </div>
              <div style='margin-top:1rem'>
                <div style='font-size:.76rem;color:#4b5563;font-weight:700;margin-bottom:6px;
                            display:flex;justify-content:space-between;'>
                  <span>Model confidence</span><span>{conf_safe * 100:.1f}%</span></div>
                <div style='height:10px;border-radius:999px;overflow:hidden;background:#eaf0f7;'>
                  <div style='height:100%;width:{conf_safe * 100:.1f}%;
                       border-radius:999px;background:linear-gradient(90deg,#006a3d,{color});'></div>
                </div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render():
    stats = fetch_api_status()
    model_names = get_model_names(stats)

    hero(
        "Decision Support · Forecast",
        "Forecast & Scenarios",
        "Classify current and hypothetical conditions with the tuned hybrid SVM model. "
        "Feed data from any supported city or hand-enter a scenario for planning.",
        chips=[
            ("Model", ", ".join(model_names[:2]) if model_names else "No model loaded",
             "good" if model_names else "bad"),
            ("Backend", "Online" if stats else "Offline", "good" if stats else "bad"),
        ],
        breadcrumb=True,
    )

    if not stats:
        banner(
            "warn",
            "Backend API is not reachable — prediction requests will be unavailable. "
            "Start <b>localhost:8000</b> to enable live and scenario forecasts.",
        )

    tab_live, tab_scenario = st.tabs(["Live city forecast", "Scenario assessment"])

    with tab_live:
        panel_open(
            "Live forecast",
            "target",
            "Fetch real-time meteorology and air chemistry for a city and classify it instantly.",
        )
        live_city = st.selectbox("Select city", CITIES, index=0, key="live_pred_city")
        if st.button("Fetch live data & forecast", key="live_predict_btn"):
            with st.spinner(f"Fetching live data for {live_city} from Open-Meteo..."):
                data = fetch_predict_live(live_city)
            if data and data.get("status") == "success":
                _result_card(
                    live_city,
                    data.get("prediction", "Unknown"),
                    data.get("confidence", 0),
                    readings=data.get("live_readings") or {},
                )
                st.caption(
                    f"Source: {data.get('source', 'unknown')} · "
                    f"Timestamp: {data.get('timestamp', 'N/A')}"
                )
            else:
                banner("err", "Live forecast failed. Confirm the model is loaded on the backend.")
        else:
            st.caption("Select a city and run the forecast. Requires the backend at "
                       "localhost:8000 with a trained model.")
        panel_close()

    with tab_scenario:
        panel_open(
            "Scenario assessment",
            "flask",
            "Input a hypothetical air-quality profile to see what the model would classify.",
        )
        with st.form("predict_form"):
            c0, c1, c2 = st.columns(3)
            with c0:
                pm25 = st.number_input("PM2.5 (µg/m³)", 0.0, 500.0, 25.0, 0.1)
                pm10 = st.number_input("PM10 (µg/m³)", 0.0, 1000.0, 50.0, 0.1)
                no2 = st.number_input("NO₂ (ppb)", 0.0, 500.0, 20.0, 0.1)
            with c1:
                so2 = st.number_input("SO₂ (ppb)", 0.0, 500.0, 5.0, 0.1)
                co = st.number_input("CO (ppm)", 0.0, 50.0, 0.5, 0.01)
                o3 = st.number_input("O₃ (ppb)", 0.0, 500.0, 30.0, 0.1)
            with c2:
                temperature = st.number_input("Temperature (°C)", -20.0, 60.0, 25.0, 0.1)
                humidity = st.number_input("Humidity (%)", 0.0, 100.0, 60.0, 0.1)
                wind_speed = st.number_input("Wind speed (m/s)", 0.0, 60.0, 5.0, 0.1)

            run_optimized = st.form_submit_button("Run optimized model")
            run_baseline = st.form_submit_button("Compare with baseline")

        if run_optimized or run_baseline:
            payload = {
                "pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co,
                "o3": o3, "temperature": temperature, "humidity": humidity,
                "wind_speed": wind_speed,
            }
            with st.spinner("Running SVM classification..."):
                model_kind = "baseline" if run_baseline else "optimized"
                result = post_prediction(payload, model_type=model_kind)
            if not result:
                banner("err", "Prediction failed — is the backend running?")
            else:
                _result_card(
                    "Scenario",
                    result.get("prediction", "Unknown"),
                    result.get("confidence", 0),
                )
                st.caption(f"Model: {'baseline SVM' if run_baseline else 'optimized SVM (hybrid)'}")
        panel_close()

    legend(
        [
            ("Good", "#16a34a"),
            ("Moderate", "#eab308"),
            ("Unhealthy", "#f97316"),
            ("Very Unhealthy", "#ef4444"),
            ("Hazardous", "#5f0f0f"),
        ]
    )

    foot_note(
        "The optimized model is preferred for operational decisions.",
        "Forecasts use Open-Meteo/OpenAQ inputs and the tuned hybrid SVM.",
        "SMOTE-Tomek balancing mitigates minority-class bias in rare high-risk episodes.",
    )