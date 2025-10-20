"""Exceptions for Barco Pulse integration."""

from __future__ import annotations


class BarcoError(Exception):
    """Base exception for Barco Pulse."""


class BarcoConnectionError(BarcoError):
    """Connection error."""


class BarcoAuthError(BarcoError):
    """Authentication error."""


class BarcoApiError(BarcoError):
    """API error."""

    def __init__(self, code: int, message: str) -> None:
        """Initialize with JSON-RPC error code and message."""
        self.code = code
        self.message = message
        super().__init__(f"API Error {code}: {message}")


class BarcoStateError(BarcoError):
    """State-dependent property error."""
