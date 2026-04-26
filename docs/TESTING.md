# Testing Strategy — EV Battery Thermal GNC & State Estimation Suite

## Overview

The test suite uses **pytest** with 8 unit tests covering controller behavior, physics correctness, simulation integration, and safety cutoff. Tests are in `test_simulation.py` at the project root.

## Running Tests

```bash
# Run all tests with verbose output
pytest test_simulation.py -v

# Run a specific test
pytest test_simulation.py::test_simulation_reaches_setpoint -v

# Run with short summary
pytest test_simulation.py
```

## Test Inventory

### Controller Clamping Tests

| Test | What It Validates | Requirement |
|---|---|---|
| `test_duty_cycle_clamp_positive_error` | Large positive error (cold battery at -50°F) produces duty cycle in [0.0, 1.0] | Req 8.1 |
| `test_duty_cycle_clamp_negative_error` | Large negative error (hot battery at 114°F) produces duty cycle in [0.0, 1.0] | Req 8.2 |
| `test_duty_cycle_zero_at_setpoint` | Fresh controller at exactly 104°F returns duty cycle = 0.0 | Req 8.3 |

These tests verify the controller never produces values outside the valid range, regardless of input extremes.

### Physics Tests

| Test | What It Validates | Requirement |
|---|---|---|
| `test_heat_loss_zero_at_equilibrium` | `heat_loss()` returns exactly 0.0 when battery temp equals ambient temp | Req 2.4 |

This confirms Newton's Law of Cooling behaves correctly at the boundary condition.

### Full Simulation Integration Tests

| Test | What It Validates | Requirement |
|---|---|---|
| `test_simulation_reaches_setpoint` | Final temperature within 2°F of 104°F after 600s | Req 8.4, 6.2 |
| `test_simulation_no_overshoot_beyond_109` | Maximum temperature across all 601 data points ≤ 109°F | Req 8.5, 6.1 |
| `test_simulation_settles_within_500s` | All temperatures at t ≥ 500s are within 2°F of 104°F | Req 6.2 |

These are end-to-end tests that run the full simulation with default parameters and check the results against the stability requirements.

### Safety Cutoff Tests

| Test | What It Validates | Requirement |
|---|---|---|
| `test_safety_cutoff_above_115` | Controller returns 0.0 when battery exceeds 115°F | Req 6.3 |

## Test Configuration

### Default Simulation Parameters (used by all integration tests)

```python
Battery(temperature=32.0, thermal_mass=5000.0)
Environment(ambient_temp=32.0, heat_transfer_coeff=50.0)
Controller(kp=0.013, ki=0.0002, kd=0.06)
SimulationEngine(duration=600.0, dt=1.0)
```

### Matplotlib Backend

The test file does not import Matplotlib — it only tests the simulation logic and controller behavior. No GUI backend is needed.

## Requirements Traceability Matrix

| Requirement | Test(s) |
|---|---|
| 2.4 — Heat loss zero at equilibrium | `test_heat_loss_zero_at_equilibrium` |
| 6.2 — Settling within 500s | `test_simulation_settles_within_500s`, `test_simulation_reaches_setpoint` |
| 6.3 — Safety cutoff above 115°F | `test_safety_cutoff_above_115` |
| 8.1 — Duty cycle clamped (positive error) | `test_duty_cycle_clamp_positive_error` |
| 8.2 — Duty cycle clamped (negative error) | `test_duty_cycle_clamp_negative_error` |
| 8.3 — Duty cycle zero at setpoint | `test_duty_cycle_zero_at_setpoint` |
| 8.4 — Simulation reaches setpoint | `test_simulation_reaches_setpoint` |
| 8.5 — No overshoot beyond 109°F | `test_simulation_no_overshoot_beyond_109` |

## Extending the Tests

### Adding a New Unit Test

```python
def test_safety_cutoff_above_115():
    """Controller returns 0.0 when battery exceeds 115°F."""
    ctrl = Controller(kp=0.013, ki=0.0002, kd=0.06)
    assert ctrl.compute(120.0, 1.0) == 0.0
```

### Adding a Property-Based Test (with Hypothesis)

The design document defines 8 correctness properties suitable for property-based testing. To add them:

```bash
pip install hypothesis
```

```python
from hypothesis import given, settings, strategies as st

@settings(max_examples=100)
@given(temp=st.floats(min_value=-100, max_value=300, allow_nan=False, allow_infinity=False))
def test_prop_battery_temp_roundtrip(temp):
    """Property 1: Temperature set via setter equals value from getter."""
    b = Battery(temperature=0.0, thermal_mass=1000.0)
    b.temperature = temp
    assert b.temperature == temp
```

### Running in CI/CD

The tests require no special environment. A minimal CI configuration:

```yaml
# GitHub Actions example
- name: Install dependencies
  run: pip install matplotlib pytest

- name: Run tests
  run: pytest test_simulation.py -v
```

The `Agg` backend is set in the test file itself, so no `MPLBACKEND` environment variable is needed.
