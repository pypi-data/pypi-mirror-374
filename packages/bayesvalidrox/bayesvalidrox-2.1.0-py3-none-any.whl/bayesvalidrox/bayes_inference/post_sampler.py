#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template and parent class for classes that generate samples from the posterior.
"""

import gc
import platform
import warnings
import numpy as np
from scipy import stats
import pandas as pd


class PostSampler:
    """
    Template class for generating posterior samples.
    This class describes all the properties and functions that are needed to
    interface with the class BayesInference.

    Attributes
    ----------
    engine : object, optional
        Trained bvr.Engine object. The default is None.
    discrepancy : object, optional
        Object of class bvr.Discrepancy. The default is None.
    observation : dict, optional
        Measurement/observation to use as reference. The default is None.
    out_names : list, optional
        The list of requested output keys to be used for the analysis.
        The default is `None`. If None, all the defined outputs from the engine
        are used.
    selected_indices : dict, optional
        A dictionary with the selected indices of each model output. The
        default is `None`. If `None`, all measurement points are used in the
        analysis.
    use_emulator : bool
        Set to True if the emulator/metamodel should be used in the analysis.
        If False, the model is run.
    out_dir : string, optional
        The output directory. The default is ''.
    """

    def __init__(
        self,
        engine=None,
        discrepancy=None,
        observation=None,
        out_names=None,
        selected_indices=None,
        use_emulator=False,
        out_dir="",
    ):
        # Assign properties - objects
        self.engine = engine
        self.discrepancy = discrepancy
        self.observation = observation

        # Assign properties - settings
        self.selected_indices = selected_indices
        self.out_names = out_names
        self.use_emulator = use_emulator
        self.out_dir = out_dir

        # System settings
        self.dtype = None
        if platform.system() == "Windows" or platform.system() == "Darwin":
            warnings.warn(
                "Performing the inference on windows or MacOS can lead to reduced accuracy!"
            )
            self.dtype = np.longdouble
        else:
            self.dtype = np.float128

    def run_sampler(self) -> pd.DataFrame:
        """
        Performs sampling to update the prior distribution on the
        input parameters.

        Returns
        -------
        posterior : pd.DataFrame
            Posterior samples of the input parameters.

        """
        return None

    # -------------------------------------------------------------------------
    def normpdf(
        self,
        outputs,
        std_outputs=None,
        rmse=None,
    ) -> np.ndarray:
        """
        Calculates the likelihood of simulation outputs compared with
        observation data.

        Parameters
        ----------
        outputs : dict
            The metamodel outputs as an array of shape
            (n_samples, n_measurement) for each model output.
        std_outputs : dict of 2d np arrays, optional
            Standard deviation (uncertainty) associated to the output.
            The default is None.
        rmse : dict, optional
            A dictionary containing the root mean squared error as array of
            shape (n_samples, n_measurement) for each model output. The default
            is None.

        Returns
        -------
        logLik : np.ndarray
            Log-likelihoods. Shape: (n_samples)

        """
        # Loop over the output keys
        loglik = 0.0
        for _, out in enumerate(self.out_names):

            # (Meta)Model Output
            _, nout = outputs[out].shape

            # Select the data points to compare
            if self.selected_indices is not None:
                indices = self.selected_indices
                if isinstance(indices, dict):
                    indices = indices[out]
            else:
                indices = list(range(nout))

            data = None
            try:
                data = self.observation[out].values[~np.isnan(self.observation[out])]
            except AttributeError:
                data = self.observation[out][~np.isnan(self.observation[out])]

            # Prepare data uncertainty / error estimation (sigma2s)
            non_nan_indices = ~np.isnan(self.discrepancy.total_sigma2[out])
            tot_sigma2s = self.discrepancy.total_sigma2[out][non_nan_indices][:nout]

            # Add the std and rmse if they are given
            if rmse is not None:
                tot_sigma2s += rmse[out] ** 2
            if std_outputs is not None:
                tot_sigma2s += np.mean(std_outputs[out]) ** 2

            # Set up Covariance Matrix
            covmatrix = np.diag(tot_sigma2s)

            # Use given total_sigma2 and move to next itr
            loglik += stats.multivariate_normal.logpdf(
                outputs[out][:, indices],
                data[indices],
                np.diag(covmatrix[indices, indices]),
                allow_singular=True,
            )

        return loglik

    # -------------------------------------------------------------------------
    def _corr_factor_bme(
        self, samples, model_outputs, metamod_outputs, log_bme
    ) -> np.ndarray:
        """
        Calculates the correction factor for BMEs.
        # TODO: should this be protected?

        Parameters
        ----------
        samples : np.ndarray
            Samples that the model and metamodel were evaluated on.
        model_outputs : dict
            Model outputs on X.
        metamod_outputs : dict
            MetaModel outputs on X.
        log_bme : np.ndarray
            The log_BME obtained from the estimated likelihoods

        Returns
        -------
        np.log(weights) : np.ndarray
            Correction factors # TODO: factors or log of factors?

        """
        # Loop over the outputs
        loglik_data = np.zeros(samples.shape[0])
        loglik_model = np.zeros(samples.shape[0])
        for _, out in enumerate(self.out_names):
            _, nout = model_outputs[out].shape
            if self.selected_indices is not None:
                indices = self.selected_indices
                if isinstance(indices, dict):
                    indices = indices[out]
            else:
                indices = list(range(nout))

            try:
                data = self.observation[out].values[~np.isnan(self.observation[out])]
            except AttributeError:
                data = self.observation[out][~np.isnan(self.observation[out])]

            # Covariance Matrix from sigma2s
            non_nan_indices = ~np.isnan(self.discrepancy.total_sigma2[out])
            tot_sigma2s = self.discrepancy.total_sigma2[out][non_nan_indices][:nout]
            covmatrix_data = np.diag(tot_sigma2s)

            for i, _ in enumerate(samples):
                # Calculate covMatrix with the surrogate error
                covmatrix = np.eye(len(model_outputs[out][i])) * 1 / (2 * np.pi)
                covmatrix = np.diag(covmatrix[indices, indices])
                covmatrix_data = np.diag(covmatrix_data[indices, indices])

                # Compute likelilhood output vs data
                loglik_data[i] += stats.multivariate_normal.logpdf(
                    metamod_outputs[out][i][indices], data[indices], covmatrix_data
                )

                # Compute likelilhood output vs surrogate
                loglik_model[i] += stats.multivariate_normal.logpdf(
                    metamod_outputs[out][i][indices],
                    model_outputs[out][i][indices],
                    covmatrix,
                )

        # Calculate log weights
        loglik_data -= log_bme
        return np.log(np.mean(np.exp(loglik_model + loglik_data)))

    def calculate_loglik_logbme(
        self, model_evals, surr_error=None, std_outputs=None
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Calculate log-likelihoods and logbme on the perturbed data.
        This function assumes everything as Gaussian.

        Parameters
        ----------
        model_evals : dict
            Model or metamodel outputs as a dictionary.
        surr_error : dict, optional
            A dictionary containing the root mean squared error as array of
            shape (n_samples, n_measurement) for each model output. The default
            is None.
        std_outputs : dict of 2d np arrays, optional
            Standard deviation (uncertainty) associated to the output.
            The default is None.

        Returns
        -------
        log_likelihood : np.ndarray
            The calculated loglikelihoods.
            Size: (n_samples, n_bootstrap_itr).

        log_bme : np.ndarray
            The log bme. This also accounts for metamodel error, if
            self.use_emulator is True. Size: (1,n_bootstrap_itr).

        """
        # Log likelihood
        log_likelihoods = self.normpdf(
            model_evals, rmse=surr_error, std_outputs=std_outputs
        )

        # Calculate logbme
        log_bme = np.log(np.nanmean(np.exp(log_likelihoods, dtype=self.dtype)))

        # BME correction when using Emulator - use training data as validation data
        bme_corr = 0
        if self.use_emulator:
            metamod_outputs, _ = self.engine.eval_metamodel(self.engine.exp_design.x)
            bme_corr = self._corr_factor_bme(
                self.engine.exp_design.x,
                self.engine.exp_design.y,
                metamod_outputs,
                log_bme,
            )
        log_bme += bme_corr

        # Clear memory
        gc.collect(generation=2)
        return log_likelihoods, log_bme
