# -*- coding: utf-8 -*-
"""
Test the ExpDesigns class in bayesvalidrox.
Class ExpDesigns: 
    generate_samples
    generate_ed
    read_from_file
    random_sampler
    pcm_sampler
Other function tests to be found in parent class 'InputSpace'

"""
import sys

sys.path.append("src/")
import pytest
import numpy as np

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns

# %% Test ExpDesign.pcm_sampler

# TODO: these all have what looks like pcm-sampler issues
if 0:

    def test_pcm_sampler_noinit() -> None:
        """
        Sample via pcm without init_param_space
        """
        x = np.random.uniform(0, 1, 1000)
        inp = Input()
        inp.add_marginals()
        inp.marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.pcm_sampler(4, 2)

    def test_pcm_sampler_lowdeg() -> None:
        """
        Sample via pcm with init_param_space and small max_deg
        """
        x = np.random.uniform(0, 1, 1000)
        inp = Input()
        inp.add_marginals()
        inp.marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.init_param_space(2)
        exp.pcm_sampler(4, 2)

    def test_pcm_sampler_highdeg() -> None:
        """
        Sample via pcm with init_param_space and high max_deg
        """
        x = np.random.uniform(0, 1, 1000)
        inp = Input()
        inp.add_marginals()
        inp.marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.init_param_space(30)
        exp.pcm_sampler(4, 4)

    def test_pcm_sampler_lscm() -> None:
        """
        Sample via pcm with init_param_space and samplin gmethod 'lscm'
        """
        x = np.random.uniform(0, 1, 1000)
        inp = Input()
        inp.add_marginals()
        inp.marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.init_param_space(1)
        exp.sampling_method = "lscm"
        exp.pcm_sampler(4, 4)

    def test_pcm_sampler_rawdata_1d() -> None:
        """
        Sample via pcm, init_param_space implicitly, has raw data
        """
        x = np.random.uniform(0, 1, (1, 1000))
        inp = Input()
        inp.add_marginals()
        inp.marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.raw_data = np.random.uniform(0, 1, 1000)
        exp.pcm_sampler(4, 4)


def test_pcm_sampler_rawdata() -> None:
    """
    Sample via pcm, init_param_space implicitly, has raw data
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.raw_data = np.random.uniform(0, 1, 1000)
    with pytest.raises(AttributeError) as excinfo:
        exp.pcm_sampler(4, 4)
    assert str(excinfo.value) == "Data should be a 1D array"


# %% Test ExpDesign.random_sampler


def test_random_sampler() -> None:
    """
    Sample randomly, init_param_space implicitly
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.random_sampler(4)


def test_random_sampler_largedataj_dist0() -> None:
    """
    Sample randomly, init_param_space implicitly, more samples wanted than given,
    j_dist available, priors given via samples
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.init_param_space(max_deg=1)
    exp.random_sampler(100000)


def test_random_sampler_largedataj_dist1() -> None:
    """
    Sample randomly, init_param_space implicitly, more samples wanted than given,
    j_dist available, prior distributions given
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    exp = ExpDesigns(inp)
    exp.init_param_space(max_deg=1)
    exp.random_sampler(100000)


def test_random_sampler_rawdata() -> None:
    """
    Sample randomly, init_param_space implicitly, has 2d raw data
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.raw_data = np.random.uniform(0, 1, (1, 1000))
    exp.random_sampler(4)


def test_random_sampler_rawdata1d() -> None:
    """
    Sample randomly, init_param_space implicitly, has raw data, but only 1d
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.raw_data = np.random.uniform(0, 1, 1000)
    with pytest.raises(AttributeError) as excinfo:
        exp.random_sampler(4)
    assert (
        str(excinfo.value)
        == "The given raw data for sampling should have two dimensions"
    )


def test_random_sampler_fewdata() -> None:
    """
    Sample randomly, init_param_space implicitly, has few 2d raw datapoints
    """
    x = np.random.uniform(0, 1, 5)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.raw_data = np.random.uniform(0, 1, (1, 1000))
    exp.random_sampler(7)


# %% Test ExpDesign.generate_samples


def test_generate_samples() -> None:
    """
    Generate samples according to chosen scheme
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.generate_samples(4)


def test_generate_samples_grid() -> None:
    """
    Generate samples on grid, check against ref.
    """
    inp = Input()
    for i in range(2):
        inp.add_marginals(
            name=str(i),
            dist_type="uniform",
            parameters=[-5, 5],
        )
    exp = ExpDesigns(inp)
    exp.sampling_method = "grid"
    exp.n_init_samples = 140

    # Test Exp_design
    exp.generate_ed()
    x = exp.x

    # TODO: assert the number of samples that were generated!

    # Compare generate_ed with generate_samples
    samples = exp.generate_samples(140, "grid")
    x = x[x[:, 0].argsort()]
    x = x[x[:, 1].argsort(kind="mergesort")]

    samples = samples[samples[:, 0].argsort()]
    samples = samples[samples[:, 1].argsort(kind="mergesort")]

    assert x.shape == samples.shape
    assert np.sum(np.abs(x - x)) == 0
    assert np.sum(np.abs(x - samples)) == 0


# %% Test ExpDesign.generate_ed


def test_generate_ed() -> None:
    """
    Generate ED as is
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.n_init_samples = 4
    exp.generate_ed()


def test_generate_ed_negsamplenum():
    """
    Generate ED for neg number of samples
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="random")
    exp.n_init_samples = -1
    with pytest.raises(ValueError) as excinfo:
        exp.generate_ed()
    assert (
        str(excinfo.value)
        == "A negative number of samples cannot be created. Please provide positive n_samples"
    )


def test_generate_ed_usernox() -> None:
    """
    User-defined ED without samples
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="user")
    exp.n_init_samples = 4
    with pytest.raises(AttributeError) as excinfo:
        exp.generate_ed()
    assert (
        str(excinfo.value)
        == "User-defined sampling cannot proceed as no samples provided. "
        "Please add them to this class as attribute X"
    )


def test_generate_ed_userxdimerr() -> None:
    """
    User-defined ED with wrong shape of samples
    """
    x = np.random.uniform(0, 1, 1000)
    X = np.random.uniform(0, 1, (2, 1, 1000))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="user")
    exp.n_init_samples = 4
    exp.x = X
    with pytest.raises(AttributeError) as excinfo:
        exp.generate_ed()
    assert str(excinfo.value) == "The provided samples shuld have 2 dimensions"


def test_generate_ed_xnouser() -> None:
    """
    ED with user-defined samples, set to 'user'
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.x = [[0], [1]]
    exp.n_init_samples = 4
    with pytest.warns(UserWarning) as excinfo:
        exp.generate_ed()
    assert excinfo._record == True
    assert exp.sampling_method == "user"


def test_generate_ed_ynouser() -> None:
    """
    ED with user-defined Y, warn for rerunning model
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.y = {"a": [1]}
    exp.n_init_samples = 4
    with pytest.warns(UserWarning) as excinfo:
        exp.generate_ed()
    assert excinfo._record == True
    assert exp.y is None


def test_generate_ed_userx() -> None:
    """
    User-defined ED with wrong shape of samples
    """
    x = np.random.uniform(0, 1, 1000)
    X = np.random.uniform(0, 1, (3, 1000))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="user")
    exp.x = X
    exp.n_init_samples = 4
    exp.generate_ed()


# TODO: this looks like a pcm-sampler issue
if 0:

    def test_generate_ed_pcm() -> None:
        """
        PCM-defined ED
        """
        x = np.random.uniform(0, 1, 1000)
        inp = Input()
        inp.add_marginals()
        inp.marginals[0].input_data = x
        exp = ExpDesigns(inp, sampling_method="PCM")
        exp.n_init_samples = 4
        exp.generate_ed()


def test_generate_ed_random() -> None:
    """
    Random-defined ED
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="random")
    exp.n_init_samples = 4
    exp.generate_ed()


def test_generate_ed_usertrafo() -> None:
    """
    User-defined ED
    """
    x = np.random.uniform(0, 1, 1000)
    X = np.random.uniform(0, 1, (1, 1000))
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="user")
    exp.meta_Model_type = "gpe"
    exp.x = X
    exp.n_init_samples = 4
    exp.generate_ed()


def test_generate_ed_randomtrafo() -> None:
    """
    User-defined ED
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="random")
    exp.n_init_samples = 4
    exp.generate_ed()


def test_generate_ed_latin() -> None:
    """
    latin-hypercube-defined ED
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="latin-hypercube")
    exp.n_init_samples = 4
    exp.generate_ed(1)


# %% Test ExpDesign.read_from_file


def test_read_from_file_nofile():
    """
    No file given to read in
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="user")
    with pytest.raises(AttributeError) as excinfo:
        exp.read_from_file(["Out"])
    assert (
        str(excinfo.value)
        == "ExpDesign cannot be read in, please provide hdf5 file first"
    )


def test_read_from_file_wrongcomp():
    """
    Correct file, incorrect output name
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="user")
    exp.hdf5_file = "tests/ExpDesign_testfile.hdf5"
    with pytest.raises(KeyError) as excinfo:
        exp.read_from_file(["Out"])
    assert str(excinfo.value) == "'Unable to open object (component not found)'"


def test_read_from_file():
    """
    Read from testfile
    """
    x = np.random.uniform(0, 1, 1000)
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method="user")
    exp.hdf5_file = "tests/ExpDesign_testfile.hdf5"
    exp.read_from_file(["Z"])
