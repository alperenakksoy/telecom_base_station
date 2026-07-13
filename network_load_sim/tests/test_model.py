"""
Tests for M_i (models/load_model.py) and KS_i (kernel/solver.py)
layers (Durán 2020).
"""

import numpy as np

from models.load_model import traffic_demand, load_ode, make_city_weights
from kernel.solver import solve_city


def test_morning_peak_higher_than_night():
    assert traffic_demand(8, center_weight=1.0) > traffic_demand(3, center_weight=1.0)


def test_evening_peak_higher_than_midday():
    assert traffic_demand(18) > traffic_demand(12)


def test_center_weight_scales_linearly():
    base = traffic_demand(10, center_weight=1.0)
    doubled = traffic_demand(10, center_weight=2.0)
    assert np.isclose(doubled, 2 * base)


def test_load_ode_decreases_when_load_high_and_mu_high():
    dL = load_ode(L=5.0, t=2.0, mu=1.2, center_weight=1.0)
    assert dL < 0


def test_load_ode_increases_at_zero_load_morning_peak():
    dL = load_ode(L=0.0, t=8.0, mu=1.2, center_weight=1.0)
    assert dL > 0


def test_city_weights_center_greater_than_edge():
    weights = make_city_weights(20)
    center = weights[10, 10]
    edge = weights[0, 0]
    assert center > edge


def test_city_weights_shape():
    weights = make_city_weights(20)
    assert weights.shape == (20, 20)


def test_city_weights_range():
    weights = make_city_weights(20)
    assert np.all(weights >= 0.3) and np.all(weights <= 1.6)


def test_solve_city_shape():
    result = solve_city(grid_size=5, n_steps=50)
    assert result["L"].shape == (50, 5, 5)


def test_solve_city_nonnegative():
    result = solve_city(grid_size=5, n_steps=50)
    assert np.all(result["L"] >= 0)


def test_solve_city_peak_load_time_range():
    result = solve_city(grid_size=5, n_steps=50)
    assert 6 <= result["peak_load_time"] <= 22
