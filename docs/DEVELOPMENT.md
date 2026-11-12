# Development guide

Home Assistant tests require Linux. Use Linux or WSL with Python 3.14 (the CI version).

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
ruff check custom_components tests
ruff format --check custom_components tests
pytest
```

## Architecture

| Module | Responsibility |
|---|---|
| coordinator.py | Observations, key discovery, validation and fallback |
| forecast.py | Forecast scheduling, caching and provider selection |
| providers/ | Provider adapters, shared HTTP helpers and circuit breakers |
| calculations.py, conditions.py | Pure calculations and condition mappings |
| models.py | Normalized provider data structures |
| settings.py | Effective settings: options override entry data |
| config_flow.py | Setup, options and reauthentication |
| sensor.py, binary_sensor.py, weather.py, entity.py | Entities reading coordinator data |

## Adding a provider

1. Add a provider adapter with ProviderInfo and fetch functions. Raise ProviderError
   on failure; normalize results using models.py.
2. Add condition mappings with parameterized tests.
3. Add an anonymized response fixture and parser tests.
4. Review service terms and document attribution in CREDITS.md.

## Conventions

- Preserve existing entity keys and unique IDs.
- Add regression tests for bug fixes and run the complete suite before publishing.
- Keep the version in manifest.json; release tags must match it.
- Write documentation, comments and GitHub project text in English.
- Keep UI strings in strings.json and translations/*.json. Existing translations
  and historical fixtures are retained.
- Never publish credentials, SERVER.md or PLAN.md.

See [REVIEW.md](REVIEW.md) for review findings and limitations.
