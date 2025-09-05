# -*- coding: utf-8 -*-
"""
Tests the classes in bayes_linear in bayesvalidrox

"""

import numpy as np
import pytest
from bayesvalidrox.surrogate_models.bayes_linear import (
    VBLinearRegression,
    EBLinearRegression,
)


@pytest.fixture
def simple_data():
    """Fixture for simple linear regression data."""
    X = np.array([[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 5.0]])
    y = np.dot(X, np.array([2.0, -1.0])) + 3.0
    return X, y


def test_vb_init_defaults():
    """Test default initialization of VBLinearRegression."""
    model = VBLinearRegression()
    assert model.n_iter == 100
    assert model.tol == 1e-4
    assert model.fit_intercept is True
    assert model.a == 1e-4
    assert model.b == 1e-4
    assert model.c == 1e-4
    assert model.d == 1e-4


def test_vb_fit_sets_attributes(simple_data):
    """Test that fitting VBLinearRegression sets required attributes."""
    X, y = simple_data
    model = VBLinearRegression()
    model.fit(X, y)
    assert model.coef_ is not None
    assert model.intercept_ is not None
    assert model.alpha_ is not None
    assert model.beta_ is not None
    assert model.eigvals_ is not None
    assert model.eigvecs_ is not None


def test_vb_predict_shape(simple_data):
    """Test prediction shape of VBLinearRegression."""
    X, y = simple_data
    model = VBLinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    assert y_pred.shape == y.shape


def test_vb_predict_std(simple_data):
    """Test prediction with standard deviation output."""
    X, y = simple_data
    model = VBLinearRegression()
    model.fit(X, y)
    y_pred, y_std = model.predict(X, return_std=True)
    assert y_pred.shape == y.shape
    assert y_std.shape == y.shape
    assert np.all(y_std > 0)


def test_vb_zero_variance_y():
    """Ensure VBLinearRegression handles zero-variance target."""
    X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    y = np.array([5.0, 5.0, 5.0])
    model = VBLinearRegression()
    model.fit(X, y)
    assert model.coef_ is not None
    assert isinstance(model.intercept_, float)


def test_vb_predict_unseen_data(simple_data):
    """Test prediction on new unseen data."""
    X, y = simple_data
    model = VBLinearRegression()
    model.fit(X, y)
    x_new = np.array([[6.0, 7.0], [8.0, 9.0]])
    y_new = model.predict(x_new)
    assert y_new.shape[0] == x_new.shape[0]


def test_eblr_init_defaults():
    """
    Init eblr
    """
    model = EBLinearRegression()
    assert model.n_iter == 300
    assert model.optimizer == "fp"
    assert model.fit_intercept
    assert model.normalize
    assert model.alpha == 1
    assert model.perfect_fit_tol == 1e-6


def test_eblr_invalid_optimizer():
    """
    Init eblr with wrong optimizer
    """
    with pytest.raises(ValueError):
        EBLinearRegression(optimizer="invalid")


def test_eblr_fit_and_predict():
    """
    Fit and predict with eblr
    """
    X = np.array([[1, 2], [3, 4], [5, 6]])
    y = np.array([2, 4, 6])
    model = EBLinearRegression(n_iter=100)
    model.fit(X, y)
    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    assert np.all(np.isfinite(y_pred))


def test_eblr_predict_with_std():
    """
    Eblr with stdev
    """
    X = np.array([[1, 2], [3, 4], [5, 6]])
    y = np.array([2, 4, 6])
    model = EBLinearRegression()
    model.fit(X, y)
    y_pred, std_pred = model.predict(X, return_std=True)
    assert y_pred.shape == y.shape
    assert std_pred.shape == y.shape
    assert np.all(std_pred >= 0)
