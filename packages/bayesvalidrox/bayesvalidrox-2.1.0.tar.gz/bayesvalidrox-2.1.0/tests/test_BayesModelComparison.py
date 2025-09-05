# -*- coding: utf-8 -*-
"""
Test the BayesModelComparison class in bayesvalidrox.
Tests are available for the following functions
Class BayesModelComparison: 
    create_model_comparison
    compare_models
    generate_dataset
    __perturb_data
    cal_model_weight
    plot_just_analysis
    plot_model_weights
    plot_bayes_factor
    
"""
import sys

sys.path.append("src/")
# import pytest
# import numpy as np

from bayesvalidrox.bayes_inference.bayes_model_comparison import BayesModelComparison

# from bayesvalidrox.surrogate_models.input_space import InputSpace


def test_bmc() -> None:
    """
    Build BMC without inputs
    """
    BayesModelComparison(None, None)
