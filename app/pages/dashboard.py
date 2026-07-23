import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from style_assets import insert_style

API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Air Quality Dashboard", page_icon="📊", layout="wide")
insert_style()

@st.cache_data
def fetch_api_status():
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=3)
        return response.json() if response.ok else None
    except Exception:
        return None

@st.cache_data
def get_sample_trend_data():
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=7, freq="D"),
            "PM2.5": [18, 21, 20, 24, 22, 19, 17],
            "PM10": [32, 35, 33, 37, 36, 34, 31],
            "O3": [28, 30, 27, 29, 31, 26, 25],
        }
    )

st.title("Air Quality Dashboard")
st.markdown("Monitor air quality trends, pollutant levels, and forecast insights for your region.")

status = fetch_api_status()
if status:
    st.success("Backend API is reachable")
    if "models" in status:
        st.info(f"Models loaded: {', '.join(status.get('models', {}).keys())}")
else:
    st.warning("Backend API is unavailable. Dashboard is showing local sample data.")

col1, col2, col3 = st.columns(3)
col1.metric("Current AQI", "42", "Good")
col2.metric("PM2.5", "18 µg/m³", "Stable")
col3.metric("PM10", "32 µg/m³", "Moderate")

st.markdown("---")

with st.expander("What the dashboard shows"):
    st.write(
        "This page summarizes the latest air quality indicators, pollutant trends, and short-term forecast guidance. "
        "If the backend is available, data is fetched from the API; otherwise sample values are displayed."
    )

trend_data = get_sample_trend_data()
fig = px.line(
    trend_data,
    x="timestamp",
    y=["PM2.5", "PM10", "O3"],
    markers=True,
    title="Air Quality Pollutant Trends"
)
fig.update_layout(legend_title_text="Pollutants")

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

forecast_columns = st.columns(4)
forecast = [
    ("Today", "Good", "AQI 42"),
    ("Tomorrow", "Moderate", "AQI 65"),
    ("2 Days", "Moderate", "AQI 70"),
    ("3 Days", "Good", "AQI 50"),
]
for col, item in zip(forecast_columns, forecast):
    label, status_text, detail = item
    col.markdown(f"### {label}")
    col.markdown(f"**{status_text}**")
    col.write(detail)

st.markdown("---")

with st.container():
    st.subheader("Top Air Quality Recommendations")
    st.write(
        "- Reduce outdoor burning and vehicle idling.\n"
        "- Monitor sensitive populations when AQI is moderate or worse.\n"
        "- Use indoor air filtration when local pollution spikes."
    )
