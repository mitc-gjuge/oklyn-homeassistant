"""Client asynchrone minimal pour l'API publique Oklyn.

API : https://api.oklyn.fr/public/v1/device/{device_id}/...
Authentification : en-tête `X-Api-Token: <cle_api>`

FORME DES RÉPONSES (confirmée en live le 2026-06-16)
----------------------------------------------------
Mesures `GET data/<mesure>` :
    {"recorded": "2026-...Z", "value": 6.88, "status": "normal", "value_raw": 6.88}
Pompe `GET pump` :
    {"pump": "auto", "status": "off", "changed_at": "2026-...Z"}
    -> `pump` = mode choisi (off/on/auto) ; `status` = la pompe tourne-t-elle vraiment.
Auxiliaire `GET aux` :
    {"aux": "off", "status": "off", "changed_at": null}

Le décodage cible désormais ces champs explicitement. `_extract_scalar()` reste
utilisé comme filet de sécurité si la forme évoluait.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_BASE = "https://api.oklyn.fr/public/v1"
AUTH_HEADER = "X-Api-Token"

# Délai max (secondes) par requête, pour ne jamais bloquer le coordinator.
REQUEST_TIMEOUT_S = 30

# Mesures exposées par .../data/<mesure> (liste complète confirmée en live) :
#   water = température de l'eau, air = température de l'air,
#   ph = pH, orp = potentiel RedOx (mV), salt = salinité (g/L)
MEASURES: tuple[str, ...] = ("water", "air", "ph", "orp", "salt")

# Contacts auxiliaires pilotables (endpoints confirmés en live). L'appareil en
# expose deux : `aux` (le premier, sans suffixe) et `aux2`.
AUX_CONTACTS: tuple[str, ...] = ("aux", "aux2")


class OklynError(Exception):
    """Erreur de communication avec l'API Oklyn."""


class OklynAuthError(OklynError):
    """Clé API invalide ou refusée (401/403)."""


def _extract_scalar(payload: Any, *preferred_keys: str) -> Any:
    """Extrait une valeur scalaire d'une réponse de forme inconnue.

    On tente plusieurs formes courantes, dans l'ordre :
      - dict avec une clé attendue (ex. {"ph": 7.2} ou {"pump": "auto"})
      - dict avec une clé générique ("value", "data", "state", "result")
      - dict à une seule entrée -> on prend sa valeur
      - valeur scalaire directe (ex. 7.2 ou "auto")

    >>> SI LE PARSING EST FAUX, C'EST ICI QU'ON CORRIGE. <<<
    """
    if isinstance(payload, dict):
        for key in (*preferred_keys, "value", "data", "state", "result"):
            if key in payload:
                return payload[key]
        if len(payload) == 1:
            return next(iter(payload.values()))
        return None
    return payload


def _as_float(value: Any) -> float | None:
    """Convertit en float, ou None si impossible."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _field(payload: Any, key: str) -> Any:
    """Lecture défensive d'un champ d'un dict de réponse (None si absent)."""
    return payload.get(key) if isinstance(payload, dict) else None


def _is_on(value: Any) -> bool | None:
    """Interprète un champ d'état Oklyn ('on'/'off') en booléen, ou None."""
    if value is None:
        return None
    return str(value).lower() == "on"


def _parse_measure(payload: Any) -> dict[str, Any]:
    """Décode une réponse `data/<mesure>` : valeur calibrée + métadonnées.

    On cible explicitement `value` ; `_extract_scalar` sert de filet de
    sécurité si la forme du JSON venait à changer.
    """
    if isinstance(payload, dict) and "value" in payload:
        value = _as_float(payload["value"])
    else:
        value = _as_float(_extract_scalar(payload))
    return {
        "value": value,
        "status": _field(payload, "status"),
        "recorded": _field(payload, "recorded"),
    }


class OklynClient:
    """Client asynchrone pour un appareil Oklyn."""

    def __init__(
        self, api_key: str, device_id: str, session: aiohttp.ClientSession
    ) -> None:
        self._session = session
        self._device_id = device_id
        self._headers = {AUTH_HEADER: api_key}

    @property
    def _device_url(self) -> str:
        return f"{API_BASE}/device/{self._device_id}"

    async def _request(self, method: str, path: str, json: dict | None = None) -> Any:
        url = f"{self._device_url}/{path}"
        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers,
                json=json,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_S),
            ) as resp:
                if resp.status in (401, 403):
                    raise OklynAuthError(f"Authentification refusée ({resp.status})")
                resp.raise_for_status()
                if resp.content_type == "application/json":
                    return await resp.json()
                return await resp.text()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise OklynError(f"Erreur réseau sur {url} : {err}") from err

    async def async_validate(self) -> None:
        """Vérifie la clé API et le device_id (utilisé par le config flow)."""
        await self._request("GET", "pump")

    async def async_set_pump(self, mode: str) -> None:
        """Modifie le mode de filtration (off / on / auto)."""
        await self._request("PUT", "pump", json={"pump": mode})

    async def async_set_aux(self, contact: str, state: str) -> None:
        """Modifie l'état d'un contact auxiliaire (`aux` ou `aux2`) -> on / off.

        Le corps PUT `{"aux": state}` est confirmé en live (2026-06-16) pour les
        deux contacts : c'est l'endpoint (`aux` vs `aux2`) qui différencie le
        contact, la clé du corps reste `aux` dans les deux cas.
        """
        await self._request("PUT", contact, json={"aux": state})

    async def async_get_all(self) -> dict[str, Any]:
        """Récupère toutes les données en une fois (appels concurrents)."""
        paths = [f"data/{m}" for m in MEASURES]
        paths.append("pump")
        paths.extend(AUX_CONTACTS)
        responses = await asyncio.gather(*[self._request("GET", p) for p in paths])
        by_path = dict(zip(paths, responses, strict=True))

        data: dict[str, Any] = {}
        for measure in MEASURES:
            data[measure] = _parse_measure(by_path[f"data/{measure}"])

        pump_payload = by_path["pump"]
        data["pump"] = {
            "mode": _extract_scalar(pump_payload, "pump"),
            "running": _is_on(_field(pump_payload, "status")),
            "changed_at": _field(pump_payload, "changed_at"),
        }
        for contact in AUX_CONTACTS:
            aux_payload = by_path[contact]
            data[contact] = {
                "state": _extract_scalar(aux_payload, "aux"),
                "status": _field(aux_payload, "status"),
                "changed_at": _field(aux_payload, "changed_at"),
            }
        return data
