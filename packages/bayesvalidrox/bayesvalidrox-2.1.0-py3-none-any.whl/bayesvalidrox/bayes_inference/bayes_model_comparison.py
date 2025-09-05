#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class for Bayesian Model Selection and comparison.
"""

import os
import platform
import copy
from tqdm import tqdm
from scipy import stats
import numpy as np
import seaborn as sns
from matplotlib import patches
import matplotlib.pylab as plt
import pandas as pd
from .bayes_inference import BayesInference

# Load the mplstyle
plt.style.use(os.path.join(os.path.split(__file__)[0], "../", "bayesvalidrox.mplstyle"))


class BayesModelComparison:
    """
    A class to perform Bayesian Analysis.

    Attributes
    ----------
    model_dict : dict
        A dictionary of model names and bvr.engine objects for each model.
    bayes_opts : dict
        A dictionary given the `BayesInference` options.
    perturbed_data : array of shape (n_bootstrap_itrs, n_obs), optional
        User defined perturbed data. The default is `None`.
    n_bootstrap : int
        Number of bootstrap iteration. The default is `1000`.
    data_noise_level : float
        A noise level to perturb the data set. The default is `0.01`.
    use_emulator : bool
        Set to True if the emulator/metamodel should be used in the analysis.
        If False, the model is run.
    out_dir : string, optional
        Name of output folder for the generated plots. The default
        is 'Outputs_Comparison/'.
    out_format : str, optional
        Format that the generated plots are stored as. Supports 'pdf' and 'png'.
        The default is 'pdf'.

    """

    def __init__(
        self,
        model_dict,
        bayes_opts,
        perturbed_data=None,
        n_bootstrap=1000,
        data_noise_level=0.01,
        use_emulator=True,
        out_dir="Outputs_Comparison/",
        out_format='pdf'
    ):
        # Inputs
        self.model_dict = model_dict
        self.bayes_opts = bayes_opts
        self.perturbed_data = perturbed_data
        self.n_bootstrap = n_bootstrap
        self.data_noise_level = data_noise_level
        self.use_emulator = use_emulator
        self.out_dir = out_dir
        self.out_format = out_format

        # Other parameters
        self.model_names = None
        self.n_meas = None
        self.n_perturb = None
        self.bme_dict = {}
        self.dtype = None

    # --------------------------------------------------------------------------
    def setup(self):
        """
        Initialize parameters that are needed for all types of model comparison

        """
        if not isinstance(self.model_dict, dict):
            raise AttributeError(
                "To run model comparsion, you need to pass a dictionary of models."
            )

        # Extract model names
        self.model_names = [*self.model_dict]

        # Find n_bootstrap
        if self.perturbed_data is not None:
            self.n_bootstrap = self.perturbed_data.shape[0]

        # Output directory
        os.makedirs(self.out_dir, exist_ok=True)

        # System settings
        if platform.system() == "Windows" or platform.system() == "Darwin":
            print("")
            print(
                "WARNING: Performing the inference on windows or MacOS \
                    can lead to reduced accuracy!"
            )
            print("")
            self.dtype = np.longdouble
        else:
            self.dtype = np.float128

    # --------------------------------------------------------------------------
    def model_comparison_all(self) -> dict:
        """
        Performs all three types of model comparison:
            * Bayes Factors
            * Model weights
            * Justifiability analysis

        Returns
        -------
        results : dict
            A dictionary that contains the calculated BME values, model weights
            and confusion matrix

        """
        bme_dict = self.calc_bayes_factors()
        model_weights = self.calc_model_weights()
        confusion_matrix = self.calc_justifiability_analysis()

        results = {
            "BME": bme_dict,
            "Model weights": model_weights,
            "Confusion matrix": confusion_matrix,
        }
        return results

    # --------------------------------------------------------------------------
    def calc_bayes_factors(self) -> dict:
        """
        Calculate the BayesFactors for each pair of models in the model_dict
        with respect to given data.

        Returns
        -------
        bme_dict : dict
            The calculated BME values for each model

        """
        # Run the setup
        self.setup()

        # Run Bayesian validation for each model
        for model in self.model_names:
            print("-" * 20)
            print(f"Bayesian inference of {model}.\n")
            bayes = BayesInference(self.model_dict[model])

            # Set BayesInference options
            for key, value in self.bayes_opts.items():
                if key in bayes.__dict__:
                    setattr(bayes, key, value)
            bayes.use_emulator = self.use_emulator

            # Perturb observations for Bayes Factor
            if self.perturbed_data is None:
                bayes.n_bootstrap_itrs = self.n_bootstrap
                bayes.bootstrap_noise = self.data_noise_level
            else:
                bayes.perturbed_data = self.perturbed_data

            log_bme = bayes.run_validation()
            self.bme_dict[model] = np.exp(log_bme, dtype=self.dtype)
            print("-" * 20)

            # Get other calculated values
            if self.perturbed_data is None:
                self.perturbed_data = bayes.perturbed_data

        # Create kde plot for bayes factors
        self.plot_bayes_factor(self.bme_dict)
        return self.bme_dict

    def calc_model_weights(self) -> dict:
        """
        Calculate the model weights from BME evaluations for Bayes factors.

        Returns
        -------
        model_weights : dict
            The calculated weights for each model

        """
        # Get BMEs via Bayes Factors if not already done so
        if self.bme_dict is None:
            self.calc_bayes_factors()

        # Stack the BME values for all models
        all_bme = np.vstack(list(self.bme_dict.values()))

        # Model weights
        model_weights = np.divide(all_bme, np.nansum(all_bme, axis=0))

        # Create box plot for model weights
        self.plot_model_weights(model_weights)
        return model_weights

    # -------------------------------------------------------------------------
    def calc_justifiability_analysis(self) -> dict:
        """
        Perform justifiability analysis by calculating the confusion matrix

        Returns
        -------
        confusion_matrix: dict
            The averaged confusion matrix.

        """
        # Do setup
        self.setup()

        # Extend model names
        model_names = self.model_names
        if model_names[0] != "Observation":
            model_names.insert(0, "Observation")
        n_models = len(model_names)

        # Generate datasets of model evaluations and stdevs
        just_list, var_list, sampler = self.generate_ja_dataset()

        # Start and end of each model in likelihood matrix
        start = []
        end = []
        for i in range(n_models):
            if i == 0:
                start.append(0)
                end.append(self.n_perturb)
            else:
                start.append(end[i - 1])
                end.append(end[i - 1] + self.n_bootstrap)

        # Calculate Likelihood + Posterior of each column against each column
        total_n_runs = self.n_perturb + (n_models - 1) * self.n_bootstrap
        likelihoods = np.zeros((total_n_runs, total_n_runs))
        for i in range(n_models):
            for j in range(n_models):
                obs = copy.deepcopy(just_list[i])
                var = copy.deepcopy(var_list[i])
                for cnt in tqdm(
                    range(end[i] - start[i]), desc=f"Likelihood model {i} vs {j}"
                ):
                    for out in obs.keys():
                        if out == "x_values":
                            continue
                        obs[out] = np.array([just_list[i][out][cnt, :]])
                        var[out] = np.array([var_list[i][out][cnt, :]])
                    sampler.observation = obs
                    sampler.discrepancy.total_sigma2 = var
                    like, _ = sampler.calculate_loglik_logbme(
                        just_list[j], std_outputs=var_list[j]
                    )
                    likelihoods[start[i] + cnt, start[j] : end[j]] = like

        # Accumulate likelihoods into a posterior matrix
        accum_lik = np.zeros((n_models, n_models))
        sum_lik = np.sum(likelihoods, axis=1)
        for mod1 in range(n_models):
            for mod2 in range(n_models):
                accum_lik[mod1, mod2] = np.mean(
                    likelihoods[start[mod1] : end[mod1], start[mod2] : end[mod2]]
                    / sum_lik[start[mod2] : end[mod2]]
                )
        # Correction for surrogate
        if self.use_emulator:
            print("Correct for surrogates")
            correction_factor = np.zeros(accum_lik.shape[0])
            for i, name in enumerate(self.model_names):
                if i == 0:
                    correction_factor[i] = 1
                    continue
                engine = self.model_dict[name]
                num_train = engine.exp_design.x.shape[0]
                train_mean, _ = engine.eval_metamodel(engine.exp_design.x)

                # Format to shape: #train, #steps * #outkeys
                metamod_out_list = []
                mod_out_list = []
                for out in train_mean.keys():
                    for out_i in range(train_mean[out].shape[1]):
                        metamod_out_list.append(train_mean[out][:, out_i])
                        mod_out_list.append(engine.exp_design.y[out][:, out_i])
                metamod_out = np.swapaxes(np.array(metamod_out_list), 0, 1)
                mod_out = np.swapaxes(np.array(mod_out_list), 0, 1)
                error = metamod_out - mod_out

                # Likelihood of surrogate against model
                surr_likelihoods = 0
                for n_t in range(num_train):
                    a = np.atleast_2d(metamod_out[n_t, :] - mod_out[n_t, :])
                    b = np.linalg.pinv(np.diag(error[n_t, :]))
                    surr_likelihoods += np.exp(-0.5 * (np.matmul(a, np.matmul(b, a.T))))
                correction_factor[i] = surr_likelihoods[0, 0]

            correction_matrix = np.ones((n_models, n_models))
            for i in range(n_models):
                correction_matrix[i, :] *= correction_factor[i]
                correction_matrix[:, i] *= correction_factor[i]
            accum_lik = np.multiply(accum_lik, correction_matrix)

        # Norm each 'generated by' column to sum 1
        just_model_weights = accum_lik
        for i in range(just_model_weights.shape[0]):
            just_model_weights[i, :] /= np.sum(just_model_weights[i, :])

        # Confusion matrix over all measurement points
        confusion_matrix = pd.DataFrame()
        confusion_matrix["Generated by"] = model_names
        for i, _ in enumerate(model_names):  # 'Associated to'
            confusion_matrix[model_names[i]] = just_model_weights[:, i]

        # Plot model weights
        self.plot_confusion_matrix(confusion_matrix)
        return confusion_matrix

    # -------------------------------------------------------------------------
    def generate_ja_dataset(self) -> tuple[list, list, object]:
        """
        Generates the data set for the justifiability analysis.

        Returns
        -------
        just_list: list
            List of the model outputs for each of the given models, as well as the
            perturbed observations.
        var_list : list
            List of the uncertainty/stdev associated with each model output and
            perturbed observation.
        sampler : object
            bvr.PostSampler object.

        """

        # Perturb observations
        bayes = BayesInference(self.model_dict[self.model_names[1]])
        for key, value in self.bayes_opts.items():
            if key in bayes.__dict__:
                setattr(bayes, key, value)
        bayes.use_emulator = self.use_emulator

        # Perturb observations for Bayes Factor
        bayes.name = "valid"
        bayes.n_bootstrap_itrs = self.n_bootstrap
        bayes.bootstrap_noise = self.data_noise_level
        bayes.setup()
        if self.perturbed_data is None:
            self.perturbed_data = bayes.perturb_data(
                bayes.measured_data, bayes.out_names
            )
        self.n_perturb = self.perturbed_data.shape[0]

        # Transform measurement uncertainty into model output format
        var_list = []
        var = bayes.discrepancy.total_sigma2.to_dict()
        if var is None:
            raise AttributeError("No measurement uncertainty given!")
        for out in var.keys():
            trafo = []
            for i in var[out].keys():
                trafo.append(var[out][i])
            trafo_long = []
            for i in range(self.n_perturb):
                trafo_long.append(trafo)
            var[out] = np.array(trafo_long)
        var_list.append(var)

        # Transform perturbed data into model output format
        just_list = []
        output = {}
        for cnt, out in enumerate(var.keys()):
            output[out] = []
            n_t = var[out].shape[1]
            output[out] = self.perturbed_data[:, n_t * cnt : n_t * (cnt + 1)]
        just_list.append(output)

        # Generate MC evaluations of the models
        for key, engine in self.model_dict.items():
            y_hat, y_std = engine.eval_metamodel(nsamples=self.n_bootstrap)
            just_list.append(y_hat)

            # Set stdev to 0 if not given
            if y_std is None:
                y_std = copy.deepcopy(y_hat)
                for key in y_hat:
                    if key != "x_values":
                        y_std[key] *= 0
            var_list.append(y_std)

        return just_list, var_list, bayes.sampler

    # -------------------------------------------------------------------------
    def plot_confusion_matrix(self, confusion_matrix):
        """
        Visualizes the confusion matrix and the model weights for the
        justifiability analysis.

        Parameters
        ----------
        confusion_matrix: dict
            The averaged confusion matrix.

        """
        print(confusion_matrix)
        model_names = [model.replace("_", "$-$") for model in self.model_names]

        # Plot the averaged confusion matrix
        cf = confusion_matrix[self.model_names].to_numpy()
        g = sns.heatmap(
            cf.T,
            annot=True,
            cmap="Blues",
            xticklabels=model_names,
            yticklabels=model_names,
            annot_kws={"size": 24},
        )
        g.xaxis.tick_top()
        g.xaxis.set_label_position("top")
        # g.set_xlabel(r"\textbf{Data generated by:}", labelpad=15)
        # g.set_ylabel(r"\textbf{Model weight for:}", labelpad=15)
        g.figure.savefig(f"{self.out_dir}confusionMatrix_full.{self.out_format}", bbox_inches="tight")
        plt.close()

    # -------------------------------------------------------------------------
    def plot_model_weights(self, model_weights):
        """
        Visualizes the model weights resulting from BMS via the observation
        data.

        Parameters
        ----------
        model_weights : array
            Model weights.

        """
        # Create figure
        fig, ax = plt.subplots()
        font_size = 40

        # Filter data using np.isnan
        mask = ~np.isnan(model_weights.T)
        filtered_data = [d[m] for d, m in zip(model_weights, mask.T)]

        # Create the boxplot
        bp = ax.boxplot(filtered_data, patch_artist=True, showfliers=False)

        # change outline color, fill color and linewidth of the boxes
        for box in bp["boxes"]:
            # change outline color
            box.set(color="#7570b3", linewidth=4)
            # change fill color
            box.set(facecolor="#1b9e77")

        # change color and linewidth of the whiskers
        for whisker in bp["whiskers"]:
            whisker.set(color="#7570b3", linewidth=2)

        # change color and linewidth of the caps
        for cap in bp["caps"]:
            cap.set(color="#7570b3", linewidth=2)

        # change color and linewidth of the medians
        for median in bp["medians"]:
            median.set(color="#b2df8a", linewidth=2)

        # Customize the axes
        model_names = [model.replace("_", "$-$") for model in self.model_names]
        ax.set_xticklabels(model_names)
        ax.set_ylabel("Weight", fontsize=font_size)
        ax.set_ylim((-0.05, 1.05))
        for t in ax.get_xticklabels():
            t.set_fontsize(font_size)
        for t in ax.get_yticklabels():
            t.set_fontsize(font_size)

        # Title
        plt.title("Posterior Model Weights")

        # Save the figure
        fig.savefig(f"./{self.out_dir}model_weights.{self.out_format}", bbox_inches="tight")

        plt.close()

    # -------------------------------------------------------------------------
    def plot_bayes_factor(self, bme_dict):
        """
        Plots the Bayes factor distibutions in a :math:`N_m \\times N_m`
        matrix, where :math:`N_m` is the number of the models.

        Parameters
        ----------
        bme_dict : dict
            A dictionary containing the BME values of the models.

        """
        # Plot setup
        font_size = 40
        colors = ["blue", "green", "gray", "brown"]
        model_names = list(bme_dict.keys())
        n_models = len(model_names)

        # Plots
        _, axes = plt.subplots(nrows=n_models, ncols=n_models, sharex=True, sharey=True)
        for i, key_i in enumerate(model_names):
            for j, key_j in enumerate(model_names):
                ax = axes[i, j]
                # Set size of the ticks
                for t in ax.get_xticklabels():
                    t.set_fontsize(font_size)
                for t in ax.get_yticklabels():
                    t.set_fontsize(font_size)

                if j != i:
                    # Null hypothesis: key_j is the better model
                    bayes_factor = np.log10(np.divide(bme_dict[key_i], bme_dict[key_j]))

                    # Taken from seaborn's source code (utils.py and
                    # distributions.py)
                    def seaborn_kde_support(data, bw, gridsize, cut, clip):
                        if clip is None:
                            clip = (-np.inf, np.inf)
                        support_min = max(data.min() - bw * cut, clip[0])
                        support_max = min(data.max() + bw * cut, clip[1])
                        return np.linspace(support_min, support_max, gridsize)

                    kde_estim = stats.gaussian_kde(bayes_factor, bw_method="scott")

                    # Linearization of data, mimics seaborn's internal code
                    bw = kde_estim.scotts_factor() * np.std(bayes_factor)
                    linearized = seaborn_kde_support(bayes_factor, bw, 100, 3, None)

                    # Compute values of the estimated function on the
                    # estimated linearized inputs
                    z = kde_estim.evaluate(linearized)

                    # https://stackoverflow.com/questions/29661574/normalize-
                    # numpy-array-columns-in-python
                    def normalize(x):
                        return (x - x.min(0)) / x.ptp(0)

                    # Normalize so it is between 0;1
                    z_2 = normalize(z)
                    ax.plot(linearized, z_2, "-", color=colors[i], linewidth=4)
                    ax.fill_between(linearized, 0, z_2, color=colors[i], alpha=0.25)

                    # Draw BF significant levels according to Jeffreys 1961
                    # Strong evidence for both models
                    ax.axvline(x=np.log10(3), ymin=0, linewidth=4, color="dimgrey")
                    # Strong evidence for one model
                    ax.axvline(x=np.log10(10), ymin=0, linewidth=4, color="orange")
                    # Decisive evidence for one model
                    ax.axvline(x=np.log10(100), ymin=0, linewidth=4, color="r")

                    bf_label = (
                        key_i.replace("_", "$-$") + "/" + key_j.replace("_", "$-$")
                    )
                    legend_elements = [
                        patches.Patch(
                            facecolor=colors[i],
                            edgecolor=colors[i],
                            label=f"BF({bf_label})",
                        )
                    ]
                    ax.legend(
                        loc="upper left",
                        handles=legend_elements,
                        fontsize=font_size - (n_models + 1) * 5,
                    )

                elif j == i:
                    # Build a rectangle in axes coords
                    left, width = 0, 1
                    bottom, height = 0, 1

                    p = patches.Rectangle(
                        (left, bottom),
                        width,
                        height,
                        color="white",
                        fill=True,
                        transform=ax.transAxes,
                        clip_on=False,
                    )
                    ax.grid(False)
                    ax.add_patch(p)
                    fsize = font_size + 20 if n_models < 4 else font_size
                    ax.text(
                        0.5,
                        0.5,
                        key_i.replace("_", "$-$"),
                        horizontalalignment="center",
                        verticalalignment="center",
                        fontsize=fsize,
                        color=colors[i],
                        transform=ax.transAxes,
                    )

        # Customize axes
        custom_ylim = (0, 1.05)
        plt.setp(axes, ylim=custom_ylim)

        # Set labels
        for i in range(n_models):
            axes[-1, i].set_xlabel("log$_{10}$(BF)", fontsize=font_size)
            axes[i, 0].set_ylabel("Probability", fontsize=font_size)

        # Adjust subplots
        plt.subplots_adjust(wspace=0.2, hspace=0.1)
        plt.savefig(f"./{self.out_dir}Bayes_Factor_kde_plot.{self.out_format}", bbox_inches="tight")
        plt.close()
