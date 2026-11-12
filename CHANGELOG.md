# Changelog

Historical upstream releases below are English summaries. The original detailed
records remain in Git history. Original author: Aiasz; see CREDITS.md.

## Unreleased

- Make English the primary repository documentation language.
- Point installation, documentation and issue links to dielessen/wunderground-ha.
- Remove the preselected Hungarian station and city from new installations.
- Add a city country code to setup and options, defaulting to Home Assistant's
  country for new entries. Apply it to fallback URLs, geocoding and cache keys.
  Existing entries retain HU until changed. Blank disables public-page fallback.
- Redact location/station identifiers from diagnostics; export exception types
  instead of raw messages that could expose credentials or locations.
- Add regional and diagnostics regression tests and a code-review report.

## 1.7.1 — 2026-10-31 (upstream)

- Add always-on Open-Meteo sunshine duration and supplementation of missing wind
  gusts, precipitation rate, solar radiation and UV; preserve real measurements.
- Standardize the estimated attribute, replacing estimated_from_forecast for UV.
- Remove personal-location wording from documentation; expand tests.

## 1.7.0 — 2026-10-31 (upstream)

- Allow setup without a working automatically discovered key when a fallback city
  exists. Reject empty station IDs and invalid manually entered keys.
- Fill fallback coordinates through geocoding, estimate compass-sector bearings
  (plus/minus 11.25 degrees), calculate heat index and supplement UV from forecasts.
- Add optional European/US AQI, six pollutants and six pollen species. Use
  MeteoSwiss pollen categories; no category is assigned to olive pollen.
- Add UV categories and a UV-protection sensor. UV fallback still required
  Open-Meteo forecasts at this release; other missing fields remained unavailable.

## 1.6.1 — 2026-10-31 (upstream)

- Add public WU city-page observation fallback, source diagnostics and shared
  derived calculations. This uses WU's nearby station, not necessarily the configured
  station. Verified on Hungarian HTML; station dashboard JavaScript APIs are unused.

## 1.6.0 — 2026-10-31 (upstream)

- Add 72-hour forecasts, blending, 14-day accuracy scoring and model selection.
- Add persistent daily extremes, pressure tendency, diagnostics, refresh service,
  forecast caching, API usage sensors, retries and circuit breakers.
- Separate forecasts from observation updates. Constrain today's forecast by
  recorded measurements and use hourly conditions at night.
- Suggest Kaposvar and IKAPOS27 in setup; preserve entity identifiers.
- Avoid unnecessary reloads when changing keys.

## 1.5.0 — 2026-10-31 (upstream)

- Add English UI, provider adapters, station health, reauthentication, translated
  compass states, wet-bulb temperature, richer weather attributes, tests and CI.
- Add the MIT license, credits and changelog.
- Fix WU daypart indexing/icon mappings; prefer the five-day forecast endpoint.
- Fix overlapping MET Norway precipitation windows and local-day aggregation.
- Improve night, snow, fog, strong-wind and solar-derived conditions.
- Fix empty options overwriting keys, lost forecasts, excessive API calls,
  weather-card updates, timestamps, feels-like values and setup errors.
- Prevent station-ID edits from orphaning entities; migrate to configuration v3.
- Fix hard-coded versions/names and cloud-base calculations.
- Validate discovered keys, limit retries and preserve manual keys. Shared website
  keys may be rejected; a personal key is recommended.
- Remove explicit aiohttp dependency; record minimum Home Assistant as 2024.12.0.

## 1.4.1 — 2026-04-07 (upstream)

- Fix NaN wind speeds on forecast cards.

## 1.4.0 — 2026-04-07 (upstream)

- Add WU → MET Norway → Open-Meteo forecast fallback.

## 1.3.0 — 2026-03-02 (upstream)

- Add demo mode and automatic key discovery/rediscovery.

## 1.2.0 — 2026-02-27 (upstream)

- Add API requests, seven-day forecasts, forecast cities and calculated sensors.

## 1.1.0 / 1.0.0 (upstream)

- Move to API-based observations after the initial HTML-scraping release.
