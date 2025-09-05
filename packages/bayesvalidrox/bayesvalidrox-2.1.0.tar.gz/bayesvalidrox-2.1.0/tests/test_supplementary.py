# -*- coding: utf-8 -*-
"""
Test the supplementary functions  in bayesvalidrox.
Tests are available for the following functions:
    check_ranges
    hellinger_distance
    subdomain
    create_psi
    corr_loocv_error
    kernel_rbf
    gelman_rubin
    
"""
import sys
import math
import numpy as np
import pytest

sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.input_space import InputSpace
from bayesvalidrox.surrogate_models.polynomial_chaos import PCE
from bayesvalidrox.surrogate_models.supplementary import (
    corr_loocv_error,
    create_psi,
    hellinger_distance,
    check_ranges,
    subdomain,
    kernel_rbf,
    gelman_rubin,
)


@pytest.fixture
def pce_inputspace():
    """
    PCE-Metamodel with input space
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    samples = np.array([[0.2], [0.8]])
    mm = PCE(inp)
    mm.CollocationPoints = samples
    mm.input_space = InputSpace(mm.input_obj, mm.meta_model_type)
    n_init_samples = samples.shape[0]
    mm.input_space.n_init_samples = n_init_samples
    mm.input_space.init_param_space(np.max(mm.pce_deg))
    return mm


# %% Test check_ranges


def test_check_ranges() -> None:
    """
    Check to see if theta lies in expected ranges
    """
    theta = [0.5, 1.2]
    ranges = [[0, 1], [1, 2]]
    assert check_ranges(theta, ranges) == True


def test_check_ranges_inv() -> None:
    """
    Check to see if theta lies not in expected ranges
    """
    theta = [1.5, 1.2]
    ranges = [[0, 1], [1, 2]]
    assert check_ranges(theta, ranges) == False


# %% Test hellinger_distance


def test_hellinger_distance_isnan() -> None:
    """
    Calculate Hellinger distance-nan
    """
    p = [0]
    q = [1]
    math.isnan(hellinger_distance(p, q))


def test_hellinger_distance_0() -> None:
    """
    Calculate Hellinger distance-0
    """
    p = [0, 1, 2]
    q = [1, 0, 2]
    assert hellinger_distance(p, q) == 0.0


def test_hellinger_distance_1() -> None:
    """
    Calculate Hellinger distance-1
    """
    p = [0, 1, 2]
    q = [0, 0, 0]
    assert hellinger_distance(p, q) == 1.0


# %% Test subdomain


def test_subdomain() -> None:
    """
    Create subdomains from bounds
    """
    subdomain([(0, 1), (0, 1)], 2)


# %% Test create_psi


def test_create_psi(pce_inputspace) -> None:
    """
    Create psi-matrix
    """
    mm = pce_inputspace
    samples = np.array([[0.2], [0.8]])
    mm.build_metamodel()

    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    create_psi(basis_indices, univ_bas)


# %% Test corr_loocv_error


def test_corr_loocv_error_nosparse(pce_inputspace) -> None:
    """
    Corrected loocv error
    """
    mm = pce_inputspace
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    outs = mm.regression(samples, outputs, psi)
    corr_loocv_error(outs["clf_poly"], outs["sparePsi"], outs["coeffs"], outputs)


def test_corr_loocv_error_singley(pce_inputspace) -> None:
    """
    Corrected loocv error
    """
    mm = pce_inputspace
    samples = np.array([[0.2]])
    outputs = np.array([0.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    outs = mm.regression(samples, outputs, psi)
    corr_loocv_error(outs["clf_poly"], outs["sparePsi"], outs["coeffs"], outputs)


def test_corr_loocv_error_sparse(pce_inputspace) -> None:
    """
    Corrected loocv error from sparse results
    """
    mm = pce_inputspace
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)
    mm.pce_reg_method = "ebl"

    outs = mm.regression(samples, outputs, psi, sparsity=True)
    corr_loocv_error(outs["clf_poly"], outs["sparePsi"], outs["coeffs"], outputs)


# %% Test _kernel_rbf


def test_kernel_rbf() -> None:
    """
    Create RBF kernel
    """
    X = [[0, 0], [1, 1.5]]
    pars = [1, 0.5, 1]
    kernel_rbf(X, pars)


def test_kernel_rbf_lesspar() -> None:
    """
    Create RBF kernel with too few parameters
    """
    X = [[0, 0], [1, 1.5]]
    pars = [1, 2]
    with pytest.raises(AttributeError) as excinfo:
        kernel_rbf(X, pars)
    assert str(excinfo.value) == "Provide 3 parameters for the RBF kernel!"


# %% Test gelmain_rubin


def test_gelman_rubin() -> None:
    """
    Calculate gelman-rubin
    """
    chain = [[[1], [2]]]
    gelman_rubin(chain)


def test_gelman_rubin_returnvar() -> None:
    """
    Calculate gelman-rubin returning var
    """
    chain = [[[1], [2]]]
    gelman_rubin(chain, return_var=True)
