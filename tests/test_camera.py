"""Unit tests for _async_extract_jpeg (camera.py)."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.rene_koch_ag.camera import _async_extract_jpeg

# A minimal valid JPEG: SOI (FF D8) ... EOI (FF D9)
MINIMAL_JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"\x00" * 10 + b"\xff\xd9"


def _make_response(chunks: list[bytes]) -> MagicMock:
    """Build a mock aiohttp.ClientResponse whose content streams the given chunks."""
    response = MagicMock()

    async def _iter_chunked(_size: int):
        for chunk in chunks:
            yield chunk

    response.content.iter_chunked = _iter_chunked
    return response


async def test_extracts_jpeg_from_single_chunk() -> None:
    response = _make_response([MINIMAL_JPEG])
    result = await _async_extract_jpeg(response)
    assert result is not None
    assert result.startswith(b"\xff\xd8")
    assert result.endswith(b"\xff\xd9")


async def test_extracts_jpeg_from_multiple_chunks() -> None:
    half = len(MINIMAL_JPEG) // 2
    response = _make_response([MINIMAL_JPEG[:half], MINIMAL_JPEG[half:]])
    result = await _async_extract_jpeg(response)
    assert result == MINIMAL_JPEG


async def test_jpeg_embedded_in_multipart_boundary() -> None:
    """JPEG should be found even when surrounded by MJPEG boundary noise."""
    noise_before = b"--boundary\r\nContent-Type: image/jpeg\r\n\r\n"
    noise_after = b"\r\n--boundary--\r\n"
    data = noise_before + MINIMAL_JPEG + noise_after
    response = _make_response([data])
    result = await _async_extract_jpeg(response)
    assert result == MINIMAL_JPEG


async def test_returns_none_when_no_jpeg_marker() -> None:
    response = _make_response([b"no jpeg here at all"])
    result = await _async_extract_jpeg(response)
    assert result is None


async def test_returns_none_when_only_soi_no_eoi() -> None:
    """Start-of-image marker present but stream ends before end-of-image."""
    response = _make_response([b"\xff\xd8\xff\xe0some data without EOI"])
    result = await _async_extract_jpeg(response)
    assert result is None


async def test_returns_none_when_stream_exceeds_max_bytes() -> None:
    """Bail out and return None when too much data arrives with no frame."""
    # 1 MB + 1 byte of garbage with no JPEG markers
    large_chunk = b"\x00" * (1_000_000 + 1)
    response = _make_response([large_chunk])
    result = await _async_extract_jpeg(response)
    assert result is None


async def test_empty_stream_returns_none() -> None:
    response = _make_response([])
    result = await _async_extract_jpeg(response)
    assert result is None
