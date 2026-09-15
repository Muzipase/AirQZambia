"""Shared data layer for the AirQ Zambia Streamlit command center.

All API access lives here behind Streamlit's cache so views stay lean and
the whole app degrades gracefully to sample data when the backend is down.
"""

import io
import os

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")

CITIES = ["Lusaka", "Ndola", "Kitwe"]
DATA_SOURCES = ["Auto (Open-Meteo + OpenAQ)", "Open-Meteo", "OpenAQ"]
SOURCE_API_MAP = {
    "Auto (Open-Meteo + OpenAQ)": "auto",
    "Open-Meteo": "openmeteo",
    "OpenAQ": "openaq",
}

# All six criteria pollutants with labels, units and WHO reference values.
# Open-Meteo reports every pollutant in µg/m³ (including CO).
POLLUTANTS = {
    "pm25": {"label": "PM2.5", "unit": "µg/m³", "who_annual": 5, "who_24h": 15,
             "desc": "Fine particles (≤ 2.5 µm)"},
    "pm10": {"label": "PM10", "unit": "µg/m³", "who_annual": 15, "who_24h": 45,
             "desc": "Inhalable particles (≤ 10 µm)"},
    "no2": {"label": "NO₂", "unit": "µg/m³", "who_annual": 10, "who_24h": 25,
            "desc": "Nitrogen dioxide"},
    "so2": {"label": "SO₂", "unit": "µg/m³", "who_annual": 40, "who_24h": 40,
            "desc": "Sulphur dioxide"},
    "co": {"label": "CO", "unit": "µg/m³", "who_annual": 4000, "who_24h": 4000,
           "desc": "Carbon monoxide"},
    "o3": {"label": "O₃", "unit": "µg/m³", "who_annual": 100, "who_24h": 100,
           "desc": "Ground-level ozone"},
}

TREND_COLUMNS = ["PM2.5", "PM10", "NO₂", "SO₂", "CO", "O₃"]


def _get(path, params=None, timeout=8):
    try:
        response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=timeout)
        return response.json() if response.ok else None
    except requests.RequestException:
        return None


def _post(path, json=None, timeout=15):
    try:
        response = requests.post(f"{API_BASE_URL}{path}", json=json, timeout=timeout)
        return response.json() if response.ok else None
    except requests.RequestException:
        return None


@st.cache_data(ttl=120)
def fetch_api_status():
    return _get("/status")


@st.cache_data(ttl=120)
def fetch_evaluation_metrics():
    return _get("/api/evaluation/metrics") or {}


@st.cache_data(ttl=120)
def fetch_comparison_data():
    return _get("/api/evaluation/comparison") or {}


@st.cache_data(ttl=120)
def fetch_shap_summary():
    result = _get("/api/explainability/shap-summary", timeout=20)
    if result is None:
        return None
    if isinstance(result, dict):
        return result.get("shap_summary", result)
    return result


@st.cache_data(ttl=15)
def fetch_live_feed(source="auto", city=None):
    params = {"source": source}
    if city:
        params["city"] = city
    return _get("/api/data/fetch", params=params, timeout=30)


@st.cache_data(ttl=15)
def fetch_predict_live(city):
    return _get("/api/predict/live", params={"city": city}, timeout=25)


@st.cache_data(ttl=120)
def fetch_raw_csv():
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/data/download", params={"data_type": "raw"}, timeout=15
        )
        if response.ok:
            return pd.read_csv(io.StringIO(response.text))
    except (requests.RequestException, Exception):
        pass
    return None


@st.cache_data(ttl=1800)
def fetch_historical(city, start_date):
    """Real daily-averaged history from the backend (Open-Meteo archive)."""
    result = _get(
        f"/public/city/{city}/historical",
        params={"start_date": start_date, "end_date": "", "pollutants": "pm25,pm10,no2,so2,co,o3"},
        timeout=25,
    )
    if not result or result.get("status") != "ok":
        return None
    rows = result.get("daily")
    if not rows:
        return None
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def post_prediction(payload, model_type="optimized"):
    path = f"/api/predict?model_type={model_type}" if model_type == "baseline" else "/api/predict"
    return _post(path, json=payload)


def post_cross_validate(folds):
    return _post(f"/api/evaluation/cross-validate?folds={folds}", timeout=60)


def post_explain_prediction(payload):
    return _post("/api/explainability/explain-prediction", json=payload, timeout=20)


# ---------------------------------------------------------------------------
# Helpers / fallback data
# ---------------------------------------------------------------------------

def get_model_names(status):
    if not status:
        return []
    models = status.get("models") or {}
    return list(models.keys()) if isinstance(models, dict) else []


def format_model_names(status):
    names = get_model_names(status)
    return ", ".join(names) if names else "No model loaded"


@st.cache_data(ttl=120)
def get_sample_trend_data():
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=7, freq="D"),
            "PM2.5": [18, 21, 20, 24, 22, 19, 17],
            "PM10": [32, 35, 33, 37, 36, 34, 31],
            "NO₂": [9, 11, 10, 12, 11, 9, 8],
            "SO₂": [6, 7, 6, 8, 7, 6, 6],
            "CO": [420, 460, 440, 480, 470, 430, 410],
            "O₃": [28, 30, 27, 29, 31, 26, 25],
        }
    )


# Sample current concentrations used on frontend list lookups / frontend.
SAMPLE_READINGS = {
    "pm25": 24.1, "pm10": 26.7, "no2": 2.2, "so2": 1.7,
    "co": 217.0, "o3": 91.0,
}


def get_pollutant_readings(source="auto", city="Lusaka"):
    """Return the latest concentration for every pollutant, preferring the
    backend live feed and falling back to approved reference values."""
    live = fetch_predict_live(city)
    if live and live.get("status") == "success" and live.get("live_readings"):
        readings = {}
        for key in POLLUTANTS:
            value = live["live_readings"].get(key)
            if value is not None:
                readings[key] = float(value)
        if readings:
            return readings
    return dict(SAMPLE_READINGS)


def classify_pm25(pm25):
    """Return (aqi_level, health_message) using US-EPA PM2.5 breakpoints."""
    if pm25 <= 12.0:
        return "Good", "Air quality is satisfactory and poses little or no risk."
    if pm25 <= 35.4:
        return "Moderate", "Acceptable air quality; sensitive groups should limit prolonged exposure."
    if pm25 <= 55.4:
        return "Sensitive", "Unhealthy for sensitive groups — reduce outdoor activity if sensitive."
    if pm25 <= 150.4:
        return "Unhealthy", "Health effects possible for everyone; limit outdoor activity."
    return "Hazardous", "Health alert — serious effects likely; stay indoors where possible."


def get_aqi_for_city(city):
    """Static fallback readings used when live data is not available."""
    if city == "Ndola":
        return 118, "Sensitive", "Unhealthy for sensitive groups — take precautions."
    if city == "Kitwe":
        return 156, "Unhealthy", "Limit outdoor activity and keep windows closed."
    return 42, "Good", "Air quality is safe for all activities."


def get_live_aqi_for_city(source="auto", city="Lusaka"):
    """Prefer the backend's raw feed; fall back to a static reading."""
    feed = fetch_live_feed(source=source, city=city)
    if feed and feed.get("status") == "success":
        raw = fetch_raw_csv()
        if raw is not None and "pm25" in raw.columns and len(raw) > 0:
            latest_pm25 = float(raw["pm25"].iloc[-1])
            level, message = classify_pm25(latest_pm25)
            return round(latest_pm25, 1), level, message
    return get_aqi_for_city(city)


def get_live_snapshot(city="Lusaka", source="auto"):
    """Rich, real-time snapshot for the Command Center hero card.

    Built from /api/predict/live when available (prediction, confidence and
    per-pollutant readings), else from the raw feed, else from approved
    reference values. AQI number follows the app convention: PM2.5 quick
    index classified with US-EPA breakpoints.
    """
    predict = fetch_predict_live(city)
    if predict and predict.get("status") == "success":
        readings = predict.get("live_readings") or {}
        pm25 = readings.get("pm25")
        if pm25 is not None:
            pm25 = float(pm25)
        else:
            pm25 = SAMPLE_READINGS["pm25"]
        level, message = classify_pm25(pm25)
        latest = float(readings["pm25"]) if readings.get("pm25") is not None else pm25
        timestamp = predict.get("timestamp")
        return {
            "city": city,
            "value": round(latest, 1),
            "unit": "AQI",
            "label": level,
            "color": _aqi_color(level),
            "message": message,
            "readings": {k: float(v) for k, v in readings.items() if k in POLLUTANTS and v is not None},
            "prediction": predict.get("prediction"),
            "confidence": predict.get("confidence"),
            "model_label": "Bayesian-Optimized SVM (hybrid)",
            "source_note": predict.get("source", "Open-Meteo + OpenAQ"),
            "timestamp": timestamp,
        }
    value, level, message = get_live_aqi_for_city(source=source, city=city)
    return {
        "city": city,
        "value": value,
        "unit": "AQI",
        "label": level,
        "color": _aqi_color(level),
        "message": message,
        "readings": get_pollutant_readings(source=source, city=city),
        "prediction": None,
        "confidence": None,
        "model_label": "Bayesian-Optimized SVM (hybrid)",
        "source_note": SOURCE_API_MAP.get(source, "Open-Meteo + OpenAQ"),
        "timestamp": None,
    }


def _aqi_color(level):
    try:
        from style_assets import AQI_COLORS
    except Exception:
        AQI_COLORS = {
            "Good": "#16a34a", "Moderate": "#eab308", "Sensitive": "#f97316",
            "Unhealthy": "#ef4444", "Very Unhealthy": "#7c2d92", "Hazardous": "#5f0f0f",
        }
    return AQI_COLORS.get(level, "#eab308")


def pollutant_status(value, who_24h, pm25_override=None):
    """Status label + colour for a pollutant concentration.

    PM2.5 uses its US-EPA class (matches the AQI convention); the other
    pollutants are graded against their WHO 24-hour guideline ratio.
    """
    if pm25_override is not None:
        label = classify_pm25(pm25_override)[0]
        color = _aqi_color(label)
        return label, color
    ratio = float(value) / who_24h if who_24h else 0.0
    if ratio <= 1.0:
        return "Good", "#16a34a"
    if ratio <= 1.5:
        return "Moderate", "#eab308"
    if ratio <= 2.0:
        return "Elevated", "#f97316"
    return "Unhealthy", "#ef4444"


def _minutes_ago(timestamp):
    from datetime import datetime

    if not timestamp:
        return None
    try:
        ts = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.astimezone()
        delta = (datetime.now(ts.tzinfo) - ts).total_seconds() // 60
        return max(0, int(delta))
    except (TypeError, ValueError):
        return None


def get_trend_frame(period, city="Lusaka"):
    """Real trend series for a period ('24h'|'7d'|'30d').

    24h: hourly station feed from the last backend fetch.
    7d/30d: daily averages from the Open-Meteo archive.
    Returns (label, DataFrame) or (label, None) when the data is unavailable.
    """
    from datetime import timedelta

    if period == "24h":
        raw = fetch_raw_csv()
        if raw is None or "timestamp" not in raw.columns or "pm25" not in raw.columns:
            return "24h", None
        df = raw.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        if city and "city" in df.columns:
            df = df[df["city"].astype(str).str.lower() == city.lower()]
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        if df.empty:
            return "24h", None
        return "24h", df

    days = 7 if period == "7d" else 30
    start = (pd.Timestamp.now().normalize() - timedelta(days=days + 1)).strftime("%Y-%m-%d")
    df = fetch_historical(city, start)
    if df is None or df.empty:
        return (f"{days}d", None)
    df = df.tail(days).reset_index(drop=True)
    return f"{days}d", df


def get_sample_metrics():
    return {
        "accuracy": 0.91,
        "precision": 0.88,
        "recall": 0.86,
        "f1_score": 0.87,
        "roc_auc": 0.93,
        "support": 120,
    }