"""Tests for the Streamlit multi-pollutant EPA AQI computation (app/state.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import state  # noqa: E402


def test_pm25_to_aqi_known_points():
    assert state.pm25_to_aqi(0.0) == 0
    assert state.pm25_to_aqi(12.0) == 50
    assert state.pm25_to_aqi(24.1) == 76
    assert state.pm25_to_aqi(150.4) == 200
    assert state.pm25_to_aqi(300.0) == 340
    assert state.pm25_to_aqi(1000.0) == 500


def test_per_pollutant_subindex_reference_points():
    assert state.pm10_to_aqi(54.0) == 50
    assert state.pm10_to_aqi(154.0) == 100
    assert state.no2_to_aqi(53.0) == 50
    assert state.no2_to_aqi(100.0) == 100
    assert state.so2_to_aqi(35.0) == 50
    assert state.so2_to_aqi(185.0) == 150
    assert state.co_to_aqi(4.4 * 1000) == 50
    assert state.o3_to_aqi(108.0) == 50


def test_non_finite_and_missing_return_none():
    assert state.pm10_to_aqi(None) is None
    assert state.no2_to_aqi(float("nan")) is None
    assert state.pm25_to_aqi("") is None


def test_compute_aqi_uses_worst_pollutant_and_dominant():
    readings = {
        "pm25": 8.0,    # AQI 33
        "pm10": 300.0,   # AQI ~173 -> dominant
        "no2": 1.5,
        "so2": 1.1,
        "co": 236.0,
        "o3": 139.0,
    }
    aqi, dominant, sub = state.compute_aqi(readings)
    assert aqi == max(sub.values())
    assert aqi > sub["pm25"]
    assert dominant == "pm10"
    assert sub["pm25"] == 33


def test_compute_aqi_pm25_fallback():
    aqi, dominant, sub = state.compute_aqi({"pm25": 24.1})
    assert aqi == 76
    assert dominant == "pm25"
    assert sub == {"pm25": 76}


def test_compute_aqi_empty():
    assert state.compute_aqi({}) == (None, None, {})
    assert state.compute_aqi({"pm25": None}) == (None, None, {})


def test_classify_aqi_bands_and_names():
    assert state.classify_aqi(50)[0] == "Good"
    assert state.classify_aqi(75)[0] == "Moderate"
    assert state.classify_aqi(120)[0] == "Unhealthy"
    assert state.classify_aqi(170)[0] == "Very Unhealthy"
    assert state.classify_aqi(250)[0] == "Hazardous"


def test_sample_readings_produce_a_multi_pollutant_aqi():
    aqi, dominant, sub = state.compute_aqi(state.SAMPLE_READINGS)
    assert aqi is not None
    assert dominant in state.POLLUTANTS
    assert set(sub) <= set(state.POLLUTANTS)