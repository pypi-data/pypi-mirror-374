# -*- coding: utf-8 -*-
"""
Test the OrthogonalMatchingPursuit class in bayesvalidrox.

"""

import numpy as np
import pytest
from bayesvalidrox.surrogate_models.orthogonal_matching_pursuit import (
    OrthogonalMatchingPursuit,
    corr,
)


@pytest.fixture
def sample_data():
    """Synthetic data for testing"""
    np.random.seed(42)
    X = np.random.randn(50, 5)
    y = 2 * X[:, 0] - 3 * X[:, 1] + 0.1 * np.random.randn(50)
    return X, y


def test_omp_fit_predict_shapes(sample_data):
    """
    Test that fitting and predicting produce correctly shaped outputs and coefficients.
    """
    X, y = sample_data
    model = OrthogonalMatchingPursuit()
    model.fit(X, y)
    y_pred = model.predict(X)

    # Coefficients should be a 1D array matching number of features
    assert hasattr(model, "coef_")
    assert isinstance(model.coef_, np.ndarray)
    assert model.coef_.shape == (X.shape[1],)

    # Predictions should match the target shape
    assert isinstance(y_pred, np.ndarray)
    assert y_pred.shape == y.shape


def test_corr_function():
    """
    Test the standalone correlation function as implemented.
    """
    np.random.seed(0)
    X = np.random.randn(10, 3)
    y = np.random.randn(10)

    corr_value = np.array([corr(X[:, i], y) for i in range(X.shape[1])])
    # Expected based on implementation: abs(X.T@y) / sqrt(sum(X**2))
    expected_corr = np.abs(X.T.dot(y)) / np.sqrt((X**2).sum(axis=0))

    assert isinstance(corr_value, np.ndarray)
    assert corr_value.shape == (X.shape[1],)
    assert np.allclose(corr_value, expected_corr, atol=1e-8)


def test_omp_predict_only_shape():
    """
    Test that predict returns correctly shaped output after fitting.
    """
    X = np.random.randn(20, 3)
    y = np.random.randn(20)
    model = OrthogonalMatchingPursuit()
    model.fit(X, y)
    y_pred = model.predict(X)

    assert isinstance(y_pred, np.ndarray)
    assert y_pred.shape == y.shape


def test_omp_preprocess_returns_correct_shapes():
    """
    Ensure _preprocess_data returns expected shapes and types
    """
    X = np.random.randn(20, 3)
    y = np.random.randn(20)
    model = OrthogonalMatchingPursuit()
    x_p, yp, x_offset, y_offset, x_scale = model._preprocess_data(X, y)
    assert x_p.shape == X.shape
    assert yp.shape == y.shape
    assert x_offset.shape == (X.shape[1],)
    assert x_scale.shape == (X.shape[1],)
    assert isinstance(y_offset, float)


def test_omp_handles_constant_feature_no_intercept():
    """
    Fit with a constant column in X, without intercept centering.
    """
    X = np.random.randn(30, 4)
    X[:, 0] = 1.0  # constant column
    y = 2 * X[:, 1] + np.random.randn(30)
    model = OrthogonalMatchingPursuit(fit_intercept=False)
    model.fit(X, y)
    assert hasattr(model, "coef_")
    assert model.coef_.shape == (X.shape[1],)


def test_loo_error_zero_variance_target():
    """
    LOO error should be zero when target variance is zero.
    """
    psi = np.random.randn(15, 4)
    y = np.ones(15)
    a = psi.T @ psi
    a_inv = np.linalg.pinv(a)
    coeffs = a_inv @ psi.T @ y
    model = OrthogonalMatchingPursuit()
    error = model.loo_error(psi, a_inv, y, coeffs)
    assert error == 0.0


def test_predict_manual_coefficients():
    """Test predict with manually assigned coefficients and intercept"""
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    model = OrthogonalMatchingPursuit()
    model.coef_ = np.array([0.5, -1.0])
    model.intercept_ = 2.0
    y_pred = model.predict(X)
    expected = X @ model.coef_ + model.intercept_
    assert np.allclose(y_pred, expected)


def test_fit_recovers_coefficient_no_intercept():
    """Test fit recovers true coefficient on a simple linear model without intercept"""
    X = np.arange(10).reshape(-1, 1)
    true_coef = np.array([2.0])
    y = 2 * X.ravel()
    model = OrthogonalMatchingPursuit(fit_intercept=False)
    model.fit(X, y)
    assert np.allclose(model.coef_, true_coef, atol=1e-6)
    assert model.intercept_ == 0.0


def test_omp_early_stopping():
    """
    Verify that the model stops adding features early and doesn't use all available ones.
    """
    np.random.seed(0)
    X = np.random.randn(40, 20)
    y = X[:, 0] * 2 + 0.1 * np.random.randn(40)

    model = OrthogonalMatchingPursuit()
    model.fit(X, y)

    # Should only select a few features (ideally just one)
    assert np.count_nonzero(model.coef_) <= 3


def test_omp_underdetermined_system():
    """
    Ensure that model does not crash and produces finite coefficients with n < p.
    """
    X = np.random.randn(10, 30)
    y = np.random.randn(10)

    model = OrthogonalMatchingPursuit()
    model.fit(X, y)

    assert np.isfinite(model.coef_).all()
    assert model.coef_.shape == (X.shape[1],)


def test_omp_overdetermined_system():
    """
    Ensure that model handles overdetermined systems robustly.
    """
    X = np.random.randn(100, 10)
    y = 3 * X[:, 2] - 2 * X[:, 4] + 0.01 * np.random.randn(100)

    model = OrthogonalMatchingPursuit()
    model.fit(X, y)

    # Should recover signal roughly
    assert abs(model.coef_[2]) > 1.0
    assert abs(model.coef_[4]) > 1.0


def test_omp_predict_on_unseen_data():
    """
    Train on one set, predict on new inputs of matching shape.
    """
    x_train = np.random.randn(50, 5)
    y_train = 2 * x_train[:, 0] + np.random.randn(50)
    x_test = np.random.randn(10, 5)

    model = OrthogonalMatchingPursuit()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)

    assert y_pred.shape == (10,)
    assert np.isfinite(y_pred).all()


def test_omp_no_signal_zero_coefficients():
    """
    When no feature explains the target, all coefficients should be zero.
    """
    X = np.random.randn(30, 5)
    y = np.zeros(30)

    model = OrthogonalMatchingPursuit()
    model.fit(X, y)

    assert np.allclose(model.coef_, 0.0)
    assert model.intercept_ == 0.0
