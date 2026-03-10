"""HTTP client for the Rene Koch AG SIP Gateway REST API."""

from __future__ import annotations

import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)


class KochAgApiError(Exception):
    """Raised when an API request fails."""


class CannotConnectError(KochAgApiError):
    """Raised when the gateway is not reachable."""


class KochAgApi:
    """Async HTTP client for the Rene Koch AG SIP Gateway.

    Replace the placeholder endpoint paths below with the actual endpoints
    documented in the Rene Koch AG SIP Gateway API reference.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int = 80,
    ) -> None:
        self._session = session
        self._base_url = f"http://{host}:{port}"

    async def async_check_reachable(self) -> None:
        """Verify the gateway is reachable with a lightweight HEAD request."""
        url = f"{self._base_url}/"
        try:
            async with self._session.head(url, timeout=aiohttp.ClientTimeout(total=10)):
                pass
        except aiohttp.ClientConnectionError as err:
            raise CannotConnectError(f"Cannot connect to {url}: {err}") from err
        except (TimeoutError, aiohttp.ClientError) as err:
            raise KochAgApiError(f"Request to {url} failed: {err}") from err

    async def async_open_door(self) -> None:
        """Send the door-open command to the gateway."""
        url = f"{self._base_url}/user/control.php"
        try:
            async with self._session.get(
                url,
                params={"linkbutton": "tuer"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                body = await response.json(content_type=None)
        except aiohttp.ClientConnectionError as err:
            raise CannotConnectError(f"Cannot connect to {url}: {err}") from err
        except (TimeoutError, aiohttp.ClientError) as err:
            raise KochAgApiError(f"Door-open request to {url} failed: {err}") from err

        _LOGGER.debug("Door-open response: %s", body)
        data = body.get("data", {})
        if not data.get("success"):
            detail = data.get("detail", "unknown error")
            raise KochAgApiError(f"Door-open command rejected: {detail}")
