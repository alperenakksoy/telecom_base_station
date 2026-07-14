"""
IM_k — Integration module / output representation
(Durán 2020). Interactive matplotlib-slider control panel
for exploring the city network load model.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

from kernel.solver import solve_city
from integration.animator import plot_summary
from models.load_model import DAY_NAMES

PLAY_STEP_HOURS = 0.2   # hours advanced per timer tick
PLAY_INTERVAL_MS = 100  # ms between timer ticks


def run_interactive(grid_size: int = 15, n_steps: int = 97) -> None:
    """
    Opens a heatmap with slider controls:
    - Hour: which point in the 24h cycle to display
    - Capacity (mu): network processing capacity
    - City Density: multiplier on city-center traffic weight
    - Day of Week: shifts peak hours/amplitude (weekday vs weekend)

    A Play/Pause button auto-advances the Hour slider over time;
    the Hour slider can still be dragged manually at any point
    (dragging it while playing simply jumps playback to that hour).

    Changing mu / density / day re-solves the ODE for the whole city;
    changing hour just re-displays the already-solved frame.
    """
    state = {
        "result": solve_city(grid_size=grid_size, mu=1.2, n_steps=n_steps,
                              day_of_week=0, density_scale=1.0)
    }

    fig, ax = plt.subplots(figsize=(8, 9))
    plt.subplots_adjust(bottom=0.32)

    im = ax.imshow(state["result"]["L"][0],
                    cmap="RdYlGn_r",
                    vmin=0, vmax=1.2,
                    interpolation="bilinear",
                    origin="upper")
    plt.colorbar(im, ax=ax, label="Load Level")
    title_text = ax.set_title("")
    overload_text = ax.text(0.02, 0.02, "",
                             transform=ax.transAxes, color="red",
                             fontsize=11)
    ax.set_xlabel("City East-West")
    ax.set_ylabel("City North-South")
    ax.set_xticks([])
    ax.set_yticks([])

    ax_hour = plt.axes((0.15, 0.20, 0.55, 0.03))
    ax_mu = plt.axes((0.15, 0.14, 0.7, 0.03))
    ax_density = plt.axes((0.15, 0.08, 0.7, 0.03))
    ax_day = plt.axes((0.15, 0.02, 0.55, 0.03))
    ax_play = plt.axes((0.76, 0.195, 0.1, 0.04))
    ax_summary = plt.axes((0.76, 0.02, 0.1, 0.04))

    hour_slider = Slider(ax_hour, "Hour", 0.0, 24.0, valinit=0.0)
    mu_slider = Slider(ax_mu, "Capacity (mu)", 0.5, 3.0, valinit=1.2)
    density_slider = Slider(ax_density, "City Density", 0.3, 2.0, valinit=1.0)
    day_slider = Slider(ax_day, "Day of Week", 0, 6, valinit=0, valstep=1)
    play_button = Button(ax_play, "Pause")
    summary_button = Button(ax_summary, "Summary")

    playing = {"on": True}

    def redraw_frame(*_args) -> None:
        result = state["result"]
        t_val = hour_slider.val
        idx = int(np.argmin(np.abs(result["t"] - t_val)))
        L_frame = result["L"][idx]

        im.set_data(L_frame)
        hour = int(t_val)
        minute = int((t_val % 1) * 60)
        day_name = DAY_NAMES[int(day_slider.val)]
        title_text.set_text(f"Network Load — {day_name} {hour:02d}:{minute:02d}")

        n_red = int(np.sum(L_frame > 0.7))
        if n_red > 0:
            overload_text.set_text(f"⚠ Overloaded: {n_red} stations")
            overload_text.set_color("red")
        else:
            overload_text.set_text("✓ All stations normal")
            overload_text.set_color("green")

        fig.canvas.draw_idle()

    def recompute_and_redraw(*_args) -> None:
        state["result"] = solve_city(
            grid_size=grid_size,
            mu=mu_slider.val,
            n_steps=n_steps,
            day_of_week=int(day_slider.val),
            density_scale=density_slider.val,
        )
        redraw_frame()

    def advance_playback() -> None:
        if not playing["on"]:
            return
        next_hour = hour_slider.val + PLAY_STEP_HOURS
        if next_hour > 24.0:
            next_hour -= 24.0
        hour_slider.set_val(next_hour)  # triggers redraw_frame via on_changed

    def toggle_play(_event) -> None:
        playing["on"] = not playing["on"]
        play_button.label.set_text("Pause" if playing["on"] else "Play")

    def show_summary(_event) -> None:
        # Freezes the currently solved result (fixed mu/density/day) into
        # a separate static figure, so it isn't affected by continued sliding.
        plot_summary(state["result"])

    hour_slider.on_changed(redraw_frame)
    mu_slider.on_changed(recompute_and_redraw)
    density_slider.on_changed(recompute_and_redraw)
    day_slider.on_changed(recompute_and_redraw)
    play_button.on_clicked(toggle_play)
    summary_button.on_clicked(show_summary)

    timer = fig.canvas.new_timer(interval=PLAY_INTERVAL_MS)
    timer.add_callback(advance_playback)
    timer.start()

    redraw_frame()
    plt.show()


if __name__ == "__main__":
    run_interactive()
