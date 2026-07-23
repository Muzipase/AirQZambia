import streamlit as st
import requests
from style_assets import insert_style

API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Predictions", page_icon="🎯", layout="wide")
insert_style()

def get_prediction(data: dict, model_type: str = "optimized") -> dict:
    try:
        if model_type == "baseline":
            response = requests.post(f"{API_BASE_URL}/api/predict?model_type=baseline", json=data, timeout=10)
        else:
            response = requests.post(f"{API_BASE_URL}/api/predict", json=data, timeout=10)
        return response.json() if response.ok else {"error": response.text}
    except Exception as exc:
        return {"error": str(exc)}

st.title("Air Quality Predictions")

st.markdown("Provide air quality measurements to generate a model prediction for pollution risk.")

with st.form(key="prediction_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pm25 = st.number_input("PM2.5 (µg/m³)", min_value=0.0, value=25.0)
        pm10 = st.number_input("PM10 (µg/m³)", min_value=0.0, value=50.0)
        no2 = st.number_input("NO₂ (ppb)", min_value=0.0, value=20.0)
    with col2:
        so2 = st.number_input("SO₂ (ppb)", min_value=0.0, value=5.0)
        co = st.number_input("CO (ppm)", min_value=0.0, value=0.5)
        o3 = st.number_input("O₃ (ppb)", min_value=0.0, value=30.0)
    with col3:
        temperature = st.number_input("Temperature (°C)", value=25.0)
        humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=60.0)
        wind_speed = st.number_input("Wind Speed (m/s)", min_value=0.0, value=5.0)

    submit_action = st.form_submit_button("Make Prediction")

if submit_action:
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
    st.info("Sending request to prediction endpoint...")
    result = get_prediction(payload, model_type="optimized")
    if "error" in result:
        st.error(f"Prediction failed: {result['error']}")
    else:
        st.success("Prediction completed")
        st.json(result)
        if result.get("prediction"):
            st.markdown(f"### Predicted Category: {result['prediction']}")
            if "confidence" in result:
                st.write(f"Confidence: {result['confidence']:.2%}")

st.markdown("---")

st.subheader("Baseline Model Prediction")
if st.button("Run Baseline Prediction"):
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
    result = get_prediction(payload, model_type="baseline")
    if "error" in result:
        st.error(f"Baseline prediction failed: {result['error']}")
    else:
        st.success("Baseline prediction completed")
        st.json(result)

st.markdown("---")

st.write(
    "Use the optimized model for more reliable predictions. If the API is unavailable, ensure the backend is running at `http://localhost:8000`."
)
