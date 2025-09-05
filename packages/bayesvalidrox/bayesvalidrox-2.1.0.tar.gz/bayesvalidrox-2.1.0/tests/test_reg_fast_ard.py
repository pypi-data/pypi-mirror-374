# -*- coding: utf-8 -*-
"""
Test the RegressionFastARD class for bayesvalidrox

Tests are available for the following functions

"""

import numpy as np
import pytest

from bayesvalidrox.surrogate_models.reg_fast_ard import (
    RegressionFastARD,
    update_precisions,
)


@pytest.fixture
def sample_data():
    """
    Sample data
    """
    np.random.seed(0)
    X = np.random.randn(20, 3)
    y = X @ np.array([1.5, -2.0, 0.5]) + 0.1 * np.random.randn(20)
    return X, y


@pytest.fixture
def ard_model():
    """
    Basic RegFastARD object
    """
    return RegressionFastARD(n_iter=50)


@pytest.fixture
def synthetic_regression_data():
    """
    Regression data
    """
    np.random.seed(42)
    X = np.random.randn(100, 5)
    true_coef = np.array([1.0, 0.0, -2.0, 0.0, 0.5])
    y = X @ true_coef + 0.1 * np.random.randn(100)
    return X, y


@pytest.fixture
def regression_model():
    """
    Mod RegFastARD object
    """
    return RegressionFastARD(n_iter=100, tol=1e-4)


def test_model_instantiation() -> None:
    """
    Instantiate RegressionFastARD
    """
    model = RegressionFastARD()
    assert isinstance(model, RegressionFastARD)


def test_model_fit_and_attributes(sample_data, ard_model) -> None:
    """
    Fit RegressionFastARD and check learned attributes
    """
    X, y = sample_data
    ard_model.fit(X, y)
    assert ard_model.coef_.shape == (3,)
    assert isinstance(ard_model.intercept_, float)
    assert ard_model.active_.shape == (3,)
    assert ard_model.lambda_.shape == (3,)
    assert ard_model.sigma_ is not None
    assert hasattr(ard_model, "converged")


def test_model_predict() -> None:
    """
    Predict using RegressionFastARD
    """
    np.random.seed(1)
    X = np.random.randn(10, 2)
    y = X @ np.array([2.0, -1.0]) + 0.05 * np.random.randn(10)
    model = RegressionFastARD(n_iter=30)
    model.fit(X, y)
    y_pred = model.predict(X)
    assert y_pred.shape == (10,)

    y_pred2, std_pred = model.predict(X, return_std=True)
    assert y_pred2.shape == (10,)
    assert std_pred.shape == (10,)


def test_posterior_distribution() -> None:
    """
    Run _posterior_dist with full covariance
    """
    np.random.seed(2)
    X = np.random.randn(8, 2)
    y = X @ np.array([1.0, 2.0]) + 0.1 * np.random.randn(8)
    model = RegressionFastARD(n_iter=10)
    model.fit(X, y)

    active = model.active_
    aa = model.lambda_[active]
    beta = model.alpha_
    xx = np.dot(X.T, X)[active][:, active]
    xy = np.dot(X.T, y)[active]

    mn, sn, _ = model._posterior_dist(aa, beta, xx, xy, full_covar=True)
    assert mn.shape[0] == np.sum(active)
    assert sn.shape[0] == sn.shape[1]


def test_sparsity_quality_metric() -> None:
    """
    Run _sparsity_quality function
    """
    np.random.seed(3)
    X = np.random.randn(12, 4)
    y = X @ np.array([1.0, 0.0, -1.0, 2.0]) + 0.1 * np.random.randn(12)
    model = RegressionFastARD(n_iter=10)
    model.fit(X, y)

    xx = np.dot(X.T, X)
    xxd = np.diag(xx)
    xy = np.dot(X.T, y)
    active = model.active_
    aa = model.lambda_[active]
    beta = model.alpha_
    xxa = xx[active][:, active]
    xya = xy[active]
    _, ri, cholesky = model._posterior_dist(aa, beta, xxa, xya)

    s, q, s1, q1 = model._sparsity_quality(
        xx, xxd, xy, xya, aa, ri, active, beta, cholesky
    )

    assert len(s) == 4
    assert len(q) == 4
    assert len(s1) == 4
    assert len(q1) == 4


def test_log_marginal_likelihood() -> None:
    """
    Evaluate log marginal likelihood
    """
    np.random.seed(4)
    X = np.random.randn(10, 3)
    y = X @ np.array([1.0, 2.0, 3.0]) + 0.1 * np.random.randn(10)
    model = RegressionFastARD(n_iter=10)
    model.fit(X, y)

    active = model.active_
    xxa = np.dot(X.T, X)[active][:, active]
    xya = np.dot(X.T, y)[active]
    aa = model.lambda_[active]
    beta = model.alpha_

    score = model.log_marginal_like(xxa, xya, aa, beta)
    assert isinstance(score, float)


def test_update_precisions_runs() -> None:
    """
    Test update_precisions function
    """
    q1 = np.array([1.0, 2.0, 3.0])
    s1 = np.array([0.5, 0.5, 0.5])
    q = np.array([1.0, 2.0, 3.0])
    s = np.array([0.5, 0.5, 0.5])
    a = np.array([1.0, 1.0, 1.0])
    active = np.array([False, True, False])
    tol = 1e-3
    n_samples = 10
    clf_bias = False

    a_new, converged = update_precisions(
        q1, s1, q, s, a, active, tol, n_samples, clf_bias
    )

    assert isinstance(converged, bool)
    assert a_new.shape == (3,)


def test_model_fit_converges(regression_model, synthetic_regression_data):
    """
    Ensure model converges on synthetic data
    """
    X, y = synthetic_regression_data
    regression_model.fit(X, y)
    assert regression_model.converged is True


def test_predict_std_returns_zero_if_var_y_flagged():
    """
    Predictive std should be 0 if model.flag var_y is set (zero variance case)
    """
    X = np.ones((10, 3))
    y = np.ones(10)
    model = RegressionFastARD(n_iter=10)
    model.fit(X, y)
    _, std = model.predict(X, return_std=True)
    assert np.allclose(std, 0.0)


def test_fit_manual_start():
    """
    Fit model with manual starting feature
    """
    np.random.seed(0)
    X = np.random.randn(20, 4)
    y = X[:, 2] * 3 + 0.1 * np.random.randn(20)
    model = RegressionFastARD(n_iter=50, start=[2])
    model.fit(X, y)
    assert model.active_[2]


def test_repr_stability():
    """
    Model repr must return informative string
    """
    model = RegressionFastARD()
    assert isinstance(repr(model), str)
    assert "RegressionFastARD" in repr(model)
