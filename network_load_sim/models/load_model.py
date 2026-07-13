"""
M_i — Mathematical model layer (Durán 2020).
Defines the ODE for base station traffic load
and the time-varying traffic demand function.
"""

import numpy as np

DEFAULT_GRID = 20       # 20x20 city grid
DEFAULT_MU = 1.2        # network capacity
DEFAULT_T_MAX = 24.0    # 24 hours

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Weekday vs weekend peak profile: (morning_hour, morning_amp, evening_hour, evening_amp, night_base)
WEEKDAY_PROFILE = (8, 0.6, 18, 0.9, 0.1)
WEEKEND_PROFILE = (11, 0.3, 20, 0.6, 0.15)


def traffic_demand(t: float, center_weight: float = 1.0, day_of_week: int = 0) -> float:
    """
    Returns traffic demand at hour t (0-24).
    Models two daily peaks: morning and evening.
    center_weight: city center stations get higher demand.
    day_of_week: 0=Mon ... 4=Fri (weekday profile, morning 8h/evening 18h),
                 5=Sat, 6=Sun (weekend profile: later, lower peaks).
    """
    is_weekend = day_of_week >= 5
    morning_hour, morning_amp, evening_hour, evening_amp, night = (
        WEEKEND_PROFILE if is_weekend else WEEKDAY_PROFILE
    )
    morning = morning_amp * np.exp(-((t - morning_hour) ** 2) / 4)
    evening = evening_amp * np.exp(-((t - evening_hour) ** 2) / 6)
    return (morning + evening + night) * center_weight


def load_ode(L: float, t: float, mu: float, center_weight: float, day_of_week: int = 0) -> float:
    """
    ODE for base station load:
    dL/dt = lambda(t) - mu * L

    L   = current load (0 to 1+)
    t   = time in hours
    mu  = network processing capacity
    center_weight = traffic multiplier for location
    day_of_week = 0=Mon ... 6=Sun, shifts peak timing/amplitude
    Returns: dL/dt
    """
    lam = traffic_demand(t, center_weight, day_of_week)
    return lam - mu * L


def make_city_weights(grid_size: int) -> np.ndarray:
    """
    Creates a grid_size x grid_size array of
    center_weight values.
    City center (middle) has weight 1.5.
    Suburbs (edges) have weight 0.4.
    Uses Gaussian distribution centered at grid middle.
    Returns: 2D numpy array of weights.
    """
    cx, cy = grid_size // 2, grid_size // 2
    x = np.arange(grid_size)
    y = np.arange(grid_size)
    xx, yy = np.meshgrid(x, y)
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    sigma = grid_size / 3
    weights = 0.4 + 1.1 * np.exp(-dist ** 2 / (2 * sigma ** 2))
    return weights
