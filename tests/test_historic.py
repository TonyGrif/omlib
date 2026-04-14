"""Tests for omlib.historic.HistoricAPI."""

import pytest
import requests
import responses as rsps

from omlib.client import Client
from omlib.historic import HistoricAPI

_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
_MOCK_RESPONSE = {
    "latitude": 48.8,
    "longitude": 2.3,
    "hourly": {"temperature_2m": [20.1]},
}


def _make_api(base_url: str | None = None, **kwargs) -> HistoricAPI:
    return HistoricAPI(
        Client(base_url=base_url),
        48.8,
        2.3,
        "2024-01-01",
        "2024-01-31",
        **kwargs,
    )


def _url(call_index: int = 0) -> str:
    url = rsps.calls[call_index].request.url
    assert url is not None
    return url


@rsps.activate
def test_archive_returns_parsed_json() -> None:
    rsps.add(rsps.GET, _ARCHIVE_URL, json=_MOCK_RESPONSE, status=200)

    result = _make_api().archive()

    assert result == _MOCK_RESPONSE


@rsps.activate
def test_archive_required_params_in_query() -> None:
    rsps.add(rsps.GET, _ARCHIVE_URL, json=_MOCK_RESPONSE, status=200)

    _make_api().archive()

    url = _url()
    assert "latitude=48.8" in url
    assert "longitude=2.3" in url
    assert "start_date=2024-01-01" in url
    assert "end_date=2024-01-31" in url


@rsps.activate
def test_archive_hourly_list_joined() -> None:
    rsps.add(rsps.GET, _ARCHIVE_URL, json=_MOCK_RESPONSE, status=200)

    _make_api().archive(hourly=["temperature_2m", "precipitation"])

    assert "hourly=temperature_2m%2Cprecipitation" in _url()


@rsps.activate
def test_archive_timezone_forwarded() -> None:
    rsps.add(rsps.GET, _ARCHIVE_URL, json=_MOCK_RESPONSE, status=200)

    _make_api(timezone="Europe/Paris").archive()

    assert "timezone=Europe%2FParis" in _url()


@rsps.activate
def test_archive_none_params_omitted() -> None:
    rsps.add(rsps.GET, _ARCHIVE_URL, json=_MOCK_RESPONSE, status=200)

    _make_api().archive()

    url = _url()
    assert "timezone" not in url
    assert "temperature_unit" not in url
    assert "wind_speed_unit" not in url
    assert "precipitation_unit" not in url


@rsps.activate
def test_archive_base_url_override() -> None:
    custom_url = "http://localhost:8080/v1/archive"
    rsps.add(rsps.GET, custom_url, json=_MOCK_RESPONSE, status=200)

    _make_api(base_url="http://localhost:8080").archive()

    assert _url().startswith(custom_url)


@rsps.activate
def test_archive_http_error_raises() -> None:
    rsps.add(
        rsps.GET,
        _ARCHIVE_URL,
        json={"error": True, "reason": "bad request"},
        status=400,
    )

    with pytest.raises(requests.HTTPError):
        _make_api().archive()


def test_session_retries_on_status_codes() -> None:
    api = _make_api()
    session = api._session()
    adapter = session.get_adapter("https://")
    retry = adapter.max_retries

    assert retry.backoff_factor == 0.5
    assert 429 in retry.status_forcelist
    assert retry.allowed_methods == frozenset(["GET"])


@rsps.activate
def test_public_attrs_update_query() -> None:
    rsps.add(rsps.GET, _ARCHIVE_URL, json=_MOCK_RESPONSE, status=200)

    api = _make_api()
    api.latitude = 51.5
    api.longitude = -0.1
    api.start_date = "2024-06-01"
    api.end_date = "2024-06-30"
    api.timezone = "Europe/London"
    api.archive()

    url = _url()
    assert "latitude=51.5" in url
    assert "longitude=-0.1" in url
    assert "start_date=2024-06-01" in url
    assert "end_date=2024-06-30" in url
    assert "timezone=Europe%2FLondon" in url
