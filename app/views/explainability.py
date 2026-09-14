"""Explainability — feature contributions and per-prediction rationale.

Hierarchy: MODEL EXPLAINABILITY → "What influenced the prediction?" →
Global Feature Importance (backend SHAP summary) → Prediction Explanation
(per-scenario Shapley contributions). SHAP calculations stay untouched on
the backend; this view only renders them.
"""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from style_assets import banner, foot_note, hero, ico, panel_close, panel_open, section_label
from state import (
    fetch_api_status,
    fetch_shap_summary,
    get_model_names,
    post_explain_prediction,
)


def _is_shap_summary(value):
    return (
        isinstance(value, dict)
        and ("feature_importances" in value or "importance" in value
             or "shap_values" in value or "summary" in value)
    )


def _feature_bars(summary):
    """Render a clean horizontal bar chart from a structured SHAP summary."""
    importance = summary.get("feature_importances") or summary.get("importance")
    if isinstance(importance, dict):
        items = sorted(importance.items(), key=lambda kv: float(kv[1]), reverse=True)
    elif isinstance(importance, list):
        if importance and isinstance(importance[0], dict) and "feature" in importance[0]:
            items = [(it.get("feature"), it.get("importance") or it.get("value"))
                     for it in importance]
            items = sorted(items, key=lambda kv: float(kv[1]), reverse=True)
        else:
            features = summary.get("features") or [
                f"feature {i + 1}" for i in range(len(importance))
            ]
            items = sorted(zip(features, importance),
                           key=lambda kv: float(kv[1]), reverse=True)
    elif isinstance(summary, dict) and all(
        isinstance(k, str) for k in summary.keys()
    ) and all(isinstance(v, (int, float)) for v in summary.values()):
        items = sorted(summary.items(), key=lambda kv: float(kv[1]), reverse=True)
    else:
        return None

    if not items:
        return None

    df = pd.DataFrame(items[:12], columns=["feature", "importance"])
    fig = px.bar(
        df,
        x="importance",
        y="feature",
        orientation="h",
        color="importance",
        color_continuous_scale=["#d1d5db", "#22c55e", "#006a3d"],
        template="plotly_white",
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=10, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
        xaxis=dict(tickfont=dict(size=11), title=None),
        font=dict(family="Inter", color="#111827", size=13),
    )
    st.plotly_chart(fig, width="stretch", key="shap_features")
    return items


def render():
    stats = fetch_api_status()
    model_names = get_model_names(stats)

    hero(
        "Transparency · Explainability",
        "Model Explainability",
        "What influenced the prediction? SHAP attributes each air-quality "
        "classification to the input signals that drove it.",
        chips=[
            ("Backend", "Online" if stats else "Offline", "good" if stats else "bad"),
            ("Model", ", ".join(model_names) if model_names else "No model loaded",
             "good" if model_names else "bad"),
        ],
        breadcrumb=True,
    )

    if not stats:
        banner(
            "warn",
            "SHAP details come from the backend. Start <b>localhost:8000</b> "
            "and generate a summary to populate this view.",
        )

    section_label("Global feature importance", "mean SHAP contribution across predictions")
    panel_open(
        "Global feature importance",
        "cpu",
        "Which inputs most strongly influence the model across the evaluation set.",
    )
    st.markdown(
        f"<p class='section-kicker'>{ico('sparkles', 14)} "
        "Higher values = greater influence on the classification decision.</p>",
        unsafe_allow_html=True,
    )

    summary = fetch_shap_summary()
    if summary and _is_shap_summary(summary):
        items = _feature_bars(summary)
        if items is None:
            display = json.dumps(summary, indent=2)
            st.text_area(
                "SHAP summary (read only)",
                value=display,
                height=300,
                key="shap_summary",
                disabled=True,
            )
    elif summary:
        display = summary if isinstance(summary, str) else json.dumps(summary, indent=2)
        st.info(
            "A structured SHAP summary is not available yet — showing the raw "
            "backend payload. Generate the summary on the API to unlock the chart."
        )
        st.text_area(
            "SHAP summary (read only)",
            value=display,
            height=300,
            key="shap_summary",
            disabled=True,
        )
    else:
        banner(
            "info",
            "SHAP summary has not been generated yet on the backend. Generate it "
            "via the API to see which features matter most.",
        )
    panel_close()

    section_label("Prediction explanation", "Shapley contributions for a specific scenario")
    panel_open(
        "Explain a specific forecast",
        "target",
        "Enter a scenario and see how each feature pushed the classification.",
    )
    st.markdown(
        f"<p class='section-kicker'>{ico('activity', 14)} "
        "Positive contributions nudge toward higher-risk classes.</p>",
        unsafe_allow_html=True,
    )
    with st.form("explain_form"):
        c0, c1, c2 = st.columns(3)
        with c0:
            pm25 = st.number_input("PM2.5 (µg/m³)", 0.0, 500.0, 25.0, 0.1, key="ex_pm25")
            pm10 = st.number_input("PM10 (µg/m³)", 0.0, 1000.0, 50.0, 0.1, key="ex_pm10")
            no2 = st.number_input("NO₂ (ppb)", 0.0, 500.0, 20.0, 0.1, key="ex_no2")
        with c1:
            so2 = st.number_input("SO₂ (ppb)", 0.0, 500.0, 5.0, 0.1, key="ex_so2")
            co = st.number_input("CO (ppm)", 0.0, 50.0, 0.5, 0.01, key="ex_co")
            o3 = st.number_input("O₃ (ppb)", 0.0, 500.0, 30.0, 0.1, key="ex_o3")
        with c2:
            temperature = st.number_input("Temperature (°C)", -20.0, 60.0, 25.0, 0.1,
                                          key="ex_temperature")
            humidity = st.number_input("Humidity (%)", 0.0, 100.0, 60.0, 0.1, key="ex_humidity")
            wind_speed = st.number_input("Wind speed (m/s)", 0.0, 60.0, 5.0, 0.1, key="ex_wind")

        explain = st.form_submit_button("Explain scenario")

    if explain:
        payload = {
            "pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co,
            "o3": o3, "temperature": temperature, "humidity": humidity,
            "wind_speed": wind_speed,
        }
        with st.spinner("Computing SHAP explanation..."):
            explanation = post_explain_prediction(payload)
        if explanation:
            st.json(explanation)
        else:
            banner("err", "Backend did not return an explanation. Confirm the API is running.")
    panel_close()

    foot_note(
        "Explainability confirms the system responds to the right input signals.",
        "SHAP values are Shapley contributions averaged appropriately per class.",
        "Feature influence is shown exactly as computed by the backend — no post-processing.",
    )