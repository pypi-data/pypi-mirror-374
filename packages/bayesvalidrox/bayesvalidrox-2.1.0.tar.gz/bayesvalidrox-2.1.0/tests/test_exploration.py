# -*- coding: utf-8 -*-
"""
Test the Exploration class for bayesvalidrox

Tests are available for the following functions
class Exploration:
    get_exploration_samples
    ger_vornoi_samples
    get_mc_samples
    approximate_voronoi
    _build_dist_matrix_point

"""

import sys
import pytest
import numpy as np

sys.path.append("src/")
sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.exploration import Exploration


@pytest.fixture
def expdesign():
    """
    Generates basic exp-design
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    inp.add_marginals()
    inp.marginals[1].dist_type = "normal"
    inp.marginals[1].parameters = [0, 1]

    expdes = ExpDesigns(inp, sampling_method="random")
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.x = np.array([[0, 0], [1, 0], [0.5, 1]])
    return expdes


# %% Test Exploration init


def test_exploration(expdesign) -> None:
    """
    Init Exploration object
    """
    explore = Exploration(expdesign, 10)
    assert isinstance(explore, Exploration)
    assert explore.n_candidates == 10
    assert explore.mc_criterion == "mc-intersite-proj-th"
    assert explore.verbose == False


# %% Test get_exploration_samples


def test_get_exploration_samples(expdesign) -> None:
    """
    Generate exploration samples
    """
    explore = Exploration(expdesign, 10)

    # With voronoi
    explore.exp_design.explore_method = "voronoi"
    n_samples = explore.n_candidates * explore.exp_design.x.shape[0]
    samples, scores = explore.get_exploration_samples()
    assert samples.shape == (n_samples, 2)
    assert scores.shape == (explore.exp_design.x.shape[0],)

    # Run with random
    explore.exp_design.explore_method = "random"
    samples, scores = explore.get_exploration_samples()
    assert samples.shape == (explore.n_candidates, 2)
    assert scores.shape == (explore.n_candidates,)


# %% Test get_vornoi_samples


def test_get_vornoi_samples(expdesign) -> None:
    """
    Generate voronoi samples
    """
    explore = Exploration(expdesign, 10)
    # Number of generated samples: n_candidates*old_n_xtrain
    n_samples = explore.n_candidates * explore.exp_design.x.shape[0]

    # Standard settings
    samples, scores = explore.get_vornoi_samples()
    assert samples.shape == (n_samples, 2)
    assert scores.shape == (explore.exp_design.x.shape[0],)

    # Other mc option
    explore.mc_criterion = "mc-intersite-proj"
    samples, scores = explore.get_vornoi_samples()
    assert samples.shape == (n_samples, 2)
    assert scores.shape == (explore.exp_design.x.shape[0],)


# %% Test get_mc_samples


def test_get_mc_samples(expdesign) -> None:
    """
    Create mc samples
    """
    explore = Exploration(expdesign, 10)
    # Number of generated samples: n_candidates
    n_samples = explore.n_candidates

    # MC type 1
    explore.mc_criterion = "mc-intersite-proj"
    samples, scores = explore.get_mc_samples()
    assert samples.shape == (n_samples, 2)
    assert scores.shape == (n_samples,)

    # Other mc option
    explore.mc_criterion = "mc-intersite-proj-th"
    samples, scores = explore.get_mc_samples()
    assert samples.shape == (n_samples, 2)
    assert scores.shape == (n_samples,)


# %% Test approximate_voronoi():


def test_approximate_voronoi(expdesign) -> None:
    """
    Run voronoi approx
    """
    explore = Exploration(expdesign, 10)
    samples = np.array([[1, 1], [0, 0], [0.5, 0.5]])

    areas = explore.approximate_voronoi(samples)

    assert areas.shape[0] == samples.shape[0]
    assert len(explore.closest_points) == samples.shape[0]
    assert (
        explore.closest_points[0].shape[0]
        + explore.closest_points[1].shape[0]
        + explore.closest_points[2].shape[0]
        == explore.w * samples.shape[0]
    )
    assert explore.closest_points[0].shape[1] == samples.shape[1]


# %% Test _build_dist_matrix_point


def test_build_dist_matrix_point(expdesign) -> None:
    """
    Calculate intersite distance of points to point.
    """
    explore = Exploration(expdesign, 10)
    samples = np.array([[1, 1], [0, 0]])
    point = np.array([1, 1])

    # Run with standard settings
    dist = explore._build_dist_matrix_point(samples, point)
    assert dist[0][0] == 0
    assert dist[1][0] == pytest.approx(2, abs=0.001)

    # Run with square root
    dist = explore._build_dist_matrix_point(samples, point, do_sqrt=True)
    assert dist[0][0] == 0
    assert dist[1][0] == pytest.approx(np.sqrt(2), abs=0.001)
