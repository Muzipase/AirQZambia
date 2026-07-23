import streamlit as st
import requests
from style_assets import insert_style

API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="SHAP Analysis", page_icon="🧠", layout="wide")
insert_style()

@st.cache_data
def fetch_shap_summary():
    try:
        response = requests.get(f"{API_BASE_URL}/api/explainability/shap-summary", timeout=10)
        return response.json() if response.ok else None
    except Exception:
        return None

st.title("SHAP Explainability")

st.markdown("Interpret the model by exploring feature importance and local explanations for air quality predictions.")

if st.button("Load SHAP Summary"):
    summary = fetch_shap_summary()
    if summary:
        st.success("SHAP summary loaded")
        st.json(summary.get("shap_summary", summary))
    else:
        st.warning("Could not fetch SHAP summary. Make sure the backend API is running.")

st.markdown("---")

st.subheader("Explain a Specific Prediction")
col1, col2, col3 = st.columns(3)
with col1:
    pm25 = st.number_input("PM2.5 (µg/m³)", min_value=0.0, value=25.0, key="expl_shap_pm25")
    pm10 = st.number_input("PM10 (µg/m³)", min_value=0.0, value=50.0, key="expl_shap_pm10")
    no2 = st.number_input("NO₂ (ppb)", min_value=0.0, value=20.0, key="expl_shap_no2")
with col2:
    so2 = st.number_input("SO₂ (ppb)", min_value=0.0, value=5.0, key="expl_shap_so2")
    co = st.number_input("CO (ppm)", min_value=0.0, value=0.5, key="expl_shap_co")
    o3 = st.number_input("O₃ (ppb)", min_value=0.0, value=30.0, key="expl_shap_o3")
with col3:
    temperature = st.number_input("Temperature (°C)", value=25.0, key="expl_shap_temp")
    humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=60.0, key="expl_shap_humidity")
    wind_speed = st.number_input("Wind Speed (m/s)", min_value=0.0, value=5.0, key="expl_shap_wind")

if st.button("Explain Prediction"):
    payload = {
        "pm25": pm25,
        "pm10": pm10,
        "no2": no2,
        "so2": so2,
        "co": co,
        "o3": o3,
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
    }
    try:
        response = requests.post(f"{API_BASE_URL}/api/explainability/explain-prediction", json=payload, timeout=10)
        if response.ok:
            explanation = response.json()
            st.success("SHAP explanation retrieved")
            st.json(explanation)
        else:
            st.error("Backend did not return an explanation. Check API status.")
            st.write(response.text)
    except Exception as exc:
        st.error(f"Failed to compute SHAP explanation: {exc}")

st.markdown("---")

st.write(
    "The SHAP explanation section shows how each feature influenced the prediction. "
    "If the backend is not available, the page will still render and the summary button will report the connection issue."
)
