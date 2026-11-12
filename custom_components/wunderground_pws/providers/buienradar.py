"""Buienradar national five-day forecast (not a point-specific forecast).

Use with linked attribution for private, non-commercial use; see
https://www.buienradar.nl/overbuienradar/gratis-weerdata
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

import aiohttp

from ..calculations import safe_float
from ..const import TIMEOUT_FORECAST
from ..models import DailyForecastPoint, HourlyForecastPoint, local_midnight_utc_iso
from ._http import request_json
from .base import Capability, ProviderError, ProviderInfo, ProviderNoDataError

URL = "https://data.buienradar.nl/2.0/feed/json"
INFO = ProviderInfo(
    key="buienradar",
    name="Buienradar (Netherlands national)",
    attribution="Buienradar.nl (https://www.buienradar.nl)",
    capabilities=frozenset({Capability.DAILY}),
)


def _condition(description: str) -> str | None:
    """Map recognizable Dutch descriptions; leave unknown descriptions unset."""
    text = description.lower()
    for word, condition in (
        ("onweer", "lightning-rainy"),
        ("hagel", "hail"),
        ("sneeuw", "snowy"),
        ("mist", "fog"),
        ("regen", "rainy"),
        ("bui", "rainy"),
        ("opklaring", "partlycloudy"),
        ("zonnig", "sunny"),
        ("zwaar bewolkt", "cloudy"),
        ("geheel bewolkt", "cloudy"),
    ):
        if word in text:
            return condition
    return None


def parse_forecast(data: dict[str, Any], now: datetime | None = None) -> list[DailyForecastPoint]:
    """Use the national temperature envelope; do not invent values from ranges."""
    tz = ZoneInfo("Europe/Amsterdam")
    today = (now or datetime.now(UTC)).astimezone(tz).date()
    forecast = data.get("forecast")
    if not isinstance(forecast, dict):
        return []
    daily: list[DailyForecastPoint] = []
    for row in forecast.get("fivedayforecast") or []:
        if not isinstance(row, dict):
            continue
        try:
            day = datetime.fromisoformat(row["day"]).date()
        except (KeyError, TypeError, ValueError):
            continue
        if day < today:
            continue
        rain_min, rain_max = safe_float(row.get("mmRainMin")), safe_float(row.get("mmRainMax"))
        daily.append(
            DailyForecastPoint(
                datetime=local_midnight_utc_iso(day, tz),
                temperature=safe_float(row.get("maxtemperatureMax")),
                templow=safe_float(row.get("mintemperatureMin")),
                precipitation=rain_min if rain_min == rain_max else None,
                precipitation_probability=safe_float(row.get("rainChance")),
                condition=_condition(str(row.get("weatherdescription", ""))),
            )
        )
    return sorted(daily, key=lambda p: p["datetime"])[:5]


async def fetch_forecast(
    session: aiohttp.ClientSession,
) -> tuple[list[DailyForecastPoint], list[HourlyForecastPoint]]:
    """Fetch the national JSON feed; no hourly forecast is provided."""
    _, data, _ = await request_json(session, URL, provider="buienradar", timeout=TIMEOUT_FORECAST)
    if not isinstance(data, dict):
        raise ProviderError("buienradar: unexpected payload")
    daily = parse_forecast(data)
    if not daily:
        raise ProviderNoDataError("buienradar: no forecast returned")
    return daily, []
