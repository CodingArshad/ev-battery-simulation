"""Controller module — PID feedback controller with duty-cycle clamping."""


class Controller:
    """PID feedback controller for battery thermal pre-conditioning.

    Computes a duty cycle in [0.0, 1.0] based on the error between the
    setpoint and the current battery temperature.  Includes a hard safety
    cutoff that forces the duty cycle to 0.0 when the battery exceeds 115°F.
    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        setpoint: float = 104.0,
        max_power: float = 7000.0,
    ) -> None:
        """Create a Controller instance.

        Args:
            kp: Proportional gain.
            ki: Integral gain.
            kd: Derivative gain.
            setpoint: Target temperature in °F (default 104°F).
            max_power: Maximum heater power in watts (default 7000W).
        """
        self.kp: float = float(kp)
        self.ki: float = float(ki)
        self.kd: float = float(kd)
        self.setpoint: float = float(setpoint)
        self.max_power: float = float(max_power)

        self.integral: float = 0.0
        self.prev_error: float = 0.0

    def compute(self, current_temp: float, dt: float) -> float:
        """Compute duty cycle based on current temperature.

        Args:
            current_temp: Current battery temperature in °F.
            dt: Time step in seconds.

        Returns:
            Duty cycle clamped to [0.0, 1.0].  Returns 0.0 if
            current_temp exceeds 115°F (safety cutoff).

        Raises:
            ValueError: If dt is not positive.
        """
        if dt <= 0:
            raise ValueError(f"dt must be positive, got {dt}")

        # Safety cutoff — immediately return 0 if battery is too hot
        if current_temp > 115.0:
            return 0.0

        error = self.setpoint - current_temp

        # Integral accumulation
        self.integral += error * dt

        # Derivative calculation
        derivative = (error - self.prev_error) / dt

        # PID output (raw)
        raw_output = self.kp * error + self.ki * self.integral + self.kd * derivative

        # Clamp duty cycle to [0.0, 1.0]
        duty_cycle = max(0.0, min(1.0, raw_output))

        # Store error for next derivative calculation
        self.prev_error = error

        return duty_cycle

    def reset(self) -> None:
        """Reset integral accumulator and previous error to zero."""
        self.integral = 0.0
        self.prev_error = 0.0
