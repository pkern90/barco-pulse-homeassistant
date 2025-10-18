"""Switch platform for barco_pulse."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .entity import BarcoPulseEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BarcoPulseDataUpdateCoordinator
    from .data import BarcoPulseConfigEntry

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="power",
        name="Power",
        icon="mdi:power",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: BarcoPulseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        BarcoPulseSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class BarcoPulseSwitch(BarcoPulseEntity, SwitchEntity):
    """barco_pulse switch class."""

    def __init__(
        self,
        coordinator: BarcoPulseDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        # Update unique_id to include entity description key
        self._attr_unique_id = f"{self._attr_unique_id}_{entity_description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        # Return None if no data available
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("power", {}).get("is_on", False)

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        await self.coordinator.config_entry.runtime_data.client.power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self.coordinator.config_entry.runtime_data.client.power_off()
        await self.coordinator.async_request_refresh()
