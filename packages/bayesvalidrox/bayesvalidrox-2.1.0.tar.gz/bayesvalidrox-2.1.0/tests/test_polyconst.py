# -*- coding: utf-8 -*-
"""
Test the various classes and functions provided for constructing the polynomials.
Tests are available for the following functions:
    apoly_construction      - x
    glexindex             
    cross_truncate

"""
import sys

sys.path.append("src/")
sys.path.append("../src/")
import pytest
import numpy as np

from bayesvalidrox.surrogate_models.apoly_construction import apoly_construction
from bayesvalidrox.surrogate_models.glexindex import glexindex, cross_truncate

# %% Test apoly_construction


def test_apoly_construction_dimerr() -> None:
    """
    Cannot construct with wrong dim of data
    """
    data = np.random.uniform(0, 1, (3, 1000))
    with pytest.raises(AttributeError) as excinfo:
        apoly_construction(data, 3)
    assert str(excinfo.value) == "Data should be a 1D array"


def test_apoly_construction() -> None:
    """
    Construct poly for aPC
    """
    data = np.random.uniform(0, 1, 1000)
    apoly_construction(data, 3)


def test_apoly_construction_deg0() -> None:
    """
    Construct poly for aPC for degree 0
    """
    data = np.random.uniform(0, 1, 1000)
    apoly_construction(data, 0)


def test_apoly_construction_negdeg() -> None:
    """
    Construct poly for aPC for negative degree -- this works??
    """
    data = np.random.uniform(0, 1, 1000)
    apoly_construction(data, -2)


# %% Test glexindex


def test_glexindex() -> None:
    """
    Create monomial exponent dict
    """
    glexindex(0)


# %% Test cross_truncate


def test_cross_truncate() -> None:
    """
    Truncate indices via Lp norm
    """
    # cross_truncate(np.array([0,1,2]), 2, 1)
    # TODO: issue testing cross_truncate
    None
