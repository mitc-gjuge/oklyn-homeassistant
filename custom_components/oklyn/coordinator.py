"""Coordinator : interroge l'API Oklyn à intervalle régulier."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OklynAuthError, OklynClient, OklynError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Type alias : l'entrée de configuration porte directement son coordinator
type OklynConfigEntry = ConfigEntry[OklynDataUpdateCoordinator]


class OklynDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Centralise les requêtes vers un appareil Oklyn."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: OklynClient,
        scan_interval: int,
        device_id: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({device_id})",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.device_id = device_id

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_get_all()
        except OklynAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except OklynError as err:
            raise UpdateFailed(str(err)) from err
