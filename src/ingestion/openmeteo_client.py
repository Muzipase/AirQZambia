import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pandas as pd
import requests

OPENMETEO_AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
OPENMETEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

STUDY_CITIES: Dict[str, Dict[str, float]] = {
    "Lusaka": {"latitude": -15.3875, "longitude": 28.3228},
    "Ndola": {"latitude": -12.8000, "longitude": 28.2167},
    "Kitwe": {"latitude": -10.8833, "longitude": 27.7833},
}

TARGET_PARAMETERS = ["pm25", "pm10", "no2", "so2", "co", "o3"]

OPENMETEO_POLLUTANT_MAP = {
    "pm2_5": "pm25",
    "pm10": "pm10",
    "nitrogen_dioxide": "no2",
    "sulphur_dioxide": "so2",
    "carbon_monoxide": "co",
    "ozone": "o3",
}

OPENMETEO_WEATHER_MAP = {
    "temperature_2m": "temperature",
    "relative_humidity_2m": "humidity",
    "wind_speed_10m": "wind_speed",
}

logger = logging.getLogger(__name__)


def get_city_coordinates(city: Optional[str] = None) -> List[Dict[str, object]]:
    """Return coordinate list for the requested city or all study cities."""
    if city and city in STUDY_CITIES:
        return [{"city": city, **STUDY_CITIES[city]}]
    return [{"city": name, **coords} for name, coords in STUDY_CITIES.items()]


def _fetch_aq_hourly(
    latitude: float,
    longitude: float,
    forecast_days: int = 1,
) -> Optional[Dict]:
    """Fetch hourly air quality data from Open-Meteo for a single location."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(OPENMETEO_POLLUTANT_MAP.keys()),
        "timezone": "Africa/Lusaka",
        "forecast_days": forecast_days,
    }
    try:
        response = requests.get(OPENMETEO_AQ_URL, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Open-Meteo AQ request failed for (%s, %s): %s", latitude, longitude, exc)
        return None


def _fetch_aq_historical(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    variables: Optional[List[str]] = None,
) -> Optional[Dict]:
    """Fetch historical hourly air quality data from Open-Meteo.

    Parameters
    ----------
    latitude, longitude : float
        Coordinates.
    start_date, end_date : str
        ISO date strings (yyyy-mm-dd).
    variables : list of str, optional
        Open-Meteo variable names (e.g. ``["pm2_5", "pm10"]``).
        Defaults to all standard pollutants.

    Returns
    -------
    dict or None
        Raw Open-Meteo JSON response.
    """
    if variables is None:
        variables = list(OPENMETEO_POLLUTANT_MAP.keys())

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(variables),
        "timezone": "Africa/Lusaka",
        "start_date": start_date,
        "end_date": end_date,
    }
    try:
        response = requests.get(OPENMETEO_AQ_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Open-Meteo historical AQ request failed for (%s, %s): %s", latitude, longitude, exc)
        return None


def _fetch_weather_hourly(
    latitude: float,
    longitude: float,
    forecast_days: int = 1,
) -> Optional[Dict]:
    """Fetch hourly weather data from Open-Meteo for a single location."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(OPENMETEO_WEATHER_MAP.keys()),
        "timezone": "Africa/Lusaka",
        "forecast_days": forecast_days,
    }
    try:
        response = requests.get(OPENMETEO_WEATHER_URL, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Open-Meteo weather request failed for (%s, %s): %s", latitude, longitude, exc)
        return None


def _build_city_dataframe(
    city: str,
    aq_data: Optional[Dict],
    weather_data: Optional[Dict],
) -> pd.DataFrame:
    """Combine air quality and weather JSON into a single wide-format DataFrame."""
    if aq_data is None or "hourly" not in aq_data:
        return pd.DataFrame()

    hourly = aq_data["hourly"]
    times = hourly.get("time", [])
    if not times:
        return pd.DataFrame()

    n = len(times)
    col_data: Dict[str, object] = {
        "location": [f"{city} Open-Meteo"] * n,
        "city": [city] * n,
        "country": ["ZM"] * n,
        "timestamp": times,
    }

    for openmeteo_key, target_key in OPENMETEO_POLLUTANT_MAP.items():
        values = hourly.get(openmeteo_key, [])
        col_data[target_key] = [values[i] if i < len(values) else None for i in range(n)]

    if weather_data and "hourly" in weather_data:
        wh = weather_data["hourly"]
        for openmeteo_key, target_key in OPENMETEO_WEATHER_MAP.items():
            values = wh.get(openmeteo_key, [])
            col_data[target_key] = [values[i] if i < len(values) else None for i in range(n)]

    return pd.DataFrame(col_data)


def fetch_openmeteo_measurements(
    city: Optional[str] = None,
    forecast_days: int = 1,
) -> pd.DataFrame:
    """Fetch air quality (and weather) measurements from Open-Meteo for study cities.

    Returns a wide-format DataFrame with columns matching the OpenAQ output schema:
    location, city, country, timestamp, pm25, pm10, no2, so2, co, o3,
    and optional temperature, humidity, wind_speed.
    """
    city_coords = get_city_coordinates(city)
    frames: List[pd.DataFrame] = []

    def _fetch_one(entry: Dict) -> pd.DataFrame:
        name = entry["city"]
        lat = entry["latitude"]
        lon = entry["longitude"]
        logger.info("Fetching Open-Meteo data for %s (%s, %s)", name, lat, lon)
        aq = _fetch_aq_hourly(lat, lon, forecast_days=forecast_days)
        wx = _fetch_weather_hourly(lat, lon, forecast_days=forecast_days)
        return _build_city_dataframe(name, aq, wx)

    with ThreadPoolExecutor(max_workers=min(len(city_coords), 6)) as pool:
        futures = {pool.submit(_fetch_one, entry): entry for entry in city_coords}
        for future in as_completed(futures):
            city_df = future.result()
            if not city_df.empty:
                frames.append(city_df)

    if not frames:
        logger.warning("No data returned from Open-Meteo for any city")
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined["timestamp"] = pd.to_datetime(combined["timestamp"], errors="coerce")
    combined = combined.dropna(subset=["timestamp"])

    for param in TARGET_PARAMETERS:
        if param not in combined.columns:
            combined[param] = pd.NA

    return combined
