"""Helper functions for Barco Pulse integration."""

# ruff: noqa: UP047

from __future__ import annotations

import logging
import time
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar
from weakref import WeakValueDictionary

from homeassistant.exceptions import HomeAssistantError

from .const import PRESET_MAX_NUMBER
from .exceptions import BarcoConnectionError, BarcoStateError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from .coordinator import BarcoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")

# Track last refresh time per coordinator using weak references
# This prevents memory leaks when coordinators are deleted
_LAST_REFRESH_TIMES: dict[int, float] = {}
_COORDINATOR_REFS: WeakValueDictionary[int, Any] = WeakValueDictionary()
_REFRESH_COOLDOWN = 0.5  # Minimum seconds between refresh requests
_CLEANUP_THRESHOLD = 100  # Clean up stale entries when dict grows beyond this


def handle_api_errors(
    func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    """
    Handle API errors for entity commands.

    Catches BarcoStateError, BarcoConnectionError, and generic exceptions,
    logging appropriately and raising HomeAssistantError to the user.
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except BarcoStateError as err:
            _LOGGER.warning(
                "%s failed - projector not ready: %s",
                func.__name__,
                err,
            )
            msg = f"Projector not ready: {err}"
            raise HomeAssistantError(msg) from err
        except BarcoConnectionError as err:
            _LOGGER.exception(
                "Connection error during %s",
                func.__name__,
            )
            msg = f"Connection error: {err}"
            raise HomeAssistantError(msg) from err
        except Exception as err:
            _LOGGER.exception(
                "Unexpected error during %s",
                func.__name__,
            )
            msg = f"{func.__name__} failed: {err}"
            raise HomeAssistantError(msg) from err

    return wrapper


async def safe_refresh(
    coordinator: BarcoDataUpdateCoordinator,
    operation_name: str = "operation",
) -> None:
    """
    Request coordinator refresh with throttling to prevent overlapping updates.

    This function schedules a background refresh without blocking the caller,
    preventing Home Assistant from becoming unresponsive during power operations.

    Args:
        coordinator: DataUpdateCoordinator instance
        operation_name: Name of operation for logging (optional)

    """
    coordinator_id = id(coordinator)
    current_time = time.time()

    # Store weak reference to coordinator to enable cleanup
    if coordinator_id not in _COORDINATOR_REFS:
        _COORDINATOR_REFS[coordinator_id] = coordinator

    # Check if we're in cooldown period
    last_refresh = _LAST_REFRESH_TIMES.get(coordinator_id, 0)
    time_since_last = current_time - last_refresh

    if time_since_last < _REFRESH_COOLDOWN:
        _LOGGER.debug(
            "Skipping refresh after %s (cooldown: %.2fs remaining)",
            operation_name,
            _REFRESH_COOLDOWN - time_since_last,
        )
        return

    # Update last refresh time
    _LAST_REFRESH_TIMES[coordinator_id] = current_time

    # Clean up stale entries (coordinators that no longer exist)
    # This runs periodically to prevent memory leaks
    if len(_LAST_REFRESH_TIMES) > _CLEANUP_THRESHOLD:
        stale_ids = [cid for cid in _LAST_REFRESH_TIMES if cid not in _COORDINATOR_REFS]
        for cid in stale_ids:
            _LAST_REFRESH_TIMES.pop(cid, None)
        if stale_ids:
            _LOGGER.debug("Cleaned up %d stale refresh entries", len(stale_ids))

    # Schedule refresh as background task - don't await to prevent blocking
    # The coordinator will handle any errors internally
    _LOGGER.debug("Scheduling background refresh after %s", operation_name)
    coordinator.hass.async_create_task(
        coordinator.async_request_refresh(),
        f"barco_pulse_refresh_{operation_name}",
    )


# Preset handling utilities

# Expected number of parts when splitting "Preset N" format
PRESET_DISPLAY_PARTS_COUNT = 2


def format_preset_display(preset_num: int) -> str:
    """
    Format preset number for display in UI (e.g., 5 -> 'Preset 5').

    Args:
        preset_num: Preset number (0-29)

    Returns:
        Formatted preset string for display

    """
    return f"Preset {preset_num}"


def parse_preset_display(preset_str: str) -> int | None:
    """
    Parse preset display string to number (e.g., 'Preset 5' -> 5).

    Args:
        preset_str: Preset string from UI

    Returns:
        Preset number, or None if invalid format

    """
    try:
        parts = preset_str.split()
        if len(parts) == PRESET_DISPLAY_PARTS_COUNT and parts[0] == "Preset":
            preset_num = int(parts[1])
            if 0 <= preset_num <= PRESET_MAX_NUMBER:
                return preset_num
    except (ValueError, IndexError):
        # Invalid format or number; returning None is expected for parse failures
        pass
    return None


def parse_preset_command(command: str) -> int | None:
    """
    Parse preset command string to number (e.g., 'preset_5' -> 5).

    Args:
        command: Command string from remote/automation

    Returns:
        Preset number, or None if invalid format

    """
    if not command.startswith("preset_"):
        return None

    try:
        preset_num = int(command[7:])
        if 0 <= preset_num <= PRESET_MAX_NUMBER:
            return preset_num
    except (ValueError, IndexError):
        # Invalid format or number; returning None is expected for parse failures
        pass
    return None
