"""
IM_k — Integration module / output representation
(Durán 2020). Creates matplotlib animation of
city network load over 24 hours.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def create_animation(result: dict,
                      interval: int = 100,
                      save_path: str = None,
                      show: bool = True):
    """
    Creates animated heatmap of network load.

    interval: ms between frames (100ms = normal speed)
    save_path: if given, saves as .mp4 using ffmpeg
    show: if True, calls plt.show()

    Visual design:
    - colormap: use custom: green→yellow→red
      (RdYlGn_r from matplotlib)
    - vmin=0, vmax=1.2 (so overload shows deep red)
    - colorbar on right: label "Load Level"
    - title updates each frame:
      f"Network Load — {hour:02d}:{minute:02d}"
      where hour = int(t), minute = int((t%1)*60)
    - add text annotation bottom left:
      f"Overloaded: {n_red} stations"
      color red if n_red > 0 else green
    - figure size: (8, 7)
    - tight_layout()
    """
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(result["L"][0],
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
    fig.tight_layout()

    def update(frame):
        L_frame = result["L"][frame]
        t = result["t"][frame]
        hour = int(t)
        minute = int((t % 1) * 60)
        im.set_data(L_frame)
        title_text.set_text(
            f"Network Load — {hour:02d}:{minute:02d}")
        n_red = int(np.sum(L_frame > 0.7))
        if n_red > 0:
            overload_text.set_text(
                f"⚠ Overloaded: {n_red} stations")
            overload_text.set_color("red")
        else:
            overload_text.set_text("✓ All stations normal")
            overload_text.set_color("green")
        return [im, title_text, overload_text]

    anim = FuncAnimation(fig, update,
                          frames=len(result["t"]),
                          interval=interval, blit=False)

    if save_path:
        anim.save(save_path, writer="ffmpeg", fps=10, dpi=150)
        print(f"Saved to {save_path}")

    if show:
        plt.show()

    return anim


def plot_summary(result: dict, save_path: str = None):
    """
    Static summary plot — shown after animation.
    2 subplots:

    Left: heatmap at peak hour
    - title: f"Peak Load (Hour {peak:.0f}:00)"

    Right: line chart
    - X: hours 0-24
    - Y: percentage of overloaded stations
    - red line
    - title: "% Overloaded Stations Over 24h"
    - X label: "Hour of Day"
    - Y label: "% Overloaded"
    - vertical dashed lines at hour 8 and 18
      with labels "Morning peak" and "Evening peak"
    """
    t = result["t"]
    L = result["L"]
    grid_size = result["grid_size"]
    peak = result["peak_load_time"]

    peak_idx = int(np.argmin(np.abs(t - peak)))
    L_peak = L[peak_idx]

    pct_overloaded = 100.0 * np.sum(L > 0.7, axis=(1, 2)) / (grid_size * grid_size)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    im = ax1.imshow(L_peak, cmap="RdYlGn_r", vmin=0, vmax=1.2,
                     interpolation="bilinear", origin="upper")
    ax1.set_title(f"Peak Load (Hour {peak:.0f}:00)")
    ax1.set_xticks([])
    ax1.set_yticks([])
    plt.colorbar(im, ax=ax1, label="Load Level")

    ax2.plot(t, pct_overloaded, color="red")
    ax2.set_title("% Overloaded Stations Over 24h")
    ax2.set_xlabel("Hour of Day")
    ax2.set_ylabel("% Overloaded")
    ax2.axvline(8, color="gray", linestyle="--")
    ax2.text(8, ax2.get_ylim()[1] * 0.95, "Morning peak",
              rotation=90, va="top", ha="right", color="gray")
    ax2.axvline(18, color="gray", linestyle="--")
    ax2.text(18, ax2.get_ylim()[1] * 0.95, "Evening peak",
              rotation=90, va="top", ha="right", color="gray")

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"Saved to {save_path}")

    plt.show()

    return fig
