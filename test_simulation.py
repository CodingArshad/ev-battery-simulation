"""Unit tests for the EV Battery Thermal GNC simulation suite.

Covers controller clamping, setpoint behavior, simulation integration,
and heat loss equilibrium.
"""

import pytest

from battery import Battery
from controller import Controller
from environment import Environment
from simulation import SimulationEngine


# ---------------------------------------------------------------------------
# Helper: build default simulation components
# ---------------------------------------------------------------------------

def _make_default_engine():
    """Return (battery, environment, controller, engine) with default params."""
    battery = Battery(temperature=32.0, thermal_mass=5000.0)
    environment = Environment(ambient_temp=32.0, heat_transfer_coeff=50.0)
    controller = Controller(kp=0.013, ki=0.0002, kd=0.06)
    engine = SimulationEngine(
        battery=battery,
        environment=environment,
        controller=controller,
        duration=600.0,
        dt=1.0,
    )
    return battery, environment, controller, engine


def _run_default_simulation():
    """Run the default simulation and return the results dict."""
    _, _, _, engine = _make_default_engine()
    return engine.run()


# ===========================================================================
# Controller clamping & setpoint tests  (Req 8.1, 8.2, 8.3)
# ===========================================================================

def test_duty_cycle_clamp_positive_error():
    """Large positive error (cold battery) -> duty cycle clamped <= 1.0.

    Validates: Requirement 8.1
    """
    controller = Controller(kp=1.2, ki=0.01, kd=0.5)
    duty = controller.compute(current_temp=-50.0, dt=1.0)
    assert duty <= 1.0
    assert duty >= 0.0


def test_duty_cycle_clamp_negative_error():
    """Large negative error (hot battery, but <= 115 F) -> duty cycle clamped >= 0.0.

    Validates: Requirement 8.2
    """
    controller = Controller(kp=1.2, ki=0.01, kd=0.5)
    duty = controller.compute(current_temp=114.0, dt=1.0)
    assert duty >= 0.0
    assert duty <= 1.0


def test_duty_cycle_zero_at_setpoint():
    """At setpoint with zero integral -> duty cycle is 0.0.

    Validates: Requirement 8.3
    """
    controller = Controller(kp=1.2, ki=0.01, kd=0.5)
    assert controller.integral == 0.0
    assert controller.prev_error == 0.0
    duty = controller.compute(current_temp=104.0, dt=1.0)
    assert duty == 0.0


# ===========================================================================
# Heat loss at equilibrium  (Req 2.4)
# ===========================================================================

def test_heat_loss_zero_at_equilibrium():
    """heat_loss returns 0 when battery temp equals ambient temp.

    Validates: Requirement 2.4
    """
    env = Environment(ambient_temp=32.0, heat_transfer_coeff=50.0)
    loss = env.heat_loss(battery_temp=32.0)
    assert loss == 0.0


# ===========================================================================
# Full-simulation integration tests  (Req 8.4, 8.5, 6.1, 6.2)
# ===========================================================================

def test_simulation_reaches_setpoint():
    """Full simulation reaches within 2 F of 104 F by the end.

    Validates: Requirements 8.4, 6.2
    """
    results = _run_default_simulation()
    final_temp = results["temperature"][-1]
    assert abs(final_temp - 104.0) <= 2.0, (
        f"Final temperature {final_temp:.2f} F is not within 2 F of setpoint 104 F"
    )


def test_simulation_no_overshoot_beyond_109():
    """Full simulation max temperature <= 109 F.

    Validates: Requirements 8.5, 6.1
    """
    results = _run_default_simulation()
    max_temp = max(results["temperature"])
    assert max_temp <= 109.0, (
        f"Max temperature {max_temp:.2f} F exceeds 109 F overshoot limit"
    )


def test_simulation_settles_within_500s():
    """Temperature within 2 F of setpoint by t = 500 s and stays there.

    Validates: Requirement 6.2
    """
    results = _run_default_simulation()
    time_list = results["time"]
    temp_list = results["temperature"]

    for i, t in enumerate(time_list):
        if t >= 500.0:
            settled_temps = temp_list[i:]
            for temp in settled_temps:
                assert abs(temp - 104.0) <= 2.0, (
                    f"Temperature {temp:.2f} F at t>=500s is not within 2 F of 104 F"
                )
            return

    pytest.fail("Simulation did not reach t = 500 s")


# ===========================================================================
# Safety cutoff  (Req 6.3)
# ===========================================================================

def test_safety_cutoff_above_115():
    """Controller returns 0.0 when battery exceeds 115 F.

    Validates: Requirement 6.3
    """
    controller = Controller(kp=0.013, ki=0.0002, kd=0.06)
    assert controller.compute(120.0, 1.0) == 0.0
    assert controller.compute(115.01, 1.0) == 0.0
