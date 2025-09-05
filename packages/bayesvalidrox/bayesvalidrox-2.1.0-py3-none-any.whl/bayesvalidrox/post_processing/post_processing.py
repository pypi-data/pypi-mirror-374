#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of postprocessing functions into a class.
"""

import os
import itertools
from itertools import combinations
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, ScalarFormatter
from matplotlib.offsetbox import AnchoredText
from matplotlib.gridspec import GridSpec
import seaborn as sns

plt.style.use(os.path.join(os.path.split(__file__)[0], "../", "bayesvalidrox.mplstyle"))


class PostProcessing:
    """
    This class provides post-processing functions for the trained metamodels.

    Parameters
    ----------
    engine : obj
        Trained Engine object, is expected to contain a trained MetaModel object.
    name : string
        Name of the PostProcessing object to be used for saving the generated files.
        The default is 'calib'.
    out_dir : string
        Output directory in which the PostProcessing results are placed.
        The results are contained in a subfolder '/Outputs_PostProcessing_name'
        The default is ''.
    out_format : string
        Format of the saved plots. Supports 'png' and 'pdf'. The default is 'pdf'.

    Raises
    ------
    AttributeError
        `engine` must be trained.

    """

    def __init__(self, engine, name="calib", out_dir="", out_format="pdf"):
        # PostProcessing only available for trained engines
        if not engine.trained:
            raise AttributeError(
                "PostProcessing can only be performed on trained engines."
            )

        if not engine.meta_model:
            raise AttributeError(
                "PostProcessing can only be performed on engines with a trained MetaModel."
            )

        self.engine = engine
        self.name = name
        self.out_format = out_format
        self.par_names = self.engine.exp_design.par_names
        self.x_values = self.engine.exp_design.x_values

        # Initialize attributes
        self.plot_type = ""
        self.xlabel = "Time [s]"
        self.sobol = None
        self.totalsobol = None
        self.out_dir = f"./{out_dir}/Outputs_PostProcessing_{self.name}/"

        # Create output folder for the plots
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

    def plot_expdesign(self, n_mc=10000, show_samples=False):
        """
        Visualizes training samples over their given distributions as a
        pairplot.

        Parameters
        ----------
        n_mc : int, optional
            Number of samples from the priors to use for plotting.
            The default is 10000.
        show_samples : bool, optional
            If set to True the training samples are also visualized.
            The default is False.

        Returns
        -------
        None.

        """
        exp_des = self.engine.exp_design
        if len(exp_des.input_object.marginals) > 10:
            raise ValueError("Plot not possible for more than 10 input parameters")

        # Generate the plot
        names = []
        for _, marg in enumerate(exp_des.input_object.marginals):
            names.append(marg.name)

        # Generate prior samples
        samples = exp_des.generate_samples(n_mc, "random")
        n_marg = samples.shape[1]

        fig, axes = plt.subplots(
            nrows=n_marg, ncols=n_marg, figsize=(4 * len(names), 4 * len(names))
        )
        fig.subplots_adjust(hspace=0.05, wspace=0.05)

        if len(names) == 1:
            # Prior
            label = names[0]
            axes.annotate(
                label, (0.5, 0.5), xycoords="axes fraction", ha="center", va="center"
            )
            data = pd.DataFrame({label: samples[:, 0]})
            axes = sns.kdeplot(data=data, x=label, color="gray", ax=axes, fill=True)

            # Training points
            x_init = exp_des.x[: exp_des.n_init_samples, :]
            x_seq = exp_des.x[exp_des.n_init_samples :, :]
            for col, x in {"red": x_init, "blue": x_seq}.items():
                data = pd.DataFrame({label: x[:, 0]})
                axes = sns.histplot(
                    data=data,
                    x=label,
                    color=col,
                    ax=axes,
                    fill=True,
                    alpha=0.2,
                    stat="density",
                )
            # Remove added labels
            axes.set_ylabel("")
            axes.set_xlabel("")
            axes.xaxis.set_visible(True)

            # Legend
            # h, l = axes.get_legend_handles_labels()
            # fig.legend(h, l, loc="center left", bbox_to_anchor=(0.9, 0.5))

        else:
            # Diagonal subplots
            for i, label in enumerate(names):
                # Prior
                axes[i, i].annotate(
                    label,
                    (0.5, 0.5),
                    xycoords="axes fraction",
                    ha="center",
                    va="center",
                )
                data = pd.DataFrame({label: samples[:, i]})
                axes[i, i] = sns.kdeplot(
                    data=data, x=label, color="gray", ax=axes[i, i], fill=True
                )

                # Training points
                x_init = exp_des.x[: exp_des.n_init_samples, :]
                x_seq = exp_des.x[exp_des.n_init_samples :, :]
                for col, x in {"red": x_init, "blue": x_seq}.items():
                    data = pd.DataFrame({label: x[:, i]})
                    axes[i, i] = sns.histplot(
                        data=data,
                        x=label,
                        color=col,
                        ax=axes[i, i],
                        fill=True,
                        alpha=0.2,
                        stat="density",
                    )

                # Remove added labels
                axes[i, i].set_ylabel("")
                axes[i, i].set_xlabel("")

            # KDE plot
            for i, j in zip(*np.triu_indices_from(axes, k=1)):
                for x, y in [(i, j), (j, i)]:
                    axes[x, y] = sns.kdeplot(
                        x=samples[:, y],
                        y=samples[:, x],
                        ax=axes[x, y],
                        levels=5,
                        color="gray",
                        label="marginal",
                        fill=True,
                    )

            # Scatter plots
            if show_samples:
                x_init = exp_des.x[: exp_des.n_init_samples, :]
                x_seq = exp_des.x[exp_des.n_init_samples :, :]

                for i, j in zip(*np.triu_indices_from(axes, k=1)):
                    for x, y in [(i, j), (j, i)]:
                        axes[x, y].scatter(
                            x_init[:, y],
                            x_init[:, x],
                            color="red",
                            marker="x",
                            label="training points",
                        )
                        axes[x, y].scatter(
                            x_seq[:, y],
                            x_seq[:, x],
                            color="blue",  #'cyan',
                            # edgecolors='black',
                            label="sequential points",
                        )

            # Manage ticks, labels
            for ax in axes.flat:
                ax.xaxis.set_visible(False)
                ax.yaxis.set_visible(False)
                ax.grid(False)

                # Set up ticks only on one side for the "edge" subplots
                if ax.get_subplotspec().is_first_col():
                    ax.yaxis.set_ticks_position("left")
                if ax.get_subplotspec().is_last_col():
                    ax.yaxis.set_ticks_position("right")
                if ax.get_subplotspec().is_first_row():
                    ax.xaxis.set_ticks_position("top")
                if ax.get_subplotspec().is_last_row():
                    ax.xaxis.set_ticks_position("bottom")

            # Turn on the proper x or y axes ticks.
            for i, j in zip(range(n_marg), itertools.cycle((-1, 0))):
                axes[j, i].xaxis.set_visible(True)
                axes[i, j].yaxis.set_visible(True)

            # Legend
            h, l = axes[0, 1].get_legend_handles_labels()
            fig.legend(h, l, loc="center left", bbox_to_anchor=(0.9, 0.5))
        # Store
        plt.savefig(f"{self.out_dir}/priors.{self.out_format}", bbox_inches="tight")
        plt.close()

    # -------------------------------------------------------------------------
    def plot_moments(self, plot_type: str = "line"):
        """
        Plots the moments in a user defined output format (standard is pdf) in the directory
        `Outputs_PostProcessing`.

        Parameters
        ----------
        plot_type : str, optional
            Supports 'bar' for barplots and 'line'
            for lineplots The default is `line`.

        Raises
        ------
        AttributeError
            Plot type must be 'bar' or 'line'.

        Returns
        -------
        means: dict
            Mean of the model outputs.
        means: dict
            Standard deviation of the model outputs.

        """
        if plot_type not in ["bar", "line"]:
            raise AttributeError("The wanted plot-type is not supported.")
        bar_plot = bool(plot_type == "bar")
        meta_model_type = self.engine.meta_model.meta_model_type

        # Read Monte-Carlo reference
        mc_reference = {}
        try:
            mc_reference = self.engine.model.read_observation("mc_ref")
        except AttributeError:
            mc_reference = {}

        # Compute the moments with the PCEModel object
        means, stds = self.engine.meta_model.calculate_moments()

        # Plot the best fit line
        for key in self.engine.out_names:
            fig, ax = plt.subplots(nrows=1, ncols=2)

            # Extract mean and std
            mean_data = means[key]
            std_data = stds[key]

            # Plot: bar plot or line plot
            if bar_plot:
                ax[0].bar(
                    list(map(str, self.x_values)), mean_data, color="b", width=0.25
                )
                ax[1].bar(
                    list(map(str, self.x_values)), std_data, color="b", width=0.25
                )
                ax[0].legend(labels=[meta_model_type])
                ax[1].legend(labels=[meta_model_type])
            else:
                ax[0].plot(
                    self.x_values,
                    mean_data,
                    lw=3,
                    color="k",
                    marker="x",
                    label=meta_model_type,
                )
                ax[1].plot(
                    self.x_values,
                    std_data,
                    lw=3,
                    color="k",
                    marker="x",
                    label=meta_model_type,
                )

            if mc_reference != {}:
                if bar_plot:
                    ax[0].bar(
                        list(map(str, self.x_values)),
                        mc_reference["mean"][key],
                        color="r",
                        width=0.25,
                    )
                    ax[1].bar(
                        list(map(str, self.x_values)),
                        mc_reference["std"][key],
                        color="r",
                        width=0.25,
                    )
                    ax[0].legend(labels=[meta_model_type])
                    ax[1].legend(labels=[meta_model_type])
                else:
                    ax[0].plot(
                        self.x_values,
                        mc_reference["mean"][key],
                        lw=3,
                        marker="x",
                        color="r",
                        label="Ref.",
                    )
                    ax[1].plot(
                        self.x_values,
                        mc_reference["std"][key],
                        lw=3,
                        marker="x",
                        color="r",
                        label="Ref.",
                    )

            # Label the axes and provide a title
            ax[0].set_xlabel(self.xlabel)
            ax[1].set_xlabel(self.xlabel)
            ax[0].set_ylabel(key)
            ax[1].set_ylabel(key)

            # Provide a title
            ax[0].set_title("Mean of " + key)
            ax[1].set_title("Std of " + key)

            if not bar_plot:
                ax[0].legend(loc="best")
                ax[1].legend(loc="best")
            plt.tight_layout()
            fig.savefig(
                f"{self.out_dir}Mean_Std_PCE_{key}.{self.out_format}",
                bbox_inches="tight",
            )
            plt.close()

        return means, stds

    # -------------------------------------------------------------------------
    def validate_metamodel(self, n_samples=None, sampling_method="random"):
        """
        Evaluates all available validation metrics for the engine on validation samples
        and visualizes the results.

        Parameters
        ----------
        n_samples : int, optional
            Number of validation samples to generate.
            If this is set to None, then the validation samples in the exp_design
            are used.
            The default is None.
        sampling_method : str, optional
            Sampling method. The default is `'random'`.

        Returns
        -------
        valid, bayes : dict, dict
            Evaluation of the applicable metrics.
        """
        # Get validation samples (from exp_design or generate from model)
        x_valid, y_valid = None, None
        if n_samples is not None:
            x_valid = self.engine.exp_design.generate_samples(
                n_samples, sampling_method
            )
            y_valid, _ = self.engine.model.run_model_parallel(x_valid, store_hdf5=False)
            self.engine.exp_design.x_valid = x_valid
            self.engine.exp_design.y_valid = y_valid
        else:
            x_valid = self.engine.exp_design.x_valid
            y_valid = self.engine.exp_design.y_valid

        y_mm, y_std_mm = self.engine.eval_metamodel(x_valid)
        y_mm_t, _ = self.engine.eval_metamodel(self.engine.exp_design.x)

        # Run engine.validate - not storing in engine
        out = self.engine.validate(store=False, verbose=True)

        ### PLOT
        # Plot over time
        self.plot_validation_outputs(y_valid, y_mm, y_std_mm)

        # Linear correl plot (including r2 score in the corner)
        self.plot_correl(self.engine.exp_design.y, y_mm_t, name="train")
        self.plot_correl(y_valid, y_mm, r_2=out[0]["r2"], name="valid")

        # Plot the residuals
        self.plot_residual_hist(y_valid, y_mm)

        # Sequential metrics plot
        self.plot_seq_design_diagnostics(metrics=out, name="post")

        return out

    def plot_correl(self, y_model, y_mm, r_2=None, name="valid") -> None:
        """
        Plot the correlation between the model and metamodel outputs.

        Parameters
        ----------
        y_model : dict
            Model evaluations.
        y_mm : dict
            MetaModel evaluations.
        r_2 : dict, optional
            R2 score for each output key (as a list per key).
            The default is None.
        name : string, optional
            Name of the file.
            The default is 'valid'.

        """
        # Create one subfigure per output key - cut off each ~10 keys
        n_plots = 10
        n_keys = len(self.engine.out_names)
        n_rows = int(n_keys / n_plots) + 1

        fig = plt.figure(figsize=(5 * n_plots, 4 * n_rows))
        gs_ = GridSpec(n_rows, n_plots, wspace=0.3, hspace=0.3)

        for k_idx, key in enumerate(self.engine.out_names):
            row = int(k_idx / n_plots)
            index = k_idx % n_plots

            # plot
            ax = fig.add_subplot(gs_[row, index])
            ax.plot(
                [0, 1], [0, 1], transform=ax.transAxes, color="gray", linestyle="dashed"
            )
            ax.scatter(y_model[key], y_mm[key])

            # Labels
            ax.set_title(key)
            if row == 0:
                ax.set_xlabel("model")
            if index == 0:
                ax.set_ylabel("metamodel")

            # Show R2 value
            if r_2 is not None:
                bbox = {"boxstyle": "round", "fc": "0.9"}
                ax.annotate(
                    f"$R^2$ = {r_2[key][-1]:.2f}",
                    xy=(0.48, 0.1),
                    xycoords="axes fraction",
                    bbox=bbox,
                    fontsize=20,
                )

        fig.savefig(
            f"./{self.out_dir}/correl_{name}.{self.out_format}",
            bbox_inches="tight",
        )
        plt.close()

    def plot_seq_design_diagnostics(
        self, plot_single=True, metrics=None, name="engine"
    ) -> None:
        """
        Plots the validation metrics calculated in the engine.

        Parameters
        ----------
        plot_single : bool
            If set to True, generates a single file with all the results.
            If set to False, generates a file for each validation type.
        metrics : list
            List of the metrics dictionaries, if generated in validation and
            not as part of the engine.
        name : str, optional
            Name of the plot. Will be 'post' if used from self.validate_metamodel.
            The default is 'engine'.

        """
        if metrics is None:
            valid_metrics = self.engine.valid_metrics
            bayes_metrics = self.engine.bayes_metrics
            n_samples = self.engine.n_samples
        else:
            valid_metrics = metrics[0]
            bayes_metrics = metrics[1]
            n_samples = np.array([self.engine.n_samples[-1]])

        if (
            len(list(valid_metrics.keys())) == 0
            and len(list(bayes_metrics.keys())) == 0
        ):
            print("No validation metrics available to plot.")
            return None

        valid_types = list(valid_metrics.keys())
        bayes_types = list(bayes_metrics.keys())

        line_styles = ["-", "--", "-.", ":"]
        markers = ["o", "s", "^", "d", "v", "x"]
        sizes = ["14", "10", "6", "4", "2", "1"]  # extend if needed

        # All plots in a single file
        if plot_single:
            fig = plt.figure()
            num_grid = np.max([len(valid_types), len(bayes_types)])
            gs_ = GridSpec(2, num_grid, wspace=0.5, hspace=0.3)
            for v_id, v_type in enumerate(valid_types):
                ax = fig.add_subplot(gs_[0, v_id])

                for k_id, key in enumerate(valid_metrics[v_type]):
                    vals = valid_metrics[v_type][key]
                    if np.ndim(vals) > 1:
                        mean_vals = np.mean(vals, axis=1)
                        std_vals = np.std(vals, axis=1)
                    else:
                        mean_vals = vals
                        std_vals = np.zeros_like(mean_vals)

                    ax.errorbar(
                        n_samples,
                        mean_vals,
                        yerr=std_vals,
                        fmt=f"{markers[k_id % len(markers)]}{line_styles[k_id % len(line_styles)]}",
                        markersize=sizes[k_id % len(sizes)],
                        capsize=5,
                        label=key,
                    )

                ax.set_xlabel("n_samples", fontsize=20)
                ax.set_ylabel(v_type, fontsize=20)
                ax.tick_params(axis="both", which="major", labelsize=20)

                ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}"))
                formatter = ScalarFormatter(useMathText=True)
                formatter.set_powerlimits((-2, 2))
                ax.yaxis.set_major_formatter(formatter)
                ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
                ax.yaxis.get_offset_text().set_fontsize(20)
                ax.yaxis.get_offset_text().set_va("bottom")

                if v_id == 0:
                    plt.legend(fontsize=20)

            for b_id, b_type in enumerate(bayes_types):
                # check if bayes_metrics[b_type] is an empty list or None
                vals = bayes_metrics[b_type]
                if not isinstance(vals, (list, np.ndarray)) or len(vals) == 0:
                    print(f"Warning: bayes_metrics[{b_type}] is empty or None")
                else:
                    ax = fig.add_subplot(gs_[1, b_id])
                    ax.plot(n_samples, bayes_metrics[b_type], color="limegreen")
                    ax.scatter(
                        n_samples,
                        bayes_metrics[b_type],
                        color="limegreen",
                        label=b_type,
                    )

                    ax.set_xlabel("n_samples", fontsize=20)
                    ax.set_ylabel(b_type, fontsize=20)
                    ax.tick_params(axis="both", which="major", labelsize=20)

                    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}"))
                    formatter = ScalarFormatter(useMathText=True)
                    formatter.set_powerlimits((-2, 2))
                    ax.yaxis.set_major_formatter(formatter)
                    ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
                    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.3f}"))
                    ax.yaxis.get_offset_text().set_fontsize(20)
                    ax.yaxis.get_offset_text().set_va("bottom")
                    ax.legend(fontsize=20)

            fig.savefig(
                f"./{self.out_dir}/validation_{name}.{self.out_format}",
                bbox_inches="tight",
            )
            plt.close()

        # One file per plot
        if plot_single is False:
            for v_id, v_type in enumerate(valid_types):
                fig, ax = plt.subplots(figsize=(5, 5))
                for k_id, key in enumerate(valid_metrics[v_type]):
                    vals = valid_metrics[v_type][key]
                    mean_vals = vals
                    std_vals = np.zeros_like(mean_vals)
                    if np.ndim(vals) > 1:
                        mean_vals = np.mean(vals, axis=1)
                        std_vals = np.std(vals, axis=1)

                    ax.errorbar(
                        n_samples,
                        mean_vals,
                        yerr=std_vals,
                        fmt=f"{markers[k_id % len(markers)]}{line_styles[k_id % len(line_styles)]}",
                        markersize=sizes[k_id % len(sizes)],
                        capsize=5,
                        label=key,
                    )

                ax.set_xlabel("n_samples", fontsize=20)
                ax.set_ylabel(v_type, fontsize=20)
                ax.tick_params(axis="both", which="major", labelsize=20)

                ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}"))
                formatter = ScalarFormatter(useMathText=True)
                formatter.set_powerlimits((-2, 2))
                ax.yaxis.set_major_formatter(formatter)
                ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
                ax.yaxis.get_offset_text().set_fontsize(20)
                ax.yaxis.get_offset_text().set_va("bottom")

                plt.legend(fontsize=20)
                plt.savefig(
                    f"./{self.out_dir}/validation_{name}_{v_type}.{self.out_format}",
                    bbox_inches="tight",
                )
                plt.close()
            for b_id, b_type in enumerate(bayes_types):
                vals = bayes_metrics[b_type]
                if not isinstance(vals, (list, np.ndarray)) or len(vals) == 0:
                    print(f"Warning: bayes_metrics[{b_type}] is empty or None")
                else:
                    fig, ax = plt.subplots(figsize=(5, 5))
                    ax.plot(n_samples, bayes_metrics[b_type], color="limegreen")
                    ax.scatter(
                        n_samples,
                        bayes_metrics[b_type],
                        color="limegreen",
                        label=b_type,
                    )

                    ax.set_xlabel("n_samples", fontsize=20)
                    ax.set_ylabel(b_type, fontsize=20)
                    ax.tick_params(axis="both", which="major", labelsize=20)

                    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}"))
                    formatter = ScalarFormatter(useMathText=True)
                    formatter.set_powerlimits((-2, 2))
                    ax.yaxis.set_major_formatter(formatter)
                    ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
                    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.3f}"))
                    ax.yaxis.get_offset_text().set_fontsize(20)
                    ax.yaxis.get_offset_text().set_va("bottom")
                    plt.savefig(
                        f"./{self.out_dir}/validation_{name}_{b_type}.{self.out_format}",
                        bbox_inches="tight",
                    )
                    plt.close()
        return None

    # -------------------------------------------------------------------------
    def sobol_indices(
        self, plot_type: str = "line", save: bool = True, plot: bool = True
    ):
        """
        Visualizes and writes out Sobol' and Total Sobol' indices of the trained metamodel.
        One file is created for each index and output key.

        Parameters
        ----------
        plot_type : str, optional
            Plot type, supports 'line' for lineplots and 'bar' for barplots.
            The default is `line`.
            Bar chart can be selected by `bar`.
        save : bool, optional
            Write out the inidces as csv files if set to True. The default
            is True.

        Raises
        ------
        AttributeError
            MetaModel in given Engine needs to be of type 'pce' or 'apce'.
        AttributeError
            Plot-type must be 'line' or 'bar'.

        Returns
        -------
        sobol_all : dict
            All possible Sobol' indices for the given metamodel.
        total_sobol_all : dict
            All Total Sobol' indices for the given metamodel.

        """
        # This function currently only supports PCE/aPCE
        metamod = self.engine.meta_model
        if not hasattr(metamod, "meta_model_type"):
            raise AttributeError("Sobol indices only support PCE-type models!")
        if metamod.meta_model_type.lower() not in ["pce", "apce"]:
            raise AttributeError("Sobol indices only support PCE-type models!")

        if plot_type not in ["line", "bar"]:
            raise AttributeError("The wanted plot type is not supported.")

        # Extract the necessary variables
        max_order = np.max(metamod.pce_deg)
        outputs = self.engine.out_names
        if metamod.sobol is None:
            metamod.calculate_sobol(y_train=self.engine.exp_design.y)
        sobol_all, total_sobol_all = metamod.sobol, metamod.total_sobol
        self.sobol = sobol_all
        self.totalsobol = total_sobol_all

        # Save indices
        if save:
            for _, output in enumerate(outputs):
                total_sobol = total_sobol_all[output]
                np.savetxt(
                    f"{self.out_dir}totalsobol_" + output.replace("/", "_") + ".csv",
                    total_sobol.T,
                    delimiter=",",
                    header=",".join(self.par_names),
                    comments="",
                )

                for i_order in range(1, max_order + 1):
                    sobol = sobol_all[i_order][output][0]
                    np.savetxt(
                        f"{self.out_dir}sobol_{i_order}_"
                        + output.replace("/", "_")
                        + ".csv",
                        sobol.T,
                        delimiter=",",
                        header=",".join(self.par_names),
                        comments="",
                    )

        if plot:
            # Plot Sobol' indices
            for output in outputs:
                self.plot_type = plot_type

                for i_order in range(1, max_order + 1):
                    par_names_i = (
                        list(combinations(self.par_names, i_order))
                        if (i_order != 1)
                        else self.par_names
                    )

                    sobol_values = self.sobol[i_order][
                        output
                    ]  # shape: (n_params, n_times) or similar

                    sobol_ = np.asarray(sobol_values)
                    if sobol_.ndim == 2:
                        sobol_3d = sobol_[np.newaxis, :, :]
                    elif sobol_.ndim == 3:
                        sobol_3d = sobol_
                    else:
                        raise ValueError(
                            f"Unexpected shape for Sobol indices: {sobol_.shape}"
                        )

                    q_5 = np.quantile(sobol_3d, q=0.05, axis=0)
                    q_97_5 = np.quantile(sobol_3d, q=0.975, axis=0)

                    if isinstance(self.x_values, np.ndarray):
                        x_val = self.x_values
                    elif isinstance(self.x_values, dict):
                        x_val = np.array(self.x_values[output])
                    else:
                        raise TypeError(
                            f"x_values must be either a numpy array or a dict with output keys, got {type(self.x_values)}."
                        )

                    self.plot_sobol(
                        sobol_values={output: sobol_values},
                        par_names=par_names_i,
                        outputs=[output],
                        sobol_type="sobol",
                        i_order=i_order,
                        x=x_val,
                        xlabel=self.xlabel,
                        plot_type=self.plot_type,
                        out_dir=self.out_dir,
                        out_format=self.out_format,
                        quantiles=(q_5, q_97_5),
                    )

                # Now plot total Sobol (only once per output)
                total_sobol = self.totalsobol[output]
                if total_sobol.ndim == 2:
                    sobol_3d = total_sobol[np.newaxis, :, :]
                elif total_sobol.ndim == 3:
                    sobol_3d = total_sobol
                else:
                    raise ValueError(
                        f"Unexpected shape for total Sobol indices: {total_sobol.shape}"
                    )

                q_5 = np.quantile(sobol_3d, q=0.05, axis=0)
                q_97_5 = np.quantile(sobol_3d, q=0.975, axis=0)

                if isinstance(self.x_values, np.ndarray):
                    x_val = self.x_values
                elif isinstance(self.x_values, dict):
                    x_val = np.array(self.x_values[output])
                else:
                    raise TypeError(
                        f"x_values must be either a numpy array or a dict with output keys, got {type(self.x_values)}."
                    )

                self.plot_sobol(
                    sobol_values={output: total_sobol},
                    par_names=self.par_names,
                    outputs=[output],
                    sobol_type="totalsobol",
                    x=self.x_values,
                    xlabel=self.xlabel,
                    plot_type=self.plot_type,
                    out_dir=self.out_dir,
                    out_format=self.out_format,
                    quantiles=(q_5, q_97_5),
                )
                # self.plot_sobol(par_names_i, outputs, sobol_type="sobol", i_order=i_order)
                # self.plot_sobol(self.par_names, outputs, sobol_type="totalsobol")

        return sobol_all, total_sobol_all

    # -------------------------------------------------------------------------
    def plot_sobol(
        self,
        sobol_values: dict,
        par_names: list,
        outputs: list,
        sobol_type: str = "sobol",
        i_order: int = 1,
        x: np.ndarray = None,
        xlabel: str = "Time",
        plot_type: str = "line",
        out_dir: str = "./",
        out_format: str = "png",
        quantiles: tuple = None,
    ):
        """
        Generalized function to plot Sobol' indices from PCE models or SALib.

        Parameters
        ----------
        sobol_values : dict
            Dictionary of Sobol' indices for each output.
        par_names : list
            List of parameter names or interaction tuples.
        outputs : list
            List of output variable names.
        sobol_type : str
            'sobol' or 'totalsobol'.
        i_order : int
            Order of Sobol' index (only for sobol_type='sobol').
        x : np.ndarray, optional
            X-axis values (e.g., time). If None, defaults to index range.
        xlabel : str
            Label for x-axis.
        plot_type : str
            'line' or 'bar'.
        out_dir : str
            Output directory for plots.
        out_format : str
            File format for saving plots.
        quantiles : tuple, optional
            Tuple of (q5, q975) quantile arrays for confidence intervals.
        """

        for output in outputs:
            sobol = sobol_values[output]
            if sobol_type == "sobol" and isinstance(sobol, list):
                sobol = sobol[0]

            sobol_ = np.asarray(sobol)

            # Ensure sobol_ is (n_params, n_times)
            if sobol_.ndim == 1:
                sobol_ = sobol_[:, np.newaxis]
            elif sobol_.ndim == 2:
                # already (n_params, n_times)
                pass
            elif sobol_.ndim == 3:
                if sobol_.shape[0] == 1:
                    sobol_ = sobol_[0]  # (n_params, n_times)
                else:
                    # shape (n_samples, n_params, n_times)
                    sobol_3d = sobol_  # keep for quantiles
                    sobol_ = sobol_.mean(axis=0)  # (n_params, n_times) for plotting
            else:
                raise ValueError(f"Unexpected sobol array shape: {sobol_.shape}")

            # Construct 3D array for quantiles if not already
            if "sobol_3d" not in locals():
                sobol_3d = sobol_[np.newaxis, :, :]

            # Quantile bounds
            if quantiles is not None:
                q_5, q_97_5 = quantiles
            else:
                if sobol_3d.shape[0] == 1:
                    q_5 = q_97_5 = sobol_[0]
                    print(f"[INFO] Only one Sobol sample → no quantile band shown.")
                else:
                    q_5 = np.quantile(sobol_3d, q=0.05, axis=0)
                    q_97_5 = np.quantile(sobol_3d, q=0.975, axis=0)

            # Start plotting
            fig = plt.figure()
            ax = fig.add_axes([0, 0, 1, 1])

            if plot_type == "bar":
                df_data = {xlabel: x}
                for i, name in enumerate(par_names):
                    df_data[str(name)] = sobol_[i]
                df = pd.DataFrame(df_data)
                df.plot(
                    x=xlabel,
                    y=[str(p) for p in par_names],
                    kind="bar",
                    ax=ax,
                    rot=0,
                    colormap="Dark2",
                    yerr=q_97_5 - q_5 if not np.allclose(q_5, q_97_5) else None,
                )
            else:  # line plot
                for i, sobol_indices in enumerate(sobol_):
                    ax.plot(x, sobol_indices, label=par_names[i], marker="x", lw=2.5)
                    if not np.allclose(q_5[i], q_97_5[i]):
                        ax.fill_between(x, q_5[i], q_97_5[i], alpha=0.15, color="gray")

            # Labels and titles
            ylabel = (
                "Sobol indices, $S$"
                if sobol_type == "sobol"
                else "Total Sobol indices, $S^T$"
            )
            ax.set_ylabel(ylabel)
            ax.set_xlabel(xlabel)
            ax.legend(loc="best", frameon=True)
            title = (
                f"{i_order} order Sobol' indices of {output}"
                if sobol_type == "sobol"
                else f"Total Sobol' indices of {output}"
            )
            ax.set_title(title)

            # Save plot
            filename = (
                f"{out_dir}Sobol_indices_{i_order}_{output}.{out_format}"
                if sobol_type == "sobol"
                else f"{out_dir}TotalSobol_indices_{output}.{out_format}"
            )
            fig.savefig(filename, bbox_inches="tight")
            plt.close(fig)

    # -------------------------------------------------------------------------
    def plot_residual_hist(self, y, y_mm) -> None:
        """
        Checks the quality of the metamodel residuals via visualization and
        Normality (Shapiro-Wilk) test.

        Parameters
        ----------
        y : dict
            Model evaluations.
        y_mm : dict
            Corresponding MetaModel evaluations

        """
        for key in y_mm.keys():
            # Get residuals
            residuals = y[key] - y_mm[key]
            labels = y["x_values"]
            cmap = mpl.colormaps["viridis"]
            colors = cmap(np.linspace(0, 1, labels.shape[0]))

            # Plot histogram
            plt.hist(residuals, bins=20, edgecolor="k", label=labels, color=colors)
            plt.ylabel("Count")
            plt.xlabel("Residuals")
            plt.title(f"{key}: Histogram of residuals")
            plt.legend(title=self.xlabel, loc="center left", bbox_to_anchor=(1.03, 0.5))

            # Normality (Shapiro-Wilk) test of the residuals
            ax = plt.gca()
            _, p = stats.shapiro(residuals)
            if p < 0.01:
                ann_text = "The residuals seem to come from a Gaussian Process."
            else:
                ann_text = "The normality assumption may not hold."
            at = AnchoredText(
                ann_text, prop={"size": 30}, frameon=True, loc="upper left"
            )
            at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
            ax.add_artist(at)
            plt.savefig(
                f"./{self.out_dir}/Hist_Residuals.{self.out_format}",
                bbox_inches="tight",
            )
            plt.close()

    # -------------------------------------------------------------------------
    def plot_validation_outputs(self, model_out, out_mean, out_std=None):
        """
        Plots outputs for visual comparison of metamodel outputs with that of
        the (full) multioutput original model

        Parameters
        ----------
        model_out : dict
            Model outputs.
        out_mean : dict
            MetaModel mean outputs.
        out_std : dict
            MetaModel stdev outputs.

        Raises
        ------
        AttributeError: This evaluation only support PCE-type models!

        Returns
        -------
        None

        """
        for _, key in enumerate(self.engine.out_names):
            # Transform into dataframe
            data = pd.DataFrame()
            type_ = []  # model or metamodel
            idx = []  # Eval index
            x_axis = []  # x-values
            lower = []
            mean = []
            upper = []
            for i in range(out_mean[key].shape[0]):
                for t in range(out_mean[key].shape[1]):
                    # Model output
                    type_.append("model")
                    idx.append(str(i))
                    x_axis.append(self.x_values[t])
                    lower.append(model_out[key][i][t])
                    mean.append(model_out[key][i][t])
                    upper.append(model_out[key][i][t])
                    # Metamodel output
                    type_.append("metamodel")
                    idx.append(str(i))
                    x_axis.append(self.x_values[t])
                    mean.append(out_mean[key][i][t])
                    if out_std is not None:
                        lower.append(out_mean[key][i][t] - out_std[key][i][t])
                        upper.append(out_mean[key][i][t] + out_std[key][i][t])
                    else:
                        lower.append(out_mean[key][i][t])
                        upper.append(out_mean[key][i][t])
            data["type"] = type_
            data["idx"] = idx
            data["x_values"] = x_axis
            data["lower"] = lower
            data[key] = mean
            data["upper"] = upper

            # Plot the lines
            ax = sns.lineplot(
                data=data,
                x="x_values",
                y=key,
                ci=None,
                markers=True,
                hue="idx",
                style="type",
            )

            # Add MetaModel stdev
            data_ = data[data["type"] == "metamodel"]
            for idx in range(out_mean[key].shape[0]):
                sub_data = data_[data_["idx"] == str(idx)]
                ax.fill_between(
                    sub_data.x_values, sub_data.lower, sub_data.upper, alpha=0.2
                )
            ax.set_xlabel(self.xlabel)
            plt.legend(loc="upper right")

            # Save to file
            key = key.replace(" ", "_")
            plt.savefig(
                f"./{self.out_dir}/Model_vs_MetaModel_{key}.{self.out_format}",
                bbox_inches="tight",
            )
            plt.close()
