"""Helper functions for Barco Pulse integration."""

# ruff: noqa: BLE001, UP047

from __future__ import annotations

import logging
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

from homeassistant.exceptions import HomeAssistantError

from .exceptions import BarcoConnectionError, BarcoStateError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_LOGGER = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


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
    Request coordinator refresh without failing if refresh fails.

    Args:
        coordinator: DataUpdateCoordinator instance
        operation_name: Name of operation for logging (optional)

    """
    try:
        await coordinator.async_request_refresh()
    except Exception:
        _LOGGER.warning("Failed to refresh after %s", operation_name)
