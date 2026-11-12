# Code review — 12 November 2026

Scope: repository documentation, configuration, provider location handling,
diagnostics, and the existing automated test suite. This is a source review with
mocked provider tests, not validation against a live Home Assistant installation.

## Regional behavior

The original defaults target **Hungary**, not Norway: IKAPOS27, Kaposvár, a fixed
Hungarian public-page URL and Hungarian request language. MET Norway is one of
the forecast adapters; it receives the resolved station/city coordinates.

New installations now start without a station or city suggestion and use Home
Assistant's country as the suggested city country code. Set it to `NL` for a
Dutch city. Existing entries retain HU until changed in options, preserving
their previous fallback routing. The station ID and existing entity IDs remain
unchanged. Hungarian UI translations and original response fixtures are retained.

## Fixed findings

| Finding | Change |
|---|---|
| All public-page fallback requests went to Hungary | Configurable country code, normalized and validated before URL construction |
| City lookup could choose a namesake in another country | Pass countryCode to the geocoder and include country in persistent cache keys |
| Setup prefilled somebody else's station and city | Empty station/city suggestions |
| Diagnostics could expose station/location identifiers and arbitrary exception text | Redact identifiers and export only the exception class |
| Documentation, maintainer and issue links still referred to the upstream project | English documentation and this repository's links; original attribution retained |

Country filtering follows the [Open-Meteo geocoding API](https://open-meteo.com/en/docs/geocoding-api).

## Remaining limitations and follow-up risks

- **Public-page fallback:** the HTML parser has only a Hungarian metric fixture.
  Country selection does not prove Dutch live-page compatibility. Temperature,
  dew-point and wind parsing assume metric values; another layout or imperial
  response needs explicit unit handling. Some countries require a more specific
  WU URL path than country/city. Prefer observations through a personal WU API key.
- **Automatic key discovery:** shared keys extracted from the website can be
  rejected or removed. This is inherited behavior, not a reliable substitute for
  a personal API key.
- **Hourly timestamps:** Open-Meteo parsing subtracts one utc_offset_seconds value
  from local timestamps. Forecasts spanning a daylight-saving transition need
  dedicated fixtures and UTC/unix-time handling; this was not changed here.
- **Sunshine duration:** the sensor reads daily forecast sunshine_duration, not
  accumulated observed sunshine up to the current moment. Treat it as a model
  estimate for the day, despite its current “today” label.
- **Compatibility:** CI targets current test dependencies on Python 3.14. The
  advertised minimum Home Assistant 2024.12 has not been independently retested.

## Follow-up: single-provider forecasts (1.8.0)

The forecast coordinator now selects exactly one provider, including KNMI via
Open-Meteo, Weerlive and Buienradar. Legacy auto/blend modes migrate to Open-Meteo.
WU/Buienradar have no hourly forecast; no other provider supplies missing hours.
Persisted caches carry a provider/model/location identity. Provider constraints and
terms are documented in the main README. PWS observations and independent solar /
optional air-quality supplements are separate from forecast selection.

Validation for 1.8.0: 294 tests pass under Linux/WSL, including provider selection,
migration, provider switching/cache invalidation, failure isolation, new response
parsers, credentials and diagnostics. A live KNMI/Open-Meteo request returned seven
daily and 168 hourly points using the integration's requested variables; the
integration exposes at most 72 hours. This is not a live HA installation test.

## Validation (initial review)


The unmodified upstream baseline passed 271 tests under Linux/WSL. All **277 tests**
in the updated suite pass, along with Ruff lint and formatting checks. The updated
suite adds coverage for Dutch routing, blank-country fallback disabling,
geocoding filters/cache separation, setup defaults and diagnostics redaction.
Run the commands in [DEVELOPMENT.md](DEVELOPMENT.md) to reproduce validation.
