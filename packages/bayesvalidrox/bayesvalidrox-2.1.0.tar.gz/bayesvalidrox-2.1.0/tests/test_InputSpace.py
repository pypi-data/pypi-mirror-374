# -*- coding: utf-8 -*-
"""
Test the InputSpace class in bayesvalidrox.
Tests are available for the following functions
Class InputSpace: 
    check_valid_inputs  - x
    init_param_space    - x
    build_polytypes     - x
    transform           - x

"""
import sys
import pytest
import numpy as np

sys.path.append("src/")
sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.input_space import InputSpace


# %% Test InputSpace.check_valid_input


def test_check_valid_input_hasmarg() -> None:
    """
    Distribution not built if no marginals set
    """
    inp = Input()
    with pytest.raises(AssertionError) as excinfo:
        InputSpace(inp)
    assert str(excinfo.value) == "Cannot build distributions if no marginals are given"


def test_check_valid_input_haspriors() -> None:
    """
    Distribution not built if no distribution set for the marginals
    """
    inp = Input()
    inp.add_marginals()
    with pytest.raises(AssertionError) as excinfo:
        InputSpace(inp)
    assert str(excinfo.value) == "Not all marginals were provided priors"


def test_check_valid_input_priorsmatch() -> None:
    """
    Distribution not built if dist types do not align
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    inp.add_marginals()
    inp.marginals[1].dist_type = "normal"
    inp.marginals[1].parameters = [0, 1]
    with pytest.raises(AssertionError) as excinfo:
        InputSpace(inp)
    assert (
        str(excinfo.value)
        == "Distributions cannot be built as the priors have different types"
    )


def test_check_valid_input_samples() -> None:
    """
    Design built correctly - samples
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    inp.add_marginals()
    inp.marginals[1].input_data = x + 2
    InputSpace(inp)


def test_check_valid_input_both() -> None:
    """
    Design no built - samples and dist type given
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    inp.marginals[0].dist_type = "normal"
    with pytest.raises(AssertionError) as excinfo:
        InputSpace(inp)
    assert (
        str(excinfo.value)
        == "Both samples and distribution type are given. Please choose only one."
    )


# def test_check_valid_input_distnotok() -> None:
#    """
#    Design built incorrectly - dist types without parameters
#    """
#    inp = Input()
#    inp.add_marginals()
#    inp.marginals[0].dist_type = 'normal'
#    inp.add_marginals()
#    inp.marginals[1].dist_type = 'normal'
#    with pytest.raises(AssertionError) as excinfo:
#        exp = InputSpace(inp)
#    assert str(excinfo.value) == 'Some distributions do not have characteristic values'


def test_check_valid_input_distok() -> None:
    """
    Design built correctly - dist types
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    inp.add_marginals()
    inp.marginals[1].dist_type = "normal"
    inp.marginals[1].parameters = [0, 1]
    InputSpace(inp)


def test_check_valid_input_noapc() -> None:
    """
    Design built correctly - no apc
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    inp.add_marginals()
    inp.marginals[1].dist_type = "normal"
    inp.marginals[1].parameters = [0, 1]
    InputSpace(inp, meta_model_type="gpe")


# %% Test InputSpace.build_polytypes
# def test_build_polytypes_normalerr() -> None:
#     """
#     Build dist 'normal' - too few params
#     """
#     inp = Input()
#     inp.add_marginals()
#     inp.marginals[0].dist_type = 'normal'
#     inp.marginals[0].parameters = []
#     exp = InputSpace(inp)
#     with pytest.raises(AssertionError) as excinfo:
#         exp.build_polytypes(False)
#     assert str(excinfo.value) == 'Distribution has too few parameters!'


def test_build_polytypes_normal() -> None:
    """
    Build dist 'normal'
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    exp = InputSpace(inp)
    exp.build_polytypes(False)


def test_build_polytypes_uniferr() -> None:
    """
    Build dist 'unif' - too few params
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "unif"
    inp.marginals[0].parameters = []
    exp = InputSpace(inp)
    with pytest.raises(AssertionError) as excinfo:
        exp.build_polytypes(False)
    assert str(excinfo.value) == "Distribution has too few parameters!"


def test_build_polytypes_unif() -> None:
    """
    Build dist 'unif'
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "unif"
    inp.marginals[0].parameters = [0, 1]
    exp = InputSpace(inp)
    exp.build_polytypes(False)


def test_build_polytypes_gammaerr() -> None:
    """
    Build dist 'gamma' - too few params
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "gamma"
    inp.marginals[0].parameters = []
    exp = InputSpace(inp)
    with pytest.raises(AssertionError) as excinfo:
        exp.build_polytypes(False)
    assert str(excinfo.value) == "Distribution has too few parameters!"


# noinspection SpellCheckingInspection
def test_build_polytypes_gamma() -> None:
    """
    Build dist 'gamma'
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "gamma"
    inp.marginals[0].parameters = [0, 1, 0]
    exp = InputSpace(inp)
    with pytest.raises(ValueError) as excinfo:
        exp.build_polytypes(False)
    assert (
        str(excinfo.value) == "Parameter values are not valid, please set differently"
    )


# noinspection SpellCheckingInspection
def test_build_polytypes_betaerr() -> None:
    """
    Build dist 'beta' - too few params
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "beta"
    inp.marginals[0].parameters = []
    exp = InputSpace(inp)
    with pytest.raises(AssertionError) as excinfo:
        exp.build_polytypes(False)
    assert str(excinfo.value) == "Distribution has too few parameters!"


# def test_build_polytypes_beta() -> None:
#    """
#    Build dist 'beta'
#    """
#    inp = Input()
#    inp.add_marginals()
#    inp.marginals[0].dist_type = 'beta'
#    inp.marginals[0].parameters = [0.5, 1, 2, 3]
#    exp = InputSpace(inp)
#    exp.build_polytypes(False)


# noinspection SpellCheckingInspection
def test_build_polytypes_lognormerr() -> None:
    """
    Build dist 'lognorm' - too few params
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "lognorm"
    inp.marginals[0].parameters = []
    exp = InputSpace(inp)
    with pytest.raises(AssertionError) as excinfo:
        exp.build_polytypes(False)
    assert str(excinfo.value) == "Distribution has too few parameters!"


def test_build_polytypes_lognorm() -> None:
    """
    Build dist 'lognorm'
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "lognorm"
    inp.marginals[0].parameters = [0.5, 1, 2, 3]
    exp = InputSpace(inp)
    exp.build_polytypes(False)


def test_build_polytypes_exponerr() -> None:
    """
    Build dist 'expon' - too few params
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "beta"
    inp.marginals[0].parameters = []
    exp = InputSpace(inp)
    with pytest.raises(AssertionError) as excinfo:
        exp.build_polytypes(False)
    assert str(excinfo.value) == "Distribution has too few parameters!"


def test_build_polytypes_expon() -> None:
    """
    Build dist 'expon'
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "expon"
    inp.marginals[0].parameters = [0.5, 1, 2, 3]
    exp = InputSpace(inp)
    exp.build_polytypes(False)


def test_build_polytypes_weibullerr() -> None:
    """
    Build dist 'weibull' - too few params
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "weibull"
    inp.marginals[0].parameters = []
    exp = InputSpace(inp)
    with pytest.raises(AssertionError) as excinfo:
        exp.build_polytypes(False)
    assert str(excinfo.value) == "Distribution has too few parameters!"


def test_build_polytypes_weibull() -> None:
    """
    Build dist 'weibull'
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "weibull"
    inp.marginals[0].parameters = [0.5, 1, 2, 3]
    exp = InputSpace(inp)
    exp.build_polytypes(False)


def test_build_polytypes_arbitrary() -> None:
    """
    Build poly 'arbitrary'
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.build_polytypes(False)


def test_build_polytypes_rosenblatt() -> None:
    """
    Build dist with rosenblatt
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.build_polytypes(True)


def test_build_polytypes_samples() -> None:
    """
    Build dist from samples
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.build_polytypes(False)


def test_build_polytypes_samples2d() -> None:
    """
    Build dist from samples - samples too high dim
    """
    x = np.random.uniform(0, 1, (2, 1000))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    with pytest.raises(ValueError) as excinfo:
        exp.build_polytypes(False)
    assert (
        str(excinfo.value) == "The samples provided to the Marginals should be 1D only"
    )


# %% Test InputSpace.init_param_space


def test_init_param_space_nomaxdegsample() -> None:
    """
    Init param space without max_deg for given samples
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.init_param_space()


def test_init_param_space_maxdeg() -> None:
    """
    Init param space with max_deg for given samples
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)


def test_init_param_space_maxdegdist() -> None:
    """
    Init param space with max_deg for given dist (not uniform)
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "expon"
    inp.marginals[0].parameters = [0.5, 1, 2, 3]
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)


def test_init_param_space_maxdegdistunif() -> None:
    """
    Init param space with max_deg for given dist (uniform)
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "unif"
    inp.marginals[0].parameters = [0.5, 1, 2, 3]
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)


# %% Test InputSpace.transform


def test_transform_noparamspace() -> None:
    """
    Call transform without a built j_dist
    """
    x = np.random.uniform(0, 1, 1000)
    y = np.random.uniform(0, 1, (2, 1000))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    with pytest.raises(AttributeError) as excinfo:
        exp.transform(y)
    assert str(excinfo.value) == "Call function init_param_space first to create j_dist"


def test_transform_dimerrlow() -> None:
    """
    Call transform with too few dimensions
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    with pytest.raises(AttributeError) as excinfo:
        exp.transform(x)
    assert str(excinfo.value) == "X should have two dimensions"


def test_transform_dimerrhigh() -> None:
    """
    Call transform with too many dimensions
    """
    x = np.random.uniform(0, 1, 1000)
    y = np.random.uniform(0, 1, (1, 1, 1000))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    with pytest.raises(AttributeError) as excinfo:
        exp.transform(y)
    assert str(excinfo.value) == "X should have two dimensions"


def test_transform_dimerr0() -> None:
    """
    Call transform with wrong X.shape[0]
    """
    x = np.random.uniform(0, 1, 1000)
    y = np.random.uniform(0, 1, (2, 1000))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    with pytest.raises(AttributeError) as excinfo:
        exp.transform(y)
    assert (
        str(excinfo.value)
        == "The second dimension of X should be the same size as the number "
        "of marginals in the input_object"
    )


def test_transform_paramspace() -> None:
    """
    Transform successfully
    """
    x = np.random.uniform(0, 1, 1000)
    y = np.random.uniform(0, 1, (1000, 1))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    exp.transform(y)


if 0:  # TODO: See Issue #41, use these again when the issue is removed

    def test_transform_rosenblatt() -> None:
        """
        Transform with rosenblatt
        """
        x = np.random.uniform(0, 1, 1000)
        y = np.random.uniform(0, 1, (1000, 1))
        inp = Input()
        inp.rosenblatt = True
        inp.add_marginals()
        inp.marginals[0].input_data = x
        exp = InputSpace(inp)
        exp.init_param_space(max_deg=2)
        exp.transform(y)

    def test_transform_rosenblattuser() -> None:
        """
        Transform with rosenblatt and method 'user'
        """
        x = np.random.uniform(0, 1, 1000)
        y = np.random.uniform(0, 1, (1000, 1))
        inp = Input()
        inp.rosenblatt = True
        inp.add_marginals()
        inp.marginals[0].input_data = x
        exp = InputSpace(inp)
        exp.init_param_space(max_deg=2)
        exp.transform(y, method="user")


def test_transform_user() -> None:
    """
    Transform with method 'user'
    """
    x = np.random.uniform(0, 1, 1000)
    y = np.random.uniform(0, 1, (1000, 1))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    exp.transform(y, method="user")


def test_transform_uniform() -> None:
    """
    Transform uniform dist
    """
    y = np.random.uniform(0, 1, (1000, 1))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "unif"
    inp.marginals[0].parameters = [0, 1]
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    exp.transform(y)


def test_transform_norm() -> None:
    """
    Transform normal dist
    """
    y = np.random.uniform(0, 1, (1000, 1))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "norm"
    inp.marginals[0].parameters = [0, 1]
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    exp.transform(y)


# TODO: what are these other params here???
def test_transform_gammanoparam() -> None:
    """
    Transform gamma dist - no parameters
    """
    y = np.random.uniform(0, 1, (1000, 1))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "gamma"
    inp.marginals[0].parameters = [1, 1, 0]
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    with pytest.raises(AttributeError) as excinfo:
        exp.transform(y)
    assert (
        str(excinfo.value)
        == "Additional parameters have to be set for the gamma distribution!"
    )


def test_transform_gammaparam() -> None:
    """
    Transform gamma dist - with parameters
    """
    y = np.random.uniform(0, 1, (1000, 1))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "gamma"
    inp.marginals[0].parameters = [1, 1, 0]
    exp = InputSpace(inp)
    exp.init_param_space(max_deg=2)
    exp.transform(y, params=[1, 1])
