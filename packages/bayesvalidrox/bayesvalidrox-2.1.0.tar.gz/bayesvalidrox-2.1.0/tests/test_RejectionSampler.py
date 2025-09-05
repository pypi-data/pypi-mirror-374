# -*- coding: utf-8 -*-
"""
Test the BayesInference class for bayesvalidrox

Tests are available for the following functions
class RejectionSampler:
    serun_sampler
    calculate_valid_metrics
"""

import sys
import numpy as np

sys.path.append("src/")
sys.path.append("../src/")

from bayesvalidrox.bayes_inference.rejection_sampler import RejectionSampler


# %% Test MCMC init


def test_rejectionsampler() -> None:
    """
    Construct a RejectionSampler object
    """
    RejectionSampler()


# %% Test rejection_sampling
def test_rejection_sampling_nologlik() -> None:
    """
    Perform rejection sampling without given log likelihood
    """
    rej = RejectionSampler()
    rej.prior_samples = np.array([[0, 0, 1]])
    rej.log_likes = np.array([[1]])
    rej.run_sampler()
