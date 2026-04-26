# API Reference — EV Battery Thermal GNC & State Estimation Suite

## battery.py

### `class Battery`

Models the EV battery as a lumped thermal mass with a single temperature state.

#### `__init__(temperature: float, thermal_mass: float) -> None`

Create a Battery instance.

| Parameter | Type | Unit | Description |
|---|---|---|---|
| `temperature` | float | °F | Initial battery temperature |
| `thermal_mass` | float | J/°F | Thermal inertia (mass × specific heat capacity) |

**Raises:**
- `TypeError` — if `temperature` is non-numeric
- `TypeError` — if `thermal_mass` is non-numeric
- `ValueError` — if `thermal_mass <= 0`

**Example:**
```python
battery = Battery(temperature=32.0, thermal_mass=5000.0)
```

#### `temperature` (property)

Get or set the current battery temperature in °F.

```python
current = battery.temperature    # getter → 32.0
battery.temperature = 50.0       # setter
```

**Setter raises:** `TypeError` if value is non-numeric.

#### `dT_dt(net_heat: float) -> float`

Compute the rate of temperature change.

| Parameter | Type | Unit | Description |
|---|---|---|---|
| `net_heat` | float | W | Net heat input (heater power minus heat loss) |

**Returns:** Rate of temperature change in °F/s, computed as `net_heat / thermal_mass`.

```python
rate = battery.dT_dt(5000.0)  # → 1.0 °F/s for thermal_mass=5000
```

---

## environment.py

### `class Environment`

Models heat loss from the battery to the surroundings using Newton's Law of Cooling.

#### `__init__(ambient_temp: float, heat_transfer_coeff: float) -> None`

Create an Environment instance.

| Parameter | Type | Unit | Description |
|---|---|---|---|
| `ambient_temp` | float | °F | Ambient (outside) temperature |
| `heat_transfer_coeff` | float | W/°F | h·A product (convection coefficient × surface area) |

**Raises:** `ValueError` — if `heat_transfer_coeff < 0`

**Example:**
```python
env = Environment(ambient_temp=32.0, heat_transfer_coeff=50.0)
```

#### `ambient_temp` (property, read-only)

Returns the ambient temperature in °F.

```python
env.ambient_temp  # → 32.0
```

#### `heat_loss(battery_temp: float) -> float`

Compute heat loss from battery to environment.

| Parameter | Type | Unit | Description |
|---|---|---|---|
| `battery_temp` | float | °F | Current battery temperature |

**Returns:** Heat loss in watts. Positive means heat leaving the battery.

**Formula:** `heat_transfer_coeff × (battery_temp - ambient_temp)`

```python
env.heat_loss(82.0)   # → 50 × (82 - 32) = 2500.0 W
env.heat_loss(32.0)   # → 0.0 W (equilibrium)
```

---

## controller.py

### `class Controller`

PID feedback controller with duty-cycle clamping and safety cutoff.

#### `__init__(kp, ki, kd, setpoint=104.0, max_power=7000.0) -> None`

Create a Controller instance.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `kp` | float | — | Proportional gain |
| `ki` | float | — | Integral gain |
| `kd` | float | — | Derivative gain |
| `setpoint` | float | 104.0 | Target temperature in °F |
| `max_power` | float | 7000.0 | Maximum heater power in watts |

**Internal state** (initialized to 0.0):
- `integral` — accumulated error integral (°F·s)
- `prev_error` — error from previous time step (°F)

**Example:**
```python
ctrl = Controller(kp=0.013, ki=0.0002, kd=0.06)
```

#### `compute(current_temp: float, dt: float) -> float`

Compute the heater duty cycle based on current temperature.

| Parameter | Type | Unit | Description |
|---|---|---|---|
| `current_temp` | float | °F | Current battery temperature |
| `dt` | float | s | Time step |

**Returns:** Duty cycle in [0.0, 1.0].

**Behavior:**
1. If `dt <= 0` → raises `ValueError`
2. If `current_temp > 115.0` → returns `0.0` (safety cutoff)
3. Otherwise → computes PID output and clamps to [0.0, 1.0]

```python
ctrl.compute(32.0, 1.0)    # → 1.0 (full power, large error)
ctrl.compute(104.0, 1.0)   # → 0.0 (at setpoint, fresh controller)
ctrl.compute(120.0, 1.0)   # → 0.0 (safety cutoff)
```

#### `reset() -> None`

Reset the integral accumulator and previous error to zero. Use when restarting a simulation with the same controller.

```python
ctrl.reset()
# ctrl.integral == 0.0
# ctrl.prev_error == 0.0
```

---

## simulation.py

### `class SimulationEngine`

Orchestrates the time-stepping loop using forward Euler integration.

#### `__init__(battery, environment, controller, duration=600.0, dt=1.0) -> None`

Create a SimulationEngine instance.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `battery` | Battery | — | Battery instance |
| `environment` | Environment | — | Environment instance |
| `controller` | Controller | — | Controller instance |
| `duration` | float | 600.0 | Total simulation time in seconds |
| `dt` | float | 1.0 | Time step in seconds |

**Raises:** `ValueError` — if `duration <= 0`, `dt <= 0`, or `dt > duration`

#### `run() -> dict`

Execute the simulation and return recorded data.

**Returns:** Dictionary with four lists, each of length `floor(duration / dt) + 1`:

| Key | Type | Description |
|---|---|---|
| `'time'` | list[float] | Time stamps in seconds (starts at 0.0) |
| `'temperature'` | list[float] | Battery temperature at each step (°F) |
| `'ambient'` | list[float] | Ambient temperature at each step (°F) |
| `'duty_cycle'` | list[float] | Controller duty cycle at each step |

**Example:**
```python
engine = SimulationEngine(battery, env, ctrl, duration=600.0, dt=1.0)
results = engine.run()

results['time'][-1]         # → 600.0
results['temperature'][-1]  # → ~104.0
len(results['time'])        # → 601
```

---

## main.py

### `build_dashboard() -> None`

Launch an interactive Matplotlib window with real-time sliders for PID gains (Kp, Ki, Kd) and temperatures (initial, ambient, setpoint). Dragging any slider re-runs the simulation and updates the charts instantly.

**Sliders:**
- Kp (0.001-0.1), Ki (0.0-0.005), Kd (0.0-1.0)
- Initial Temp (-20-100 F), Ambient Temp (-20-100 F), Setpoint (80-130 F)

**Usage:**
```bash
python main.py
```

### `run_simulation(kp, ki, kd, t_initial, t_ambient, t_setpoint) -> dict`

Run a simulation with the given parameters. Returns the same dict format as `SimulationEngine.run()`.
