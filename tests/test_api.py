"""Unit tests for KochAgApi (api.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from custom_components.rene_koch_ag.api import (
    CannotConnectError,
    KochAgApi,
    KochAgApiError,
)


def _make_api(
    session: MagicMock, host: str = "192.168.1.1", port: int = 80
) -> KochAgApi:
    return KochAgApi(session, host, port)


def _mock_context(return_value: MagicMock | None = None) -> MagicMock:
    """Return an async context manager mock."""
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=return_value or MagicMock())
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


# ---------------------------------------------------------------------------
# async_check_reachable
# ---------------------------------------------------------------------------


async def test_check_reachable_success() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.head.return_value = _mock_context()

    api = _make_api(session)
    await api.async_check_reachable()  # should not raise

    session.head.assert_called_once()
    url = session.head.call_args[0][0]
    assert url == "http://192.168.1.1:80/"


async def test_check_reachable_connection_error() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.head.side_effect = aiohttp.ClientConnectionError("refused")

    api = _make_api(session)
    with pytest.raises(CannotConnectError):
        await api.async_check_reachable()


async def test_check_reachable_timeout() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.head.side_effect = TimeoutError()

    api = _make_api(session)
    with pytest.raises(KochAgApiError):
        await api.async_check_reachable()


async def test_check_reachable_client_error() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.head.side_effect = aiohttp.ClientError("bad")

    api = _make_api(session)
    with pytest.raises(KochAgApiError):
        await api.async_check_reachable()


# ---------------------------------------------------------------------------
# async_open_door
# ---------------------------------------------------------------------------


def _open_door_response(success: bool, detail: str = "ok") -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    data: dict = {"success": success}
    if not success:
        data["detail"] = detail
    resp.json = AsyncMock(return_value={"data": data})
    return resp


async def test_open_door_success() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.get.return_value = _mock_context(_open_door_response(success=True))

    api = _make_api(session)
    await api.async_open_door()  # should not raise

    session.get.assert_called_once()
    call_kwargs = session.get.call_args
    assert "linkbutton" in call_kwargs[1]["params"]
    assert call_kwargs[1]["params"]["linkbutton"] == "tuer"


async def test_open_door_rejected_by_gateway() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.get.return_value = _mock_context(
        _open_door_response(success=False, detail="access denied")
    )

    api = _make_api(session)
    with pytest.raises(KochAgApiError, match="access denied"):
        await api.async_open_door()


async def test_open_door_connection_error() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.get.side_effect = aiohttp.ClientConnectionError("no route")

    api = _make_api(session)
    with pytest.raises(CannotConnectError):
        await api.async_open_door()


async def test_open_door_http_error() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    resp = MagicMock()
    resp.raise_for_status.side_effect = aiohttp.ClientResponseError(
        MagicMock(), MagicMock(), status=500
    )
    resp.json = AsyncMock()
    session.get.return_value = _mock_context(resp)

    api = _make_api(session)
    with pytest.raises(KochAgApiError):
        await api.async_open_door()


async def test_open_door_timeout() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.get.side_effect = TimeoutError()

    api = _make_api(session)
    with pytest.raises(KochAgApiError):
        await api.async_open_door()


async def test_api_base_url_uses_custom_port() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.head.return_value = _mock_context()

    api = _make_api(session, host="10.0.0.5", port=8080)
    await api.async_check_reachable()

    url = session.head.call_args[0][0]
    assert url == "http://10.0.0.5:8080/"
