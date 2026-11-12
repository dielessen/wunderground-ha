"""Dutch forecast adapters and strict single-provider selection."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.wunderground_pws.const import (
    DOMAIN,
    METNO_FORECAST_URL,
    OPEN_METEO_FORECAST_URL,
)
from custom_components.wunderground_pws.diagnostics import async_get_config_entry_diagnostics
from custom_components.wunderground_pws.providers import buienradar, weerlive
from custom_components.wunderground_pws.providers.base import (
    ProviderAuthError,
    ProviderError,
    ProviderNoDataError,
)

from .conftest import API_KEY, STATION, calls_to, load_json, make_entry, mock_apis

NOW = datetime(2026, 11, 12, 14, 55, tzinfo=UTC)
KEY = "personal-weerlive-test-key"


def test_weerlive_real_response_and_units() -> None:
    daily, hourly = weerlive.parse_forecast(load_json("weerlive_forecast.json"), NOW)
    assert len(daily) == 5
    assert len(hourly) == 24
    assert daily[0]["datetime"] == "2026-11-11T23:00:00+00:00"
    assert daily[0]["temperature"] == 9
    assert daily[0]["wind_speed"] == 18
    assert daily[0]["precipitation_probability"] == 50
    assert "precipitation" not in daily[0]
    assert hourly[0]["datetime"] == "2026-11-12T15:00:00+00:00"
    assert hourly[0]["wind_speed"] == 14
    assert hourly[0]["precipitation"] == 0
    assert hourly[3]["condition"] == "clear-night"


def test_weerlive_epoch_timestamps_distinguish_repeated_dst_hour() -> None:
    payload = {
        "uur_verw": [
            {"timestamp": datetime(2026, 10, 25, h, tzinfo=UTC).timestamp(), "temp": 10}
            for h in (0, 1)
        ]
    }
    _, hours = weerlive.parse_forecast(payload, datetime(2026, 10, 25, tzinfo=UTC))
    assert [p["datetime"] for p in hours] == [
        "2026-10-25T00:00:00+00:00",
        "2026-10-25T01:00:00+00:00",
    ]


def test_buienradar_national_ranges_are_not_point_estimates() -> None:
    points = buienradar.parse_forecast(load_json("buienradar_forecast.json"), NOW)
    assert len(points) == 5
    assert points[0]["templow"] == 1
    assert points[0]["temperature"] == 10
    assert points[0]["condition"] == "partlycloudy"
    assert "wind_speed" not in points[0]  # feed wind is not a documented km/h speed
    payload = {
        "forecast": {"fivedayforecast": [{"day": "2026-11-12", "mmRainMin": 1, "mmRainMax": 4}]}
    }
    assert buienradar.parse_forecast(payload, NOW)[0]["precipitation"] is None


@pytest.mark.parametrize(
    "source", ["wunderground", "openmeteo", "metno", "knmi", "weerlive", "buienradar"]
)
async def test_only_selected_forecast_provider_is_called(
    hass, aioclient_mock, freezer, source
) -> None:
    freezer.move_to(NOW)
    mock_apis(aioclient_mock)
    aioclient_mock.get(weerlive.URL, json=load_json("weerlive_forecast.json"))
    aioclient_mock.get(buienradar.URL, json=load_json("buienradar_forecast.json"))
    entry = make_entry(
        data={"forecast_source": source, "country_code": "NL", "weerlive_api_key": KEY}
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    forecast = entry.runtime_data.forecast
    # Independent observation supplements are outside the forecast coordinator.
    aioclient_mock.mock_calls.clear()
    await forecast.async_refresh_if_due(force=True)
    allowed = {
        "wunderground": "api.weather.com/v3/",
        "openmeteo": OPEN_METEO_FORECAST_URL,
        "knmi": OPEN_METEO_FORECAST_URL,
        "metno": METNO_FORECAST_URL,
        "weerlive": weerlive.URL,
        "buienradar": buienradar.URL,
    }[source]
    assert all(allowed in str(call[1]) for call in aioclient_mock.mock_calls)
    if source != "metno":  # default MET fixture intentionally has no data
        assert aioclient_mock.mock_calls
        assert forecast.data["sources_used"] == [source]
        assert forecast.source_used == source
    if source in ("buienradar", "wunderground"):
        assert forecast.hourly == []
    if source == "knmi":
        assert calls_to(aioclient_mock, "models=knmi_seamless")
    if source == "weerlive":
        result = await async_get_config_entry_diagnostics(hass, entry)
        assert KEY not in json.dumps(result, default=str)


async def test_missing_weerlive_key_never_uses_demo_or_network(hass, aioclient_mock) -> None:
    with pytest.raises(ProviderAuthError):
        await weerlive.fetch_forecast(async_get_clientsession(hass), 52.3, 4.9, "")
    assert not aioclient_mock.mock_calls


async def test_provider_errors_do_not_expose_key(hass) -> None:
    with (
        patch.object(weerlive, "request_json", side_effect=ProviderError(f"URL?key={KEY}")),
        pytest.raises(ProviderError) as error,
    ):
        await weerlive.fetch_forecast(async_get_clientsession(hass), 52.3, 4.9, KEY)
    assert KEY not in str(error.value)


async def test_empty_api_payload_is_unavailable(hass, aioclient_mock) -> None:
    aioclient_mock.get(weerlive.URL, json={"error": "invalid key"})
    aioclient_mock.get(buienradar.URL, json={"forecast": {}})
    with pytest.raises(ProviderNoDataError):
        await weerlive.fetch_forecast(async_get_clientsession(hass), 52.3, 4.9, KEY)
    with pytest.raises(ProviderNoDataError):
        await buienradar.fetch_forecast(async_get_clientsession(hass))


@pytest.mark.parametrize(
    ("source", "country", "key", "error"),
    [
        ("weerlive", "NL", "", "weerlive_api_key"),
        ("buienradar", "DE", "", "country_code"),
    ],
)
async def test_setup_checks_provider_requirements(hass, source, country, key, error) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "station_id": STATION,
            "api_key": API_KEY,
            "scan_interval": 5,
            "forecast_source": source,
            "country_code": country,
            "weerlive_api_key": key,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert error in result["errors"]


async def test_setup_saves_separate_weerlive_key(hass, aioclient_mock, freezer) -> None:
    freezer.move_to(NOW)
    mock_apis(aioclient_mock)
    aioclient_mock.get(weerlive.URL, json=load_json("weerlive_forecast.json"))
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "station_id": STATION,
            "api_key": API_KEY,
            "scan_interval": 5,
            "forecast_source": "weerlive",
            "country_code": "NL",
            "weerlive_api_key": KEY,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["weerlive_api_key"] == KEY
    assert result["data"]["api_key"] == API_KEY
    await hass.async_block_till_done()


async def test_switching_provider_discards_previous_cached_forecast(
    hass, aioclient_mock, freezer
) -> None:
    freezer.move_to(NOW)
    mock_apis(aioclient_mock)
    aioclient_mock.get(buienradar.URL, json=load_json("buienradar_forecast.json"))
    entry = make_entry(data={"forecast_source": "wunderground", "country_code": "NL"})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    old = entry.runtime_data.forecast
    assert old.source_used == "wunderground"
    # Save immediately to reproduce a restart/option change before the cache TTL.
    await old._bundle_store.async_save({**old.data, "selection": old._selection()})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "api_key": API_KEY,
            "scan_interval": 5,
            "city": "",
            "country_code": "NL",
            "forecast_source": "buienradar",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    current = entry.runtime_data.forecast
    assert current is not old
    assert current.source_used == "buienradar"
    assert current.hourly == []
    assert current.daily[0]["temperature"] == 10


async def test_selected_provider_failure_keeps_only_its_own_cached_data(
    hass, aioclient_mock, freezer
) -> None:
    freezer.move_to(NOW)
    mock_apis(aioclient_mock)
    aioclient_mock.get(buienradar.URL, json=load_json("buienradar_forecast.json"))
    entry = make_entry(data={"forecast_source": "buienradar", "country_code": "NL"})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    forecast = entry.runtime_data.forecast
    previous = list(forecast.daily)
    aioclient_mock.clear_requests()
    aioclient_mock.get(buienradar.URL, status=503)
    await forecast.async_refresh_if_due(force=True)
    assert forecast.stale
    assert forecast.daily == previous
    assert forecast.source_used == "buienradar"
    assert all(buienradar.URL in str(c[1]) for c in aioclient_mock.mock_calls)
