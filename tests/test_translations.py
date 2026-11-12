"""Check complete translations and placeholder/enum parity across supported languages."""

from __future__ import annotations

import json
import pathlib
from string import Formatter

import pytest

from custom_components.wunderground_pws.binary_sensor import STATION_ONLINE, UV_PROTECTION
from custom_components.wunderground_pws.calculations import COMPASS_SLUGS
from custom_components.wunderground_pws.const import FORECAST_SOURCES, OPENMETEO_MODELS, UV_LEVELS
from custom_components.wunderground_pws.sensor import (
    AIR_QUALITY_SENSOR_DESCRIPTIONS,
    SENSOR_DESCRIPTIONS,
    UV_LEVEL_DESCRIPTION,
)

ROOT = pathlib.Path(__file__).parent.parent / "custom_components" / "wunderground_pws"
LANGUAGES = ("en", "nl", "hu")


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _paths(obj: dict, prefix: str = "") -> set[str]:
    out: set[str] = set()
    for key, value in obj.items():
        here = f"{prefix}/{key}"
        out.add(here)
        if isinstance(value, dict):
            out |= _paths(value, here)
    return out


def test_strings_json_matches_english_translation() -> None:
    assert _load(ROOT / "strings.json") == _load(ROOT / "translations" / "en.json")


@pytest.mark.parametrize("language", ("nl", "hu"))
def test_translation_has_exactly_the_english_keys(language) -> None:
    en = _paths(_load(ROOT / "translations" / "en.json"))
    translated = _paths(_load(ROOT / "translations" / f"{language}.json"))
    assert en == translated, f"Different keys in {language}.json: {en ^ translated}"


def test_every_entity_translation_key_is_translated() -> None:
    for lang in LANGUAGES:
        entity = _load(ROOT / "translations" / f"{lang}.json")["entity"]
        for description in SENSOR_DESCRIPTIONS:
            assert description.translation_key in entity["sensor"], (lang, description.key)
        for description in AIR_QUALITY_SENSOR_DESCRIPTIONS:
            assert description.translation_key in entity["sensor"], (lang, description.key)
        assert UV_LEVEL_DESCRIPTION.translation_key in entity["sensor"]
        assert STATION_ONLINE.translation_key in entity["binary_sensor"]
        assert UV_PROTECTION.translation_key in entity["binary_sensor"]
        assert "weather" in entity["weather"]


def test_compass_enum_states_are_translated() -> None:
    for lang in LANGUAGES:
        sensor = _load(ROOT / "translations" / f"{lang}.json")["entity"]["sensor"]
        assert set(sensor["wind_compass"]["state"]) == set(COMPASS_SLUGS)


def test_uv_level_enum_states_are_translated() -> None:
    for lang in LANGUAGES:
        sensor = _load(ROOT / "translations" / f"{lang}.json")["entity"]["sensor"]
        assert set(sensor["uv_level"]["state"]) == set(UV_LEVELS)


def test_enable_air_quality_option_is_translated() -> None:
    for lang in LANGUAGES:
        opt = _load(ROOT / "translations" / f"{lang}.json")["options"]["step"]["init"]["data"]
        assert "enable_air_quality" in opt


@pytest.mark.parametrize("language", LANGUAGES)
def test_translated_texts_are_nonempty_and_preserve_placeholders(language) -> None:
    def check(source, translated):
        if isinstance(source, dict):
            for key, value in source.items():
                check(value, translated[key])
        else:
            assert isinstance(translated, str) and translated.strip()
            source_fields = [field for _, field, _, _ in Formatter().parse(source) if field]
            translated_fields = [field for _, field, _, _ in Formatter().parse(translated) if field]
            assert sorted(source_fields) == sorted(translated_fields)

    check(_load(ROOT / "strings.json"), _load(ROOT / "translations" / f"{language}.json"))


@pytest.mark.parametrize("language", LANGUAGES)
def test_all_provider_choices_and_states_are_translated(language) -> None:
    data = _load(ROOT / "translations" / f"{language}.json")
    assert set(data["selector"]["forecast_source"]["options"]) == set(FORECAST_SOURCES)
    assert set(data["entity"]["sensor"]["forecast_source"]["state"]) == set(FORECAST_SOURCES)
    assert set(data["selector"]["openmeteo_model"]["options"]) == set(OPENMETEO_MODELS)


def test_dutch_compass_uses_dutch_directions() -> None:
    states = _load(ROOT / "translations" / "nl.json")["entity"]["sensor"]["wind_compass"]["state"]
    assert states["e"] == "O"
    assert states["s"] == "Z"
    assert states["nne"] == "NNO"
    assert states["sw"] == "ZW"
