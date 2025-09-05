# -*- coding: utf-8 -*-
"""
Test the MCM class of bayesvalidrox
Tests are available for the following functions
_check_ranges           - x
gelmain_rubin
_iterative_scheme
_my_ESS                 - x
Class MCMC: 
    run_sampler
    log_prior
    log_likelihood
    log_posterior
    eval_model
    train_error_model
    marginal_llk_emcee
"""
import sys
import pandas as pd
import numpy as np

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.meta_model import MetaModel
from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.surrogate_models.engine import Engine
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy
from bayesvalidrox.bayes_inference.mcmc import MCMC
from bayesvalidrox.bayes_inference.bayes_inference import BayesInference

sys.path.append("src/")
sys.path.append("../src/")


# %% Test MCMC init


def test_mcmc() -> None:
    """
    Construct an MCMC object
    """
    mcmc_params = {}
    par_list = [
        "prior_samples",
        "n_walkers",
        "n_burn",
        "n_steps",
        "moves",
        "multiprocessing",
        "verbose",
    ]
    init_val = [None, 100, 200, 100000, None, False, False]
    for i, _ in enumerate(par_list):
        if par_list[i] not in list(mcmc_params.keys()):
            mcmc_params[par_list[i]] = init_val[i]

    MCMC(None, mcmc_params, None)


# %% Test run_sampler
# if 0:  # TODO: Update for reworked code (2.0.0)

# def test_run_sampler() -> None:
#     """
#     Run short MCMC

#     Returns
#     -------
#     None
#         DESCRIPTION.

#     """
#     inp = Input()
#     inp.add_marginals()
#     inp.marginals[0].dist_type = "normal"
#     inp.marginals[0].parameters = [0, 1]

#     expdes = ExpDesigns(inp)
#     expdes.n_init_samples = 2
#     expdes.n_max_samples = 4
#     expdes.x = np.array([[0], [1], [0.5]])
#     expdes.y = {"Z": [[0.4], [0.5], [0.45]]}
#     expdes.x_values = np.array([0])

#     mm = MetaModel(inp)
#     mm.fit(expdes.x, expdes.y)
#     expdes.generate_ed(max_deg=2)

#     mod = PL()
#     mod.observations = {"Z": np.array([0.45]), "x_values": np.array([0])}
#     mod.output.names = ["Z"]
#     engine = Engine(mm, mod, expdes)

#     obs_data = pd.DataFrame(mod.observations, columns=mod.output.names)
#     disc = Discrepancy("")
#     disc.type = "Gaussian"
#     disc.parameters = (obs_data * 0.15) ** 2
#     disc.opt_sigma = "B"

#     bi = BayesInference(engine)
#     bi.discrepancy = disc
#     bi.inference_method = "mcmc"
#     bi.setup()
#     total_sigma2s = {"Z": np.array([0.15])}
#     bi.perform_bootstrap(total_sigma2s)
#     #data = bi.perturbed_data
#     #selected_indices = np.nonzero(data)[0]
#     mcmc = MCMC(
#         engine,
#         bi.mcmc_params,
#         disc,
#         None,
#         False,
#         None,
#         [],
#         True,
#         "Outputs_testMCMC",
#         "MCMC",
#     )

#     mcmc.nburn = 10
#     mcmc.nsteps = 50
#     mcmc.run_sampler(mod.observations, total_sigma2s)


# %% Test log_prior

# %% Test log_likelihood

# %% Test log_posterior

# %% Test eval_model

# %% Test train_error_model


# %% Main

if __name__ == "__main__":
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.x = np.array([[0], [1], [0.5]])
    expdes.y = {"Z": [[0.4], [0.5], [0.45]]}
    # expdes.x_values = np.array([0]) #  Error in plots if this is not available

    mm = MetaModel(inp)
    mm.fit(expdes.x, expdes.y)
    expdes.generate_ed(max_deg=2)

    mod = PL()
    mod.observations = {"Z": np.array([0.45]), "x_values": np.array([0])}
    mod.output.names = ["Z"]

    engine = Engine(mm, mod, expdes)

    # sigma2Dict = {"Z": np.array([0.05])}
    # sigma2Dict = pd.DataFrame(sigma2Dict, columns=["Z"])
    # obs_data = pd.DataFrame(mod.observations, columns=mod.output.names)
    # disc = Discrepancy("")
    # disc.type = "Gaussian"
    # disc.parameters = (obs_data * 0.15) ** 2
    # disc.opt_sigma = "B"

    # bi = BayesInference(engine)
    # bi.discrepancy = disc
    # bi.inference_method = "mcmc"
    # bi.setup()

    # # chain = [[[1],[2]]]
    # total_sigma2s = {"Z": np.array([0.15])}
    # mcmc = MCMC(bi)
    # mcmc.nsteps = 50
    # mcmc.nburn = 10
    # mcmc.run_sampler(mod.observations, total_sigma2s)
    # # mcmc.gelmain_rubin(chain)
