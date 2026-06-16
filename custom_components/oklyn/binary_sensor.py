"""Capteur binaire Oklyn : la filtration tourne-t-elle réellement.

Le `select` expose le *mode* choisi (off/on/auto) ; ce capteur expose l'état
*réel* de la pompe, renvoyé par l'API dans le champ `status` de `GET pump`.
"""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import OklynConfigEntry
from .entity import OklynEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OklynConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([OklynPumpRunningSensor(entry.runtime_data)])


class OklynPumpRunningSensor(OklynEntity, BinarySensorEntity):
    """Indique si la pompe de filtration est effectivement en marche."""

    _attr_translation_key = "pump_running"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_icon = "mdi:pump"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_pump_running"

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get("pump", {}).get("running")
