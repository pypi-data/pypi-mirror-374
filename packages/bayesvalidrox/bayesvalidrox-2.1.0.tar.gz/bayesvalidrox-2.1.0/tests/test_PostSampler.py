# -*- coding: utf-8 -*-
"""
Test the BayesInference class for bayesvalidrox

Tests are available for the following functions
class PostSampler:
    run_sampler       
    normpdf
    _corr_factor_bme
    calculate_loglik_logbme
"""

import sys
import pytest
import numpy as np

sys.path.append("src/")
sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.polynomial_chaos import PCE
from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.surrogate_models.engine import Engine
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy
from bayesvalidrox.bayes_inference.post_sampler import PostSampler


@pytest.fixture
def basic_engine_trained():
    """
    Engine with trained PCE
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp, sampling_method="user")
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.x = np.array([[0], [1], [0.5]])
    expdes.y = {"Z": [[0.4], [0.5], [0.45]]}
    expdes.x_values = np.array([0])

    mm = PCE(inp)
    mod = PL()
    mod.observations = {"Z": np.array([0.45]), "x_values": np.array([0])}
    mod.output.names = ["Z"]

    engine = Engine(mm, mod, expdes)
    engine.train_normal()

    return engine


# %% Test PostSampler init


def test_postsampler() -> None:
    """
    Construct a PostSampler object
    """
    PostSampler()


def test_normpdf() -> None:
    """
    Run basic normpdf.
    """
    outputs = {"Z": np.array([[0]])}

    observations = {"Z": np.array([0.45]), "x_values": np.array([0])}
    disc = Discrepancy("Gaussian", observations)
    disc.build_discrepancy()

    sam = PostSampler()
    sam.discrepancy = disc
    sam.out_names = ["Z"]
    sam.observation = outputs
    sam.normpdf(outputs)
    # TODO: what would be the normpdf of data on data?


# %% Test corr_factor_BME


def test_corr_factor_bme() -> None:
    """
    Calculate correction factor
    """
    obs_data = {"Z": np.array([[0.45]])}
    log_bme = [0]
    samples = np.array([[0]])
    outputs = {"Z": np.array([[0]])}

    observations = {"Z": np.array([0.45]), "x_values": np.array([0])}
    disc = Discrepancy("Gaussian", observations)
    disc.build_discrepancy()

    sam = PostSampler()
    sam.discrepancy = disc
    sam.out_names = ["Z"]
    sam.observation = outputs
    sam._corr_factor_bme(
        samples, model_outputs=obs_data, metamod_outputs=obs_data, log_bme=log_bme
    )
    # TODO: what would be the correction for data on data?


def test_corr_factor_bme_selectedindices() -> None:
    """
    Calculate correction factor for given indices
    """
    obs_data = {"Z": np.array([[0.45]])}
    log_bme = [0]
    samples = np.array([[0]])
    outputs = {"Z": np.array([[0]])}

    observations = {"Z": np.array([0.45]), "x_values": np.array([0])}
    disc = Discrepancy("Gaussian", observations)
    disc.build_discrepancy()

    sam = PostSampler()
    sam.discrepancy = disc
    sam.out_names = ["Z"]
    sam.observation = outputs
    sam.selected_indices = {"Z": [0]}  # TODO: check for the form of these somewhere?
    sam._corr_factor_bme(
        samples, model_outputs=obs_data, metamod_outputs=obs_data, log_bme=log_bme
    )
