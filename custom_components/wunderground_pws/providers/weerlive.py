"""Weerlive v2 location forecasts; personal key, private/study use with attribution.

Documentation and terms: https://weerlive.nl/delen.php
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
from .base import Capability, ProviderAuthError, ProviderError, ProviderInfo, ProviderNoDataError

URL = "https://weerlive.nl/api/weerlive_api_v2.php"
INFO = ProviderInfo(
    key="weerlive",
    name="Weerlive",
    attribution="Weather data via Weerlive.nl (https://weerlive.nl/delen.php)",
    capabilities=frozenset({Capability.DAILY, Capability.HOURLY}),
)
_CONDITIONS = {
    "zonnig": "sunny",
    "onbewolkt": "sunny",
    "bliksem": "lightning-rainy",
    "regen": "rainy",
    "buien": "rainy",
    "hagel": "hail",
    "mist": "fog",
    "sneeuw": "snowy",
    "bewolkt": "cloudy",
    "zwaarbewolkt": "cloudy",
    "lichtbewolkt": "partlycloudy",
    "halfbewolkt": "partlycloudy",
    "halfbewolkt_regen": "rainy",
    "nachtmist": "fog",
    "helderenacht": "clear-night",
    "nachtbewolkt": "cloudy",
}


def parse_forecast(
    data: dict[str, Any], now: datetime | None = None
) -> tuple[list[DailyForecastPoint], list[HourlyForecastPoint]]:
    """Normalize documented daily fields and UTC epoch hourly timestamps.

    Weerlive dates are Dutch local dates, independent of HA's own time zone.
    Missing precipitation amounts/probabilities stay unknown, never inferred.
    """
    tz = ZoneInfo("Europe/Amsterdam")
    cutoff = (now or datetime.now(UTC)).astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    daily: list[DailyForecastPoint] = []
    for row in data.get("wk_verw") or []:
        if not isinstance(row, dict):
            continue
        try:
            day = datetime.strptime(row["dag"], "%d-%m-%Y").date()
        except (KeyError, TypeError, ValueError):
            continue
        if day < cutoff.astimezone(tz).date():
            continue
        daily.append(
            DailyForecastPoint(
                datetime=local_midnight_utc_iso(day, tz),
                temperature=safe_float(row.get("max_temp")),
                templow=safe_float(row.get("min_temp")),
                wind_speed=safe_float(row.get("windkmh")),
                precipitation_probability=safe_float(row.get("neersl_perc_dag")),
                condition=_CONDITIONS.get(str(row.get("image", "")).lower()),
            )
        )
    hourly: list[HourlyForecastPoint] = []
    for row in data.get("uur_verw") or []:
        if not isinstance(row, dict):
            continue
        stamp = safe_float(row.get("timestamp"))
        if stamp is None:
            continue
        try:
            instant = datetime.fromtimestamp(stamp, UTC)
        except (ValueError, OverflowError, OSError):
            continue
        if instant < cutoff:
            continue
        hourly.append(
            HourlyForecastPoint(
                datetime=instant.isoformat(),
                temperature=safe_float(row.get("temp")),
                precipitation=safe_float(row.get("neersl")),
                wind_speed=safe_float(row.get("windkmh")),
                wind_bearing=safe_float(row.get("windrgr")),
                condition=_CONDITIONS.get(str(row.get("image", "")).lower()),
            )
        )
    return sorted(daily, key=lambda p: p["datetime"])[:5], sorted(
        hourly, key=lambda p: p["datetime"]
    )[:24]


async def fetch_forecast(
    session: aiohttp.ClientSession, lat: float, lon: float, api_key: str
) -> tuple[list[DailyForecastPoint], list[HourlyForecastPoint]]:
    """Fetch one location using the user's key; never use the shared demo key."""
    if not api_key:
        raise ProviderAuthError("weerlive: a personal API key is required")
    try:
        _, data, _ = await request_json(
            session,
            URL,
            provider="weerlive",
            timeout=TIMEOUT_FORECAST,
            params={"key": api_key, "locatie": f"{lat:.4f},{lon:.4f}"},
        )
    except ProviderError as exc:
        # Network exception messages may contain the credential-bearing URL.
        raise ProviderError("weerlive: request failed; check connectivity, key and quota") from exc
    if not isinstance(data, dict):
        raise ProviderError("weerlive: unexpected payload")
    result = parse_forecast(data)
    if not any(result):
        # Do not include the API's error text, which may contain the key.
        raise ProviderNoDataError("weerlive: no forecast returned; check key, quota and location")
    return result
