# -*- coding: utf-8 -*-
"""
Test the RegressionFastLaplace class for bayesvalidrox

Tests are available for the following functions

"""

import numpy as np
import pytest
from sklearn.datasets import make_regression
from bayesvalidrox.surrogate_models.reg_fast_laplace import RegressionFastLaplace


@pytest.fixture
def laplace_data():
    """
    Generate synthetic data for testing Laplace regression
    """
    np.random.seed(42)
    X, y = make_regression(n_samples=100, n_features=10, noise=0.1)
    return X, y


@pytest.fixture
def laplace_model():
    """
    Instantiate Laplace regression model
    """
    return RegressionFastLaplace(n_iter=50, n_kfold=3, tol=1e-6)


def test_laplace_fit_runs(laplace_model, laplace_data):
    """
    Fit RegressionFastLaplace and check attributes
    """
    X, y = laplace_data
    model = laplace_model.fit(X, y)
    assert hasattr(model, "coef_")
    assert hasattr(model, "sigma_")
    assert hasattr(model, "active_")
    assert hasattr(model, "gamma")
    assert hasattr(model, "lambda_")
    assert hasattr(model, "intercept_")


def test_laplace_predict_shape(laplace_model, laplace_data):
    """
    Check shape of Laplace prediction
    """
    X, y = laplace_data
    model = laplace_model.fit(X, y)
    y_pred = model.predict(X)
    assert y_pred.shape == (X.shape[0],)


def test_laplace_predict_std(laplace_model, laplace_data):
    """
    Predict with standard deviation enabled
    """
    X, y = laplace_data
    model = laplace_model.fit(X, y)
    y_pred, std_pred = model.predict(X, return_std=True)
    assert y_pred.shape == (X.shape[0],)
    assert std_pred.shape == (X.shape[0],)
    assert np.all(std_pred >= 0.0)


def test_laplace_fit_with_intercept():
    """
    Fit with intercept enabled
    """
    X = np.random.randn(40, 5)
    y = 3.0 + 2 * X[:, 0] + 0.1 * np.random.randn(40)
    model = RegressionFastLaplace(n_iter=20, n_kfold=2, fit_intercept=True)
    model.fit(X, y)
    assert isinstance(model.intercept_, float)
    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
