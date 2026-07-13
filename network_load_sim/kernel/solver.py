"""
KS_i — Kernel simulation layer (Durán 2020).
Solves the load ODE for every base station
using scipy odeint. This is the recasting step.
"""

import numpy as np
from scipy.integrate import odeint

from models.load_model import load_ode, make_city_weights


def solve_city(grid_size: int = 20,
               mu: float = 1.2,
               t_max: float = 24.0,
               n_steps: int = 240,
               day_of_week: int = 0,
               density_scale: float = 1.0) -> dict:
    """
    Solves load ODE for all grid_size x grid_size
    base stations.

    For each station (i,j):
      - get center_weight from make_city_weights(), scaled by density_scale
      - solve load_ode with odeint from t=0 to t=t_max
      - initial condition L0 = 0.1 (low night load)

    n_steps: number of time points (240 = every 6 min)
    day_of_week: 0=Mon ... 6=Sun, shifts peak timing/amplitude
    density_scale: multiplier on city-center weight (traffic density)

    Returns dict:
    {
      "t": 1D array of time points (length n_steps),
      "L": 3D array shape (n_steps, grid_size, grid_size),
          L[k, i, j] = load of station (i,j) at time t[k]
      "weights": 2D array of center_weights,
      "grid_size": int,
      "mu": float,
      "day_of_week": int,
      "density_scale": float,
      "peak_load_time": float (hour of max avg load),
      "max_overloaded": int (max stations over 0.7 at any time)
    }
    """
    t = np.linspace(0, t_max, n_steps)
    weights = make_city_weights(grid_size) * density_scale
    L = np.zeros((n_steps, grid_size, grid_size))

    for i in range(grid_size):
        for j in range(grid_size):
            w = weights[i, j]
            sol = odeint(load_ode, 0.1, t, args=(mu, w, day_of_week))
            L[:, i, j] = sol[:, 0]

    mean_load = L.mean(axis=(1, 2))
    peak_load_time = float(t[np.argmax(mean_load)])
    max_overloaded = int(np.max(np.sum(L > 0.7, axis=(1, 2))))

    return {
        "t": t,
        "L": L,
        "weights": weights,
        "grid_size": grid_size,
        "mu": mu,
        "day_of_week": day_of_week,
        "density_scale": density_scale,
        "peak_load_time": peak_load_time,
        "max_overloaded": max_overloaded,
    }


if __name__ == "__main__":
    result = solve_city(grid_size=10, mu=1.2)
    print(f"Peak load at hour: {result['peak_load_time']:.1f}")
    print(f"Max overloaded stations: {result['max_overloaded']}")
    print(f"L shape: {result['L'].shape}")
