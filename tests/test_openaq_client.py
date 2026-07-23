import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ingestion import openaq_client


class _FailingResponse:
    def raise_for_status(self):
        raise requests.HTTPError("410 Client Error: Gone")


def test_fetch_openaq_measurements_returns_fallback_when_api_fails(monkeypatch):
    monkeypatch.setattr(openaq_client.requests, "get", lambda *args, **kwargs: _FailingResponse())

    df = openaq_client.fetch_openaq_measurements(limit=5)

    assert not df.empty
    assert len(df) >= 4
    assert {"pm25", "pm10", "no2", "so2", "co", "o3"}.issubset(df.columns)
