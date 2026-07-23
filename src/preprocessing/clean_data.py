import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names, remove duplicates, and drop invalid records."""
    if df is None:
        return pd.DataFrame()

    data = df.copy()
    data.columns = [str(col).strip().lower() for col in data.columns]

    if "timestamp" in data.columns:
        data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")

    data = data.drop_duplicates().reset_index(drop=True)
    data = data.dropna(subset=["pm25", "pm10", "no2", "so2", "co", "o3"], how="all")

    # Cast numeric pollutant columns
    for column in ["pm25", "pm10", "no2", "so2", "co", "o3", "temperature", "humidity", "wind_speed"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce").astype(float)

    return data
