"""Interactive dashboard with sliders for PID gains and temperatures.

Run with:  python main.py

Drag any slider to re-run the simulation in real time and see how the
battery temperature and heater duty cycle respond.
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import time as _time

from battery import Battery
from environment import Environment
from controller import Controller
from simulation import SimulationEngine


# ── Default values ──────────────────────────────────────────────────────
DEFAULTS = {
    "kp": 0.013,
    "ki": 0.0002,
    "kd": 0.06,
    "t_initial": 32.0,
    "t_ambient": 32.0,
    "t_setpoint": 104.0,
}


def run_simulation(kp, ki, kd, t_initial, t_ambient, t_setpoint):
    """Run the thermal simulation with the given parameters."""
    battery = Battery(temperature=t_initial, thermal_mass=5000.0)
    environment = Environment(ambient_temp=t_ambient, heat_transfer_coeff=50.0)
    controller = Controller(kp=kp, ki=ki, kd=kd, setpoint=t_setpoint)
    engine = SimulationEngine(
        battery=battery,
        environment=environment,
        controller=controller,
        duration=600.0,
        dt=1.0,
    )
    return engine.run()


def build_dashboard():
    """Build the interactive Matplotlib dashboard with sliders."""

    # ── Create figure — tall enough for charts + sliders ────────────────
    fig = plt.figure(figsize=(14, 11), num="EV Battery Thermal GNC")
    fig.patch.set_facecolor("#FAFAFA")

    # Prevent flickering on resize by using blitting-friendly redraw
    fig.canvas.mpl_connect("resize_event", lambda e: fig.canvas.draw_idle())

    # ── Chart axes (top 55% of figure) ──────────────────────────────────
    #                  [left, bottom, width, height]
    ax_temp = fig.add_axes([0.08, 0.58, 0.88, 0.33])
    ax_duty = fig.add_axes([0.08, 0.38, 0.88, 0.17], sharex=ax_temp)

    # ── Slider axes — manually positioned for readability ───────────────
    # Left column: PID gains          Right column: Temperatures
    # Each slider: [left, bottom, width, height]
    slider_w = 0.30
    slider_h = 0.025
    left_x = 0.18          # left column slider start
    right_x = 0.65         # right column slider start
    row_y = [0.27, 0.21, 0.15]  # y positions for 3 rows

    slider_specs = [
        # (name,       x,       y,         min,   max,    default,            fmt,     color,       label)
        ("kp",         left_x,  row_y[0],  0.001, 0.1,    DEFAULTS["kp"],    "%.4f",  "#8e44ad",   "Kp (proportional)"),
        ("ki",         left_x,  row_y[1],  0.0,   0.005,  DEFAULTS["ki"],    "%.5f",  "#8e44ad",   "Ki (integral)"),
        ("kd",         left_x,  row_y[2],  0.0,   1.0,    DEFAULTS["kd"],    "%.3f",  "#8e44ad",   "Kd (derivative)"),
        ("t_initial",  right_x, row_y[0],  -20.0, 100.0,  DEFAULTS["t_initial"], "%.0f°F", "#e67e22", "Initial Temp"),
        ("t_ambient",  right_x, row_y[1],  -20.0, 100.0,  DEFAULTS["t_ambient"], "%.0f°F", "#16a085", "Ambient Temp"),
        ("t_setpoint", right_x, row_y[2],  80.0,  130.0,  DEFAULTS["t_setpoint"], "%.0f°F", "#27ae60", "Setpoint"),
    ]

    sliders = {}
    for name, x, y, vmin, vmax, default, fmt, color, label in slider_specs:
        ax_s = fig.add_axes([x, y, slider_w, slider_h])
        slider = Slider(
            ax_s, label, vmin, vmax,
            valinit=default, valfmt=fmt,
            color=color, alpha=0.6,
        )
        slider.label.set_fontsize(11)
        slider.valtext.set_fontsize(10)
        sliders[name] = slider

    # Section headers above slider columns
    fig.text(0.33, 0.31, "PID Gains", fontsize=12, fontweight="bold",
             ha="center", color="#8e44ad")
    fig.text(0.80, 0.31, "Temperatures", fontsize=12, fontweight="bold",
             ha="center", color="#e67e22")

    # Separator line between charts and sliders
    fig.patches.append(plt.Rectangle(
        (0.05, 0.335), 0.90, 0.001,
        transform=fig.transFigure, facecolor="#cccccc",
    ))

    # Reset button
    ax_reset = fig.add_axes([0.40, 0.08, 0.20, 0.04])
    btn_reset = Button(ax_reset, "Reset to Defaults",
                       color="#ecf0f1", hovercolor="#bdc3c7")
    btn_reset.label.set_fontsize(11)

    # ── Initial plot ────────────────────────────────────────────────────
    data = run_simulation(**DEFAULTS)

    line_temp, = ax_temp.plot(
        data["time"], data["temperature"],
        color="tab:red", linewidth=2, label="Battery Temp",
    )
    line_amb, = ax_temp.plot(
        data["time"], data["ambient"],
        color="tab:blue", linewidth=1.5, linestyle="-.", label="Ambient Temp",
    )
    line_sp = ax_temp.axhline(
        y=DEFAULTS["t_setpoint"], color="tab:green", linestyle="--",
        linewidth=1.5, label=f"Setpoint ({DEFAULTS['t_setpoint']:.0f}°F)",
    )
    line_limit = ax_temp.axhline(
        y=109.0, color="orange", linestyle=":", linewidth=1, alpha=0.6,
        label="Overshoot Limit (109°F)",
    )
    line_safety = ax_temp.axhline(
        y=115.0, color="red", linestyle=":", linewidth=1, alpha=0.6,
        label="Safety Cutoff (115°F)",
    )

    ax_temp.set_ylabel("Temperature (°F)", fontsize=12)
    ax_temp.set_ylim(0, 130)
    ax_temp.legend(loc="center right", fontsize=9)
    ax_temp.grid(True, alpha=0.3)
    ax_temp.tick_params(labelsize=10)
    plt.setp(ax_temp.get_xticklabels(), visible=False)

    # Stats text box
    stats_text = ax_temp.text(
        0.01, 0.95, "", transform=ax_temp.transAxes,
        fontsize=10, verticalalignment="top", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                  edgecolor="#aaa", alpha=0.9),
    )

    fig.suptitle(
        "EV Battery Thermal GNC — Interactive Dashboard",
        fontsize=15, fontweight="bold", y=0.96,
    )

    line_duty, = ax_duty.plot(
        data["time"], data["duty_cycle"],
        color="tab:orange", linewidth=2, label="Duty Cycle",
    )
    duty_fill = ax_duty.fill_between(
        data["time"], data["duty_cycle"], alpha=0.15, color="tab:orange",
    )
    ax_duty.set_xlabel("Time (s)", fontsize=12)
    ax_duty.set_ylabel("Duty Cycle", fontsize=12)
    ax_duty.set_ylim(-0.05, 1.1)
    ax_duty.legend(loc="upper right", fontsize=10)
    ax_duty.grid(True, alpha=0.3)
    ax_duty.tick_params(labelsize=10)

    # Store fill so we can replace it on update
    fill_collection = [duty_fill]

    # ── Update function ─────────────────────────────────────────────────
    _last_update = [0.0]

    def update(_=None):
        # Debounce: skip if called again within 50ms (prevents flicker)
        now = _time.monotonic()
        if now - _last_update[0] < 0.05:
            fig.canvas.draw_idle()
            return
        _last_update[0] = now

        kp = sliders["kp"].val
        ki = sliders["ki"].val
        kd = sliders["kd"].val
        t_initial = sliders["t_initial"].val
        t_ambient = sliders["t_ambient"].val
        t_setpoint = sliders["t_setpoint"].val

        data = run_simulation(kp, ki, kd, t_initial, t_ambient, t_setpoint)

        line_temp.set_ydata(data["temperature"])
        line_amb.set_ydata(data["ambient"])
        line_duty.set_ydata(data["duty_cycle"])

        # Update reference lines
        line_sp.set_ydata([t_setpoint, t_setpoint])
        line_sp.set_label(f"Setpoint ({t_setpoint:.0f}°F)")

        overshoot_limit = t_setpoint + 5.0
        line_limit.set_ydata([overshoot_limit, overshoot_limit])
        line_limit.set_label(f"Overshoot Limit ({overshoot_limit:.0f}°F)")

        # Replace duty cycle fill
        for coll in fill_collection:
            coll.remove()
        fill_collection.clear()
        new_fill = ax_duty.fill_between(
            data["time"], data["duty_cycle"], alpha=0.15, color="tab:orange",
        )
        fill_collection.append(new_fill)

        # Compute stats
        temps = data["temperature"]
        max_temp = max(temps)
        final_temp = temps[-1]
        overshoot = max_temp - t_setpoint

        settle_time = "N/A"
        for i, t in enumerate(data["time"]):
            if abs(temps[i] - t_setpoint) <= 2.0:
                if all(abs(temps[j] - t_setpoint) <= 2.0
                       for j in range(i, len(temps))):
                    settle_time = f"{t:.0f}s"
                    break

        stats_text.set_text(
            f"Max: {max_temp:.1f}°F   "
            f"Overshoot: {overshoot:+.1f}°F   "
            f"Final: {final_temp:.1f}°F   "
            f"Settle: {settle_time}"
        )

        # Auto-scale temperature axis
        all_temps = list(temps) + [t_ambient, t_setpoint, 115.0]
        y_min = min(all_temps) - 10
        y_max = max(max(all_temps), 120) + 10
        ax_temp.set_ylim(y_min, y_max)
        ax_temp.legend(loc="center right", fontsize=9)

        fig.canvas.draw_idle()

    # ── Connect events ──────────────────────────────────────────────────
    for slider in sliders.values():
        slider.on_changed(update)

    def reset(_):
        # Temporarily disable debounce so the final update goes through
        _last_update[0] = 0.0
        for name, slider in sliders.items():
            slider.set_val(DEFAULTS[name])
        # Force a full update after all sliders are reset
        _last_update[0] = 0.0
        update()

    btn_reset.on_clicked(reset)

    # Initial stats
    update()

    plt.show()


if __name__ == "__main__":
    build_dashboard()
