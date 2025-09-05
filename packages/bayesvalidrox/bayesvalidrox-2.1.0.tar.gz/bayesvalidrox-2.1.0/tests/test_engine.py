# -*- coding: utf-8 -*-
"""
Tests the class Engine in bayesvalidrox
Engine:
    start_engine         - x
    train_normal
    train_sequential
    eval_metamodel
    train_seq_design
    util_VarBasedDesign
    util_BayesianActiveDesign
    util_BayesianDesign
    run_util_func
    dual_annealing
    tradoff_weights      - x
    choose_next_sample
        plotter
    util_AlphOptDesign
    _normpdf            - x    Also move outside the class?
    _corr_factor_bme           Not used again in this class
    plot_posterior      - x
    _bme_calculator     - x
    _valid_error         - x
    _error_mean_std     - x 

"""
import os
import sys
import numpy as np
import pandas as pd
import pytest

import matplotlib as mpl
mpl.rcParams.update(mpl.rcParamsDefault)

sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.meta_model import MetaModel
from bayesvalidrox.surrogate_models.polynomial_chaos import PCE
from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.surrogate_models.engine import Engine
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy


from fixtures import (
    # Engines
    engine_ut,
    engine_t_pce_single,
    engine_tnomm,
    engine_t_gpe_single,
    engine_t_sequential_single,
    engine_t_pce_multi,
    engine_t_nomm_multi,
    # Support etc
    exp_des_single,
    mm_none,
    model_single,
    input_1i,
    mm_pce_single,
    mm_gpe_single,
    exp_des_multi,
    mm_pce_multi,
    model_multi,
    input_2i,
)


# %% Test Engine constructor


def test_engine_minimal() -> None:
    """
    Build Engine without inputs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    Engine(mm, mod, expdes)


# %% Test Engine.start_engine


def test_start_engine(engine_ut) -> None:
    """
    Build Engine without inputs
    """
    engine_ut.start_engine()


# %% Test Engine.train_normal
# TODO: build mock model to do this?


def test_train_normal(engine_ut) -> None:
    """
    Standard surrogate training with given points
    """
    engine = engine_ut
    engine.exp_design.x = np.array([[0], [1], [0.5]])
    engine.exp_design.y = {"Z": [[0.4], [0.5], [0.45]]}
    engine.exp_design.x_values = np.array([0])
    engine.meta_model = PCE(engine.exp_design.input_object)

    engine.train_normal()
    assert engine.trained
    # TODO: what to assert for?
    engine.train_normal(save=True)
    assert engine.trained
    assert os.path.exists(f"./surrogates/surrogate_{engine.model.name}.pk1")


def test_train_normal_nometamod(engine_ut) -> None:
    """
    Standard surrogate training without metamodel
    """
    engine = engine_ut
    engine.exp_design.x = np.array([[0], [1], [0.5]])
    engine.exp_design.y = {"Z": [[0.4], [0.5], [0.45]]}

    engine.train_normal()
    assert engine.trained


def test_train_normal_nodict(engine_ut) -> None:
    """
    Standard surrogate training with incorrect y
    """
    engine = engine_ut
    engine.exp_design.x = np.array([[0], [1], [0.5]])
    engine.exp_design.y = [[0.4], [0.5], [0.45]]

    with pytest.raises(TypeError) as excinfo:
        engine.train_normal()
    assert str(excinfo.value) == (
        "Please provide either a dictionary or a hdf5"
        "file to exp_design.hdf5_file argument."
    )


# %% Test Engine.eval_metamodel
def test_eval_metamodel(engine_t_pce_multi) -> None:
    """
    Evaluate metamodel via engine
    """
    engine = engine_t_pce_multi
    # Empty return
    out = engine.eval_metamodel()
    assert out == None

    # Using nsamples
    out = engine.eval_metamodel(nsamples=4)
    assert len(out) == 2
    assert list(out[0].keys()) == engine.out_names
    for key in engine.out_names:
        assert out[0][key].shape == (4, 10)
        assert out[1][key].shape == (4, 10)
    out = engine.eval_metamodel(nsamples=4, return_samples=True)
    assert len(out) == 3
    assert list(out[0].keys()) == engine.out_names
    for key in engine.out_names:
        assert out[0][key].shape == (4, 10)
        assert out[1][key].shape == (4, 10)
    assert out[2].shape == (4, 2)

    # Using samples
    samples = np.array([[1, 1], [0, 1], [1, 0]])
    out = engine.eval_metamodel(samples=samples)
    assert len(out) == 2
    assert list(out[0].keys()) == engine.out_names
    for key in engine.out_names:
        assert out[0][key].shape == (3, 10)
        assert out[1][key].shape == (3, 10)
    out = engine.eval_metamodel(samples=samples, return_samples=True)
    assert len(out) == 3
    assert list(out[0].keys()) == engine.out_names
    for key in engine.out_names:
        assert out[0][key].shape == (3, 10)
        assert out[1][key].shape == (3, 10)
    assert out[2].shape == (3, 2)


def test_eval_metamodel_nometamod(engine_t_nomm_multi) -> None:
    """
    Evaluate model via engine
    """
    engine = engine_t_nomm_multi
    # Empty return
    out = engine.eval_metamodel()
    assert out == None

    # Using nsamples
    out = engine.eval_metamodel(nsamples=4)
    assert len(out) == 2
    for key in engine.out_names:
        assert key in out[0].keys()
    assert "x_values" in out[0].keys()
    assert out[1] == None
    for key in engine.out_names:
        assert out[0][key].shape == (4, 10)
    out = engine.eval_metamodel(nsamples=4, return_samples=True)
    assert len(out) == 3
    for key in engine.out_names:
        assert key in out[0].keys()
    assert "x_values" in out[0].keys()
    assert out[1] == None
    for key in engine.out_names:
        assert out[0][key].shape == (4, 10)
    assert out[2].shape == (4, 2)

    # Using samples
    samples = np.array([[1, 1], [0, 1], [1, 0]])
    out = engine.eval_metamodel(samples=samples)
    assert len(out) == 2
    for key in engine.out_names:
        assert key in out[0].keys()
    assert "x_values" in out[0].keys()
    assert out[1] == None
    for key in engine.out_names:
        assert out[0][key].shape == (3, 10)
    out = engine.eval_metamodel(samples=samples, return_samples=True)
    assert len(out) == 3
    for key in engine.out_names:
        assert key in out[0].keys()
    assert "x_values" in out[0].keys()
    assert out[1] == None
    for key in engine.out_names:
        assert out[0][key].shape == (3, 10)
    assert out[2].shape == (3, 2)


# %% Test Engine.add_to_valid


def test_add_to_valid_internal() -> None:
    """
    Add to validation sets, stored in engine
    """
    engine = Engine(None, None, None)
    engine.out_names = ["a"]

    # Catch all errors
    with pytest.raises(AttributeError) as excinfo:
        out = engine.add_to_valid(name="test", values=10, v_type="other")
    assert str(excinfo.value) == ("Given validation type is not valid.")

    with pytest.raises(AttributeError) as excinfo:
        out = engine.add_to_valid(name="test", values=10, v_type="valid")
    assert str(excinfo.value) == ("Type 'valid' expects a dictionary.")

    with pytest.raises(AttributeError) as excinfo:
        out = engine.add_to_valid(name="test", values={10: 1}, v_type="bayes")
    assert str(excinfo.value) == ("Type 'bayes' expects a list or value.")

    # Add to valid
    ref_out = ({"test": {"a": [1]}}, {})
    out = engine.add_to_valid(name="test", values={"a": 1}, v_type="valid")
    assert out == None
    assert engine.valid_metrics == ref_out[0]
    assert engine.bayes_metrics == ref_out[1]
    ref_out = ({"test": {"a": [1, 2]}}, {})
    out = engine.add_to_valid(name="test", values={"a": 2}, v_type="valid")
    assert out == None
    assert engine.valid_metrics == ref_out[0]
    assert engine.bayes_metrics == ref_out[1]

    # Add to bayes
    ref_out = ({"test": {"a": [1, 2]}}, {"bme": [[15]]})
    out = engine.add_to_valid(name="bme", values=[15], v_type="bayes")
    assert out == None
    assert engine.valid_metrics == ref_out[0]
    assert engine.bayes_metrics == ref_out[1]


def test_add_to_valid_external() -> None:
    """
    Add to validation sets, returned
    """
    engine = Engine(None, None, None)
    engine.out_names = ["a"]
    storage = {}, {}

    # Catch all errors
    with pytest.raises(AttributeError) as excinfo:
        out = engine.add_to_valid(
            name="test", values=10, v_type="other", storage=storage
        )
    assert str(excinfo.value) == ("Given validation type is not valid.")

    with pytest.raises(AttributeError) as excinfo:
        out = engine.add_to_valid(
            name="test", values=10, v_type="valid", storage=storage
        )
    assert str(excinfo.value) == ("Type 'valid' expects a dictionary.")

    with pytest.raises(AttributeError) as excinfo:
        out = engine.add_to_valid(
            name="test", values={10: 1}, v_type="bayes", storage=storage
        )
    assert str(excinfo.value) == ("Type 'bayes' expects a list or value.")

    # Add to valid
    ref_out = ({"test": {"a": [1]}}, {})
    out = engine.add_to_valid(
        name="test", values={"a": 1}, v_type="valid", storage=storage
    )
    assert out == ref_out
    storage = out
    ref_out = ({"test": {"a": [1, 2]}}, {})
    out = engine.add_to_valid(
        name="test", values={"a": 2}, v_type="valid", storage=storage
    )
    assert out == ref_out

    # Add to bayes
    storage = out
    ref_out = ({"test": {"a": [1, 2]}}, {"bme": [[15]]})
    out = engine.add_to_valid(name="bme", values=[15], v_type="bayes", storage=storage)
    assert out == ref_out


# %% Test Engine.validate
def test_validate_internal(engine_t_pce_multi) -> None:
    """
    Run through the metamodel validation, strogin in the engine
    """
    # Clear training results
    engine = engine_t_pce_multi
    engine.valid_metrics, engine.bayes_metrics = {}, {}

    # Default: only modloo
    engine.validate()
    assert list(engine.valid_metrics.keys()) == ["mod_loo"]
    for key in engine.model.output.names:
        assert len(engine.valid_metrics["mod_loo"][key]) == 1
        assert len(engine.valid_metrics["mod_loo"][key]) == 1
    assert engine.bayes_metrics == {}

    # RMSE/MSE/R2: add x_valid/y_valid
    engine.exp_design.x_valid = [[0.0, 0.0], [0.5, 0.5]]
    engine.exp_design.y_valid = {
        "Z1": [
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        "Z2": [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]],
    }
    engine.valid_metrics, engine.bayes_metrics = {}, {}
    engine.validate()
    assert list(engine.valid_metrics.keys()) == ["rmse", "mse", "r2", "mod_loo"]
    for key in engine.model.output.names:
        assert len(engine.valid_metrics["rmse"][key]) == 1
        assert len(engine.valid_metrics["mse"][key]) == 1
        assert len(engine.valid_metrics["r2"][key]) == 1
    assert engine.bayes_metrics == {}

    # mean_err/std_err : add mc_ref
    engine.model.mc_reference = {
        "mean": {
            "Z1": [3, 4, 3, 4, 3, 4, 3, 4, 3, 4],
            "Z2": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        },
        "std": {
            "Z1": [3, 4, 3, 4, 3, 4, 3, 4, 3, 4],
            "Z2": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        },
    }
    engine.exp_design.x_valid, engine.exp_design.y_valid = None, None
    engine.valid_metrics, engine.bayes_metrics = {}, {}
    engine.validate()
    assert list(engine.valid_metrics.keys()) == ["mean_err", "std_err", "mod_loo"]
    for key in engine.model.output.names:
        assert len(engine.valid_metrics["mean_err"][key]) == 1
        assert len(engine.valid_metrics["std_err"][key]) == 1
    assert engine.bayes_metrics == {}

    # TODO: add checks for the Bayesian metrics


# %% Test Engine.train_sequential


def test_train_sequential(engine_t_pce_multi) -> None:
    """
    Test sequential training
    """
    engine = engine_t_pce_multi
    engine.exp_design.tradeoff_scheme = "explore_only"
    engine.exp_design.n_max_samples = engine.exp_design.x.shape[0] + 1
    engine.train_sequential()

    # Check for samples
    assert engine.exp_design.x.shape[0] == 6  # engine.exp_design.n_max_samples
    assert engine.seq_des is not None
    assert len(engine.valid_metrics["mod_loo"]) == 2


# %% Test Engine._error_mean_std


def test__error_mean_std(engine_t_pce_single) -> None:
    """
    Compare moments of surrogate and reference without mc-reference
    """
    engine = engine_t_pce_single
    engine.model.mc_reference["mean"] = {"Z": [0.5]}
    engine.model.mc_reference["std"] = {"Z": [0.0]}
    engine.model.output.names = ["Z"]
    mean, std = engine._error_mean_std()
    assert mean["Z"] < 0.02 and std["Z"] < 0.1


def test__error_mean_std_nomc(engine_tnomm) -> None:
    """
    Compare moments of surrogate and reference without mc-reference
    """
    with pytest.raises(AttributeError) as excinfo:
        engine_tnomm._error_mean_std()
    assert str(excinfo.value) == (
        "Model.mc_reference needs to be given to calculate the surrogate error!"
    )


# %% Test Engine._valid_error


def test__valid_error(engine_t_pce_single) -> None:
    """
    Calculate validation error
    """
    engine = engine_t_pce_single
    engine.exp_design.x_valid = np.array([[0.5]])
    engine.exp_design.y_valid = {"Z": np.array([[0.5]])}
    rmse, mse, _, valid_error = engine._valid_error()
    assert rmse["Z"][0] < 0.1
    assert mse["Z"][0] < 0.1
    # assert 0<r2['Z']<1 # TODO: sensible assert for R2
    assert np.isnan(valid_error["Z"])


# %% Test Engine._bme_calculator


def test__bme_calculator(engine_t_pce_multi) -> None:
    """
    Calculate BME
    """
    engine = engine_t_pce_multi
    obs_data = {
        "Z1": np.array([0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8, 0.4, 0.4, 0.4]),
        "Z2": np.array([0.4, 0.4, 0.4, 0.8, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]),
    }
    sigma_2_dict = {
        "Z1": np.array([0.05, 0.05, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]),
        "Z2": np.array([0.05, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]),
    }
    disc = Discrepancy(parameters=sigma_2_dict)
    disc.build_discrepancy()
    engine.discrepancy = disc
    sigma_2_dict = pd.DataFrame(sigma_2_dict, columns=["Z1", "Z2"])
    engine._bme_calculator(obs_data)


def test__bme_calculator_rmse(engine_t_pce_multi) -> None:
    """
    Calculate BME with given RMSE
    """
    engine = engine_t_pce_multi
    obs_data = {
        "Z1": np.array([0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8, 0.4, 0.4, 0.4]),
        "Z2": np.array([0.4, 0.4, 0.4, 0.8, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]),
    }
    sigma_2_dict = {
        "Z1": np.array([0.05, 0.05, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]),
        "Z2": np.array([0.05, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]),
    }
    disc = Discrepancy(parameters=sigma_2_dict)
    disc.build_discrepancy()
    engine.discrepancy = disc
    sigma_2_dict = pd.DataFrame(sigma_2_dict, columns=["Z1", "Z2"])
    rmse = {"Z1": 0.1, "Z2": 0.1}

    engine._bme_calculator(obs_data, rmse=rmse)
    # Note: if error appears here it might also be due to inoptimal choice of training samples
