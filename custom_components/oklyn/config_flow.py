"""Config flow pour l'intégration Oklyn."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OklynAuthError, OklynClient, OklynError
from .const import (
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL_S,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class OklynConfigFlow(ConfigFlow, domain=DOMAIN):
    """Assistant de configuration via l'UI."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OklynOptionsFlow:
        """Expose le flux d'options (réglage de l'intervalle de polling)."""
        return OklynOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = OklynClient(
                user_input[CONF_API_KEY],
                user_input[CONF_DEVICE_ID],
                session,
            )
            try:
                await client.async_validate()
            except OklynAuthError:
                errors["base"] = "invalid_auth"
            except OklynError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Piscine Oklyn ({user_input[CONF_DEVICE_ID]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ID): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )


class OklynOptionsFlow(OptionsFlow):
    """Flux d'options : intervalle de rafraîchissement."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL_S, DEFAULT_SCAN_INTERVAL
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL_S, default=current
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=30,
                            max=3600,
                            step=10,
                            unit_of_measurement="s",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )
