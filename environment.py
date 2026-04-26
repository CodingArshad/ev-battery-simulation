"""Environment module — models heat loss using Newton's Law of Cooling."""


class Environment:
    """Models heat loss from the battery to the surroundings.

    Uses Newton's Law of Cooling: heat_loss = h·A × (T_battery - T_ambient),
    where h·A is the heat transfer coefficient in W/°F.
    """

    def __init__(self, ambient_temp: float, heat_transfer_coeff: float) -> None:
        """Create an Environment instance.

        Args:
            ambient_temp: Ambient temperature in °F.
            heat_transfer_coeff: h·A product in W/°F.

        Raises:
            ValueError: If heat_transfer_coeff is negative.
        """
        if heat_transfer_coeff < 0:
            raise ValueError(
                f"heat_transfer_coeff must be non-negative, got {heat_transfer_coeff}"
            )

        self._ambient_temp: float = float(ambient_temp)
        self._heat_transfer_coeff: float = float(heat_transfer_coeff)

    @property
    def ambient_temp(self) -> float:
        """Ambient temperature in °F."""
        return self._ambient_temp

    def heat_loss(self, battery_temp: float) -> float:
        """Compute heat loss from battery to environment.

        Args:
            battery_temp: Current battery temperature in °F.

        Returns:
            Heat loss in watts. Positive means heat leaving the battery.
            Computed as heat_transfer_coeff × (battery_temp - ambient_temp).
        """
        return self._heat_transfer_coeff * (battery_temp - self._ambient_temp)
