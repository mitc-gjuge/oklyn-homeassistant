"""Intégration Oklyn (pilotage de piscine) pour Home Assistant."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OklynClient
from .const import CONF_DEVICE_ID, CONF_SCAN_INTERVAL_S, DEFAULT_SCAN_INTERVAL
from .coordinator import OklynConfigEntry, OklynDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: OklynConfigEntry) -> bool:
    """Configure une entrée Oklyn."""
    session = async_get_clientsession(hass)
    client = OklynClient(
        entry.data[CONF_API_KEY],
        entry.data[CONF_DEVICE_ID],
        session,
    )

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL_S, DEFAULT_SCAN_INTERVAL)
    coordinator = OklynDataUpdateCoordinator(hass, client, scan_interval, entry)

    # Premier refresh : échoue proprement si l'API ne répond pas
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: OklynConfigEntry) -> None:
    """Recharge l'intégration quand les options changent."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: OklynConfigEntry) -> bool:
    """Décharge une entrée Oklyn."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
