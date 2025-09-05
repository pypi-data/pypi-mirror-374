# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Mon Jul 28 2025

import h5py
import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger

from . import correct_brighter_fatter, psf_utils
from .tiled_regressor import TiledRobustPolynomialRegressor as Regressor

LOGGER = logger.get_logger(__file__)
ERR_VAL = 999.0


def colnames_derivative(cols, ax):
    """
    Create column names for derivatives with respect to an axis.

    :param cols: List of column names to derive from
    :param ax: Axis for the derivative ('x' or 'y')
    :return: List of new column names for derivatives
    """
    return [f"{c}_dd{ax}" for c in cols]


def get_model_derivatives(
    cat, filepath_psfmodel, cols, psfmodel_corr_brighter_fatter, delta=1e-2
):
    """
    Calculate spatial derivatives of PSF model parameters.

    :param cat: Input catalog with X_IMAGE, Y_IMAGE columns
    :param filepath_psfmodel: Path to the PSF model file
    :param cols: List of column names to calculate derivatives for
    :param psfmodel_corr_brighter_fatter: Parameters for brighter-fatter correction
    :param delta: Step size for finite difference calculation
    :return: Catalog with additional columns for derivatives
    """
    dims = ["x", "y"]
    for d in dims:
        col_names_der = colnames_derivative(cols, d)
        f = f"{d}_IMAGE".upper()

        # Calculate model at position - delta/2
        cat_dm = cat.copy()
        cat_dm[f] -= delta / 2.0
        cat_dm = predict_psf_for_catalogue_storing(
            cat_dm, filepath_psfmodel, psfmodel_corr_brighter_fatter
        )[0]

        # Calculate model at position + delta/2
        cat_dp = cat.copy()
        cat_dp[f] += delta / 2.0
        cat_dp = predict_psf_for_catalogue_storing(
            cat_dp, filepath_psfmodel, psfmodel_corr_brighter_fatter
        )[0]

        # Calculate centered finite difference
        cat = at.add_cols(cat, names=col_names_der)
        for cv, cd in zip(cols, col_names_der):
            cat[cd] = (cat_dp[cv] - cat_dm[cv]) / delta

    return cat


def predict_psf(position_xy, position_weights, regressor, settings, n_per_chunk=1000):
    """
    Predict PSF parameters at given positions using a fitted regressor.

    :param position_xy: Array of (x,y) positions, shape (n, 2)
    :param position_weights: Weights for each position, shape (n, m)
    :param regressor: Fitted regressor object
    :param settings: Dictionary with model settings, including scale factors
    :param n_per_chunk: Number of samples to process in each batch
    :return: Tuple of predicted parameters and a mask for positions with no coverage
    """
    position_xy_transformed = psf_utils.transform_forward(
        position_xy, scale=settings["scale_pos"]
    )

    position_xy_transformed_weights = np.concatenate(
        [position_xy_transformed, position_weights], axis=1
    )

    position_par_transformed = regressor.predict(
        position_xy_transformed_weights, batch_size=n_per_chunk
    )

    position_par_post = psf_utils.transform_inverse(
        position_par_transformed, settings["scale_par"]
    )

    select_no_coverage = (position_weights.sum(axis=1) == 0) | np.any(
        ~np.isfinite(position_par_post), axis=1
    )
    position_par_post[select_no_coverage] = 0

    return position_par_post, select_no_coverage


def predict_psf_with_file(position_xy, filepath_psfmodel, id_pointing="all"):
    """
    Predict PSF parameters at given positions using a saved PSF model file.

    :param position_xy: Array of (x,y) positions, shape (n, 2)
    :param filepath_psfmodel: Path to the PSF model file
    :param id_pointing: ID of the pointing to use, or 'all'
    :return: Generator yielding predicted parameters and number of exposures
    """
    if position_xy.shape[1] != 2:
        raise ValueError(
            f"Invalid position_xy shape (should be n_obj x 2) {position_xy.shape}"
        )

    # Setup interpolator
    with h5py.File(filepath_psfmodel, "r") as fh5:
        par_names = at.set_loading_dtypes(fh5["par_names"][...])
        pointings_maps = fh5["map_pointings"]
        position_weights = psf_utils.get_position_weights(
            position_xy[:, 0], position_xy[:, 1], pointings_maps
        )
        poly_coeffs = fh5["arr_pointings_polycoeffs"][...]
        unseen_pointings = fh5["unseen_pointings"][...]
        settings = {
            key: at.set_loading_dtypes(fh5["settings"][key][...])
            for key in fh5["settings"]
        }
        settings.setdefault("polynomial_type", "chebyshev")
        LOGGER.debug(f"polynomial_type={settings['polynomial_type']}")

        # Add debugging information
        if "scale_par" in settings:
            LOGGER.debug(f"Loaded scale_par shape: {settings['scale_par'].shape}")
            LOGGER.debug(f"First few scale_par values: {settings['scale_par'][:3]}")

    regressor = Regressor(
        poly_order=settings["poly_order"],
        ridge_alpha=settings["ridge_alpha"],
        polynomial_type=settings["polynomial_type"],
        poly_coefficients=poly_coeffs,
        unseen_pointings=unseen_pointings,
    )

    if id_pointing == "all":
        LOGGER.info(
            f"prediction for cnn models n_pos={position_xy.shape[0]} id_pointing=all"
        )

        position_par_post, select_no_coverage = predict_psf(
            position_xy, position_weights, regressor, settings
        )

        position_par_post = np.core.records.fromarrays(
            position_par_post.T, names=",".join(par_names)
        )
        psf_utils.postprocess_catalog(position_par_post)
        n_exposures = psf_utils.position_weights_to_nexp(position_weights)
        yield position_par_post, select_no_coverage, n_exposures

    else:
        raise NotImplementedError(
            "This feature is not yet implemented due to the polynomial coefficients"
            " covariances which are a tiny bit tricky but definitely doable"
        )


def predict_psf_for_catalogue(
    cat, filepath_psfmodel, id_pointing="all", psfmodel_corr_brighter_fatter=None
):
    """
    Predict PSF parameters for a given catalog.

    :param cat: Input catalog with X_IMAGE, Y_IMAGE (and MAG_AUTO if applicable) columns
    :param filepath_psfmodel: Path to the PSF model file
    :param id_pointing: ID of the pointing to use, or 'all'
    :param psfmodel_corr_brighter_fatter: Parameters for brighter-fatter correction
    :return: Generator yielding predicted parameters and number of exposures
    """
    position_xy = np.stack((cat["X_IMAGE"] - 0.5, cat["Y_IMAGE"] - 0.5), axis=-1)

    for position_par_post, select_no_coverage, n_exposures in predict_psf_with_file(
        position_xy, filepath_psfmodel, id_pointing=id_pointing
    ):
        # Set points without coverage to error value
        for par_name in position_par_post.dtype.names:
            position_par_post[par_name][select_no_coverage] = ERR_VAL

        # Apply brighter-fatter correction
        if (
            psfmodel_corr_brighter_fatter is not None
            and "apply_to_galaxies" in psfmodel_corr_brighter_fatter
            and psfmodel_corr_brighter_fatter["apply_to_galaxies"]
        ):
            LOGGER.info("added brighter-fatter to PSF prediction")
            (
                position_par_post["psf_fwhm_ipt"],
                position_par_post["psf_e1_ipt"],
                position_par_post["psf_e2_ipt"],
            ) = correct_brighter_fatter.brighter_fatter_add(
                col_mag=cat["MAG_AUTO"],
                col_fwhm=position_par_post["psf_fwhm_ipt"],
                col_e1=position_par_post["psf_e1_ipt"],
                col_e2=position_par_post["psf_e2_ipt"],
                dict_corr=psfmodel_corr_brighter_fatter,
            )

        yield position_par_post, n_exposures


def predict_psf_for_catalogue_storing(
    cat_in, filepath_psf_model, psfmodel_corr_brighter_fatter
):
    """
    Predict PSF parameters for a catalog and format for storage.

    :param cat_in: Input catalog with X_IMAGE, Y_IMAGE columns
    :param filepath_psf_model: Path to the PSF model file
    :param psfmodel_corr_brighter_fatter: Parameters for brighter-fatter correction
    :return: Tuple of output catalog with predicted parameters and number of exposures
    """
    # Predict using the generator function
    position_par_post, n_exposures = next(
        predict_psf_for_catalogue(
            cat=cat_in,
            filepath_psfmodel=filepath_psf_model,
            psfmodel_corr_brighter_fatter=psfmodel_corr_brighter_fatter,
        )
    )

    # Create output catalog with proper structure
    if "id" in cat_in.dtype.names:
        # if it is a simulated catalog, we also want to add the id of the galaxy
        dtypes = at.get_dtype(
            ("X_IMAGE", "Y_IMAGE", "id") + position_par_post.dtype.names
        )
    else:
        dtypes = at.get_dtype(("X_IMAGE", "Y_IMAGE") + position_par_post.dtype.names)

    cat_out = np.empty(len(cat_in), dtype=dtypes)

    # Copy predicted parameters
    for par_name in position_par_post.dtype.names:
        cat_out[par_name] = position_par_post[par_name]

    # Copy position information
    cat_out["X_IMAGE"] = cat_in["X_IMAGE"]
    cat_out["Y_IMAGE"] = cat_in["Y_IMAGE"]

    return cat_out, n_exposures
