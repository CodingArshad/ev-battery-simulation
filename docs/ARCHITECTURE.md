# Architecture — EV Battery Thermal GNC & State Estimation Suite

## System Overview

The suite follows a **pipeline architecture** where a central simulation engine orchestrates interactions between three domain objects (Battery, Environment, Controller) each time step, then hands the recorded data to a visualization module.

```
┌─────────────────────────────────────────────────────────┐
│                        main.py                          │
│     Interactive dashboard with sliders + simulation     │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌──────────────────────┐
│   SimulationEngine   │
│   (simulation.py)    │
│                      │
│  Euler integration   │
│  loop orchestrator   │
└──┬───────┬───────┬───┘
   │       │       │
   ▼       ▼       ▼
┌──────┐ ┌─────┐ ┌──────────┐
│Battery│ │Env  │ │Controller│
│      │ │     │ │          │
│Thermal│ │Heat │ │PID +     │
│ mass  │ │loss │ │safety    │
│model  │ │model│ │cutoff    │
└──────┘ └─────┘ └──────────┘
```

## Component Responsibilities

### Battery (`battery.py`)

Single responsibility: store temperature state and compute dT/dt.

- **State**: `_temperature` (°F), `_thermal_mass` (J/°F)
- **Physics**: `dT_dt(net_heat) = net_heat / thermal_mass`
- **Validation**: Rejects non-numeric temperature, non-positive thermal mass

The battery is a **lumped thermal mass** — a single-node approximation where the entire pack has one uniform temperature. This is standard for control-oriented thermal models where spatial gradients are not the focus.

### Environment (`environment.py`)

Single responsibility: compute heat loss to surroundings.

- **State**: `_ambient_temp` (°F), `_heat_transfer_coeff` (W/°F)
- **Physics**: `heat_loss(T_bat) = h·A × (T_bat - T_amb)` (Newton's Law of Cooling)
- **Validation**: Rejects negative heat transfer coefficient

The `h·A` product combines the convective heat transfer coefficient `h` and the surface area `A` into a single parameter, which is standard practice when the geometry is abstracted away.

### Controller (`controller.py`)

Single responsibility: compute heater duty cycle from temperature error.

- **State**: `kp`, `ki`, `kd`, `setpoint`, `max_power`, `integral`, `prev_error`
- **Algorithm**: Standard discrete PID
  ```
  error = setpoint - current_temp
  integral += error × dt
  derivative = (error - prev_error) / dt
  output = Kp × error + Ki × integral + Kd × derivative
  duty_cycle = clamp(output, 0.0, 1.0)
  ```
- **Safety**: Hard cutoff returns 0.0 if temperature > 115°F
- **Validation**: Rejects non-positive time step

The duty cycle output (0.0–1.0) represents the fraction of max heater power applied. Clamping prevents integral windup from producing nonsensical values.

### SimulationEngine (`simulation.py`)

Single responsibility: orchestrate the time-stepping loop.

- **Inputs**: Battery, Environment, Controller instances + duration + dt
- **Algorithm**: Forward Euler integration
  ```
  for each time step:
      duty_cycle = controller.compute(T_battery, dt)
      net_heat = duty_cycle × max_power - heat_loss(T_battery)
      dT = (net_heat / thermal_mass) × dt
      T_battery += dT
  ```
- **Output**: Dictionary with `time`, `temperature`, `ambient`, `duty_cycle` lists
- **Validation**: Rejects non-positive duration/dt, dt > duration

### Interactive Dashboard (`main.py`)

Single responsibility: render simulation results as an interactive Matplotlib figure with real-time sliders.

- **Input**: Uses `run_simulation()` internally with slider values
- **Output**: Two vertically stacked subplots + 6 sliders
  - Top: Battery temp + ambient temp + setpoint reference line
  - Bottom: Duty cycle over time
  - Sliders: Kp, Ki, Kd, Initial Temp, Ambient Temp, Setpoint
- **Interactive**: Dragging any slider re-runs the simulation and updates the charts

### Entry Point

`main.py` is the entry point — run `python main.py` to launch.

## Control Loop Flow (Per Time Step)

```
┌─────────────────┐
│ SimulationEngine │
│   loop start     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────┐
│ Controller       │────▶│ duty_cycle│
│ compute(T, dt)   │     │ [0.0–1.0]│
└─────────────────┘     └────┬─────┘
                              │
         ┌────────────────────┘
         ▼
┌─────────────────┐
│ heater_power =   │
│ duty × 7000 W   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────┐
│ Environment      │────▶│ heat_loss│
│ heat_loss(T)     │     │ (watts)  │
└─────────────────┘     └────┬─────┘
                              │
         ┌────────────────────┘
         ▼
┌─────────────────┐
│ net_heat =       │
│ heater - loss    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────┐
│ Battery          │────▶│ dT/dt    │
│ dT_dt(net_heat)  │     │ (°F/s)   │
└─────────────────┘     └────┬─────┘
                              │
         ┌────────────────────┘
         ▼
┌─────────────────┐
│ Euler update:    │
│ T += dT/dt × dt  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Record state     │
│ → next step      │
└─────────────────┘
```

## Data Flow

```
Battery.temperature ──▶ Controller.compute() ──▶ duty_cycle
Battery.temperature ──▶ Environment.heat_loss() ──▶ q_loss
                                                      │
duty_cycle × max_power - q_loss = net_heat ───────────┘
                                      │
net_heat ──▶ Battery.dT_dt() ──▶ rate
rate × dt ──▶ Battery.temperature (updated)
```

## File Structure

```
ev-battery-simulation/
├── battery.py                # Battery thermal mass model
├── environment.py            # Newton's Law of Cooling heat loss
├── controller.py             # PID controller with safety cutoff
├── simulation.py             # Euler integration engine
├── main.py                   # Interactive dashboard with sliders (entry point)
├── test_simulation.py        # 8 unit tests (pytest)
└── docs/
    ├── architecture_diagram.png  # System architecture diagram
    ├── project_planning.png      # Project planning notes
    ├── USER_GUIDE.md         # How to install, run, and customize
    ├── ARCHITECTURE.md       # This file
    ├── WORKFLOW.md           # Simulation workflow and control theory
    ├── API_REFERENCE.md      # Class and function signatures
    ├── TESTING.md            # Test strategy and coverage
    ├── CONFIGURATION.md      # Parameter reference and tuning presets
    └── GLOSSARY.md           # Domain, physics, and control theory terms
```

## Design Decisions

| Decision | Rationale |
|---|---|
| Lumped thermal mass (single node) | Appropriate for control-oriented simulation; distributed models add complexity without pedagogical benefit |
| Forward Euler integration | Transparent — students see `T_new = T_old + dT/dt × dt` directly; stable at dt=1s given thermal time constants of 100+ seconds |
| Duty cycle output [0, 1] | Maps naturally to a heater modulated from off to full power; prevents integral windup |
| Safety cutoff in Controller | Keeps safety logic co-located with control logic rather than scattered across modules |
| Fahrenheit throughout | Matches the project requirements; thermal mass in J/°F for dimensional consistency |
| No external config files | Simplicity — all parameters are constructor arguments with sensible defaults |
| Separate files per class | Demonstrates clean OO architecture; each module has a single responsibility |
