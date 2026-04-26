# Glossary — EV Battery Thermal GNC & State Estimation Suite

## Domain Terms

| Term | Definition |
|---|---|
| **Battery Pre-Conditioning** | The process of heating (or cooling) an EV battery to an optimal temperature before DC fast charging to maximize charge acceptance rate and protect cell health. |
| **Supercharger** | A DC fast charging station. The simulation models the scenario where the vehicle is navigating to one. |
| **Thermal Setpoint** | The target battery temperature for pre-conditioning: 104°F (40°C). This is the temperature at which lithium-ion cells accept charge most efficiently. |
| **Overshoot** | The amount by which the battery temperature exceeds the setpoint during the heating process. The system limits this to 5°F (max 109°F). |
| **Settling Time** | The time required for the battery temperature to reach and stay within 2°F of the setpoint. The system achieves this within 500 seconds. |
| **Duty Cycle** | The fraction of maximum heater power currently applied, ranging from 0.0 (off) to 1.0 (full power). At duty cycle 0.5, the heater outputs 3500W of its 7000W capacity. |
| **Cold Soak** | The condition where a vehicle has been parked long enough for the battery to reach ambient temperature. The default simulation starts from a cold soak at 32°F. |

## Physics Terms

| Term | Definition |
|---|---|
| **Newton's Law of Cooling** | Heat loss is proportional to the temperature difference between the object and its surroundings: Q = h·A × (T_object - T_ambient). |
| **Lumped Thermal Mass** | A simplification where the entire battery pack is modeled as a single node with one uniform temperature, rather than a distributed temperature field. Valid when internal conduction is fast relative to surface convection. |
| **Thermal Mass (C)** | The product of mass and specific heat capacity (J/°F). Determines how much energy is needed to change the temperature by one degree. Default: 5000 J/°F. |
| **Heat Transfer Coefficient (h·A)** | The product of the convective heat transfer coefficient and the surface area (W/°F). Determines how fast heat escapes to the environment. Default: 50 W/°F. |
| **Thermal Time Constant (τ)** | C / (h·A) = 5000 / 50 = 100 seconds. The characteristic time for the system to respond to a step change. After one time constant, the system has completed ~63% of its response. |

## Control Theory Terms

| Term | Definition |
|---|---|
| **PID Controller** | A feedback controller that computes an output from three terms: Proportional (reacts to current error), Integral (eliminates steady-state error), and Derivative (damps oscillation). |
| **Error Signal** | The difference between the setpoint and the measured value: e(t) = setpoint - current_temp. Positive error means the battery is below target. |
| **Proportional Gain (Kp)** | Multiplier for the current error. Higher Kp means stronger reaction to error, but too high causes overshoot. Default: 0.013. |
| **Integral Gain (Ki)** | Multiplier for the accumulated error over time. Eliminates steady-state offset but can cause oscillation if too large. Default: 0.0002. |
| **Derivative Gain (Kd)** | Multiplier for the rate of change of error. Provides damping to prevent overshoot. Default: 0.06. |
| **Integral Windup** | A condition where the integral term accumulates excessively (e.g., during saturation), causing large overshoot when the error changes sign. Mitigated in this system by clamping the duty cycle to [0, 1]. |
| **Safety Cutoff** | A hard override that forces the heater off (duty cycle = 0.0) when the battery exceeds 115°F, regardless of PID output. |

## Numerical Methods Terms

| Term | Definition |
|---|---|
| **Forward Euler Method** | The simplest numerical integration: T(t+dt) = T(t) + dT/dt × dt. First-order accurate. Stable when dt is small relative to the system time constant. |
| **Time Step (dt)** | The discrete interval between simulation steps. Default: 1.0 second. Smaller values increase accuracy but take longer to compute. |
| **Numerical Stability** | A method is stable if small errors don't grow unboundedly. For forward Euler, stability requires dt/τ < 2. With dt=1s and τ=100s, the ratio is 0.01 — well within the stable region. |

## Software Terms

| Term | Definition |
|---|---|
| **Matplotlib** | Python plotting library used for the dashboard visualization. |
| **pytest** | Python testing framework used for the unit test suite. |
| **Hypothesis** | Python library for property-based testing. Generates random inputs to verify that properties hold universally. |
| **Agg Backend** | A non-interactive Matplotlib rendering backend that produces images without opening GUI windows. Used in tests and headless environments. |
