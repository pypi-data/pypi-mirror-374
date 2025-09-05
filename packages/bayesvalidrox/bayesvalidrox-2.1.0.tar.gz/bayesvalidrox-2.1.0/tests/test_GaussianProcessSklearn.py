"""
Test the Gaussian Processes in bayesvalidrox

Class GaussianProcessSklearn
    build_meta_model       - x
    check_is_gaussian      - x
    build_kernels          - x
    transform_x            - x
    fit                    - x 
    adaptive_regression    - x
    scale_x                - x 
    eval_meta_model        - x
    calculate_moments      - x
"""

import sys
import numpy as np
import pytest

from sklearn.preprocessing import MinMaxScaler, StandardScaler

sys.path.append("../src/")

from bayesvalidrox import GPESkl, Input
from bayesvalidrox.surrogate_models.input_space import InputSpace


@pytest.fixture
def gpe():
    """
    Untrained GPE
    """

    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    samples = np.array([[0.2], [0.8]])
    meta_model = GPESkl(inp)
    meta_model.CollocationPoints = samples
    meta_model.input_space = InputSpace(
        meta_model.input_obj, meta_model.meta_model_type
    )
    meta_model.input_space.init_param_space(np.max(meta_model.pce_deg))
    return meta_model


def test_meta_model():
    """Construct GPSklearn without input"""
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    GPESkl(inp)


def test_build_metamodel(gpe) -> None:
    """
    Build GPE
    """
    meta_model = gpe
    meta_model.CollocationPoints = np.array([[0.2], [0.8]])
    meta_model.build_metamodel()


def test_check_is_gaussian(gpe) -> None:
    """
    Check if Gaussian
    """
    meta_model = gpe
    meta_model.check_is_gaussian()
    assert meta_model.is_gaussian == True, "Expected is_gaussian to be True"


def test_add_input_space() -> None:
    """
    Add InputSpace in PCE
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = GPESkl(inp)
    mm.add_input_space()


def test_fit() -> None:
    """
    Fit GPE
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = GPESkl(inp)
    meta_model.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})


# def test_fit_parallel() -> None:
#     """
#     Fit GPE in parallel
#     """
#     inp = Input()
#     inp.add_marginals()
#     inp.marginals[0].dist_type = 'normal'
#     inp.marginals[0].parameters = [0, 1]
#     mm = GPESkl(inp)
#     mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]}, parallel=True)


def test_fit_verbose() -> None:
    """
    Fit PCE verbose
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = GPESkl(inp)
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]}, verbose=True)


def test_fit_pca() -> None:
    """
    Fit PCE verbose and with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = GPESkl(inp)
    meta_model.dim_red_method = "pca"
    meta_model.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})


def test_build_kernels(gpe) -> None:
    """
    Build kernels
    """
    gpe.build_kernels()


def test_kernel_no_kertyp(gpe) -> None:
    """
    Test kernel with no kernel type
    """
    gpe.build_kernels()
    assert gpe._kernel_type == "RBF"


def test_build_kernel_wrong_kername(gpe) -> None:
    """
    Test kernel with an invalid kernel name
    """
    gpe._kernel_type = "InvalidKernel"

    with pytest.raises(
        AttributeError, match="The kernel option InvalidKernel is not available."
    ):
        gpe.build_kernels()


def test_build_kernel_wrong_kertyp(gpe) -> None:
    """
    Test building kernels with an invalid variable type
    """
    gpe._kernel_type = 123

    with pytest.raises(TypeError, match="The kernel option 123 is of an invalid type."):
        gpe.build_kernels()


def test_kernel_type_rbf(gpe) -> None:
    """
    Test kernel type
    """
    gpe._kernel_type = "RBF"
    kernel_list, kernel_names = gpe.build_kernels()

    assert len(kernel_list) == 1, "Expected only one kernel when auto_select is False"
    assert kernel_names == ["RBF"], "Expected kernel name to be 'RBF'"


def test_build_kernels_matern(gpe) -> None:
    """
    Build kernels with Matern kernel type
    """
    meta_model = gpe
    meta_model._kernel_type = "Matern"
    kernel_list, kernel_names = meta_model.build_kernels()

    assert len(kernel_list) == 1, "Expected only one kernel when auto_select is False"
    assert kernel_names == ["Matern"], "Expected kernel name to be 'Matern'"


def test_build_kernels_rq(gpe) -> None:
    """
    Build kernels with Matern kernel type
    """
    meta_model = gpe
    meta_model._kernel_type = "RQ"
    kernel_list, kernel_names = meta_model.build_kernels()

    assert len(kernel_list) == 1, "Expected only one kernel when auto_select is False"
    assert kernel_names == ["RQ"], "Expected kernel name to be 'RQ'"


def test_auto_select_kernels(gpe) -> None:
    """Build Kernels when auto_select is True"""
    meta_model = gpe
    meta_model._auto_select = True
    kernel_list, kernel_names = meta_model.build_kernels()

    assert len(kernel_list) == 3, "Expected three kernels when auto_select is True"
    assert sorted(kernel_names) == [
        "Matern",
        "RBF",
        "RQ",
    ], "Expected kernel names to be 'Matern', 'RBF', 'RQ'"


def test_build_kernels_with_length_scale(gpe) -> None:
    """
    Build kernels with specific length scale
    """
    meta_model = gpe
    meta_model.kernel_length_scale = 1.5
    meta_model.build_kernels()


def test_build_kernels_with_bounds(gpe) -> None:
    """
    Build kernels with specific bounds
    """
    meta_model = gpe
    meta_model.kernel_bounds = (1e-2, 1e1)
    meta_model.build_kernels()


def test_kernel_isotropy(gpe):
    """
    Test kernel isotropy
    """
    meta_model = gpe
    meta_model.kernel_isotropy = True
    kernels_list, _ = meta_model.build_kernels()

    assert len(kernels_list) == 1, "Expected only one kernel when auto_select is False"
    assert isinstance(
        kernels_list[0].k2.length_scale, int
    ), "Expected 1 length scales for isotropic kernel, but got a list of them"


def test_anisotropic_kernel() -> None:
    """Build anisotropic kernels for a 2d case"""
    ndim = 2
    inp = Input()
    for i in range(ndim):
        inp.add_marginals()
        inp.marginals[i].dist_type = "uniform"
        inp.marginals[i].parameters = [0, 1]
    meta_model = GPESkl(inp)
    meta_model.input_space = InputSpace(
        meta_model.input_obj, meta_model.meta_model_type
    )
    meta_model._kernel_isotropy = False
    meta_model._kernel_type = "RBF"

    kernels_list, kernel_names = meta_model.build_kernels()

    assert len(kernels_list) == 1, "Expected only one kernel when auto_select is False"
    assert kernel_names == ["RBF"], "Expected kernel name to be 'RBF'"
    assert len(kernels_list[0].k2.length_scale) == ndim, (
        f"Expected {ndim} length scales for anisotropic kernel, "
        f"but got {len(kernels_list[0].k2.length_scale)}"
    )


def test_adaptive_regression(gpe) -> None:
    """
    Regression without a specific method
    """
    samples = np.array([[0.0], [0.1]])
    outputs = np.array([[0.1], [0.1]])

    gpe.build_metamodel()
    gpe.adaptive_regression(samples, outputs, var_idx=None)


def test_adaptive_regression_verbose(gpe) -> None:
    """
    Regression without a specific method with verbose
    """
    samples = np.array([[0.0], [0.1]])
    outputs = np.array([[0.1], [0.1]])

    gpe.build_metamodel()
    gpe.adaptive_regression(samples, outputs, var_idx=None, verbose=True)


# Added:
def test_transform_scale_x_norm(gpe) -> None:
    """
    Test normalization using 'norm' (MinMaxScaler), for both
    the transform_x() and scale_x() functions.
    """
    meta_model = gpe
    meta_model.normalize_x_method = "norm"
    X = np.array([[1, 2], [3, 4], [5, 6]])
    x_transformed, scaler = meta_model.transform_x(X)  # Call directly on class

    expected_scaler = MinMaxScaler()
    expected_x_transformed = expected_scaler.fit_transform(X)

    assert np.allclose(x_transformed, expected_x_transformed), "Normalization failed"
    assert isinstance(scaler, MinMaxScaler), "Scaler object is not MinMaxScaler"

    meta_model._x_scaler = scaler
    x_scaled = meta_model.scale_x(X, meta_model._x_scaler)
    assert np.allclose(
        x_scaled, expected_x_transformed
    ), "Scaling after normalization failed"


def test_transform_scale_x_standard(gpe) -> None:
    """Test standardization using 'standard' from the Scikit-Learn
    library, for both the transformation and the
    scaling functions"""
    X = np.array([[1, 2], [3, 4], [5, 6]])
    meta_model = gpe
    meta_model.normalize_x_method = "standard"
    x_transformed, scaler = meta_model.transform_x(X)

    expected_scaler = StandardScaler()
    expected_x_transformed = expected_scaler.fit_transform(X)

    assert np.allclose(x_transformed, expected_x_transformed), "Standardization failed"
    assert isinstance(scaler, StandardScaler), "Scaler object is not StandardScaler"

    meta_model._x_scaler = scaler
    x_scaled = meta_model.scale_x(X, meta_model._x_scaler)
    assert np.allclose(
        x_scaled, expected_x_transformed
    ), "Scaling after standardization failed"


def test_transform_scale_x_strnone(gpe) -> None:
    """Test the no transformation case when transform_type is `none` as a string"""
    X = np.array([[1, 2], [3, 4], [5, 6]])
    meta_model = gpe
    meta_model.normalize_x_method = "none"
    x_transformed, scaler = meta_model.transform_x(X)

    assert np.array_equal(x_transformed, X), "No transformation failed"
    assert scaler is None, "Scaler object should be None"

    # Test scale_x(scaler=None)
    meta_model._x_scaler = scaler
    x_scaled = meta_model.scale_x(X, meta_model._x_scaler)
    assert np.allclose(x_scaled, X), "Scaling after standardization failed"


def test_transform_scale_x_none(gpe) -> None:
    """Test the no transformation case when transform_type is None"""
    X = np.array([[1, 2], [3, 4], [5, 6]])
    meta_model = gpe
    meta_model.normalize_x_method = None
    x_transformed, scaler = meta_model.transform_x(X)

    assert np.array_equal(x_transformed, X), "No transformation failed"
    assert scaler is None, "Scaler object should be None"

    # Test scale_x(scaler=None)
    meta_model._x_scaler = scaler
    x_scaled = meta_model.scale_x(X, meta_model._x_scaler)
    assert np.allclose(x_scaled, X), "Scaling after standardization failed"


def test_transform_x_user_input(gpe) -> None:
    """Test the no transformation case when the user sets the transformation type"""
    X = np.array([[1, 2], [3, 4], [5, 6]])
    meta_model = gpe
    meta_model.normalize_x_method = None
    x_transformed, scaler = meta_model.transform_x(X, transform_type="norm")

    expected_scaler = MinMaxScaler()
    expected_x_transformed = expected_scaler.fit_transform(X)

    assert np.allclose(x_transformed, expected_x_transformed), "Normalization failed"
    assert isinstance(scaler, MinMaxScaler), "Scaler object is not MinMaxScaler"

    # Test scale_x(scaler=None)
    meta_model._x_scaler = scaler
    x_scaled = meta_model.scale_x(X, meta_model._x_scaler)
    assert np.allclose(
        x_scaled, expected_x_transformed
    ), "Scaling after standardization failed"


def test_transform_x_invalid_type(gpe) -> None:
    """Test transformation with an invalid transformation type"""
    X = np.array([[1, 2], [3, 4], [5, 6]])
    meta_model = gpe

    # Expecting an AttributeError when an invalid transformation type is provided
    with pytest.raises(AttributeError, match="No scaler invalid found."):
        meta_model.transform_x(X, transform_type="invalid")


def test_transform_scale_default(gpe) -> None:
    """
    Test normalization using 'norm' (MinMaxScaler), for
    both the transform_x() and scale_x() functions.
    """
    meta_model = gpe
    X = np.array([[1, 2], [3, 4], [5, 6]])
    x_transformed, scaler = meta_model.transform_x(
        X, transform_type=None
    )  # Call directly on class

    expected_scaler = MinMaxScaler()
    expected_x_transformed = expected_scaler.fit_transform(X)

    assert np.allclose(x_transformed, expected_x_transformed), "Normalization failed"
    assert isinstance(scaler, MinMaxScaler), "Scaler object is not MinMaxScaler"


# TO Do:
def test_eval_metamodel() -> None:
    """
    Evaluate trained GPE
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = GPESkl(inp)
    meta_model.out_names = ["Z"]
    meta_model.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    meta_model.eval_metamodel([[0.4]])


def test_eval_metamodel_multiple_outputs() -> None:
    """
    Evaluate trained GPE with multiple outputs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = GPESkl(inp)
    meta_model.out_names = ["Z1", "Z2"]
    meta_model.fit(
        [[0.2], [0.4], [0.8]],
        {"Z1": [[0.4], [0.2], [0.5]], "Z2": [[0.3], [0.1], [0.4]]},
    )
    meta_model.eval_metamodel([[0.4]])


def test_eval_metamodel_normalboots() -> None:
    """
    Eval trained PCE with normal bootstrap
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = GPESkl(inp)
    mm.bootstrap_method = "normal"
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_highnormalboots() -> None:
    """
    Eval trained PCE with higher bootstrap-itrs
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = GPESkl(inp)
    mm.n_bootstrap_itrs = 2
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_pca() -> None:
    """
    Eval trained PCE with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    mm = GPESkl(inp)
    mm.dim_red_method = "pca"
    mm.out_names = ["Z"]
    mm.fit([[0.2], [0.8]], {"Z": [[0.4, 0.4], [0.5, 0.6]]})
    mm.eval_metamodel([[0.4]])


def test_pca_transformation() -> None:
    """
    Apply PCA
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = GPESkl(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    meta_model.pca_transformation(outputs, 1)


def test_pca_transformation_varcomp() -> None:
    """
    Apply PCA with set var_pca_threshold
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = GPESkl(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    meta_model.var_pca_threshold = 1
    meta_model.pca_transformation(outputs, 1)


# %% Test GPE.AutoVivification
def test_autovivification() -> None:
    """
    Creation of auto-vivification objects
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = GPESkl(inp)
    meta_model.AutoVivification()


# %% Test GPE.copy_meta_model_opts


def test_copy_meta_model_opts() -> None:
    """
    Copy the PCE with just some stats
    """
    inp = Input()
    inp.add_marginals()
    inp.marginals[0].dist_type = "normal"
    inp.marginals[0].parameters = [0, 1]
    meta_model = GPESkl(inp)
    meta_model.add_input_space()
    meta_model.copy_meta_model_opts()


def test_eval_metamodel_with_pca(gpe) -> None:
    """
    Evaluate trained GPE with PCA
    """
    meta_model = gpe
    meta_model.out_names = ["Z"]
    meta_model.dim_red_method = "pca"
    meta_model.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    meta_model.eval_metamodel([[0.4]])


def test_eval_metamodel_invalid_input(gpe) -> None:
    """
    Evaluate trained GPE with invalid input
    """
    meta_model = gpe
    meta_model.out_names = ["Z"]
    meta_model.fit([[0.2], [0.4], [0.8]], {"Z": [[0.4], [0.2], [0.5]]})
    with pytest.raises(AttributeError):
        meta_model.eval_metamodel([[0.4, 0.5]])
