"""Camera entity for the Koch AG SIP Gateway MJPEG video stream."""

from __future__ import annotations

import aiohttp
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_VIDEO_PORT, DEFAULT_VIDEO_PORT, DOMAIN

MJPEG_PATH = "/video.mjpeg"

# Safety cap: stop reading the stream after this many bytes without a full frame.
_MAX_READ_BYTES = 1_000_000


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Koch AG camera from a config entry."""
    async_add_entities([KochAgCamera(entry)])


class KochAgCamera(Camera):
    """MJPEG camera that proxies the Koch AG SIP Gateway video stream."""

    _attr_has_entity_name = True
    _attr_translation_key = "video"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__()
        host = entry.data[CONF_HOST]
        video_port = entry.data.get(CONF_VIDEO_PORT, DEFAULT_VIDEO_PORT)

        self._mjpeg_url = f"http://{host}:{video_port}{MJPEG_PATH}"
        self._attr_unique_id = f"{entry.entry_id}_camera"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Rene Koch AG",
            model="SIP Gateway",
        )

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a single JPEG frame from the MJPEG stream."""
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                self._mjpeg_url, timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")
                if "multipart" in content_type or "mjpeg" in content_type:
                    return await _async_extract_jpeg(response)
                # If the endpoint returns a plain JPEG (snapshot), read it directly.
                return await response.read()
        except (aiohttp.ClientError, TimeoutError):
            return None


async def _async_extract_jpeg(response: aiohttp.ClientResponse) -> bytes | None:
    """Extract the first complete JPEG frame from an MJPEG multipart stream.

    MJPEG streams embed JPEG frames delimited by multipart boundaries.
    JPEG frames always start with 0xFF 0xD8 (SOI) and end with 0xFF 0xD9 (EOI).
    """
    data = b""
    async for chunk in response.content.iter_chunked(4096):
        data += chunk
        start = data.find(b"\xff\xd8")
        if start >= 0:
            end = data.find(b"\xff\xd9", start)
            if end >= 0:
                return data[start : end + 2]
        if len(data) > _MAX_READ_BYTES:
            break
    return None
