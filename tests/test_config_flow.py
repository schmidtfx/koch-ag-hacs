"""Unit tests for KochAgConfigFlow (config_flow.py)."""

from __future__ import annotations

import pytest
from custom_components.rene_koch_ag.const import (
    CONF_VIDEO_PORT,
    DEFAULT_API_PORT,
    DEFAULT_VIDEO_PORT,
    DOMAIN,
)
from homeassistant import data_entry_flow
from homeassistant.const import CONF_HOST, CONF_PORT

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_form_is_shown_initially(hass) -> None:
    """The user step should display the form when no input is provided."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_creates_entry_with_defaults(hass) -> None:
    """Submitting a host should create a config entry with default ports."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: DEFAULT_API_PORT,
            CONF_VIDEO_PORT: DEFAULT_VIDEO_PORT,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == "192.168.1.100"
    assert result["data"][CONF_PORT] == DEFAULT_API_PORT
    assert result["data"][CONF_VIDEO_PORT] == DEFAULT_VIDEO_PORT


async def test_creates_entry_with_custom_ports(hass) -> None:
    """Submitting custom ports should persist them in the entry data."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "10.0.0.5",
            CONF_PORT: 8080,
            CONF_VIDEO_PORT: 9000,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_PORT] == 8080
    assert result["data"][CONF_VIDEO_PORT] == 9000


async def test_duplicate_host_port_aborted(hass) -> None:
    """A second setup with the same host:port should be aborted."""
    user_input = {
        CONF_HOST: "192.168.1.1",
        CONF_PORT: DEFAULT_API_PORT,
        CONF_VIDEO_PORT: DEFAULT_VIDEO_PORT,
    }

    # First setup succeeds.
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # Second setup with the same host + port should abort.
    result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"], user_input
    )

    assert result2["type"] == data_entry_flow.FlowResultType.ABORT
    assert result2["reason"] == "already_configured"
