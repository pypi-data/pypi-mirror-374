# -*- coding: utf-8 -*-
"""
Test the MetaModel class in bayesvalidrox.
Class MetaModel: 
    build_metamodel  - x
    update_metamodel
    update_pce_coeffs
    create_basis_indices --removed, just redirects
    add_input_space                                   -x
    univ_basis_vals
    create_psi
    fit
    adaptive_regression
    corr_loocv_error
    pca_transformation
    gaussian_process_emulator
    eval_metamodel
    create_model_error
    eval_model_error
    AutoVivification
    copy_meta_model_opts
    __select_degree
    generate_polynomials
    _compute_pce_moments
    
"""

import sys
import numpy as np

sys.path.append("../src/")

# from bayesvalidrox.surrogate_models.supplementary import create_psi

from bayesvalidrox.surrogate_models import MetaModel
from bayesvalidrox import Input

# %% Test MetaMod constructor on its own


def test_metamod() -> None:
    """
    Construct MetaModel without inputs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    MetaModel(inp)


# %% Test MetaModel.check_is_gaussian


def test_check_is_gaussian() -> None:
    """
    Checks for gaussian outputs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.check_is_gaussian()


# %% Test MetaModel.build_metamodel


def test_build_metamodel() -> None:
    """
    Build MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.build_metamodel()


# %% Test MetaMod.add_input_space


def test_add_input_space() -> None:
    """
    Add InputSpace in MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.add_input_space()


# %% Test MetaModel.fit
# Faster without these
def test_fit() -> None:
    """
    Fit MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})


def test_fit_parallel() -> None:
    """
    Fit MetaModel in parallel
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]}, parallel=True)


def test_fit_verbose() -> None:
    """
    Fit MetaModel verbose
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]}, verbose=True)


def test_fit_pca() -> None:
    """
    Fit MetaModel verbose and with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.dim_red_method = "pca"
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]}, verbose=True)


def test_fit_gpe() -> None:
    """
    Fit MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.meta_model_type = "gpe"
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})


# %% Test MetaModel.pca_transformation


def test_pca_transformation() -> None:
    """
    Apply PCA
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
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
    mm = MetaModel(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    mm.var_pca_threshold = 1
    mm.pca_transformation(outputs, 1)


def test_pca_transformation_ncomp() -> None:
    """
    Apply PCA with set n_pca_components
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    mm.pca_transformation(outputs, 1)


# %% Test MetaModel.eval_metamodel


def test_eval_metamodel() -> None:
    """
    Eval trained MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    out = mm.eval_metamodel([[0.4]])
    assert len(out) == 2


# %% Test MetaModel.AutoVivification
def test_autovivification() -> None:
    """
    Creation of auto-vivification objects
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.AutoVivification()


# %% Test MetaModel.copy_meta_model_opts


def test_copy_meta_model_opts() -> None:
    """
    Copy the metamodel with just some stats
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.add_input_space()
    mm.copy_meta_model_opts()


# %% Test MetaModel.__select_degree


# %% Test MetaModel.calculate_moments
def test_calculate_moments() -> None:
    """
    Compute moments of a surrogate with pca
    """
    None  # TODO: add test for moment calculation without PCE
