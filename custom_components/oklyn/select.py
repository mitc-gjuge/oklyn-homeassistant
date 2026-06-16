"""Mode de filtration Oklyn, exposé comme un sélecteur (off / on / auto)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import PUMP_OPTIONS
from .coordinator import OklynConfigEntry
from .entity import OklynEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OklynConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([OklynPumpSelect(entry.runtime_data)])


class OklynPumpSelect(OklynEntity, SelectEntity):
    """Sélecteur du mode de filtration de la pompe."""

    _attr_translation_key = "pump"
    _attr_icon = "mdi:pump"
    _attr_options = PUMP_OPTIONS

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_pump"

    @property
    def current_option(self) -> str | None:
        value = self.coordinator.data.get("pump", {}).get("mode")
        if value is None:
            return None
        value = str(value).lower()
        return value if value in PUMP_OPTIONS else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Distingue le mode choisi de l'état réel de la pompe."""
        pump = self.coordinator.data.get("pump", {})
        return {
            "running": pump.get("running"),
            "changed_at": pump.get("changed_at"),
        }

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.async_set_pump(option)
        await self.coordinator.async_request_refresh()
