# Ahmet Alperen Aksoy - 38421

# Telecom Base Station Load Simulation

# Telecom companies need to know which base stations will get overloaded and at what time, before it actually happens on a live network.

import numpy as np

DEFAULT_GRID = 20       # 20x20 city grid
DEFAULT_MU = 1.2        # Base station network capacity
DEFAULT_T_MAX = 24.0    # 24 hours, each seconds represents hour

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Weekday vs weekend peak profile:
# (morning_hour, morning_amplitude, morning_lambda,
#  evening_hour, evening_amplitude, evening_lambda, night_base)

# amplitude,  how high the morning peak reaches.
# lambda is decay rate, controls how sharply traffic rises/falls around the peak.
# Larger lambda = sharper peak (faster decay away from peak hour).
# This is the decay constant from exponential decay: exp(-lambda * |t - t_peak|)

WEEKDAY_PROFILE = (8,  0.6, 0.5,   18, 0.9, 0.4,   0.1)
WEEKEND_PROFILE = (11, 0.3, 0.35,  20, 0.6, 0.3,   0.15)

def make_city_weights(grid_size: int) -> np.ndarray:
    """
    exponential decay

    How much traffic does each station attract based on where it is in the city?

      Uses exponential decay with distance from center:
        weight(i,j) = 0.4 + 1.1 * exp(-decay_rate * dist)

    City center base stations handle much higher traffic because they serve dense areas with offices, shops, and transport hubs,
     while suburban stations serve fewer users and therefore experience lower traffic.

    Creates a grid_size x grid_size array of center_weight values.
    City center (middle) has weight ~1.5.
    Suburbs (edges) have weight ~0.4.
    Here distance plays the role of time, and decay_rate = lambda.


    Returns: 2D numpy array of weights.
    """
    cx, cy = grid_size // 2, grid_size // 2
    x = np.arange(grid_size)
    y = np.arange(grid_size)
    xx, yy = np.meshgrid(x, y)
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    decay_rate = 3.0 / grid_size   # controls how fast weight drops with distance
    weights = 0.4 + 1.1 * np.exp(-decay_rate * dist)
    return weights

def traffic_demand(t: float, center_weight: float = 1.0, day_of_week: int = 0) -> float:
    """
    At this specific hour of the day, how much traffic is arriving at this specific station?

    Uses exponential decay form: amp * exp(-lam * |t - t_peak|)

    λ(t) = amp × exp(−λ × |t − t_pik|) × weight

    center_weight: city center stations receive higher demand.
    day_of_week: 0=Mon...4=Fri weekday profile,
                 5=Sat, 6=Sun weekend profile.
    """
    is_weekend = day_of_week >= 5
    (morning_hour, morning_amp, morning_lam,
     evening_hour, evening_amp, evening_lam,
     night) = WEEKEND_PROFILE if is_weekend else WEEKDAY_PROFILE

    morning = morning_amp * np.exp(-morning_lam * abs(t - morning_hour))
    evening = evening_amp * np.exp(-evening_lam * abs(t - evening_hour))
    return (morning + evening + night) * center_weight


def load_ode(L: float, t: float, mu: float, center_weight: float, day_of_week: int = 0) -> float:
    """
    Is this station's load increasing or decreasing right now?

    ODE for base station load:

    dL/dt = lambda(t) - mu * L

    dL/dt → the rate of change of load
    L   = the current load. How full the station is right now.
    t   = time in hours
    mu  = network processing capacity
    mu * L =  the traffic the station can currently process.

    Returns: dL/dt
    """
    lam = traffic_demand(t, center_weight, day_of_week)
    return lam - mu * L
