"""Simulation engine module — orchestrates the time-stepping loop."""

import math

from battery import Battery
from controller import Controller
from environment import Environment


class SimulationEngine:
    """Orchestrates the thermal simulation using Euler integration.

    Each time step:
    1. Query the controller for a duty cycle based on current battery temperature.
    2. Compute net heat input: duty_cycle * max_power - heat_loss.
    3. Compute dT/dt from the battery model.
    4. Update battery temperature via forward Euler: T_new = T_old + dT/dt * dt.
    5. Record the state.
    """

    def __init__(
        self,
        battery: Battery,
        environment: Environment,
        controller: Controller,
        duration: float = 600.0,
        dt: float = 1.0,
    ) -> None:
        """Create a SimulationEngine instance.

        Args:
            battery: Battery instance.
            environment: Environment instance.
            controller: Controller instance.
            duration: Total simulation time in seconds (default 600).
            dt: Time step in seconds (default 1.0).

        Raises:
            ValueError: If duration <= 0, dt <= 0, or dt > duration.
        """
        if duration <= 0:
            raise ValueError(f"duration must be positive, got {duration}")
        if dt <= 0:
            raise ValueError(f"dt must be positive, got {dt}")
        if dt > duration:
            raise ValueError(
                f"dt ({dt}) must not exceed duration ({duration})"
            )

        self._battery = battery
        self._environment = environment
        self._controller = controller
        self._duration = float(duration)
        self._dt = float(dt)

    def run(self) -> dict:
        """Execute the simulation loop.

        Returns:
            Dictionary with keys:
                'time': list[float] — time stamps in seconds
                'temperature': list[float] — battery temp at each step
                'ambient': list[float] — ambient temp at each step
                'duty_cycle': list[float] — duty cycle at each step
        """
        time_list: list[float] = []
        temperature_list: list[float] = []
        ambient_list: list[float] = []
        duty_cycle_list: list[float] = []

        # Record initial state at t=0
        time_list.append(0.0)
        temperature_list.append(self._battery.temperature)
        ambient_list.append(self._environment.ambient_temp)
        duty_cycle_list.append(0.0)

        # Number of integration steps
        num_steps = math.floor(self._duration / self._dt)

        for i in range(num_steps):
            t = (i + 1) * self._dt

            # 1. Query controller for duty cycle
            duty_cycle = self._controller.compute(
                self._battery.temperature, self._dt
            )

            # 2. Compute net heat: heater power minus heat loss
            heater_power = duty_cycle * self._controller.max_power
            heat_loss = self._environment.heat_loss(self._battery.temperature)
            net_heat = heater_power - heat_loss

            # 3. Compute rate of temperature change
            rate = self._battery.dT_dt(net_heat)

            # 4. Euler integration: T_new = T_old + dT/dt * dt
            self._battery.temperature = (
                self._battery.temperature + rate * self._dt
            )

            # 5. Record state
            time_list.append(t)
            temperature_list.append(self._battery.temperature)
            ambient_list.append(self._environment.ambient_temp)
            duty_cycle_list.append(duty_cycle)

        return {
            "time": time_list,
            "temperature": temperature_list,
            "ambient": ambient_list,
            "duty_cycle": duty_cycle_list,
        }
