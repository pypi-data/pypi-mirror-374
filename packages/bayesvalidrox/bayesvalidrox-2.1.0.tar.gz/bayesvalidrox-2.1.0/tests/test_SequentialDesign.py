# -*- coding: utf-8 -*-
"""
Test the SequentialDesign class for bayesvalidrox
SequentialDesign:
    start_seq_design         
    choose_next_sample
        plotter
    tradoff_weights      - x
    run_util_func
    util_VarBasedDesign
    util_BayesianActiveDesign
    util_BayesianDesign
    dual_annealing
    util_AlphOptDesign
    _normpdf            - x    Also move outside the class?
    _corr_factor_BME           Not used again in this class
    _posteriorPlot      - x
    _BME_Calculator     - x
    _validError         - x
    _error_Mean_Std     - x 
    _select_indices


"""

import sys
import copy
import numpy as np
import pytest

sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.sequential_design import SequentialDesign
from bayesvalidrox.surrogate_models.polynomial_chaos import PCE
from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.surrogate_models.engine import Engine
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy
from bayesvalidrox.bayes_inference.rejection_sampler import RejectionSampler


@pytest.fixture
def basic_seq_des():
    """
    Basis sequential design with two inputs and multidim output
    """
    # Two inputs
    inp = Input()
    inp.add_marginals(dist_type="normal", parameters=[0, 1])
    inp.add_marginals(dist_type="normal", parameters=[0, 1])

    # Two outputs over time
    mod = PL()
    mod.output.names = ["Y", "Z"]
    expdes = ExpDesigns(inp, n_init_samples=5, n_max_samples=6)
    expdes.x = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [0.5, 0.3]])
    expdes.y = {
        "Y": np.array([[0, 0], [0, 2], [1, 0], [1, 2], [3, 2.7]]),
        "Z": np.array([[1, 1], [1, 0], [0, 1], [0, 0], [4, 1.9]]),
        "x_values": [0, 1],
    }

    mm = PCE(inp, pce_deg=2, pce_reg_method="fastard")
    engine = Engine(mm, mod, expdes)
    engine.start_engine()

    sigma2dict = {"Y": np.array([0.05, 0.05]), "Z": np.array([0.05, 0.05])}
    disc = Discrepancy(parameters=sigma2dict)
    disc.build_discrepancy()
    engine.discrepancy = disc

    seq_des = SequentialDesign(mm, expdes, disc, out_names=engine.out_names)
    return seq_des, engine


# %% Test Engine.choose_next_sample


def test_choose_next_sample(basic_seq_des) -> None:
    """
    Chooses new sample using all standard settings (exploration, random,...)
    """
    seq_des, _ = basic_seq_des
    x = seq_des.choose_next_sample()
    assert isinstance(x, np.ndarray)
    assert x.shape[0] == 1 and x.shape[1] == 2


def test_choose_next_sample_da_space(basic_seq_des) -> None:
    """
    Chooses new sample using dual-annealing and space-filling
    """
    seq_des, _ = basic_seq_des
    seq_des.exp_design.explore_method = "dual-annealing"
    seq_des.parallel = False
    x = seq_des.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 2
    seq_des.parallel = True
    x = seq_des.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 2


def test_choose_next_sample_loo_space(basic_seq_des) -> None:
    """
    Chooses new sample using LOO-CV
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.explore_method = "loocv"

    x = seq_des.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 2


def test_choose_next_sample_loo_wrong_surr(basic_seq_des) -> None:
    """
    Chooses new sample using LOO-CV with wrong surrogate
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.explore_method = "loocv"
    seq_des.meta_model.meta_model_type = "GPE"

    with pytest.raises(AttributeError) as excinfo:
        seq_des.choose_next_sample()
    assert str(excinfo.value) == (
        "The meta_model does not have a 'lc_error' attribute. "
        "Please check the meta_model type."
    )


def test_choose_next_sample_exploit(basic_seq_des) -> None:
    """
    Chooses new sample with exploitation
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.tradeoff_scheme = "exploit_only"
    x = seq_des.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 2


def test_get_next_sample_reproducibility(basic_seq_des):
    """Tests reproducibility of the next sample selection."""
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.tradeoff_scheme = "exploit_only"

    np.random.seed(42)
    x1 = seq_des.choose_next_sample()
    np.random.seed(42)
    x2 = seq_des.choose_next_sample()
    assert np.allclose(x1, x2)


def test_choose_next_sample_invalid_exploit(basic_seq_des) -> None:
    """
    Chooses new sample with invalid exploitation method
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.tradeoff_scheme = "exploit_only"
    seq_des.exp_design.exploit_method = "invalid"
    with pytest.raises(NameError) as excinfo:
        seq_des.choose_next_sample()
    assert str(excinfo.value) == (
        "The requested exploitation method invalid is not available."
    )


# %% Test Engine.tradeoff_weights
def test_tradeoff_weights_exploreonly(basic_seq_des) -> None:
    """
    Tradeoff weights with 'explore_only'
    """
    seq_des, _ = basic_seq_des
    x, y = seq_des.exp_design.x, seq_des.exp_design.y
    weights = seq_des.tradeoff_weights("explore_only", x, y)
    assert weights[0] == 1 and weights[1] == 0


def test_tradeoff_weights_exploitonly(basic_seq_des) -> None:
    """
    Tradeoff weights with 'exploit_only'
    """
    seq_des, _ = basic_seq_des
    x, y = seq_des.exp_design.x, seq_des.exp_design.y
    weights = seq_des.tradeoff_weights("exploit_only", x, y)
    assert weights[0] == 0 and weights[1] == 1


def test_tradeoff_weights_equal(basic_seq_des) -> None:
    """
    Tradeoff weights with 'equal' scheme
    """
    seq_des, _ = basic_seq_des
    x, y = seq_des.exp_design.x, seq_des.exp_design.y
    weights = seq_des.tradeoff_weights("equal", x, y)
    assert weights[0] == 0.5 and weights[1] == 0.5


def test_tradeoff_weights_epsdecr(basic_seq_des) -> None:
    """
    Tradeoff weights with 'epsilon-decreasing' scheme
    """
    seq_des, _ = basic_seq_des
    x, y = seq_des.exp_design.x, seq_des.exp_design.y
    weights = seq_des.tradeoff_weights("epsilon-decreasing", x, y)
    assert weights[0] == 1.0 and weights[1] == 0.0
    # TODO: check for later iterations as well


def test_tradeoff_weights_adaptive(basic_seq_des) -> None:
    """
    Tradeoff weights with 'adaptive' scheme
    """
    seq_des, _ = basic_seq_des
    x, y = seq_des.exp_design.x, seq_des.exp_design.y
    weights = seq_des.tradeoff_weights("adaptive", x, y)
    assert weights[0] == 0.5 and weights[1] == 0.5


def test_tradeoff_weights_adaptiveit1(basic_seq_des) -> None:
    """
    Tradeoff weights with 'adaptive' scheme for later iteration (not the first)
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    # Previous metamodel
    seq_des.prev_mm = engine.meta_model

    # New metamodel
    mm_new = copy.deepcopy(engine.meta_model)
    x = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [0.5, 0.3], [0.3, 0.6]])
    y = {
        "Y": np.array([[0, 0], [0, 2], [1, 0], [1, 2], [3, 2.7], [2, 4]]),
        "Z": np.array([[1, 1], [1, 0], [0, 1], [0, 0], [4, 1.9], [5, 2]]),
    }
    mm_new.fit(x, y)
    seq_des.tradeoff_weights("adaptive", x, y)


def test_tradeoff_weights_invalid_scheme(basic_seq_des) -> None:
    """Tests invalid tradeoff scheme"""
    seq_des, engine = basic_seq_des
    with pytest.raises(AttributeError):
        seq_des.tradeoff_weights(
            "not_a_scheme", engine.exp_design.x, engine.exp_design.y
        )


# %% Test exploit function


def test_run_exploitation_invalid(basic_seq_des) -> None:
    """Tests invalid exploitation method in the run_exploitation function"""
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.exploit_method = "invalid"

    all_cand = engine.exp_design.generate_samples(10)

    with pytest.raises(NameError) as excinfo:
        seq_des.run_exploitation(all_cand)
    assert (
        str(excinfo.value)
        == "The requested exploitation method invalid is not available."
    )


@pytest.mark.parametrize("util_func", ["alm", "eigf", "mi", "alc"])
def test_run_exploitation_varopt_various_utils(basic_seq_des, util_func):
    """Test run_exploitation with VarOptDesign and different util_funcs returns correct shape,
    positive normalized values"""
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.exploit_method = "VarOptDesign"
    seq_des.exp_design.util_func = util_func

    all_cand = engine.exp_design.generate_samples(5)
    norm_score = seq_des.run_exploitation(all_cand)
    assert isinstance(norm_score, np.ndarray)
    assert norm_score.shape == (5,)
    assert np.all(norm_score >= 0) and np.all(norm_score <= 1)
    assert np.isclose(np.sum(norm_score), 1.0)


@pytest.mark.parametrize(
    "util_func", ["DKL", "BME", "IE", "DIC", "BayesRisk", "DPP", "APP"]
)
def test_run_exploitation_bayesactdesign_various_utils(basic_seq_des, util_func):
    """Test run_exploitation with BayesActDesign and various util_funcs returns correct shape
    Multiple utility functions, check correct sign, normalization."""
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.observations = {"Y": np.array([0, 1]), "Z": np.array([1, 2])}

    seq_des.exp_design.exploit_method = "BayesActDesign"
    seq_des.exp_design.util_func = util_func
    all_cand = engine.exp_design.generate_samples(10)

    norm_score = seq_des.run_exploitation(all_cand)
    assert isinstance(norm_score, np.ndarray)
    assert norm_score.shape == (10,)
    assert np.all(norm_score[~np.isnan(norm_score)] >= 0) and np.all(
        norm_score[~np.isnan(norm_score)] <= 1
    )
    assert np.isclose(np.nansum(norm_score), 1.0)


# %% Test Engine.util_var_opt_design


@pytest.mark.parametrize("util_func", ["alm", "eigf", "mi", "alc"])
def test_util_var_opt_design(basic_seq_des, util_func) -> None:
    """
    Exploration weight with varoptdesign.
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    x_can = engine.exp_design.generate_samples(1)
    seq_des.x_mc = engine.exp_design.generate_samples(10)

    # Run through all util functions
    seq_des.exp_design.util_func = util_func
    phi, _ = seq_des.util_var_opt_design(x_can)
    assert phi < 100


# %% Test Engine.util_bayesian_active_design


def test_util_bayesian_active_design_requires_obs(basic_seq_des) -> None:
    """
    util_bayesian_active_design should raise if no observation is given.
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.exploit_method = "BayesActDesign"
    all_cand = engine.exp_design.generate_samples(10)

    with pytest.raises(AttributeError) as excinfo:
        seq_des.run_exploitation(all_cand)
    assert (
        str(excinfo.value)
        == "Bayesian active design can only be run if an observation is given!"
    )


def test_util_bayesian_active_design_invalid_func(basic_seq_des) -> None:
    """
    util_bayesian_active_design should raise if util_func is not supported.
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    seq_des.exp_design.exploit_method = "BayesActDesign"
    x_can = engine.exp_design.generate_samples(1)

    seq_des.rej_sampler = RejectionSampler(
        out_names=seq_des.out_names,
        use_emulator=False,
        observation={"Y": np.array([0, 1]), "Z": np.array([1, 2])},
        discrepancy=seq_des.discrepancy,
    )

    seq_des.exp_design.util_func = "wrong"
    with pytest.raises(AttributeError) as excinfo:
        seq_des.util_bayesian_active_design(x_can)
    assert str(excinfo.value) == (
        "The requested utility function wrong is not available for BayesActDesign."
    )


@pytest.mark.parametrize(
    "util_func", ["dkl", "bme", "ie", "dic", "bayesrisk", "dpp", "app"]
)
def test_util_bayesian_active_design_valid_funcs(basic_seq_des, util_func) -> None:
    """
    util_bayesian_active_design returns bayesian criteria within reasonable bounds
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    x_can = engine.exp_design.generate_samples(10)

    seq_des.rej_sampler = RejectionSampler(
        out_names=seq_des.out_names,
        use_emulator=False,
        observation={
            "Y": np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
            "Z": np.array(
                [
                    1,
                    2,
                    1,
                    2,
                    1,
                    2,
                    1,
                    2,
                ]
            ),
        },
        discrepancy=seq_des.discrepancy,
    )

    seq_des.exp_design.util_func = util_func
    phi, _ = seq_des.util_bayesian_active_design(x_can)

    assert phi.shape == (10,)


# %% Test Engine.util_alph_opt_design


def test_run_exploitation_alph_design(basic_seq_des):
    """Test run_exploitation with Alphabetic design and valid util_func returns correct shape.
    Single utility function."""
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model

    seq_des.exp_design.exploit_method = "Alphabetic"
    seq_des.exp_design.util_func = "D-opt"
    all_cand = engine.exp_design.generate_samples(10)

    norm_score = seq_des.run_exploitation(all_cand)
    assert isinstance(norm_score, np.ndarray)
    assert norm_score.shape == (10,)
    assert np.all(norm_score >= 0) and np.all(norm_score <= 1)
    assert np.isclose(np.sum(norm_score), 1.0)


@pytest.mark.parametrize("util_func", ["D-opt", "A-opt", "K-opt"])
def test_util_alph_opt_design(basic_seq_des, util_func) -> None:
    """
    Alph-opt design with all available util-functions
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    x_can = engine.exp_design.generate_samples(10)

    # Run through all util functions
    seq_des.exp_design.util_func = util_func
    phi = seq_des.util_alph_opt_design(x_can)
    assert phi.shape == (x_can.shape[0],)


def test_util_alph_opt_design_wrong_util_func(basic_seq_des) -> None:
    """
    Alph-opt design with an invalid utility function
    """
    seq_des, engine = basic_seq_des
    engine.train_normal()
    seq_des.meta_model = engine.meta_model
    x_can = engine.exp_design.generate_samples(10)

    seq_des.exp_design.util_func = "wrong"
    with pytest.raises(AttributeError) as excinfo:
        seq_des.util_alph_opt_design(x_can)
    assert str(excinfo.value) == (
        "The optimality criterion you requested has " "not been implemented yet!"
    )
