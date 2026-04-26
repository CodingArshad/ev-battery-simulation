# User Guide — EV Battery Thermal GNC & State Estimation Suite

## What This Project Does

This simulation models how an electric vehicle pre-heats its battery pack while navigating to a Supercharger. Cold batteries charge slowly, so EVs run a heater to bring the pack to an optimal 104°F (40°C) before arrival. The suite simulates that process using:

- A **physics-based thermal model** (Newton's Law of Cooling)
- A **PID feedback controller** regulating a 7kW heater
- **Euler numerical integration** stepping the system forward in time
- A **Matplotlib dashboard** visualizing the results

## Prerequisites

- Python 3.8 or later
- pip (Python package manager)

## Installation

```bash
# Clone or download the project, then install dependencies:
pip install matplotlib numpy

# Optional — for running property-based tests:
pip install pytest hypothesis
```

No other setup is required. The project has no database, no config files, and no build step.

## Quick Start

```bash
python main.py
```

This opens an interactive window with two charts and 6 sliders. Drag any slider to change PID gains or temperatures and the simulation re-runs instantly.

### Understanding the Dashboard

| What You See | What It Means |
|---|---|
| Red line climbing from 32°F toward 104°F | Battery heating up under PID control |
| Red line flattening near 104°F | Controller has reached and is maintaining the setpoint |
| Green dashed line at 104°F | Target temperature for optimal charging |
| Blue flat line at 32°F | Ambient temperature (constant in this simulation) |
| Orange line starting at ~0.78 then dropping | Heater running at high power initially, then tapering smoothly |
| Orange line near 0.51 at the end | Heater at ~51% power to maintain temperature against heat loss |

## Customizing the Simulation

Edit `main.py` to change any parameter:

```python
# Change starting conditions
battery = Battery(temperature=50.0, thermal_mass=5000.0)   # warmer start
environment = Environment(ambient_temp=50.0, heat_transfer_coeff=50.0)  # spring day

# Adjust PID tuning
controller = Controller(kp=0.013, ki=0.0002, kd=0.06)

# Run longer or with finer time steps
engine = SimulationEngine(
    battery=battery,
    environment=environment,
    controller=controller,
    duration=900.0,   # 15 minutes
    dt=0.5,           # half-second steps
)
```

### Parameter Reference

| Parameter | Default | Unit | Description |
|---|---|---|---|
| `temperature` | 32.0 | °F | Initial battery temperature |
| `thermal_mass` | 5000.0 | J/°F | Battery thermal inertia (mass × specific heat) |
| `ambient_temp` | 32.0 | °F | Outside air temperature |
| `heat_transfer_coeff` | 50.0 | W/°F | How fast heat escapes to the environment |
| `kp` | 0.013 | — | Proportional gain (reacts to current error) |
| `ki` | 0.0002 | — | Integral gain (eliminates steady-state error) |
| `kd` | 0.06 | — | Derivative gain (damps oscillation) |
| `max_power` | 7000.0 | W | Maximum heater output (7kW) |
| `duration` | 600.0 | s | How long to simulate |
| `dt` | 1.0 | s | Time step for Euler integration |

### PID Tuning Tips

- **Increase Kp** → faster response, but more overshoot
- **Increase Ki** → eliminates steady-state offset, but can cause oscillation
- **Increase Kd** → smoother approach, but too much makes the system sluggish
- The safety cutoff at 115°F forces the heater off regardless of PID output

### Things to Try in the Dashboard

1. **See overshoot in action** — drag Kp up to 0.05. The red line will shoot past 104°F before settling back down.
2. **Watch the safety cutoff trigger** — set Kp to 0.08. The battery will hit 115°F and the heater shuts off completely, then the cycle repeats.
3. **Remove derivative damping** — set Kd to 0. The temperature will oscillate around the setpoint instead of approaching smoothly.
4. **Crank up integral** — set Ki to 0.003. The controller overcorrects and the temperature wobbles.
5. **Summer scenario** — set both Initial Temp and Ambient Temp to 85°F. The battery barely needs heating and the duty cycle stays low.
6. **Arctic scenario** — set Ambient Temp to -20°F. The heater has to work much harder to fight the cold, and the duty cycle at steady state is higher.
7. **Change the target** — drag Setpoint to 120°F. Watch how the overshoot limit and settling behavior change.
8. **Hit Reset to Defaults** after each experiment to get back to the baseline.

## Running Tests

```bash
# Run all 8 unit tests
pytest test_simulation.py -v

# Expected output: 8 passed
```

The test suite validates:
- Controller duty cycle clamping (0.0 to 1.0)
- Zero output at setpoint
- Safety cutoff above 115°F
- Heat loss is zero at thermal equilibrium
- Full simulation reaches 104°F within 2°F
- No overshoot beyond 109°F
- Settling within 500 seconds

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'matplotlib'` | Run `pip install matplotlib` |
| Dashboard window doesn't appear | Check your matplotlib backend — try `matplotlib.use('TkAgg')` in `main.py` |
| Temperature overshoots past 109°F | Reduce `kp` or increase `kd` |
| Temperature never reaches 104°F | Increase `duration` or increase `kp` |
| `ValueError: thermal_mass must be positive` | Ensure `thermal_mass > 0` |
