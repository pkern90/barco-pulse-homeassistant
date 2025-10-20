"""Data models for Barco Pulse integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .api import BarcoDevice
    from .coordinator import BarcoDataUpdateCoordinator


@dataclass
class BarcoRuntimeData:
    """Runtime data for Barco Pulse integration."""

    client: BarcoDevice
    coordinator: BarcoDataUpdateCoordinator
