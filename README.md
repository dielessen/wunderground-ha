# Wunderground PWS — Home Assistant

Personal Weather Underground station measurements with **one selectable forecast provider**.
Maintained by dielessen, based on Aiasz’s MIT-licensed integration. See [CREDITS](CREDITS.md).

## Forecast providers

Select one provider in setup or in the integration options. The integration uses
that provider for both daily and hourly forecasts when available. It never contacts
another forecast provider to fill missing hours or to recover from a failure.

| Selection | Daily / hourly availability | Coverage | Credentials |
|---|---|---|---|
| Open-Meteo | Up to 7 days / 72 hours | Worldwide, depending on selected model | None for the free non-commercial service |
| KNMI via Open-Meteo | Up to 7 days / 72 hours | HARMONIE regional coverage, ECMWF extension | None for the free non-commercial service |
| MET Norway | Available local days / up to 72 hourly points | Locationforecast coverage | None |
| Weather Underground | Usually 5 days; 7-day endpoint attempted if unavailable / no hourly forecast | Subject to WU product access | WU API key |
| Weerlive | 5 days / 24 hours | Netherlands, location-specific | Personal Weerlive API key |
| Buienradar | 5 days / no hourly forecast | Netherlands, **national forecast** | None |

KNMI via Open-Meteo uses `knmi_seamless`: HARMONIE-AROME covers approximately the
first 60 hours, followed by ECMWF. This is one selected API provider with a documented
model transition. It is not a direct connection to the KNMI Open Data API.

Buienradar's public five-day feed is national, not a forecast at the configured
station's coordinates. Temperatures represent the national min/max envelope.
Unequal precipitation ranges are not converted into invented single amounts;
undocumented wind units are not shown as km/h. The separate two-hour rain nowcast
is not included in this release.

The returned period may be shorter than the maximum. Missing fields remain unknown.
On failure, the last good forecast from the **same selection** is marked stale and
kept for at most 12 hours. Changing provider, model or city invalidates the old cache.
Weather Underground and Buienradar advertise daily forecast support only in HA.

## Installation

HACS → Integrations → Custom repositories →
`https://github.com/dielessen/wunderground-ha` → category **Integration** → install
and restart Home Assistant.

For manual installation, copy `custom_components/wunderground_pws` into
`config/custom_components/` and restart.

The inherited advertised minimum Home Assistant version is 2024.12.0; validation
currently uses the current HA test dependencies on Python 3.14/Linux.

## Setup and changing provider

Settings → Devices & services → Add integration → **Wunderground PWS**.
For an installed entry, open its **Configure** options to change the forecast source.

| Field | Meaning |
|---|---|
| Station ID | Your WU PWS identifier; add another entry to change stations |
| API key | Your WU observation key; blank starts best-effort website key discovery |
| Update interval | Station observation interval, 1–60 minutes |
| Forecast / fallback city | Optional; empty uses station coordinates for forecasts |
| City country code | Two-letter code such as NL, used for geocoding and the public observation fallback |
| Forecast source | Exactly one provider from the table above |
| Personal Weerlive API key | Required only for Weerlive; separate from the WU key |
| Open-Meteo weather model | Applies only when the source is Open-Meteo; KNMI has its own fixed model choice |
| Air quality & pollen | Optional independent Open-Meteo data service |

For Weerlive and Buienradar, set the city country code to **NL**. Get your personal
Weerlive key from [Weerlive's API page](https://weerlive.nl/delen.php). Its 300-request
daily quota is per key: normal 30-minute forecast refreshes cost about 48 requests
per day per entry, plus manual refreshes/retries. Multiple entries share your quota.
The integration never uses the shared demo key in production.

## Observations and supplementary data

The forecast selector controls **forecasts**. This integration remains built around
a WU PWS for current observations and its existing entity identifiers. It is not a
standalone replacement for the observation service when selecting another forecast.

A personal [WU key](https://www.wunderground.com/member/api-keys) is recommended.
Shared keys discovered from the WU website may be rejected at any time. With a city
and country configured, observations can fall back to an unofficial public WU city
page. That page may report a different nearby station; `observation_source` and
`fallback_source_station` expose this. Its parser has only been verified against a
Hungarian metric fixture; Dutch page layout and unit compatibility are not guaranteed.
Blank country disables this public-page fallback. Existing entries retain HU until
changed in options. New entries suggest Home Assistant's country.

Independent Open-Meteo supplementary requests provide estimated missing gusts,
precipitation rate, radiation and UV, plus forecast sunshine duration for today.
Filled values are flagged `estimated`. Optional air-quality/pollen requests are
also separate from forecast selection. The forecast itself is never blended.

Other features include derived temperatures, cloud base, absolute humidity,
station health, daily measured extremes, pressure tendency, diagnostic sensors,
redacted diagnostics and the `wunderground_pws.refresh` service.

## Upgrading

Configuration schema 4 preserves station/entity IDs. Older `auto` and `blend`
forecast modes migrate to **Open-Meteo**, a single provider. Other explicit source
choices are preserved. Open the options after upgrading to choose your preferred
provider. Old caches without a matching selection are discarded and refreshed.

## Weather card

```yaml
type: weather-forecast
entity: weather.your_station_weather
forecast_type: daily
```

Use `hourly` only with an hourly-capable provider. Select the actual weather entity
from your Home Assistant instance.

## Provider terms and attribution

- KNMI data via [Open-Meteo](https://open-meteo.com/en/docs/knmi-api): CC BY 4.0;
  [free service terms](https://open-meteo.com/en/terms) restrict API use to non-commercial purposes.
- [Weerlive](https://weerlive.nl/delen.php): private/study use with linked attribution,
  personal key and 300 requests/day. Professional use requires a suitable service.
- [Buienradar.nl](https://www.buienradar.nl): non-commercial website/intranet use with
  linked attribution. Mobile/commercial applications require permission; review the
  [provider's published terms](https://www.buienradar.nl/overbuienradar/gratis-weerdata)
  for your deployment. No permission is implied by this integration's code license.
- MET Norway: Locationforecast 2.0, CC BY 4.0, identifying User-Agent and conditional caching.

See [CHANGELOG](CHANGELOG.md), [development guide](docs/DEVELOPMENT.md) and
[review notes](docs/REVIEW.md). Report bugs on [GitHub Issues](https://github.com/dielessen/wunderground-ha/issues).
The code is MIT licensed; provider data/service terms apply separately.
