"""Battery module — models the EV battery as a lumped thermal mass."""


class Battery:
    """EV battery modeled as a single thermal node.

    Stores a temperature state variable (°F) and a thermal mass (J/°F).
    Provides the rate of temperature change given a net heat input.
    """

    def __init__(self, temperature: float, thermal_mass: float) -> None:
        """Create a Battery instance.

        Args:
            temperature: Initial battery temperature in °F.
            thermal_mass: Thermal mass in J/°F (mass × specific heat capacity).

        Raises:
            TypeError: If temperature is non-numeric.
            ValueError: If thermal_mass is not positive.
        """
        if not isinstance(temperature, (int, float)):
            raise TypeError(
                f"temperature must be numeric, got {type(temperature).__name__}"
            )
        if not isinstance(thermal_mass, (int, float)):
            raise TypeError(
                f"thermal_mass must be numeric, got {type(thermal_mass).__name__}"
            )
        if thermal_mass <= 0:
            raise ValueError(
                f"thermal_mass must be positive, got {thermal_mass}"
            )

        self._temperature: float = float(temperature)
        self._thermal_mass: float = float(thermal_mass)

    @property
    def temperature(self) -> float:
        """Current battery temperature in °F."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set battery temperature in °F.

        Args:
            value: New temperature in °F.

        Raises:
            TypeError: If value is non-numeric.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"temperature must be numeric, got {type(value).__name__}"
            )
        self._temperature = float(value)

    def dT_dt(self, net_heat: float) -> float:
        """Compute rate of temperature change.

        Args:
            net_heat: Net heat input in watts (heater power minus heat loss).

        Returns:
            Rate of temperature change in °F/s, computed as net_heat / thermal_mass.
        """
        return net_heat / self._thermal_mass
