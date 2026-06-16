"""Tests unitaires du décodage des réponses Oklyn (`api.py`).

Couvre `_extract_scalar` et `_parse_measure`, le cœur du décodage des réponses
de l'API. Les formes de référence (`{"recorded","value","status","value_raw"}`
pour les mesures, `{"pump"/"aux", "status", "changed_at"}` pour les actionneurs)
sont celles confirmées en live.
"""

from __future__ import annotations

import pytest

# --------------------------------------------------------------------------- #
# _extract_scalar
# --------------------------------------------------------------------------- #


class TestExtractScalar:
    """Extraction d'une valeur scalaire d'une réponse de forme variable."""

    def test_preferred_key_present(self, api):
        assert api._extract_scalar({"pump": "auto"}, "pump") == "auto"

    def test_preferred_key_wins_over_value(self, api):
        # La clé préférée prime même si "value" existe aussi.
        assert api._extract_scalar({"value": 1, "ph": 2}, "ph") == 2

    def test_preferred_key_wins_over_other_entries(self, api):
        # Et même si le dict a plusieurs entrées (pas de repli "1 seule clé").
        assert api._extract_scalar({"pump": "auto", "status": "off"}, "pump") == "auto"

    def test_first_matching_preferred_key(self, api):
        # Plusieurs clés préférées : on prend la première présente, dans l'ordre.
        assert api._extract_scalar({"b": 2, "a": 1}, "a", "b") == 1

    def test_value_fallback(self, api):
        # Clé préférée absente -> repli sur "value".
        assert api._extract_scalar({"value": 6.88}, "ph") == 6.88

    @pytest.mark.parametrize(
        ("payload", "expected"),
        [
            ({"value": 7.2}, 7.2),
            ({"data": 5}, 5),
            ({"state": "on"}, "on"),
            ({"result": 1}, 1),
        ],
    )
    def test_generic_fallback_keys(self, api, payload, expected):
        assert api._extract_scalar(payload) == expected

    def test_generic_key_priority_order(self, api):
        # "value" passe avant "data" dans l'ordre de repli.
        assert api._extract_scalar({"data": 2, "value": 1}) == 1

    def test_single_entry_dict(self, api):
        # Dict à une seule entrée, clé inconnue -> on prend sa valeur.
        assert api._extract_scalar({"whatever": 42}) == 42

    def test_multi_entry_unknown_keys_returns_none(self, api):
        assert api._extract_scalar({"a": 1, "b": 2}) is None

    def test_empty_dict_returns_none(self, api):
        assert api._extract_scalar({}) is None

    @pytest.mark.parametrize("scalar", [7.2, "auto", 0, False, None])
    def test_scalar_passthrough(self, api, scalar):
        # Une valeur non-dict est renvoyée telle quelle.
        assert api._extract_scalar(scalar) is scalar


# --------------------------------------------------------------------------- #
# _parse_measure
# --------------------------------------------------------------------------- #


class TestParseMeasure:
    """Décodage d'une réponse `data/<mesure>` en valeur + métadonnées."""

    def test_real_api_shape(self, api):
        payload = {
            "recorded": "2026-06-16T04:27:37+00:00",
            "value": 6.88,
            "status": "normal",
            "value_raw": 6.88,
        }
        assert api._parse_measure(payload) == {
            "value": 6.88,
            "status": "normal",
            "recorded": "2026-06-16T04:27:37+00:00",
        }

    def test_temperature_shape_status_none(self, api):
        payload = {
            "recorded": "2026-06-16T04:30:00+00:00",
            "value": 28.0,
            "status": None,
            "value_raw": 28.0,
        }
        result = api._parse_measure(payload)
        assert result["value"] == 28.0
        assert result["status"] is None

    def test_value_targeted_explicitly_over_value_raw(self, api):
        # On lit `value`, pas `value_raw` (qui pourrait différer : brut vs calibré).
        payload = {"value": 7.0, "value_raw": 6.5}
        assert api._parse_measure(payload)["value"] == 7.0

    def test_string_value_is_coerced(self, api):
        assert api._parse_measure({"value": "6.88"})["value"] == 6.88

    def test_value_none_yields_none(self, api):
        assert api._parse_measure({"value": None})["value"] is None

    def test_non_numeric_value_yields_none(self, api):
        assert api._parse_measure({"value": "n/a"})["value"] is None

    def test_missing_value_falls_back_to_extract_scalar(self, api):
        # Pas de clé "value" -> repli via _extract_scalar (dict à une entrée).
        assert api._parse_measure({"ph": 7.2})["value"] == 7.2

    def test_scalar_payload(self, api):
        result = api._parse_measure(6.88)
        assert result == {"value": 6.88, "status": None, "recorded": None}

    def test_empty_dict(self, api):
        assert api._parse_measure({}) == {
            "value": None,
            "status": None,
            "recorded": None,
        }

    def test_always_returns_three_keys(self, api):
        result = api._parse_measure({"value": 1})
        assert set(result) == {"value", "status", "recorded"}
