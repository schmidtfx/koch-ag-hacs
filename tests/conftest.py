"""Shared pytest fixtures for the Rene Koch AG integration tests."""

from __future__ import annotations

import os
import sys

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def remove_editable_path_hooks():
    """Remove synthetic editable-install entries from sys.path.

    The editable install adds path-hook descriptors (e.g.
    ``__editable__.*.finder.__path_hook__``) to sys.path that HA's custom
    component loader tries to iterate as real directories, causing a
    FileNotFoundError.  Strip them for the duration of each test.
    """
    bad = [p for p in sys.path if not os.path.exists(p)]
    for p in bad:
        sys.path.remove(p)
    yield
    for p in bad:
        sys.path.append(p)
