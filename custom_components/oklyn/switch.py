"""Contact auxiliaire Oklyn, exposé comme un interrupteur."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import AUX_OFF, AUX_ON
from .coordinator import OklynConfigEntry
from .entity import OklynEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OklynConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([OklynAuxSwitch(entry.runtime_data)])


class OklynAuxSwitch(OklynEntity, SwitchEntity):
    """Interrupteur pour le contact auxiliaire."""

    _attr_translation_key = "aux"
    _attr_icon = "mdi:electric-switch"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_aux"

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get("aux", {}).get("state")
        if value is None:
            return None
        return str(value).lower() == AUX_ON

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Horodatage du dernier changement du contact auxiliaire."""
        return {
            "changed_at": self.coordinator.data.get("aux", {}).get("changed_at"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.client.async_set_aux(AUX_ON)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.client.async_set_aux(AUX_OFF)
        await self.coordinator.async_request_refresh()
