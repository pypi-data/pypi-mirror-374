#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discrepancy class for measurement uncertainty.
"""

import numpy as np


class Discrepancy:
    """
    Discrepancy class for Bayesian inference method.
    We define the reference or reality to be equal to what we can model and a
    descripancy term \\( \\epsilon \\). We consider the followin format:

    $$\\textbf{y}_{\\text{reality}} = \\mathcal{M}(\\theta) + \\epsilon,$$

    where \\( \\epsilon \\in R^{N_{out}} \\) represents the the effects of
    measurement error and model inaccuracy. For simplicity, it can be defined
    as an additive Gaussian disrepancy with zeromean and given covariance
    matrix \\( \\Sigma \\):

    $$\\epsilon \\sim \\mathcal{N}(\\epsilon|0, \\Sigma). $$

    In the context of model inversion or calibration, an observation point
    \\( \\textbf{y}_i \\in \\mathcal{y} \\) is a realization of a Gaussian
    distribution with mean value of \\(\\mathcal{M}(\\theta) \\) and covariance
    matrix of \\( \\Sigma \\).

    $$ p(\\textbf{y}|\\theta) = \\mathcal{N}(\\textbf{y}|\\mathcal{M}
                                             (\\theta))$$

    The following options are available:

    * Measurement uncertainty: With known redidual covariance matrix \\(\\Sigma\\) for
    independent measurements.

    Attributes
    ----------
    disc_type : str
        Type of the noise definition. `'Gaussian'` is only supported so far.
    parameters : dict or pandas.DataFrame
        Known residual variance \\(\\sigma^2\\), i.e. diagonal entry of the
        covariance matrix of the multivariate normal likelihood in case of
        given measurement uncertainty.

    """

    def __init__(self, disc_type="Gaussian", parameters=None):
        # Parameters for 'known' measurement uncertainty
        self.total_sigma2 = None
        self.disc_type = disc_type
        self.parameters = parameters
        self.type = None

    def build_discrepancy(self, measured_data=None):
        """
        Build used parts of the Discrepancy object.

        Parameters
        ----------
        measured_data : dict, optional
            Measurements given in dictionary. This is used to
            set the measurement uncertainty to 0 if it is not given.
            The default is None.

        """
        if (
            self.parameters is None
            and self.total_sigma2 is None
            and measured_data is None
        ):
            raise AttributeError("Cannot build Discrepancy without given values!")
        # Independent and identically distributed known uncertainty
        total_sigma2 = {}
        if self.parameters is not None:
            total_sigma2 = self.parameters
            for key in total_sigma2:
                total_sigma2[key] = np.array(total_sigma2[key])
        else:
            for key, meas in measured_data.items():
                total_sigma2[key] = np.zeros((meas.values.shape[0]))
        self.total_sigma2 = total_sigma2
