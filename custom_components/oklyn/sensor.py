"""Capteurs Oklyn : températures, pH, RedOx."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import OklynConfigEntry
from .entity import OklynEntity

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="water",
        translation_key="water",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="air",
        translation_key="air",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="ph",
        translation_key="ph",
        device_class=SensorDeviceClass.PH,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="orp",
        translation_key="orp",
        native_unit_of_measurement="mV",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SensorEntityDescription(
        key="salt",
        translation_key="salt",
        native_unit_of_measurement="g/L",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:shaker-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OklynConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(OklynSensor(coordinator, desc) for desc in SENSORS)


class OklynSensor(OklynEntity, SensorEntity):
    """Un capteur de mesure de la piscine."""

    def __init__(self, coordinator, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"

    @property
    def _measure(self) -> dict[str, Any]:
        return self.coordinator.data.get(self.entity_description.key) or {}

    @property
    def native_value(self) -> float | None:
        return self._measure.get("value")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Métadonnées Oklyn : alerte de plage et horodatage de la mesure."""
        return {
            "status": self._measure.get("status"),
            "recorded": self._measure.get("recorded"),
        }
