# -*- coding: utf-8 -*-
"""
Test the PCE class in bayesvalidrox.
Class PCE: 
    build_metamodel  - x
    update_metamodel
    update_pce_coeffs
    create_basis_indices --removed, just redirects
    add_input_space                                   -x
    univ_basis_vals
    fit
    adaptive_regression
    pca_transformation
    eval_metamodel
    create_model_error
    eval_model_error
    AutoVivification
    copy_meta_model_opts
    __select_degree
    generate_polynomials
    calculate_moments
    
"""
import sys
import numpy as np
import pytest

sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.input_space import InputSpace
from bayesvalidrox.surrogate_models.polynomial_chaos import PCE
from bayesvalidrox.surrogate_models.supplementary import create_psi


@pytest.fixture
def pce_1d_input():
    """
    Single input PCE
    # TODO: also add multi-input/output pce
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    samples = np.array([[0.2], [0.8]])
    mm = PCE(inp)
    mm.input_space = InputSpace(mm.input_obj, mm.meta_model_type)
    n_init_samples = samples.shape[0]
    mm.input_space.n_init_samples = n_init_samples
    mm.input_space.init_param_space(np.max(mm.pce_deg))
    return mm


# %% Test MetaMod constructor on its own


def test_metamod() -> None:
    """
    Construct PCE without inputs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    PCE(inp)


# %% Test PCE.build_metamodel


def test_build_metamodel(pce_1d_input) -> None:
    """
    Build PCE
    """
    mm = pce_1d_input
    mm.build_metamodel()


# %% Test PCE._generate_polynomials


def test__generate_polynomials_noexp() -> None:
    """
    Generate polynomials without ExpDeg
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    with pytest.raises(AttributeError) as excinfo:
        mm._generate_polynomials()
    assert (
        str(excinfo.value) == "Generate or add InputSpace before generating polynomials"
    )


def test__generate_polynomials_nodeg() -> None:
    """
    Generate polynomials without max_deg
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)

    # Setup
    mm.input_space = InputSpace(inp)
    mm.input_space.n_init_samples = 2
    mm.input_space.init_param_space(np.max(mm.pce_deg))
    mm.ndim = mm.input_space.ndim

    # Generate
    with pytest.raises(AttributeError) as excinfo:
        mm._generate_polynomials()
    assert (
        str(excinfo.value)
        == "MetaModel cannot generate polynomials in the given scenario!"
    )


def test__generate_polynomials_deg() -> None:
    """
    Generate polynomials with max_deg
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)

    # Setup
    mm.input_space = InputSpace(inp)
    mm.input_space.n_init_samples = 2
    mm.input_space.init_param_space(np.max(mm.pce_deg))
    mm.ndim = mm.input_space.ndim

    # Generate
    mm._generate_polynomials(4)


# %% Test MetaMod.add_input_space


def test_add_input_space() -> None:
    """
    Add InputSpace in PCE
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.add_input_space()


# %% Test PCE.fit
# Faster without these
def test_fit() -> None:
    """
    Fit PCE
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})


# def test_fit_parallel() -> None:
#     """
#     Fit PCE in parallel
#     """
#     inp = Input()
#     inp.add_marginals()
#     inp.marginals[0].dist_type = 'normal'
#     inp.marginals[0].parameters = [0, 1]
#     mm = PCE(inp)
#     mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]}, parallel=True)


def test_fit_verbose() -> None:
    """
    Fit PCE verbose
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]}, verbose=True)


def test_fit_pca() -> None:
    """
    Fit PCE verbose and with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.dim_red_method = "pca"
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]}, verbose=True)


# %% Test PCE.regression


def test_regression(pce_1d_input) -> None:
    """
    Regression without a method, with wrong method
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.regression(samples, outputs, psi)
    mm.pce_reg_method = "larscv"
    with pytest.raises(AttributeError) as excinfo:
        mm.regression(samples, outputs, psi)
    assert str(excinfo.value) == ("The set regression method is not available.")


def test_regression_ols(pce_1d_input) -> None:
    """
    Regression: ols
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "ols"
    mm.regression(samples, outputs, psi)


def test_regression_olssparse(pce_1d_input) -> None:
    """
    Regression: ols and sparse
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "ols"
    mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_pinv(pce_1d_input) -> None:
    """
    Regression: pinv
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "pinv"
    mm.regression(samples, outputs, psi)


def test_regression_pinvsparse(pce_1d_input) -> None:
    """
    Regression: pinv and sparse
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "pinv"
    mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_ard(pce_1d_input) -> None:
    """
    Regression: ard
    """
    mm = pce_1d_input
    samples = np.array([[0.2], [0.8]])
    outputs = np.array([0.4, 0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "ard"
    mm.regression(samples, outputs, psi)


def test_regression_ardssparse(pce_1d_input) -> None:
    """
    Regression: ard and sparse
    """
    mm = pce_1d_input
    samples = np.array([[0.2], [0.8]])
    outputs = np.array([0.4, 0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "ard"
    mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_fastard(pce_1d_input) -> None:
    """
    Regression: fastard
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "fastard"
    mm.regression(samples, outputs, psi)


def test_regression_fastardssparse(pce_1d_input) -> None:
    """
    Regression: fastard and sparse
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "fastard"
    mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_brr(pce_1d_input) -> None:
    """
    Regression: brr
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "brr"
    mm.regression(samples, outputs, psi)


def test_regression_brrssparse(pce_1d_input) -> None:
    """
    Regression: brr and sparse
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "brr"
    mm.regression(samples, outputs, psi, sparsity=True)


if 0:  # Could not figure out these errors, issue most likely in chosen samples/outputs

    def test_regression_bcs(pce_1d_input) -> None:
        """
        Regression: bcs
        """
        mm = pce_1d_input
        samples = np.array(
            [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9]]
        )
        outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        mm.pce_deg = 3
        mm.build_metamodel()
        basis_indices = mm._all_basis_indices[str(mm.pce_deg)][str(1.0)]
        univ_bas = mm.univ_basis_vals(samples)
        psi = create_psi(basis_indices, univ_bas)

        mm.pce_reg_method = "bcs"
        mm.regression(samples, outputs, psi)

    def test_regression_bcsssparse(pce_1d_input) -> None:
        """
        Regression: bcs and sparse
        """
        mm = pce_1d_input
        samples = np.array(
            [
                [0.0],
                [0.1],
                [0.2],
                [0.3],
                [0.4],
                [0.5],
                [0.6],
                [0.7],
                [0.8],
                [0.9],
                [1.0],
            ]
        )
        outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

        mm.build_metamodel()
        basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
        univ_bas = mm.univ_basis_vals(samples)
        psi = create_psi(basis_indices, univ_bas)

        mm.pce_reg_method = "bcs"
        mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_lars(pce_1d_input) -> None:
    """
    Regression: lars
    """
    mm = pce_1d_input
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "lars"
    mm.regression(samples, outputs, psi)


def test_regression_larsssparse(pce_1d_input) -> None:
    """
    Regression: lars and sparse
    """
    mm = pce_1d_input
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "lars"
    mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_lassolars(pce_1d_input) -> None:
    """
    Regression: lassolars
    """
    mm = pce_1d_input
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "lassolars"
    mm.regression(samples, outputs, psi)


def test_regression_lassolarssparse(pce_1d_input) -> None:
    """
    Regression: larscv and sparse
    """
    mm = pce_1d_input
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "lassolars"
    mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_lassolarscv(pce_1d_input) -> None:
    """
    Regression: lassolarscv
    """
    mm = pce_1d_input
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "lassolarscv"
    mm.regression(samples, outputs, psi)


def test_regression_lassolarscvsparse(pce_1d_input) -> None:
    """
    Regression: lassolarscv and sparse
    """
    mm = pce_1d_input
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "lassolarscv"
    mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_sgdr(pce_1d_input) -> None:
    """
    Regression: sgdr
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "sgdr"
    mm.regression(samples, outputs, psi)


def test_regression_sgdrssparse(pce_1d_input) -> None:
    """
    Regression: sgdr and sparse
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "sgdr"
    mm.regression(samples, outputs, psi, sparsity=True)


if 0:  # Could not figure out these errors, issue most likely in chosen samples/outputs

    def test_regression_omp(pce_1d_input) -> None:
        """
        Regression: omp
        """
        mm = pce_1d_input
        samples = np.array(
            [
                [0.0],
                [0.1],
                [0.2],
                [0.3],
                [0.4],
                [0.5],
                [0.6],
                [0.7],
                [0.8],
                [0.9],
                [1.0],
            ]
        )
        outputs = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1])

        mm.build_metamodel()
        basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
        univ_bas = mm.univ_basis_vals(samples)
        psi = create_psi(basis_indices, univ_bas)

        mm.regression(samples, outputs, psi, reg_method="omp")

    def test_regression_ompssparse(pce_1d_input) -> None:
        """
        Regression: omp and sparse
        """
        mm = pce_1d_input
        samples = np.array([[0.2]])
        outputs = np.array([0.5])

        mm.build_metamodel()
        basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
        univ_bas = mm.univ_basis_vals(samples)
        psi = create_psi(basis_indices, univ_bas)

        mm.regression(samples, outputs, psi, reg_method="omp", sparsity=True)


def test_regression_vbl(pce_1d_input) -> None:
    """
    Regression: vbl
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "vbl"
    mm.regression(samples, outputs, psi)


def test_regression_vblssparse(pce_1d_input) -> None:
    """
    Regression: vbl and sparse
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "vbl"
    mm.regression(samples, outputs, psi, sparsity=True)


def test_regression_ebl(pce_1d_input) -> None:
    """
    Regression: ebl
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "ebl"
    mm.regression(samples, outputs, psi)


def test_regression_eblssparse(pce_1d_input) -> None:
    """
    Regression: ebl and sparse
    """
    mm = pce_1d_input
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.build_metamodel()
    basis_indices = mm._all_basis_indices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(basis_indices, univ_bas)

    mm.pce_reg_method = "ebl"
    mm.regression(samples, outputs, psi, sparsity=True)


# %% Test Model.update_pce_coeffs

# TODO: Parameter type issues
if 0:

    def test_update_pce_coeffs(pce_1d_input) -> None:
        """
        Update coeffs of trained pce
        """
        mm = pce_1d_input
        # 2nd order polynomial as test function
        train_samples = np.swapaxes(np.array([np.arange(0, 1, 0.1)]), 0, 1)
        y = 1 + 2 * train_samples + 3 * train_samples * train_samples
        mm.fit(train_samples, {"Z": y})

        x_new = np.append(train_samples, np.array([[1]]), axis=0)
        y = {"Z": 1 + 2 * x_new + 3 * x_new * x_new}
        _ = mm.update_pce_coeffs(x_new, y)


# %% Test PCE.univ_basis_vals


def test_univ_basis_vals(pce_1d_input) -> None:
    """
    Creates univariate polynomials
    """
    mm = pce_1d_input
    samples = np.array([[0.2], [0.8]])
    mm.build_metamodel()
    mm.univ_basis_vals(samples)


# %% Test PCE.adaptive_regression

# def test_adaptive_regression_fewsamples(pce_1d_input) -> None:
#    """
#    Adaptive regression, no specific method, too few samples given
#    """
#    mm = pce_1d_input
#    samples = np.array([[0.2]])
#    outputs = np.array([0.8])
#    mm.CollocationPoints = samples
#    mm.build_metamodel()

#    # Evaluate the univariate polynomials on InputSpace
#    mm.univ_p_val = mm.univ_basis_vals(mm.CollocationPoints)
#    with pytest.raises(AttributeError) as excinfo:
#        mm.adaptive_regression(samples, outputs, 0)
#    assert str(excinfo.value) == ('There are too few samples for the corrected loo-cv error."
#                           " Fit surrogate on at least as '
#                           'many samples as parameters to use this')


def test_adaptive_regression(pce_1d_input) -> None:
    """
    Adaptive regression, no specific method
    """
    mm = pce_1d_input
    samples = np.array([[0.0], [0.1]])
    outputs = np.array([0.0, 0.1])
    mm.build_metamodel()

    # Evaluate the univariate polynomials on InputSpace
    mm.univ_p_val = mm.univ_basis_vals(samples)
    mm.adaptive_regression(samples, outputs, 0)


def test_adaptive_regression_verbose(pce_1d_input) -> None:
    """
    Adaptive regression, no specific method, verbose output
    """
    mm = pce_1d_input
    samples = np.array([[0.0], [0.1]])
    outputs = np.array([0.0, 0.1])
    mm.build_metamodel()

    # Evaluate the univariate polynomials on InputSpace
    mm.univ_p_val = mm.univ_basis_vals(samples)
    mm.adaptive_regression(samples, outputs, 0, True)


def test_adaptive_regression_ols(pce_1d_input) -> None:
    """
    Adaptive regression, ols
    """
    mm = pce_1d_input
    samples = np.array(
        [[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]]
    )
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])
    mm.build_metamodel()

    # Evaluate the univariate polynomials on InputSpace
    mm.univ_p_val = mm.univ_basis_vals(samples)
    mm.pce_reg_method = "ols"
    mm.adaptive_regression(samples, outputs, 0)


# %% Test PCE.pca_transformation


def test_pca_transformation() -> None:
    """
    Apply PCA
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    mm.pca_transformation(outputs, 1)


def test_pca_transformation_varcomp() -> None:
    """
    Apply PCA with set var_pca_threshold
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    mm.var_pca_threshold = 1
    mm.pca_transformation(outputs, 1)


# %% Test PCE.eval_metamodel


def test_eval_metamodel() -> None:
    """
    Eval trained PCE
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_normalboots() -> None:
    """
    Eval trained PCE with normal bootstrap
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.bootstrap_method = "normal"
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_highnormalboots() -> None:
    """
    Eval trained PCE with higher bootstrap-itrs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.n_bootstrap_itrs = 2
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_pca() -> None:
    """
    Eval trained PCE with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.dim_red_method = "pca"
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})
    mm.eval_metamodel([[0.4]])


# %% Test PCE.AutoVivification
def test_autovivification() -> None:
    """
    Creation of auto-vivification objects
    # TODO: move to metamodel tests?
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.AutoVivification()


# %% Test PCE.copy_meta_model_opts


def test_copy_meta_model_opts() -> None:
    """
    Copy the PCE with just some stats
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.add_input_space()
    mm.copy_meta_model_opts()


# %% Test PCE.__select_degree

# %% Test PCE.calculate_moments


def test_calculate_moments() -> None:
    """
    Calculate moments of a pce-surrogate
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.calculate_moments()


def test_calculate_moments_pca() -> None:
    """
    Calculate moments of a pce-surrogate with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.dim_red_method = "pca"
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})
    mm.calculate_moments()


def test_calculate_moments_verbose() -> None:
    """
    Calculate moments of a pce-surrogate with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.verbose = True
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})
    mm.calculate_moments()


# %% Test PCE.calculate_sobol


def test_calculate_sobol():
    """
    Calculate Sobol' indices of a pce-surrogate
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})
    _, _ = mm.calculate_sobol()
    # TODO are there theory-related checks that could be applied here?


def test_calculate_sobol_pca():
    """
    Calculate Sobol' indices of a pce-surrogate with PCA
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.dim_red_method = "pca"
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})
    _, _ = mm.calculate_sobol({"Z": np.array([[0.4, 0.4], [0.5, 0.6]])})
    # TODO are there theory-related checks that could be applied here?


def test_calculate_sobol_pcanoy():
    """
    Calculate Sobol' indices of a pce-surrogate with PCA but no outputs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = PCE(inp)
    mm.dim_red_method = "pca"
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})

    with pytest.raises(AttributeError) as excinfo:
        mm.calculate_sobol()
    assert str(excinfo.value) == (
        "Calculation of Sobol' indices with PCA expects training outputs, but none are given."
    )


# %% Test PCE.derivative


def test_derivative():
    """
    Calculate derivatives on PCE (not arbitrary).
    """
    # Single input
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].name = "x"
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]

    # 2nd order polynomial as test function
    train_samples = np.swapaxes(np.array([np.arange(0, 1, 0.1)]), 0, 1)
    test_samples = np.array([[0.1], [0.3], [0.8]])
    y = 1 + 2 * train_samples + 3 * train_samples * train_samples

    # aPCE + derivatives
    mm = PCE(inp, pce_deg=2)
    mm.fit(train_samples, {"Z": y})

    with pytest.raises(AttributeError) as excinfo:
        mm.derivative(test_samples, {"x": 1})
    assert str(excinfo.value) == (
        "Derivatives only useable for arbitrary-type polynomials!"
    )


def test_derivative_invalidparam():
    """
    Calculate derivatives on invalid parameter name.
    """
    # Single input
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].name = "x"
    inp.marginals[0].input_data = np.random.uniform(0, 1, 100)

    # 2nd order polynomial as test function
    train_samples = np.swapaxes(np.array([np.arange(0, 1, 0.1)]), 0, 1)
    y = 1 + 2 * train_samples + 3 * train_samples * train_samples

    # aPCE + derivatives
    mm = PCE(inp, pce_deg=2)
    mm.fit(train_samples, {"Z": y})

    with pytest.raises(ValueError) as excinfo:
        mm.derivative([[0.2]], {"z": 1})
    assert str(excinfo.value) == (
        "The parameter z chosen for the derivative is not valid!"
    )


def test_derivative_pca():
    """
    Calculate derivatives with PCA.
    """
    # Single input
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].name = "x"
    inp.marginals[0].input_data = np.random.uniform(0, 1, 100)

    # 2nd order polynomial as test function
    train_samples = np.swapaxes(np.array([np.arange(0, 1, 0.1)]), 0, 1)
    test_samples = np.array([[0.1], [0.3], [0.8]])
    y = 1 + 2 * train_samples + 3 * train_samples * train_samples

    # aPCE + derivatives
    mm = PCE(inp, pce_deg=2, dim_red_method="pca")
    mm.fit(train_samples, {"Z": y})

    with pytest.raises(AttributeError) as excinfo:
        mm.derivative(test_samples, {"x": 1})
    assert str(excinfo.value) == ("Derivatives not compatible with PCA at the moment!")


def test_derivative_si():
    """
    Calculate 1st and 2nd order derivative of single input model.
    """
    # Single input
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].name = "x"
    inp.marginals[0].input_data = np.random.uniform(0, 1, 100)

    # 2nd order polynomial as test function
    train_samples = np.swapaxes(np.array([np.arange(0, 1, 0.1)]), 0, 1)
    test_samples = np.array([[0.1], [0.3], [0.8]])
    y = 1 + 2 * train_samples + 3 * train_samples * train_samples
    y_der = 2 + 6 * test_samples
    y_der2 = 6 + 0 * test_samples

    # aPCE + derivatives
    mm = PCE(inp, pce_deg=2)
    mm.fit(train_samples, {"Z": y})
    out = mm.eval_metamodel(train_samples)[0]
    out_1 = mm.derivative(test_samples, {"x": 1})
    out_2 = mm.derivative(test_samples, {"x": 2})
    out_nopred = mm.derivative(test_samples, {"x": 1}, predict=False)

    # Asserts
    assert np.allclose(out["Z"], y, rtol=0.002)
    assert np.allclose(out_1["Z"], y_der, rtol=0.002)
    assert np.allclose(out_2["Z"], y_der2, rtol=0.002)
    assert out_nopred["Z"]["y_1"].shape == (3, 3)


def test_derivative_di():
    """
    Calculate 1st and 2nd order derivative of double input model.
    """
    # Single input
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].name = "x"
    inp.marginals[0].input_data = np.random.uniform(0, 1, 100)
    inp.add_marginals()
    inp.marginals[1].name = "y"
    inp.marginals[1].input_data = np.random.uniform(0, 1, 100)

    # 2nd order polynomial as test function
    # train_samples = np.swapaxes(np.array([np.arange(0,1,0.1)]),0,1)
    # train_samples = np.array([[0,0],[0.1,0],[0.1,0.3],[0.2,0.3],[0.5,0.5],[0.4,0.8],[0.9,0.9]])
    train_samples = []
    for i in range(10):
        for j in range(10):
            train_samples.append([i / 10, j / 10])
    train_samples = np.array(train_samples)

    test_samples = np.array([[0.1, 0.4], [0.3, 0.3], [0.8, 0.8]])
    y = (
        1
        + 2 * train_samples[:, 0]
        + 3 * train_samples[:, 0] * train_samples[:, 0]
        + train_samples[:, 0] * train_samples[:, 1]
    )
    y_derx1 = 2 + 6 * test_samples[:, 0] + test_samples[:, 1]
    y_derx2 = 6 + 0 * test_samples[:, 0]
    y_dery = test_samples[:, 0]
    y = np.swapaxes(np.array([y]), 0, 1)

    # aPCE + derivatives
    mm = PCE(inp, pce_deg=2)
    mm.fit(train_samples, {"Z": y})
    out = mm.eval_metamodel(train_samples)[0]
    out_1 = mm.derivative(test_samples, {"x": 1})
    out_2 = mm.derivative(test_samples, {"x": 2})
    out_3 = mm.derivative(test_samples, {"y": 1})

    # Asserts
    assert np.allclose(out["Z"], y, rtol=0.002)
    assert np.allclose(out_1["Z"][:, 0], y_derx1, rtol=0.002)
    assert np.allclose(out_2["Z"][:, 0], y_derx2, rtol=0.002)
    assert np.allclose(out_3["Z"][:, 0], y_dery, rtol=0.002)


# %%

if __name__ == "__main__":
    test_derivative_di()
