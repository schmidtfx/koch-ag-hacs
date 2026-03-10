"""Config flow for the Koch AG SIP Gateway integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import CONF_VIDEO_PORT, DEFAULT_API_PORT, DEFAULT_VIDEO_PORT, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_API_PORT): vol.All(
            int, vol.Range(min=1, max=65535)
        ),
        vol.Optional(CONF_VIDEO_PORT, default=DEFAULT_VIDEO_PORT): vol.All(
            int, vol.Range(min=1, max=65535)
        ),
    }
)


class KochAgConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Rene Koch AG SIP Gateway."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the initial step shown when the user adds the integration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            api_port = user_input.get(CONF_PORT, DEFAULT_API_PORT)

            # Unique ID is based on host + API port to identify the device.
            await self.async_set_unique_id(f"{host}:{api_port}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Rene Koch AG SIP Gateway",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
