"""Unit tests for KochAgCoordinator (coordinator.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.rene_koch_ag.api import CannotConnectError, KochAgApiError
from custom_components.rene_koch_ag.coordinator import KochAgCoordinator


@pytest.fixture
def mock_api() -> MagicMock:
    api = MagicMock()
    api.async_check_reachable = AsyncMock()
    return api


async def test_update_data_success(hass, mock_api) -> None:
    coordinator = KochAgCoordinator(hass, mock_api)
    result = await coordinator._async_update_data()

    mock_api.async_check_reachable.assert_called_once()
    assert result == {}


async def test_update_data_cannot_connect(hass, mock_api) -> None:
    mock_api.async_check_reachable.side_effect = CannotConnectError("refused")

    coordinator = KochAgCoordinator(hass, mock_api)
    with pytest.raises(UpdateFailed, match="unreachable"):
        await coordinator._async_update_data()


async def test_update_data_api_error(hass, mock_api) -> None:
    mock_api.async_check_reachable.side_effect = KochAgApiError("timeout")

    coordinator = KochAgCoordinator(hass, mock_api)
    with pytest.raises(UpdateFailed, match="Error communicating"):
        await coordinator._async_update_data()
