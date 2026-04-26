# Configuration Guide — EV Battery Thermal GNC & State Estimation Suite

## Overview

All simulation parameters can be adjusted in real time using the interactive dashboard:

```bash
python main.py
```

The default values are defined in `main.py`. You can also use the components programmatically by importing them directly.

## Default Configuration

```python
battery     = Battery(temperature=32.0, thermal_mass=5000.0)
environment = Environment(ambient_temp=32.0, heat_transfer_coeff=50.0)
controller  = Controller(kp=0.013, ki=0.0002, kd=0.06)
engine      = SimulationEngine(duration=600.0, dt=1.0)
```

Use the **interactive dashboard** to explore parameters in real time without editing code:

```bash
python main.py
```

## Parameter Groups

### Battery Parameters

| Parameter | Default | Range | Effect |
|---|---|---|---|
| `temperature` | 32.0 °F | Any numeric | Starting battery temperature. Lower values mean more heating needed. |
| `thermal_mass` | 5000.0 J/°F | > 0 | Higher values = slower temperature changes (heavier battery). |

**Scenarios:**
```python
# Mild winter day — battery at 40°F
Battery(temperature=40.0, thermal_mass=5000.0)

# Large battery pack (e.g., 100 kWh truck)
Battery(temperature=32.0, thermal_mass=15000.0)

# Small battery (e.g., PHEV)
Battery(temperature=32.0, thermal_mass=2000.0)
```

### Environment Parameters

| Parameter | Default | Range | Effect |
|---|---|---|---|
| `ambient_temp` | 32.0 °F | Any numeric | Outside air temperature. Affects heat loss rate. |
| `heat_transfer_coeff` | 50.0 W/°F | ≥ 0 | Higher = more heat loss (poor insulation or high wind). |

**Scenarios:**
```python
# Summer day — minimal heating needed
Environment(ambient_temp=85.0, heat_transfer_coeff=50.0)

# Arctic conditions
Environment(ambient_temp=-20.0, heat_transfer_coeff=70.0)

# Well-insulated battery (low heat loss)
Environment(ambient_temp=32.0, heat_transfer_coeff=20.0)

# Highway driving (high convection)
Environment(ambient_temp=32.0, heat_transfer_coeff=100.0)
```

### Controller Parameters

| Parameter | Default | Range | Effect |
|---|---|---|---|
| `kp` | 0.013 | ≥ 0 | Proportional gain. Higher = faster but more overshoot. |
| `ki` | 0.0002 | ≥ 0 | Integral gain. Higher = eliminates offset faster but risks oscillation. |
| `kd` | 0.06 | ≥ 0 | Derivative gain. Higher = smoother approach but slower. |
| `setpoint` | 104.0 °F | Any | Target temperature. |
| `max_power` | 7000.0 W | > 0 | Maximum heater output. |

**Tuning presets:**
```python
# Conservative (slow, no overshoot)
Controller(kp=0.008, ki=0.0001, kd=0.1)

# Aggressive (fast, some overshoot)
Controller(kp=0.03, ki=0.001, kd=0.02)

# Default (balanced)
Controller(kp=0.013, ki=0.0002, kd=0.06)
```

### Simulation Parameters

| Parameter | Default | Range | Effect |
|---|---|---|---|
| `duration` | 600.0 s | > 0 | Total simulation time. |
| `dt` | 1.0 s | > 0, ≤ duration | Time step. Smaller = more accurate but slower. |

**Scenarios:**
```python
# Quick test run
SimulationEngine(..., duration=120.0, dt=1.0)

# High-fidelity (fine time step)
SimulationEngine(..., duration=600.0, dt=0.1)

# Long observation (30 minutes)
SimulationEngine(..., duration=1800.0, dt=1.0)
```

## Validation Rules

The system enforces these constraints at construction time:

| Constraint | Error |
|---|---|
| `thermal_mass <= 0` | `ValueError` |
| `temperature` non-numeric | `TypeError` |
| `heat_transfer_coeff < 0` | `ValueError` |
| `duration <= 0` | `ValueError` |
| `dt <= 0` | `ValueError` |
| `dt > duration` | `ValueError` |

## Safety Limits

These are hardcoded in the controller and cannot be changed via parameters:

| Limit | Value | Behavior |
|---|---|---|
| Safety cutoff temperature | 115°F | Duty cycle forced to 0.0 |
| Duty cycle minimum | 0.0 | Heater cannot run in reverse |
| Duty cycle maximum | 1.0 | Heater cannot exceed max power |

## Creating Custom Scenarios

Here's a complete example of a custom configuration:

```python
from battery import Battery
from environment import Environment
from controller import Controller
from simulation import SimulationEngine

# Scenario: Summer pre-conditioning for a large truck battery
battery = Battery(temperature=85.0, thermal_mass=12000.0)
environment = Environment(ambient_temp=95.0, heat_transfer_coeff=40.0)
controller = Controller(kp=0.2, ki=0.001, kd=6.0, setpoint=104.0)
engine = SimulationEngine(
    battery=battery,
    environment=environment,
    controller=controller,
    duration=900.0,
    dt=1.0,
)

results = engine.run()
print(f"Final temp: {results['temperature'][-1]:.1f} F")
print(f"Max temp: {max(results['temperature']):.1f} F")
```
