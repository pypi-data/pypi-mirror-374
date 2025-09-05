# -*- coding: utf-8 -*-
"""
Test the PCEGPR class in bayesvalidrox.
Class PCEGPR: 
    build_metamodel  - x
    update_metamodel
    add_input_space                                   -x
    fit
    eval_metamodel
    AutoVivification
    copy_meta_model_opts
    calculate_moments
    
"""

import sys
import numpy as np
import pytest

sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.input_space import InputSpace
from bayesvalidrox.surrogate_models.pce_gpr import PCEGPR


@pytest.fixture
def pce_gp():
    """
    Untrained PCEGPR with single input
    # TODO: also do multi-input!
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    samples = np.array([[0.2], [0.8]])
    meta_model = PCEGPR(inp)
    meta_model.CollocationPoints = samples
    meta_model.InputSpace = InputSpace(meta_model.input_obj, meta_model.meta_model_type)
    meta_model.InputSpace.init_param_space(np.max(meta_model.pce_deg))
    return meta_model


# %% Test constructor on its own


def test_constructor() -> None:
    """
    Construct PCE without inputs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    PCEGPR(inp)


# %% Test is_gaussian
def test_check_is_gaussian() -> None:
    """
    Check if Gaussian
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = PCEGPR(inp)
    meta_model.check_is_gaussian()
    assert meta_model.is_gaussian == True, "Expected is_gaussian to be True"


# %% Test build_metamodel


def test_build_metamodel(pce_gp) -> None:
    """
    Build PCE
    """
    mm = pce_gp
    mm.build_metamodel()


# %% Test add_input_space


def test_add_input_space(pce_gp) -> None:
    """
    Add InputSpace
    """
    pce_gp.add_input_space()


# %% Test fit
# Faster without these
def test_fit(pce_gp) -> None:
    """
    Fit PCE
    """
    pce_gp.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})


# def test_fit_parallel(pce_gp) -> None:
#     """
#     Fit PCE in parallel
#     """
#     pce_gp.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]}, parallel=True)


# def test_fit_verbose(pce_gp) -> None:
#     """
#     Fit PCE verbose
#     """
#     pce_gp.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]}, verbose=True)

# def test_fit_parallelverbose(pce_gp) -> None:
#     """
#     Fit PCE verbose
#     """
#     pce_gp.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]}, parallel = True, verbose=True)


# %% Test eval_metamodel


def test_eval_metamodel(pce_gp) -> None:
    """
    Eval trained PCE
    """
    mm = pce_gp
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_normalboots(pce_gp) -> None:
    """
    Eval trained PCE with normal bootstrap
    """
    mm = pce_gp
    mm.bootstrap_method = "normal"
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_highnormalboots(pce_gp) -> None:
    """
    Eval trained PCE with higher bootstrap-itrs
    """
    mm = pce_gp
    mm.n_bootstrap_itrs = 2
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_pca(pce_gp) -> None:
    """
    Eval trained PCE with pca
    """
    mm = pce_gp
    mm.dim_red_method = "pca"
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})
    mm.eval_metamodel([[0.4]])


# %% Test AutoVivification
def test_autovivification(pce_gp) -> None:
    """
    Creation of auto-vivification objects
    """
    pce_gp.AutoVivification()


# %% Test copy_meta_model_opts


def test_copy_meta_model_opts(pce_gp) -> None:
    """
    Copy the PCE with just some stats
    """
    pce_gp.copy_meta_model_opts()


# %% Test calculate_moments


def test_calculate_moments(pce_gp) -> None:
    """
    Calculate moments of a pce-surrogate
    """
    mm = pce_gp
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.calculate_moments()


def test_calculate_moments_pca(pce_gp) -> None:
    """
    Calculate moments of a pce-surrogate with pca
    """
    mm = pce_gp
    mm.dim_red_method = "pca"
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})
    mm.calculate_moments()
