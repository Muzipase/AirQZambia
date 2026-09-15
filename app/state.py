"""Shared data layer for the AirQ Zambia Streamlit command center.

All API access lives here behind Streamlit's cache so views stay lean and
the whole app degrades gracefully to sample data when the backend is down.
"""

import io
import os
import time

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


@st.cache_data(ttl=120)
def fetch_processed_csv():
    """Real processed/training dataset from the backend, or None."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/data/download", params={"data_type": "processed"}, timeout=15
        )
        if response.ok:
            return pd.read_csv(io.StringIO(response.text))
    except (requests.RequestException, Exception):
        pass
    return None


@st.cache_data(ttl=120)
def fetch_imbalance_analysis():
    """Class-distribution analysis of the processed dataset from the backend."""
    return _get("/api/imbalance/analyze", timeout=15) or {}


@st.cache_data(ttl=120)
def fetch_system_metrics():
    """Runtime CPU / memory / up-time reporting from the backend."""
    return _get("/api/system/metrics", timeout=8) or {}


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


@st.cache_data(ttl=1800)
def fetch_historical_payload(city, start_date, end_date=""):
    """Full historical archive payload: daily frame, per-pollutant stats and range.

    Returns {"df", "stats", "date_range", "city"} or None when unavailable.
    """
    result = _get(
        f"/public/city/{city}/historical",
        params={
            "start_date": start_date,
            "end_date": end_date,
            "pollutants": "pm25,pm10,no2,so2,co,o3",
        },
        timeout=25,
    )
    if not result or result.get("status") != "ok":
        return None
    rows = result.get("daily")
    if not rows:
        return None
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return {
        "df": df,
        "stats": result.get("stats") or {},
        "date_range": result.get("date_range") or {},
        "city": result.get("city", city.title()),
    }


def post_prediction(payload, model_type="optimized"):
    path = f"/api/predict?model_type={model_type}" if model_type == "baseline" else "/api/predict"
    return _post(path, json=payload)


def post_cross_validate(folds):
    return _post(f"/api/evaluation/cross-validate?folds={folds}", timeout=60)


def run_cross_validation(folds, timeout=240, poll_interval=2):
    """Start a cross-validation job on the backend and poll until it finishes.

    The POST endpoint is asynchronous: it returns a job_id and the results are
    only exposed via the status endpoint. Returns the completed payload, an
    error payload, or None if the backend is unreachable.
    """
    job = post_cross_validate(folds)
    if not job or not job.get("job_id"):
        return job
    job_id = job["job_id"]
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        resp = _get(f"/api/evaluation/cross-validate/status/{job_id}", timeout=15)
        if not resp:
            return None
        if resp.get("status") in ("completed", "error"):
            return resp
        time.sleep(poll_interval)
    return {"status": "timeout", "error": f"Cross-validation exceeded {timeout}s."}


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


def _aqi_from_breakpoints(value, breakpoints):
    """Piecewise-linear US-EPA AQI sub-index for a concentration.

    breakpoints: list of (c_low, c_high, i_low, i_high). Returns None when the
    value is missing / non-finite, 500 when it exceeds all defined bands.
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    from math import isfinite

    if not isfinite(value):
        return None
    for c_low, c_high, i_low, i_high in breakpoints:
        if value <= c_high:
            return int(round(i_low + ((value - c_low) / (c_high - c_low)) * (i_high - i_low)))
    return 500


# ---- US-EPA 2016 AQI breakpoint tables -------------------------------
# PM2.5 / PM10 / NO2 / SO2 / O3 are graded directly in µg/m³ (Open-Meteo's
# unit). CO is graded in mg/m³ so µg/m³ values are divided by 1000 first.
PM25_AQI_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.0, 35.4, 50, 100),
    (35.4, 55.4, 100, 150),
    (55.4, 150.4, 150, 200),
    (150.4, 250.4, 200, 300),
    (250.4, 500.4, 300, 500),
]
PM10_AQI_BREAKPOINTS = [
    (0.0, 54.0, 0, 50),
    (54.0, 154.0, 50, 100),
    (154.0, 254.0, 100, 150),
    (254.0, 354.0, 150, 200),
    (354.0, 424.0, 200, 300),
    (424.0, 504.0, 300, 400),
    (504.0, 604.0, 400, 500),
]
NO2_AQI_BREAKPOINTS = [
    (0.0, 53.0, 0, 50),
    (53.0, 100.0, 50, 100),
    (100.0, 360.0, 100, 150),
    (360.0, 649.0, 150, 200),
    (649.0, 1249.0, 200, 300),
    (1249.0, 1649.0, 300, 400),
    (1649.0, 2049.0, 400, 500),
]
SO2_AQI_BREAKPOINTS = [
    (0.0, 35.0, 0, 50),
    (35.0, 75.0, 50, 100),
    (75.0, 185.0, 100, 150),
    (185.0, 304.0, 150, 200),
    (304.0, 604.0, 200, 300),
    (604.0, 804.0, 300, 400),
    (804.0, 1004.0, 400, 500),
]
CO_AQI_BREAKPOINTS = [
    (0.0, 4.4, 0, 50),
    (4.4, 9.4, 50, 100),
    (9.4, 12.4, 100, 150),
    (12.4, 15.4, 150, 200),
    (15.4, 30.4, 200, 300),
    (30.4, 40.4, 300, 400),
    (40.4, 50.4, 400, 500),
]
O3_AQI_BREAKPOINTS = [
    (0.0, 108.0, 0, 50),
    (108.0, 140.0, 50, 100),
    (140.0, 170.0, 100, 150),
    (170.0, 210.0, 150, 200),
    (210.0, 400.0, 200, 300),
    (400.0, 600.0, 300, 400),
    (600.0, 800.0, 400, 500),
]


def pm25_to_aqi(pm25):
    """US-EPA AQI index from a PM2.5 concentration using EPA breakpoints.

    Mirrors api.py `_pm25_to_aqi` and the frontend lib so all UIs present the
    same index for the same concentration.
    """
    return _aqi_from_breakpoints(pm25, PM25_AQI_BREAKPOINTS)


def pm10_to_aqi(pm10):
    """US-EPA AQI index from a PM10 concentration (µg/m³)."""
    return _aqi_from_breakpoints(pm10, PM10_AQI_BREAKPOINTS)


def no2_to_aqi(no2):
    """US-EPA AQI index from an NO2 concentration (µg/m³)."""
    return _aqi_from_breakpoints(no2, NO2_AQI_BREAKPOINTS)


def so2_to_aqi(so2):
    """US-EPA AQI index from an SO2 concentration (µg/m³)."""
    return _aqi_from_breakpoints(so2, SO2_AQI_BREAKPOINTS)


def co_to_aqi(co):
    """US-EPA AQI index from a CO concentration (µg/m³ -> mg/m³)."""
    return _aqi_from_breakpoints(co / 1000.0, CO_AQI_BREAKPOINTS)


def o3_to_aqi(o3):
    """US-EPA AQI index from an O3 concentration (µg/m³)."""
    return _aqi_from_breakpoints(o3, O3_AQI_BREAKPOINTS)


# Pollutant key -> its AQI sub-index function, in display order.
AQI_FUNCTIONS = {
    "pm25": pm25_to_aqi,
    "pm10": pm10_to_aqi,
    "no2": no2_to_aqi,
    "so2": so2_to_aqi,
    "co": co_to_aqi,
    "o3": o3_to_aqi,
}


def compute_aqi(readings):
    """US-EPA multi-pollutant AQI from per-pollutant concentrations.

    readings: dict of pollutant key -> concentration (µg/m³ for all).
    Returns (aqi, dominant pollutant key, dict of sub-indices). Missing /
    non-finite values are skipped; empty input yields (None, None, {}).
    Ties favour the earlier pollutant in AQI_FUNCTIONS order (e.g. PM2.5).
    """
    sub_indices = {}
    for pollutant, func in AQI_FUNCTIONS.items():
        value = readings.get(pollutant)
        if value is None:
            continue
        sub = func(value)
        if sub is not None:
            sub_indices[pollutant] = sub
    if not sub_indices:
        return None, None, {}
    aqi = max(sub_indices.values())
    dominant = next(p for p in AQI_FUNCTIONS if p in sub_indices and sub_indices[p] == aqi)
    return aqi, dominant, sub_indices


def classify_aqi(aqi):
    """(level, health_message) from an AQI index value using the shared bands.

    Bands mirror the Next.js landing scale and the backend so a single index
    maps to identical labels on every surface.
    """
    if aqi <= 50:
        return "Good", "Air quality is satisfactory and poses little or no risk."
    if aqi <= 100:
        return "Moderate", "Acceptable air quality; sensitive groups should limit prolonged exposure."
    if aqi <= 150:
        return "Unhealthy", "Unhealthy for sensitive groups — reduce prolonged outdoor exposure."
    if aqi <= 200:
        return "Very Unhealthy", "Health alert — serious effects possible; limit outdoor activity."
    return "Hazardous", "Health alert — serious effects likely; stay indoors where possible."


def classify_pm25(pm25):
    """Return (aqi_level, health_message) using US-EPA PM2.5 breakpoints.

    Category names mirror the backend (categorize_aqi) and Next.js UI so every
    surface reports the same labels: Good / Moderate / Unhealthy / Very
    Unhealthy / Hazardous.
    """
    if pm25 <= 12.0:
        return "Good", "Air quality is satisfactory and poses little or no risk."
    if pm25 <= 35.4:
        return "Moderate", "Acceptable air quality; sensitive groups should limit prolonged exposure."
    if pm25 <= 55.4:
        return "Unhealthy", "Air quality is unhealthy for sensitive groups — reduce prolonged outdoor exposure."
    if pm25 <= 150.4:
        return "Very Unhealthy", "Health alert — serious effects possible; limit outdoor activity."
    return "Hazardous", "Health alert — serious effects likely; stay indoors where possible."


def get_aqi_for_city(city):
    """Static fallback readings used when live data is not available."""
    if city == "Ndola":
        return 118, "Unhealthy", "Limit outdoor activity — air quality is unhealthy."
    if city == "Kitwe":
        return 156, "Very Unhealthy", "Health alert — stay indoors where possible."
    return 42, "Good", "Air quality is safe for all activities."


def get_live_aqi_for_city(source="auto", city="Lusaka"):
    """Multi-pollutant EPA AQI from the backend feed; static fallback otherwise."""
    feed = fetch_live_feed(source=source, city=city)
    if feed and feed.get("status") == "success":
        aqi, dominant, _ = compute_aqi(get_pollutant_readings(source=source, city=city))
        if aqi is not None:
            level, message = classify_aqi(aqi)
            return aqi, level, message
    return get_aqi_for_city(city)


def get_live_snapshot(city="Lusaka", source="auto"):
    """Rich, real-time snapshot for the Command Center hero card.

    Built from /api/predict/live when available (prediction, confidence and
    per-pollutant readings), else from the raw feed, else from approved
    reference values. AQI is the US-EPA multi-pollutant index — the maximum of
    the per-pollutant sub-indices — classified on the shared AQI bands.
    """
    predict = fetch_predict_live(city)
    if predict and predict.get("status") == "success":
        readings = {
            k: float(v) for k, v in (predict.get("live_readings") or {}).items()
            if k in POLLUTANTS and v is not None
        }
        if not readings:
            readings = dict(SAMPLE_READINGS)
        aqi, dominant, _ = compute_aqi(readings)
        if aqi is None:
            aqi, dominant, _ = compute_aqi(SAMPLE_READINGS)
        level, message = classify_aqi(aqi)
        timestamp = predict.get("timestamp")
        return {
            "city": city,
            "value": aqi,
            "unit": "AQI",
            "label": level,
            "color": _aqi_color(level),
            "message": message,
            "dominant": POLLUTANTS[dominant]["label"] if dominant else None,
            "readings": readings,
            "prediction": predict.get("prediction"),
            "confidence": predict.get("confidence"),
            "model_label": "Bayesian-Optimized SVM (hybrid)",
            "source_note": predict.get("source", "Open-Meteo + OpenAQ"),
            "timestamp": timestamp,
        }
    value, level, message = get_live_aqi_for_city(source=source, city=city)
    readings = get_pollutant_readings(source=source, city=city)
    _, dominant, _ = compute_aqi(readings)
    return {
        "city": city,
        "value": value,
        "unit": "AQI",
        "label": level,
        "color": _aqi_color(level),
        "message": message,
        "dominant": POLLUTANTS[dominant]["label"] if dominant else None,
        "readings": readings,
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


# ---------------------------------------------------------------------------
# ML pipeline progress
# ---------------------------------------------------------------------------

PIPELINE_STAGES = [
    {
        "key": "ingestion",
        "num": 1,
        "title": "Data ingestion & validation",
        "icon": "download",
        "desc": ("Fetch hourly air quality and meteorology from Open-Meteo + OpenAQ "
                 "for Lusaka, Kitwe and Ndola, then validate schemas and ranges."),
    },
    {
        "key": "preprocessing",
        "num": 2,
        "title": "Preprocessing & feature engineering",
        "icon": "flask",
        "desc": ("Clean, impute missing values, engineer lagged/meteorological features, "
                 "label the AQI category and scale inputs for the SVM."),
    },
    {
        "key": "imbalance",
        "num": 3,
        "title": "Imbalance analysis & SMOTE-Tomek",
        "icon": "scale",
        "desc": ("Quantify class imbalance and resample the training set with SMOTE-Tomek "
                 "so rare high-risk classes are not ignored."),
    },
    {
        "key": "training",
        "num": 4,
        "title": "Model training",
        "icon": "cpu",
        "desc": ("Train the default RBF SVM baseline and the Bayesian-optimized SVM "
                 "(TPE) on the balanced training set."),
    },
    {
        "key": "evaluation",
        "num": 5,
        "title": "Evaluation & assurance",
        "icon": "chart",
        "desc": ("Compute accuracy, precision, recall and F1 per class, persist the "
                 "baseline-vs-optimized comparison and confusion matrices."),
    },
    {
        "key": "explainability",
        "num": 6,
        "title": "Explainability (SHAP)",
        "icon": "sparkles",
        "desc": ("Attribte each classification to its input signals via SHAP and cache "
                 "the global feature-importance summary for the explainability view."),
    },
]


def build_pipeline_stages(status=None, raw=None, processed=None, imbalance=None,
                          metrics=None, has_shap=False):
    """Build a clean, backend-truthful stage report.

    Every stage's state is a pure function of the signals the API actually
    exposes, so the rail shows exactly what is on disk — nothing fabricated.

    Returns a list of dicts:
      {key, num, title, icon, desc, state, chips: [(label, value)], detail}
    """
    online = bool(status)
    models = (status or {}).get("models") or {}
    baseline_trained = str(models.get("baseline_svm", "")).lower() == "trained"
    optimized_trained = str(models.get("optimized_svm", "")).lower() == "trained"

    def _millis(n):
        try:
            return f"{int(n):,}"
        except (TypeError, ValueError):
            return "—"

    stages = []

    # Stage 1 — data ingestion
    raw_rows = len(raw) if raw is not None else 0
    raw_cols = raw.shape[1] if raw is not None else 0
    raw_status = "offline" if not online else ("completed" if raw is not None else "pending")
    stages.append({
        **PIPELINE_STAGES[0],
        "state": raw_status,
        "chips": [
            ("Records", _millis(raw_rows) if raw is not None else "—"),
            ("Columns", str(raw_cols) if raw is not None else "—"),
            ("Sources", "Open-Meteo + OpenAQ"),
        ],
        "detail": (
            {"records": raw_rows, "columns": raw_cols}
            if raw is not None else None
        ),
    })

    # Stage 2 — preprocessing
    pr_rows = len(processed) if processed is not None else 0
    pr_cols = processed.shape[1] if processed is not None else 0
    pr_state = "offline" if not online else ("completed" if processed is not None else "pending")
    stages.append({
        **PIPELINE_STAGES[1],
        "state": pr_state,
        "chips": [
            ("Records", _millis(pr_rows) if processed is not None else "—"),
            ("Features", str(pr_cols - 1) if processed is not None else "—"),
            ("Scaling", "Min-max fitted" if processed is not None else "—"),
        ],
        "detail": (
            {"records": pr_rows, "features": pr_cols - 1, "columns": list(processed.columns)}
            if processed is not None else None
        ),
    })

    # Stage 3 — imbalance analysis & SMOTE-Tomek
    has_imbalance = bool(imbalance and imbalance.get("class_distribution"))
    imb_state = "offline" if not online else (
        "completed" if has_imbalance else "pending"
    )
    class_dist = (imbalance or {}).get("class_distribution") or {}
    if class_dist:
        total = sum(int(v) for v in class_dist.values()) or 1
        dominant = max(class_dist.items(), key=lambda kv: kv[1]) if class_dist else (None, 0)
        rare = min(class_dist.items(), key=lambda kv: kv[1]) if class_dist else (None, 0)
        minority_pct = rare[1] / total * 100
        imb_chips = [
            ("Classes", str(len(class_dist))),
            ("Dominant", f"{dominant[0]} · {dominant[1] / total * 100:.0f}%"),
            ("Rarest", f"{rare[0]} · {minority_pct:.1f}%"),
        ]
    else:
        imb_chips = [("Classes", "—"), ("Dominant", "—"), ("Rarest", "—")]
    stages.append({
        **PIPELINE_STAGES[2],
        "state": imb_state,
        "chips": imb_chips,
        "detail": imbalance if has_imbalance else None,
    })

    # Stage 4 — model training
    trained_count = int(baseline_trained) + int(optimized_trained)
    tr_state = "offline" if not online else (
        "completed" if trained_count == 2 else (
            "pending" if trained_count == 0 else "partial"
        )
    )
    stages.append({
        **PIPELINE_STAGES[3],
        "state": tr_state,
        "chips": [
            ("Baseline", "trained" if baseline_trained else "absent"),
            ("Optimized", "trained" if optimized_trained else "absent"),
            ("Balancing", "SMOTE-Tomek"),
        ],
        "detail": {
            "baseline": baseline_trained,
            "optimized": optimized_trained,
            "models_present": [k for k, v in models.items()
                               if str(v).lower() == "trained"],
        },
    })

    # Stage 5 — evaluation
    metrics_payload = None
    if isinstance(metrics, dict):
        metrics_payload = metrics.get("metrics") if isinstance(metrics.get("metrics"), dict) else metrics
    has_eval = bool(metrics_payload and "accuracy" in metrics_payload)
    ev_state = "offline" if not online else ("completed" if has_eval else "pending")
    def _pct(key):
        try:
            return f"{float(metrics_payload.get(key, 0)) * 100:.1f}%"
        except (TypeError, ValueError):
            return "—"
    stages.append({
        **PIPELINE_STAGES[4],
        "state": ev_state,
        "chips": [
            ("Accuracy", _pct("accuracy")),
            ("Precision", _pct("precision")),
            ("Recall", _pct("recall")),
            ("F1", _pct("f1_score")),
        ],
        "detail": metrics_payload if has_eval else None,
    })

    # Stage 6 — explainability
    sh_state = "offline" if not online else ("completed" if has_shap else "pending")
    stages.append({
        **PIPELINE_STAGES[5],
        "state": sh_state,
        "chips": [
            ("SHAP summary", "cached" if has_shap else "not generated"),
            ("Explainer", "KernelExplainer"),
        ],
        "detail": {"has_summary": bool(has_shap)},
    })

    return stages


def pipeline_summary(stages):
    """Aggregate stage states into (state_label, completed, total, percent)."""
    total = len(stages)
    completed = sum(1 for s in stages if s["state"] == "completed")
    state = "completed" if completed == total else (
        "partial" if completed > 0 else (
            "offline" if total and all(s["state"] == "offline" for s in stages)
            else "pending"
        )
    )
    return state, completed, total, (completed / total * 100 if total else 0)