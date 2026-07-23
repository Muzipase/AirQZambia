import logging

import numpy as np
import pandas as pd

from src.ingestion.data_validator import (
    OPTIONAL_FEATURE_COLUMNS,
    REQUIRED_FEATURE_COLUMNS,
    validate_dataframe,
)
from src.ingestion.openaq_client import fetch_openaq_measurements
from src.ingestion.openmeteo_client import fetch_openmeteo_measurements

logger = logging.getLogger(__name__)

VALID_SOURCES = ("openaq", "openmeteo", "auto")
DEFAULT_SOURCE = "auto"


def _ensure_optional_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Add optional weather columns if absent so downstream preprocessing is consistent."""
    for column in OPTIONAL_FEATURE_COLUMNS:
        if column not in data.columns:
            data[column] = np.nan
    return data


def _validate_and_clean(data: pd.DataFrame, source_label: str) -> pd.DataFrame:
    """Validate a fetched dataframe and raise on failure."""
    if data.empty:
        raise ValueError(f"{source_label} returned no data")

    validation = validate_dataframe(data)
    if not validation.get("is_valid", False):
        raise ValueError(f"{source_label} data validation failed: {validation}")

    return _ensure_optional_columns(data)


def fetch_openmeteo_data(
    city: str = None,
    forecast_days: int = 1,
) -> pd.DataFrame:
    """Fetch and validate pollutant records from Open-Meteo."""
    data = fetch_openmeteo_measurements(city=city, forecast_days=forecast_days)
    return _validate_and_clean(data, "Open-Meteo")


def fetch_openaq_data(
    limit: int = 200,
    country: str = None,
    days: int = 7,
    city: str = None,
) -> pd.DataFrame:
    """Fetch and validate pollutant records from OpenAQ, optionally filtered by city."""
    data = fetch_openaq_measurements(limit=limit, country=country, days=days, city=city)
    return _validate_and_clean(data, "OpenAQ")


def fetch_data(
    source: str = DEFAULT_SOURCE,
    city: str = None,
    limit: int = 200,
    country: str = None,
    days: int = 7,
    forecast_days: int = 1,
) -> pd.DataFrame:
    """Unified data fetch with source selection and automatic fallback.

    Parameters
    ----------
    source : str
        One of ``"openaq"``, ``"openmeteo"``, or ``"auto"`` (default).
        ``"auto"`` tries Open-Meteo first, then falls back to OpenAQ.
    city : str, optional
        Filter to a specific city (e.g. ``"Lusaka"``).
    limit, country, days
        Passed through to the OpenAQ client when applicable.
    forecast_days : int
        Number of forecast days for Open-Meteo (default 1 = today only).

    Returns
    -------
    pd.DataFrame
        Validated pollutant data in wide format.
    """
    source = source.lower().strip()
    if source not in VALID_SOURCES:
        raise ValueError(f"Invalid source '{source}'. Must be one of {VALID_SOURCES}")

    if source == "openmeteo":
        return fetch_openmeteo_data(city=city, forecast_days=forecast_days)

    if source == "openaq":
        return fetch_openaq_data(limit=limit, country=country, days=days, city=city)

    # Auto mode: try Open-Meteo first (no auth required), fall back to OpenAQ
    try:
        data = fetch_openmeteo_data(city=city, forecast_days=forecast_days)
        logger.info("Auto source: Open-Meteo succeeded (%d records)", len(data))
        return data
    except Exception as exc:
        logger.warning("Auto source: Open-Meteo failed (%s), falling back to OpenAQ", exc)

    try:
        data = fetch_openaq_data(limit=limit, country=country, days=days, city=city)
        logger.info("Auto source: OpenAQ succeeded (%d records)", len(data))
        return data
    except Exception as exc:
        logger.error("Auto source: OpenAQ also failed (%s)", exc)
        raise ValueError("Both Open-Meteo and OpenAQ failed to return data")
