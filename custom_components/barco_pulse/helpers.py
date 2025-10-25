"""Helper functions for Barco Pulse integration."""

# ruff: noqa: BLE001, UP047

from __future__ import annotations

import asyncio
import logging
import time
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar
from weakref import WeakValueDictionary

from homeassistant.exceptions import HomeAssistantError

from .exceptions import BarcoConnectionError, BarcoStateError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

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
    coordinator: Any,
    operation_name: str = "operation",
) -> None:
    """
    Request coordinator refresh with throttling to prevent overlapping updates.

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

    try:
        # Wait a small delay to allow multiple rapid commands to batch
        await asyncio.sleep(0.1)
        await coordinator.async_request_refresh()
    except Exception:
        _LOGGER.warning("Failed to refresh after %s", operation_name)
