"""Custom types for barco_pulse."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import BarcoPulseApiClient
    from .coordinator import BarcoPulseDataUpdateCoordinator


type BarcoPulseConfigEntry = ConfigEntry[BarcoPulseData]


@dataclass
class BarcoPulseData:
    """Data for the Barco Pulse integration."""

    client: BarcoPulseApiClient
    coordinator: BarcoPulseDataUpdateCoordinator
    integration: Integration
