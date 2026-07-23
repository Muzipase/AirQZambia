import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import pandas as pd
import requests

OPENAQ_BASE_URL = "https://api.openaq.org/v2/measurements"
TARGET_PARAMETERS = ["pm25", "pm10", "no2", "so2", "co", "o3"]
DEFAULT_LIMIT = 200
DEFAULT_DAYS = 7

logger = logging.getLogger(__name__)


def _build_common_payload(limit: int, days: int, country: Optional[str] = None) -> Dict[str, object]:
    payload = {
        "limit": limit,
        "sort": "desc",
        "order_by": "datetime",
        "date_from": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat().replace("+00:00", "Z"),
    }
    if country:
        payload["country"] = country
    return payload


def _build_fallback_measurements(city: Optional[str] = None) -> pd.DataFrame:
    """Return a small built-in dataset when the upstream API is unavailable."""
    base_timestamp = datetime.now(timezone.utc)
    
    # City-specific data with realistic variations
    city_data = {
        "Lusaka": {"base_pm25": 8.0, "base_pm10": 12.0, "base_no2": 10.0, "country": "ZM"},
        "Ndola": {"base_pm25": 15.0, "base_pm10": 25.0, "base_no2": 15.0, "country": "ZM"},
        "Kitwe": {"base_pm25": 12.0, "base_pm10": 20.0, "base_no2": 12.0, "country": "ZM"},
    }
    
    selected_city = city if city in city_data else "Lusaka"
    city_config = city_data[selected_city]
    
    sample_rows = [
        {
            "location": f"{selected_city} Station",
            "city": selected_city,
            "country": city_config["country"],
            "timestamp": (base_timestamp - timedelta(hours=6 * index)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pm25": city_config["base_pm25"] + index * 7.0,
            "pm10": city_config["base_pm10"] + index * 10.0,
            "no2": city_config["base_no2"] + index * 4.0,
            "so2": 4.0 + index * 2.0,
            "co": 0.2 + index * 0.05,
            "o3": 20.0 + index * 6.0,
            "temperature": 24.0 + index,
            "humidity": 55.0 + index * 2.0,
            "wind_speed": 3.0 + index * 0.8,
        }
        for index in range(6)
    ]
    return pd.DataFrame(sample_rows)


def fetch_openaq_measurements(limit: int = DEFAULT_LIMIT, country: Optional[str] = None, days: int = DEFAULT_DAYS, city: Optional[str] = None) -> pd.DataFrame:
    """Fetch the latest pollutant measurements from the OpenAQ API or fall back to local sample data."""
    records = []
    payload = _build_common_payload(limit=limit, days=days, country=country)
    if city:
        payload["city"] = city

    try:
        def _fetch_parameter(parameter: str) -> List[Dict]:
            params = {**payload, "parameter": parameter}
            resp = requests.get(OPENAQ_BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json().get("results", [])

        with ThreadPoolExecutor(max_workers=min(len(TARGET_PARAMETERS), 6)) as pool:
            futures = {pool.submit(_fetch_parameter, p): p for p in TARGET_PARAMETERS}
            for future in as_completed(futures):
                data = future.result()
                for item in data:
                    date_item = item.get("date", {})
                    utc_date = date_item.get("utc") or date_item.get("local")
                    records.append(
                        {
                            "location": item.get("location"),
                            "city": item.get("city"),
                            "country": item.get("country"),
                            "timestamp": utc_date,
                            "parameter": item.get("parameter"),
                            "value": item.get("value"),
                            "unit": item.get("unit"),
                        }
                    )
    except (requests.RequestException, ValueError) as exc:
        logger.warning("OpenAQ fetch failed, using built-in sample data: %s", exc)
        return _build_fallback_measurements(city=city)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "parameter", "value"])

    if df.empty:
        return pd.DataFrame()

    pivot = (
        df.pivot_table(
            index=["location", "city", "country", "timestamp"],
            columns="parameter",
            values="value",
            aggfunc="mean",
        )
        .reset_index()
    )

    # Ensure every expected pollutant column is present
    for parameter in TARGET_PARAMETERS:
        if parameter not in pivot.columns:
            pivot[parameter] = pd.NA

    return pivot
