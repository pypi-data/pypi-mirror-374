import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.preprocessing import PolynomialFeatures


class UnderdeterminedError(ValueError):
    """
    Raised when trying to fit an underdetermined model.
    """


def get_poly_weight_basis(
    position_xy_transformed, position_weights, poly_order, polynomial_type
):
    n_stars, n_pointings = position_xy_transformed.shape[0], position_weights.shape[1]

    if polynomial_type == "standard":
        # Ensure poly_order is an integer, handling numpy scalars
        if isinstance(poly_order, np.ndarray):
            if poly_order.ndim == 0:  # 0-dimensional array (scalar)
                poly_order = int(poly_order.item())
            else:
                poly_order = int(poly_order[0])
        elif isinstance(poly_order, (list, tuple)):
            poly_order = int(poly_order[0])
        else:
            poly_order = int(poly_order)

        poly = PolynomialFeatures(
            degree=poly_order, interaction_only=False, include_bias=True
        )
        position_xy_basis = poly.fit_transform(position_xy_transformed)

    elif polynomial_type == "chebyshev":
        if position_xy_transformed.shape[1] == 1:
            position_xy_basis = np.polynomial.chebyshev.chebvander(
                x=position_xy_transformed[:, 0], deg=poly_order
            )

        elif position_xy_transformed.shape[1] == 2:
            position_xy_basis = np.polynomial.chebyshev.chebvander2d(
                x=position_xy_transformed[:, 0],
                y=position_xy_transformed[:, 1],
                deg=[poly_order, poly_order],
            )

        else:
            raise NotImplementedError(
                "Chebyshev interpolation is only implemented for 1- and 2-dim. input."
            )

    else:
        raise ValueError(f"unknown polynomial type {polynomial_type}")

    n_basis = position_xy_basis.shape[1]
    n_basis_pointings = n_pointings * n_basis
    position_weights_basis = np.zeros([n_stars, n_basis_pointings])

    for ip in range(n_pointings):
        istart = ip * n_basis
        iend = istart + n_basis
        position_weights_basis[:, istart:iend] = (
            position_weights[:, ip][:, np.newaxis] * position_xy_basis
        )

    return position_weights_basis


def var_to_weight(v):
    if v is None:
        return None
    else:
        w = 1.0 / (v**2)
        w[~np.isfinite(w)] = 0
        w[w < 0] = 0
        return w


class TiledRobustPolynomialRegressor(BaseEstimator, RegressorMixin):
    def __init__(
        self,
        poly_order=3,
        ridge_alpha=0,
        n_input_dim=2,
        polynomial_type="standard",
        poly_coefficients=None,
        set_unseen_to_mean=False,
        unseen_pointings=None,
        raise_underdetermined=False,
    ):
        self.poly_order = poly_order
        self.n_input_dim = n_input_dim
        self.ridge_alpha = ridge_alpha
        self.polynomial_type = polynomial_type
        self.arr_pointings_polycoeffs = poly_coefficients
        self.unseen_pointings = unseen_pointings
        self.set_unseen_to_mean = set_unseen_to_mean
        self.raise_underdetermined = raise_underdetermined

    def fit(self, X, y, var_y=None, method="ridge"):
        # check that there are enough data points
        if (
            len(y) < self.n_free_params(X.shape[1] - self.n_input_dim)
            and self.raise_underdetermined
        ):
            raise UnderdeterminedError

        # check shape of ridge_alpha
        n_output = y.shape[1]
        try:
            assert len(self.ridge_alpha) == n_output
            # Convert list to numpy array for sklearn compatibility
            self.ridge_alpha = np.array(self.ridge_alpha)
        except TypeError:
            self.ridge_alpha = np.full(n_output, self.ridge_alpha)

        position_weights_basis = self._get_basis(X)
        n_basis_pointings = position_weights_basis.shape[1]
        self.arr_pointings_polycoeffs = np.empty((n_output, n_basis_pointings))

        if method == "ridge":
            from sklearn.linear_model import Ridge

            reg = Ridge(alpha=self.ridge_alpha, fit_intercept=False)
            reg.fit(X=position_weights_basis, y=y)
            self.arr_pointings_polycoeffs = reg.coef_

        elif method == "huber":
            for io in range(n_output):
                from sklearn.linear_model import HuberRegressor

                w = None if var_y is None else var_to_weight(var_y[:, io])
                reg = HuberRegressor(
                    epsilon=1.01,
                    alpha=self.ridge_alpha[io],
                    fit_intercept=False,
                    max_iter=5000,
                    tol=1e-3,
                )
                reg.fit(X=position_weights_basis, y=y[:, io], sample_weight=w)
                self.arr_pointings_polycoeffs[io] = reg.coef_

        # set pointings that have not been seen during the fit
        self.unseen_pointings = self._get_unseen_pointings(X)

    def predict(self, X, batch_size=1000):
        n_batches = int(np.ceil(X.shape[0] / batch_size))
        y = np.full(
            [X.shape[0], len(self.arr_pointings_polycoeffs)],
            dtype=np.float32,
            fill_value=np.nan,
        )

        select_predict = self._get_select_predict(X)

        for ic in range(n_batches):
            si = ic * batch_size
            ei = si + batch_size

            # Only predict for objects that should be predicted in this batch
            batch_select = select_predict[si:ei]
            if np.any(batch_select):
                # Get batch data
                X_batch = X[si:ei]

                # Predict for the full batch
                y_batch = self._predict_for_seen_pointings(X_batch)

                # Only keep predictions for objects that should be predicted
                y[si:ei][batch_select] = y_batch[batch_select]

        # set unseen pointings to averages if requested
        if self.set_unseen_to_mean:
            y[~select_predict] = np.mean(y[select_predict], axis=0)

        return y

    def _predict_for_seen_pointings(self, X):
        position_weights_basis = self._get_basis(X)

        nx = X.shape[0]
        ny = len(self.arr_pointings_polycoeffs)
        y = np.zeros([nx, ny])

        # Evaluate interpolation
        for io in range(ny):
            y[:, io] = self._evaluate_basis(position_weights_basis, io)

        return y

    def _get_basis(self, X):
        position_xy_transformed = X[:, : self.n_input_dim]
        position_weights = X[:, self.n_input_dim :]
        position_weights_basis = get_poly_weight_basis(
            position_xy_transformed,
            position_weights,
            self.poly_order,
            self.polynomial_type,
        )
        return position_weights_basis

    def _get_unseen_pointings(self, X):
        position_weights = X[:, self.n_input_dim :]
        select_unseen = np.all(position_weights == 0, axis=0)
        empty_pointings = np.flatnonzero(select_unseen)
        return empty_pointings

    def _get_select_predict(self, X):
        # select objects that are not only on pointings which have not been seen during
        # the fit, this also removes objects that are no pointing at all
        position_weights_bool = X[:, self.n_input_dim :].astype(bool)
        seen_only = np.ones_like(position_weights_bool)
        seen_only[:, self.unseen_pointings] = False
        select = np.any(position_weights_bool & seen_only, axis=1)
        return select

    def _evaluate_basis(self, basis, i_dim):
        return np.dot(basis, self.arr_pointings_polycoeffs[i_dim])

    def n_free_params(self, n_pointings):
        return n_pointings * (self.poly_order + 1) ** 2
