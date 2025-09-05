# -*- coding: utf-8 -*-
"""
Test the PostProcessing class in bayesvalidrox.
"""

import sys
import os

sys.path.append("../src/")
import numpy as np
import pytest
import matplotlib

from bayesvalidrox.post_processing.post_processing import PostProcessing

matplotlib.use("Agg")

from fixtures import (
    # Engines
    engine_ut,
    engine_t_pce_single,
    engine_tnomm,
    engine_t_gpe_single,
    engine_t_sequential_single,
    engine_t_pce_multi,
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


# %% Test PostProcessing init
def test_postprocessing(
    engine_ut, engine_tnomm, engine_t_pce_single, engine_t_gpe_single
):
    """
    Init PostProcessing
    """
    # TODO: Init without engine

    # Untrained engine
    with pytest.raises(AttributeError) as excinfo:
        PostProcessing(engine_ut)
    assert (
        str(excinfo.value) == "PostProcessing can only be performed on trained engines."
    )
    with pytest.raises(AttributeError) as excinfo:
        PostProcessing(engine_tnomm)
    assert (
        str(excinfo.value)
        == "PostProcessing can only be performed on engines with a trained MetaModel."
    )

    # Fully trained engine
    PostProcessing(engine_t_pce_single)
    PostProcessing(engine_t_gpe_single)


# %% plot_moments
def test_plot_moments_pce(engine_t_pce_single) -> None:
    """
    Plot moments for PCE metamodel
    """
    engine = engine_t_pce_single
    post = PostProcessing(engine)
    mean, stdev = post.plot_moments()
    # Check the mean dict
    assert list(mean.keys()) == ["Z"]
    assert mean["Z"].shape == (1,)
    assert mean["Z"][0] == pytest.approx(0.48, abs=0.1)
    # Check the stdev dict
    assert list(stdev.keys()) == ["Z"]
    assert stdev["Z"].shape == (1,)
    assert stdev["Z"][0] == pytest.approx(0.0, abs=0.1)


def test_plot_moments_pcebar(engine_t_pce_single) -> None:
    """
    Plot moments for PCE metamodel with bar-plot
    """
    engine = engine_t_pce_single
    post = PostProcessing(engine)
    mean, stdev = post.plot_moments(plot_type="bar")
    # Check the mean dict
    assert list(mean.keys()) == ["Z"]
    assert mean["Z"].shape == (1,)
    assert mean["Z"][0] == pytest.approx(0.48, abs=0.1)
    # Check the stdev dict
    assert list(stdev.keys()) == ["Z"]
    assert stdev["Z"].shape == (1,)
    assert stdev["Z"][0] == pytest.approx(0.0, abs=0.1)


def test_plot_moments_gpe(engine_t_gpe_single) -> None:
    """
    Plot moments for GPE metamodel
    """
    engine = engine_t_gpe_single
    post = PostProcessing(engine)
    mean, stdev = post.plot_moments()
    # Check the mean dict
    assert list(mean.keys()) == ["Z"]
    assert mean["Z"].shape == (1,)
    assert mean["Z"][0] == pytest.approx(0.45, abs=0.01)
    # Check the stdev dict
    assert list(stdev.keys()) == ["Z"]
    assert stdev["Z"].shape == (1,)
    assert stdev["Z"][0] == pytest.approx(0.0, abs=0.01)


def test_plot_moments_gpebar(engine_t_gpe_single) -> None:
    """
    Plot moments for GPE metamodel with bar-plot
    """
    engine = engine_t_gpe_single
    post = PostProcessing(engine)
    mean, stdev = post.plot_moments(plot_type="bar")
    # Check the mean dict
    assert list(mean.keys()) == ["Z"]
    assert mean["Z"].shape == (1,)
    assert mean["Z"][0] == pytest.approx(0.45, abs=0.01)
    # Check the stdev dict
    assert list(stdev.keys()) == ["Z"]
    assert stdev["Z"].shape == (1,)
    assert stdev["Z"][0] == pytest.approx(0.0, abs=0.01)


# %% validate_metamodel
def test_validate_metamodel_pce(engine_t_pce_single):
    """
    Run validation on pce
    """
    engine = engine_t_pce_single
    engine.n_samples = [engine.exp_design.n_max_samples]
    samples = np.array([[0], [1], [0.5]])
    model_out_dict = {"Z": np.array([[0.4], [0.5], [0.45]]), "x_values": np.array([0])}
    engine.exp_design.x_valid = samples
    engine.exp_design.y_valid = model_out_dict

    post = PostProcessing(engine)
    post.validate_metamodel()
    # TODO: add asserts


def test_validate_metamodel_pce_multi(engine_t_pce_multi):
    """
    Run validation on pce
    """
    engine = engine_t_pce_multi
    engine.n_samples = [engine.exp_design.n_max_samples]
    samples = np.array([[0, 0], [1, 1], [0.5, 0.5]])
    model_out_dict = engine.model.run_model_parallel(samples)[0]
    engine.exp_design.x_valid = samples
    engine.exp_design.y_valid = model_out_dict

    post = PostProcessing(engine)
    post.validate_metamodel()
    # TODO: add asserts


def test_validate_metamodel_gpe(engine_t_gpe_single):
    """
    Run validation on gpe
    """
    engine = engine_t_gpe_single
    engine.n_samples = [engine.exp_design.n_max_samples]
    samples = np.array([[0], [1], [0.5]])
    model_out_dict = {"Z": np.array([[0.4], [0.5], [0.45]]), "x_values": np.array([0])}
    engine.exp_design.x_valid = samples
    engine.exp_design.y_valid = model_out_dict

    post = PostProcessing(engine)
    post.validate_metamodel()


# %% plot_seq_design_diagnoxtics


def test_plot_seq_design_diagnostics(engine_t_pce_single):
    """
    Test the plot_seq_design_diagnostics method
    """
    engine = engine_t_pce_single
    post = PostProcessing(engine)

    # Run with standard settings
    post.plot_seq_design_diagnostics()
    assert os.path.exists(f"./{post.out_dir}/validation_engine.{post.out_format}")


# %% sobol_indices


def test_sobol_indices_pce(engine_t_pce_single) -> None:
    """
    Calculate sobol indices for PCE metamodel
    """
    engine = engine_t_pce_single
    post = PostProcessing(engine)
    sobol, totalsobol = post.sobol_indices()

    assert list(totalsobol.keys()) == ["Z"]
    assert totalsobol["Z"].shape == (1, 1)
    assert totalsobol["Z"][0, 0] == 1

    print(sobol)
    assert list(sobol.keys()) == [1]
    assert list(sobol[1].keys()) == ["Z"]
    assert sobol[1]["Z"].shape == (1, 1, 1)
    assert sobol[1]["Z"][0, 0] == 1


def test_sobol_indices_with_invalid_model_type(engine_t_gpe_single) -> None:
    """
    Calculate sobol indices with invalid model type
    """
    engine = engine_t_gpe_single
    post = PostProcessing(engine)
    post.model_type = "INVALID"
    with pytest.raises(AttributeError) as excinfo:
        post.sobol_indices()
    assert "Sobol indices only support PCE-type models!" in str(excinfo.value)


# %% plot_residual_hist
def test_plot_residual_hist(engine_t_pce_multi):
    """
    Test the _plot_validation_multi method
    """
    engine = engine_t_pce_multi
    post = PostProcessing(engine)
    x = np.array([[1, 1], [0.5, 0.5], [0, 0]])
    y_val, _ = engine.eval_metamodel(x)
    model_out, _ = engine.model.run_model_parallel(x)

    post.plot_residual_hist(model_out, y_val)
    assert os.path.exists(f"./{post.out_dir}/Hist_Residuals.{post.out_format}")


# %% plot_validation_outputs only for PCE
def test_plot_validation_outputs(engine_t_pce_multi):
    """
    Test the _plot_validation_multi method
    """
    engine = engine_t_pce_multi
    post = PostProcessing(engine)
    x = np.array([[1, 1], [0.5, 0.5], [0, 0]])
    y_val, y_val_std = engine.eval_metamodel(x)
    model_out, _ = engine.model.run_model_parallel(x)

    post.plot_validation_outputs(y_val, y_val_std, model_out)
    # Check if the plot was created and saved
    assert os.path.exists(f"./{post.out_dir}/Model_vs_MetaModel_Z1.{post.out_format}")
    assert os.path.exists(f"./{post.out_dir}/Model_vs_MetaModel_Z2.{post.out_format}")


def test_plot_validation_outputs_pce(engine_t_pce_single):
    """
    Plot validation on pce (no diff to gpe)
    """
    engine = engine_t_pce_single
    post = PostProcessing(engine)
    out_mean = {"Z": np.array([[0.4], [0.5], [0.45], [0.4]])}
    out_std = {"Z": np.array([[0.1], [0.1], [0.1], [0.1]])}
    model_out_dict = {"Z": np.array([[0.4], [0.5], [0.3], [0.4]])}
    post.plot_validation_outputs(out_mean, out_std, model_out_dict)
