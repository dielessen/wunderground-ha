# Credits and attribution

Original author: **Aiasz**. This independent repository is maintained by **dielessen**
and based on [aiasz/ha-wunderground-pws](https://github.com/aiasz/ha-wunderground-pws).
The original MIT copyright and license are preserved in [LICENSE](LICENSE).

## Original feature ideas

Upstream credited the following as inspiration, without copying their code.
This repository does contain the upstream integration code.

| Feature | Source | Upstream attribution |
|---|---|---|
| English interface, hourly forecasts, air quality and pollen | ztarsoly (Zoli), [issue #1](https://github.com/aiasz/ha-wunderground-pws/issues/1) | Feature requests |
| Public city-page fallback | Aiasz | Source identification and Hungarian-page verification |
| Bilingual interface, persistent forecasts, planned alerts | [ztarsoly/ha-idokep-weather-and-forecast](https://github.com/ztarsoly/ha-idokep-weather-and-forecast) | MIT; ideas only, no Idokep data |
| Planned HungaroMet stations and radar | [FabianGabor/HA-HungaroMet](https://github.com/FabianGabor/HA-HungaroMet), [ztarsoly/ha-hungaromet-weather-and-forecast](https://github.com/ztarsoly/ha-hungaromet-weather-and-forecast) | License unspecified / MIT, as recorded upstream |
| Planned alerts | [amaximus/met_alerts_hu](https://github.com/amaximus/met_alerts_hu) | MIT; ideas only |
| WU five-day product, daypart structure, reauthentication and language | [cytech/Home-Assistant-wundergroundpws](https://github.com/cytech/Home-Assistant-wundergroundpws) | Documentation observations; no copied code; license not established upstream |

## Data providers

- Weather Underground / The Weather Company: observations and forecasts; a personal
  PWS-owner API key is recommended.
- MET Norway Locationforecast 2.0: CC BY 4.0. The integration sends an identifying
  User-Agent and supports cache expiry and conditional requests.
- Open-Meteo: CC BY 4.0; the free API is intended for non-commercial use.
  Check current service limits before deployment. Geocoding uses GeoNames data.
- HungaroMet was an upstream roadmap idea, not an implemented provider. Upstream
  recorded the attribution "Database: Meteorological Database, HungaroMet Nonprofit Zrt."
  and the requirement to preserve data and warnings unchanged.

## Formula references

- Wind chill: Environment Canada / NWS (2001).
- Wet-bulb temperature: Stull (2011), Journal of Applied Meteorology and Climatology.
- Cloud base: Espy approximation (125 m/degree C).
- Clear-sky radiation: Kasten & Czeplak (1980).
- Solar elevation: NOAA General Solar Position Calculations.

## Dutch forecast adapters (1.8.0)

- KNMI HARMONIE-AROME via Open-Meteo, using knmi_seamless (ECMWF extension).
  [API documentation](https://open-meteo.com/en/docs/knmi-api); CC BY 4.0 and
  Open-Meteo's non-commercial free-service limits apply.
- Weather data via [Weerlive.nl](https://weerlive.nl/delen.php): private/study use,
  linked credit and a personal key; 300 requests/day per key.
- [Buienradar.nl](https://www.buienradar.nl): national daily forecast;
  [published terms](https://www.buienradar.nl/overbuienradar/gratis-weerdata) require
  linked attribution and restrict use. Mobile/commercial use needs permission.
- New fixtures were captured from the documented public Buienradar JSON feed and
  Weerlive's documented demo endpoint on 12 November 2026. Only forecast numerical
  data/category fields are retained; no personal credentials or weather-report prose.
