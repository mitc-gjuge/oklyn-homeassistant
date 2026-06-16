"""Entité de base partagée par tous les types d'entités Oklyn."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import OklynDataUpdateCoordinator


class OklynEntity(CoordinatorEntity[OklynDataUpdateCoordinator]):
    """Base : rattache l'entité à l'appareil Oklyn et active les noms d'entité HA."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: OklynDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            manufacturer=MANUFACTURER,
            name=f"Piscine Oklyn {coordinator.device_id}",
            configuration_url="https://api.oklyn.fr",
        )
