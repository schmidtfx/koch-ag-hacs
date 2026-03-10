"""Button platform for the Rene Koch AG SIP Gateway — door opener."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KochAgCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the door-open button."""
    coordinator: KochAgCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KochAgDoorButton(coordinator, entry)])


class KochAgDoorButton(CoordinatorEntity[KochAgCoordinator], ButtonEntity):
    """Button that sends the door-open command to the Rene Koch AG SIP Gateway."""

    _attr_translation_key = "open_door"
    _attr_has_entity_name = True

    def __init__(self, coordinator: KochAgCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_open_door"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Rene Koch AG",
            model="SIP Gateway",
        )

    async def async_press(self) -> None:
        """Handle button press — send door-open command."""
        await self.coordinator.api.async_open_door()
