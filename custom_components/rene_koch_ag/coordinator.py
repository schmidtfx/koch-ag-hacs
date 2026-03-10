"""DataUpdateCoordinator for the Rene Koch AG SIP Gateway."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CannotConnectError, KochAgApi, KochAgApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class KochAgCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls the Rene Koch AG SIP Gateway for status updates."""

    def __init__(self, hass: HomeAssistant, api: KochAgApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Check that the gateway is reachable.

        No data is fetched — this integration has no REST state to poll.
        Raising UpdateFailed here marks the integration as unavailable in the HA UI.
        """
        try:
            await self.api.async_check_reachable()
        except CannotConnectError as err:
            raise UpdateFailed(f"Gateway unreachable: {err}") from err
        except KochAgApiError as err:
            raise UpdateFailed(f"Error communicating with Rene Koch AG gateway: {err}") from err
        return {}
