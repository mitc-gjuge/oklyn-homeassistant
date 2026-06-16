"""Contacts auxiliaires Oklyn, exposés comme des interrupteurs.

L'appareil expose deux contacts (`aux` et `aux2`) ; un interrupteur est créé
pour chacun.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import AUX_CONTACTS
from .const import AUX_OFF, AUX_ON
from .coordinator import OklynConfigEntry
from .entity import OklynEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OklynConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(OklynAuxSwitch(coordinator, contact) for contact in AUX_CONTACTS)


class OklynAuxSwitch(OklynEntity, SwitchEntity):
    """Interrupteur pour un contact auxiliaire."""

    _attr_icon = "mdi:electric-switch"

    def __init__(self, coordinator, contact: str) -> None:
        super().__init__(coordinator)
        self._contact = contact
        self._attr_translation_key = contact
        self._attr_unique_id = f"{coordinator.device_id}_{contact}"

    @property
    def _data(self) -> dict[str, Any]:
        return self.coordinator.data.get(self._contact) or {}

    @property
    def is_on(self) -> bool | None:
        value = self._data.get("state")
        if value is None:
            return None
        return str(value).lower() == AUX_ON

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Horodatage du dernier changement du contact auxiliaire."""
        return {"changed_at": self._data.get("changed_at")}

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.client.async_set_aux(self._contact, AUX_ON)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.client.async_set_aux(self._contact, AUX_OFF)
        await self.coordinator.async_request_refresh()
