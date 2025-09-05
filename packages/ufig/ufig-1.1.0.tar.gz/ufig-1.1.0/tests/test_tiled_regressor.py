# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Wed Aug 21 2024


import numpy as np
import pytest

from ufig.psf_estimation.tiled_regressor import (
    TiledRobustPolynomialRegressor,
    UnderdeterminedError,
    get_poly_weight_basis,
    var_to_weight,
)


def test_TiledRobustPolynomialRegressor_huber():
    # Test fit and predict
    X = np.random.rand(100, 5)
    y = np.zeros((100, 3))
    y[:, 0] = X[:, 0] + X[:, 1] ** 2 + np.random.uniform(-1e-2, 1e-2, 100)
    y[:, 1] = X[:, 2] + X[:, 3] ** 2 + np.random.uniform(-1e-2, 1e-2, 100)
    y[:, 2] = X[:, 4] + X[:, 0] * X[:, 1] + np.random.uniform(-1e-2, 1e-2, 100)
    model = TiledRobustPolynomialRegressor(
        poly_order=2, ridge_alpha=0.1, n_input_dim=2, polynomial_type="standard"
    )
    model.fit(X, y, method="huber")
    y_pred = model.predict(X)
    assert y_pred.shape == y.shape


def test_TiledRobustPolynomialRegressor_underdetermined():
    # Test underdetermined error
    X = np.random.rand(10, 5)
    y = np.zeros((10, 3))
    model = TiledRobustPolynomialRegressor(
        poly_order=2,
        ridge_alpha=0.1,
        n_input_dim=2,
        polynomial_type="standard",
        raise_underdetermined=True,
    )
    with pytest.raises(UnderdeterminedError):
        model.fit(X, y)


def test_TiledRobustPolynomialRegressor_ridge():
    # Test fit with unseen pointings
    X = np.random.rand(100, 5)
    y = np.zeros((100, 3))
    y[:, 0] = X[:, 0] + X[:, 1] ** 2 + np.random.uniform(-1e-2, 1e-2, 100)
    y[:, 1] = X[:, 2] + X[:, 3] ** 2 + np.random.uniform(-1e-2, 1e-2, 100)
    y[:, 2] = X[:, 4] + X[:, 0] * X[:, 1] + np.random.uniform(-1e-2, 1e-2, 100)
    model = TiledRobustPolynomialRegressor(
        poly_order=2,
        ridge_alpha=0.1,
        n_input_dim=2,
        polynomial_type="standard",
        unseen_pointings=5,
    )
    model.fit(X, y, method="ridge")
    y_pred = model.predict(X)
    assert y_pred.shape == y.shape


def test_get_poly_weight_basis():
    # Test 1D Chebyshev
    position_xy_transformed = np.random.rand(10, 1)
    position_weights = np.random.rand(10, 5)
    basis = get_poly_weight_basis(
        position_xy_transformed,
        position_weights,
        poly_order=3,
        polynomial_type="chebyshev",
    )
    assert basis.shape == (10, 5 * 4)

    # Test 2D Chebyshev
    position_xy_transformed = np.random.rand(10, 2)
    position_weights = np.random.rand(10, 5)
    basis = get_poly_weight_basis(
        position_xy_transformed,
        position_weights,
        poly_order=3,
        polynomial_type="chebyshev",
    )
    assert basis.shape == (10, 5 * 16)

    # Test standard polynomial
    position_xy_transformed = np.random.rand(10, 2)
    position_weights = np.random.rand(10, 5)
    basis = get_poly_weight_basis(
        position_xy_transformed,
        position_weights,
        poly_order=3,
        polynomial_type="standard",
    )
    assert basis.shape == (10, 5 * 10)

    # Test unsupported polynomial type
    with pytest.raises(ValueError):
        get_poly_weight_basis(
            position_xy_transformed,
            position_weights,
            poly_order=3,
            polynomial_type="unknown",
        )


def test_var_to_weight():
    # Test with None
    assert var_to_weight(None) is None

    # Test with finite values
    v = np.array([1, 4, 9])
    w = var_to_weight(v)
    assert np.allclose(w, [1, 0.0625, 0.01234568])

    # Test with non-finite values
    v = np.array([1, 0, np.inf, -np.inf, np.nan])
    w = var_to_weight(v)
    assert np.allclose(w, [1, 0, 0, 0, 0])
