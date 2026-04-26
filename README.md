# EV Battery Thermal GNC & State Estimation Suite

A Python simulation that models electric vehicle battery thermal pre-conditioning using physics-based thermal dynamics, PID feedback control, and Matplotlib visualization.

When an EV navigates to a DC fast charger, the battery must be heated to 104°F (40°C) for optimal charge acceptance. This suite simulates that process — a 7kW heater regulated by a PID controller warms a cold-soaked battery from 32°F while Newton's Law of Cooling models heat loss to the environment.

## Quick Start

```bash
pip install matplotlib
python main.py
```

An interactive window opens with two charts (temperature and heater duty cycle) and 6 sliders for PID gains and temperatures. Drag any slider to re-run the simulation in real time.

## Project Structure

```
├── battery.py                # Lumped thermal mass model
├── environment.py            # Newton's Law of Cooling heat loss
├── controller.py             # PID controller with safety cutoff at 115°F
├── simulation.py             # Forward Euler integration engine
├── main.py                   # Interactive dashboard with sliders (entry point)
├── test_simulation.py        # 8 unit tests (pytest)
└── docs/
    ├── architecture_diagram.png  # System architecture diagram
    ├── project_planning.png      # Project planning notes
    ├── USER_GUIDE.md         # Installation, usage, customization
    ├── ARCHITECTURE.md       # System design and component relationships
    ├── WORKFLOW.md           # Simulation phases and control theory
    ├── API_REFERENCE.md      # Class and function signatures
    ├── TESTING.md            # Test strategy and coverage matrix
    ├── CONFIGURATION.md      # Parameter reference and tuning presets
    └── GLOSSARY.md           # Domain, physics, and control theory terms
```

## Key Features

- **Physics-based thermal model** — Newton's Law of Cooling with configurable h·A product
- **PID feedback control** — Proportional-Integral-Derivative controller with duty cycle clamping [0, 1]
- **Safety cutoff** — Hard override at 115°F forces heater off
- **Forward Euler integration** — Transparent numerical method with 1-second time steps
- **Stability guarantees** — Overshoot ≤ 5°F, settling within 500 seconds
- **Interactive dashboard** — Real-time sliders for PID gains and temperatures
- **8 unit tests** — Controller clamping, physics correctness, simulation integration, safety cutoff

## Default Parameters

| Parameter | Value | Description |
|---|---|---|
| Initial battery temp | 32°F | Cold soak (winter) |
| Ambient temp | 32°F | Freezing conditions |
| Thermal mass | 5000 J/°F | Small EV battery pack |
| Heat transfer coeff | 50 W/°F | Moderate insulation |
| Heater max power | 7000 W | 7kW heater |
| PID gains | Kp=0.013, Ki=0.0002, Kd=0.06 | Tuned for smooth response, <5°F overshoot |
| Simulation duration | 600 s | 10 minutes |

## Running Tests

```bash
pip install pytest
pytest test_simulation.py -v
```

## Tech Stack

- Python 3.8+
- Matplotlib (visualization)
- NumPy (installed as Matplotlib dependency)
- pytest (testing)
