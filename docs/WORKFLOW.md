# Simulation Workflow & Control Theory

## The Real-World Problem

When an EV navigates to a DC fast charger (Supercharger), the battery management system (BMS) begins pre-conditioning the pack. Lithium-ion cells accept charge fastest at around 40°C (104°F). If the pack is cold (e.g., 0°C / 32°F in winter), charging at full power risks lithium plating, which permanently damages the cells.

The solution: run an onboard heater to warm the pack during the drive. The challenge: heat it fast enough to be ready on arrival, but don't overshoot and waste energy or trigger thermal protection.

This simulation models that exact scenario.

## Simulation Workflow

### Phase 1: Initialization (t = 0)

```
Battery temperature:  32°F  (cold soak — parked overnight in winter)
Ambient temperature:  32°F  (freezing outside)
Heater duty cycle:    0.0   (heater off)
Target temperature:   104°F (optimal for fast charging)
```

All components are created with their initial parameters. The simulation engine records the initial state.

### Phase 2: Aggressive Heating (t = 0 → ~200s)

The PID controller sees a large error (104 - 32 = 72°F) and commands full heater power:

```
duty_cycle ≈ 1.0  →  heater_power = 7000 W
heat_loss = 50 × (T_bat - 32)  →  small initially
net_heat ≈ 7000 W  →  rapid temperature rise
```

The battery temperature climbs roughly linearly because heat loss is small relative to heater power when the battery is still cold.

### Phase 3: Transition (t ≈ 200 → 350s)

As the battery warms, two things happen:
1. The error shrinks, so the PID reduces duty cycle
2. Heat loss increases (larger ΔT between battery and ambient)

```
T_bat ≈ 80°F
heat_loss = 50 × (80 - 32) = 2400 W
net_heat = duty × 7000 - 2400  →  heating slows
```

The derivative term (Kd) dampens the approach to prevent overshoot.

### Phase 4: Settling (t ≈ 350 → 500s)

The controller fine-tunes the duty cycle to land on 104°F:

```
T_bat ≈ 102–106°F
error ≈ ±2°F
duty_cycle ≈ 0.3–0.5  →  just enough to offset heat loss
```

The integral term (Ki) slowly eliminates any remaining steady-state offset.

### Phase 5: Steady State (t > 500s)

The battery holds at ~104°F. The heater runs at a low duty cycle that exactly balances heat loss:

```
At equilibrium:  heater_power = heat_loss
duty × 7000 = 50 × (104 - 32) = 3600 W
duty ≈ 0.51
```

## PID Control Theory

### The PID Equation

```
output(t) = Kp × e(t) + Ki × ∫e(τ)dτ + Kd × de/dt
```

Where `e(t) = setpoint - measured_value` is the error signal.

### Discrete Implementation

In this simulation, the continuous PID is discretized using forward differences:

```python
error = setpoint - current_temp           # Proportional term input
integral += error * dt                     # Integral via rectangular rule
derivative = (error - prev_error) / dt     # Derivative via backward difference
output = Kp * error + Ki * integral + Kd * derivative
duty_cycle = clamp(output, 0.0, 1.0)
```

### What Each Term Does

| Term | Role | Effect of Increasing |
|---|---|---|
| **P** (Proportional) | Reacts to current error | Faster response, more overshoot |
| **I** (Integral) | Eliminates steady-state error | Removes offset, but can cause oscillation |
| **D** (Derivative) | Predicts future error from rate of change | Smoother approach, but sluggish if too high |

### Tuned Gains

| Gain | Value | Why |
|---|---|---|
| Kp = 0.013 | Low proportional gain | Starts tapering power well before setpoint, preventing overshoot |
| Ki = 0.0002 | Very small integral | Slowly corrects offset without causing windup oscillation |
| Kd = 0.06 | Gentle derivative damping | Smooths the approach without causing duty cycle chattering |

### Safety Cutoff

If the battery exceeds 115°F, the controller forces `duty_cycle = 0.0` regardless of PID output. This is a hard override that protects against:
- Poorly tuned gains
- Sensor failures (in a real system)
- Unexpected thermal runaway

The simulation continues running — the battery cools via heat loss until it drops below 115°F, at which point the PID resumes control.

## Physics: Newton's Law of Cooling

The heat loss model uses Newton's Law of Cooling:

```
Q_loss = h·A × (T_battery - T_ambient)
```

| Symbol | Meaning | Value |
|---|---|---|
| Q_loss | Heat flow from battery to environment (W) | Computed each step |
| h·A | Heat transfer coefficient × surface area (W/°F) | 50.0 |
| T_battery | Current battery temperature (°F) | Variable |
| T_ambient | Outside air temperature (°F) | 32.0 (constant) |

Key behaviors:
- When `T_battery = T_ambient`: no heat loss (thermal equilibrium)
- When `T_battery > T_ambient`: heat flows out (positive loss)
- When `T_battery < T_ambient`: heat flows in (negative loss — environment warms the battery)

## Physics: Lumped Thermal Mass

The battery is modeled as a single thermal node with uniform temperature:

```
dT/dt = Q_net / C_thermal
```

| Symbol | Meaning | Value |
|---|---|---|
| dT/dt | Rate of temperature change (°F/s) | Computed each step |
| Q_net | Net heat input: heater power - heat loss (W) | Computed each step |
| C_thermal | Thermal mass: mass × specific heat (J/°F) | 5000.0 |

The thermal mass determines how quickly the battery responds to heating. A larger thermal mass means slower temperature changes (more energy needed per degree).

## Numerical Integration: Forward Euler

The simulation uses the simplest numerical integration method:

```
T(t + dt) = T(t) + dT/dt × dt
```

This is a first-order method. It's accurate when `dt` is small relative to the system's time constant. For this simulation:

- Thermal time constant: `C / (h·A) = 5000 / 50 = 100 seconds`
- Time step: `dt = 1.0 second`
- Ratio: `dt / τ = 0.01` — well within the stability region

Higher-order methods (RK4, scipy.odeint) would be more accurate but less transparent for educational purposes.

## Energy Balance at Steady State

At equilibrium (t > 500s), the system satisfies:

```
Heater input = Heat loss to environment
duty × 7000 = 50 × (104 - 32)
duty × 7000 = 3600
duty ≈ 0.514
```

The heater runs at about 51% power to maintain 104°F in 32°F ambient conditions. This means the system consumes approximately 3.6 kW continuously at steady state.
