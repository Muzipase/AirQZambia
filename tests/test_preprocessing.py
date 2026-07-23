import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.preprocessing.missing_values import fill_missing_values
from src.preprocessing.scaling import fit_scaler, apply_scaler_to_dataframe
from src.preprocessing.split_dataset import split_data


def test_placeholder_preprocessing():
    # Sanity placeholder test to ensure tests discoverable
    assert True


def test_apply_scaler_to_dataframe_preserves_non_numeric_columns():
    df = pd.DataFrame(
        {
            "pm25": [1.0, 2.0, 3.0],
            "pm10": [4.0, 5.0, 6.0],
            "aqi_category": ["Good", "Moderate", "Unhealthy"],
        }
    )

    _, scaler = fit_scaler(df[["pm25", "pm10"]])
    result = apply_scaler_to_dataframe(df, scaler, ["pm25", "pm10", "aqi_category"])

    assert list(result.columns) == ["pm25", "pm10", "aqi_category"]
    assert result["aqi_category"].tolist() == ["Good", "Moderate", "Unhealthy"]
    assert not result["pm25"].equals(df["pm25"])
    assert not result["pm10"].equals(df["pm10"])


def test_fill_missing_values_handles_all_missing_columns():
    df = pd.DataFrame(
        {
            "pm25": [1.0],
            "temperature": [np.nan],
            "humidity": [np.nan],
            "wind_speed": [np.nan],
        }
    )

    result = fill_missing_values(df)

    assert result["pm25"].iloc[0] == 1.0
    assert result["temperature"].iloc[0] == 0.0
    assert result["humidity"].iloc[0] == 0.0
    assert result["wind_speed"].iloc[0] == 0.0


def test_split_data_avoids_stratify_when_a_class_has_single_sample():
    X = pd.DataFrame({"feature": range(6)})
    y = pd.Series(["Good", "Moderate", "Moderate", "Unhealthy", "Unhealthy", "Hazardous"])

    X_train, X_test, y_train, y_test = split_data(X, y)

    assert len(X_train) > 0
    assert len(X_test) > 0
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)

