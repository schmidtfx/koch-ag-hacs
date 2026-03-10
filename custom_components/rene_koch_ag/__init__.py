"""Rene Koch AG SIP Gateway — Home Assistant custom integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KochAgApi
from .const import DEFAULT_API_PORT, DOMAIN
from .coordinator import KochAgCoordinator

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.CAMERA]

SERVICE_OPEN_DOOR = "open_door"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rene Koch AG SIP Gateway from a config entry."""
    session = async_get_clientsession(hass)
    api = KochAgApi(
        session,
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_API_PORT),
    )

    coordinator = KochAgCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_open_door(call: ServiceCall) -> None:
        """Handle the open_door service call."""
        await coordinator.api.async_open_door()

    hass.services.async_register(DOMAIN, SERVICE_OPEN_DOOR, handle_open_door)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
