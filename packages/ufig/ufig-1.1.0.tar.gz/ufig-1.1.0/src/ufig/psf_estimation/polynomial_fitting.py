# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Mon Jul 21 2025


import numpy as np
from cosmic_toolbox import logger

from ufig.array_util import set_flag_bit

from . import psf_utils, star_sample_selection_cnn
from .tiled_regressor import TiledRobustPolynomialRegressor as Regressor

LOGGER = logger.get_logger(__file__)


class PolynomialPSFModel:
    """
    Handles polynomial interpolation fitting for PSF spatial variation.

    This class manages:
    - Polynomial model configuration and fitting
    - Iterative outlier removal during fitting
    - Cross-validation for regularization parameter selection
    - Model validation and quality assessment
    """

    def __init__(self, config):
        """
        Initialize the polynomial PSF model with configuration parameters.

        :param config: Configuration dictionary with parameters for polynomial fitting.
        """
        self.config = config

    def fit_model(self, cat, position_weights):
        """
        Fit polynomial interpolation model to CNN predictions.

        """
        LOGGER.info("Starting polynomial model fitting")

        # Select stars for fitting and prepare parameters
        cat_fit, flags_fit, position_weights_fit = self._select_fitting_stars(
            cat, position_weights
        )

        # Prepare parameter columns and settings
        col_names_fit, col_names_ipt, settings_fit = self._prepare_fitting_config(
            cat_fit
        )

        # Fit model with iterative outlier removal
        regressor, cat_clip = self._fit_with_outlier_removal(
            cat_fit, col_names_fit, position_weights_fit, settings_fit
        )

        # Handle validation stars if requested and refit if needed
        if self.config.get("fraction_validation_stars", 0) > 0:
            regressor = self._handle_validation_stars(
                cat_fit,
                cat_clip,
                flags_fit,
                col_names_fit,
                position_weights_fit,
                settings_fit,
            )

        LOGGER.info("Polynomial model fitting complete")

        return {
            "regressor": regressor,
            "cat_fit": cat_fit,
            "cat_clip": cat_clip,
            "flags_fit": flags_fit,
            "col_names_fit": col_names_fit,
            "col_names_ipt": col_names_ipt,
            "settings_fit": settings_fit,
        }

    def _select_fitting_stars(self, cat_cnn, position_weights):
        """
        Select stars for polynomial fitting based on CNN predictions.

        :param cat_cnn: Catalog of stars with CNN predictions.
        :param position_weights: Position weights for the stars.
        :return: Tuple of (selected catalog, flags, position weights).
        """
        # Start with all stars that passed CNN quality cuts
        select_fit = np.ones(len(cat_cnn), dtype=bool)

        # Filter out stars with NaN values in CNN predictions
        cnn_columns = [col for col in cat_cnn.dtype.names if col.endswith("_cnn")]
        for col in cnn_columns:
            if np.issubdtype(cat_cnn[col].dtype, np.floating):
                select_fit &= np.isfinite(cat_cnn[col])

        n_valid = np.sum(select_fit)
        n_total = len(cat_cnn)
        LOGGER.info(
            f"CNN NaN filtering: {n_valid}/{n_total} stars have finite CNN predictions"
        )

        if n_valid == 0:
            raise ValueError(
                "No stars with finite CNN predictions available for polynomial fitting"
            )

        cat_fit = cat_cnn[select_fit]
        flags_fit = np.zeros(len(cat_fit), dtype=np.int32)
        position_weights_fit = position_weights[select_fit]

        LOGGER.info(f"Selected {len(cat_fit)} stars for polynomial fitting")

        return cat_fit, flags_fit, position_weights_fit

    def _prepare_fitting_config(self, cat_fit):
        """
        Prepare parameter columns and fitting configuration.

        :param cat_fit: Catalog of stars selected for fitting.
        :param filepath_image: Path to the image file for normalization.
        :return: Tuple of (parameter names, interpolation names, fitting settings).
        """
        # Define parameter columns for fitting
        col_names_cnn_fit = [
            col
            for col in cat_fit.dtype.names
            if col.endswith("_cnn")
            and not col.startswith("x_")
            and not col.startswith("y_")
        ]
        col_names_mom_fit = ["se_mom_fwhm", "se_mom_win", "se_mom_e1", "se_mom_e2"]

        col_names_fit = col_names_cnn_fit + col_names_mom_fit

        # Convert to interpolation column names
        col_names_cnn_ipt = self._colnames_cnn_fit_to_ipt(col_names_cnn_fit)
        col_names_mom_ipt = self._colnames_mom_fit_to_ipt(col_names_mom_fit)
        col_names_ipt = col_names_cnn_ipt + col_names_mom_ipt

        # Add astrometry columns if requested
        if self.config.get("astrometry_errors", False):
            col_names_astrometry_fit = ["astrometry_diff_x", "astrometry_diff_y"]
            col_names_astrometry_ipt = [
                f"{col}_ipt" for col in col_names_astrometry_fit
            ]
            col_names_fit += col_names_astrometry_fit
            col_names_ipt += col_names_astrometry_ipt

            # Add derivative columns
            for ax in ["x", "y"]:
                col_names_ipt += [f"{col}_dd{ax}" for col in col_names_astrometry_ipt]

        # Setup regularization parameters
        ridge_alpha = self.config.get("psfmodel_ridge_alpha", 1e-6)
        if isinstance(ridge_alpha, dict):
            ridge_alpha = [ridge_alpha[p] for p in col_names_fit]
            LOGGER.info(f"Using parameter-specific ridge alpha: {ridge_alpha}")

        # Prepare fitting settings
        settings_fit = {
            "n_max_refit": self.config.get("n_max_refit", 10),
            "poly_order": self.config.get("poly_order", 5),
            "ridge_alpha": ridge_alpha,
            "polynomial_type": self.config.get("polynomial_type", "chebyshev"),
            "n_sigma_clip": self.config.get("n_sigma_clip", 3),
            "scale_pos": np.array(
                [
                    [
                        self.config["image_shape"][1] / 2,
                        self.config["image_shape"][1] / 2,
                    ],
                    [
                        self.config["image_shape"][0] / 2,
                        self.config["image_shape"][0] / 2,
                    ],
                ]
            ),
            "scale_par": np.array(
                [
                    [np.mean(cat_fit[p]), np.std(cat_fit[p], ddof=1)]
                    for p in col_names_fit
                ]
            ),
            "raise_underdetermined": self.config.get(
                "psfmodel_raise_underdetermined_error", True
            ),
        }
        # make sure that scale par has non-zero std and set them to 1
        if np.any(settings_fit["scale_par"][:, 1] == 0):
            LOGGER.warning("Some parameters have zero standard deviation, setting to 1")
            settings_fit["scale_par"][:, 1] = np.where(
                settings_fit["scale_par"][:, 1] == 0, 1, settings_fit["scale_par"][:, 1]
            )

        return col_names_fit, col_names_ipt, settings_fit

    def _fit_with_outlier_removal(
        self, cat_fit, col_names_fit, position_weights_fit, settings_fit
    ):
        """
        Fit polynomial model with iterative outlier removal.
        :param cat_fit: Catalog of stars selected for fitting.
        :param col_names_fit: Names of parameters to fit.
        :param position_weights_fit: Position weights for the stars.
        :param settings_fit: Fitting settings including polynomial order and
                            ridge alpha.
        :return: Tuple of (fitted regressor, clipped catalog, best ridge alpha).
        """

        LOGGER.info("Fitting polynomial model with outlier removal")

        cat_select = cat_fit.copy()
        position_weights_select = position_weights_fit.copy()
        n_stars = len(cat_select)

        # Get columns to use for outlier detection
        list_cols_use_outlier = self._get_outlier_removal_columns(col_names_fit)

        # Iterative fitting with outlier removal
        for i_fit in range(settings_fit["n_max_refit"]):
            LOGGER.debug(f"Fitting iteration {i_fit + 1}, n_stars: {n_stars}")

            # Fit model
            regressor = self._fit_single_model(
                cat_select,
                col_names_fit,
                position_weights_select,
                settings_fit,
            )

            # Check for outliers
            select_keep = self._identify_outliers(
                regressor,
                cat_select,
                col_names_fit,
                position_weights_select,
                settings_fit,
                list_cols_use_outlier,
            )

            LOGGER.debug(
                f"Outlier removal: keeping {np.sum(select_keep)}/"
                f"{len(select_keep)} stars"
            )

            # Update selection
            cat_select = cat_select[select_keep]
            position_weights_select = position_weights_select[select_keep]

            # Check for convergence
            if n_stars == len(cat_select):
                LOGGER.info("Outlier removal converged")
                break

            n_stars = len(cat_select)

        return regressor, cat_select

    def _fit_single_model(self, cat, col_names_fit, position_weights, settings_fit):
        """Fit a single polynomial model."""
        position_xy = np.stack((cat["X_IMAGE"] - 0.5, cat["Y_IMAGE"] - 0.5), axis=-1)
        position_par = np.stack([cat[p] for p in col_names_fit], axis=-1)

        position_xy_transformed = psf_utils.transform_forward(
            position_xy,
            settings_fit["scale_pos"],
        )
        position_xy_transformed_weights = np.concatenate(
            (position_xy_transformed, position_weights), axis=1
        )
        position_par_transformed = psf_utils.transform_forward(
            position_par, settings_fit["scale_par"]
        )

        # Create and fit regressor
        regressor = Regressor(
            poly_order=settings_fit["poly_order"],
            ridge_alpha=settings_fit["ridge_alpha"],
            polynomial_type=settings_fit["polynomial_type"],
            set_unseen_to_mean=True,
        )

        regressor.fit(position_xy_transformed_weights, position_par_transformed)
        return regressor

    def _identify_outliers(
        self,
        regressor,
        cat,
        col_names_fit,
        position_weights,
        settings_fit,
        list_cols_use_outlier,
    ):
        """Identify outliers based on model residuals."""
        # Get predictions
        position_xy = np.stack((cat["X_IMAGE"] - 0.5, cat["Y_IMAGE"] - 0.5), axis=-1)
        position_par = np.stack([cat[p] for p in col_names_fit], axis=-1)

        position_xy_transformed = psf_utils.transform_forward(
            position_xy, settings_fit["scale_pos"]
        )
        position_xy_transformed_weights = np.concatenate(
            (position_xy_transformed, position_weights), axis=1
        )
        position_par_transformed = psf_utils.transform_forward(
            position_par, settings_fit["scale_par"]
        )

        # Get model predictions
        position_par_pred = regressor.predict(position_xy_transformed_weights)

        # Apply outlier removal
        select_keep = star_sample_selection_cnn.remove_outliers(
            x=position_par_transformed,
            y=position_par_pred,
            n_sigma=settings_fit["n_sigma_clip"],
            list_cols_use=list_cols_use_outlier,
        )

        return select_keep

    def _handle_validation_stars(
        self,
        cat_fit,
        cat_clip,
        flags_fit,
        col_names_fit,
        position_weights_fit,
        settings_fit,
    ):
        """Handle validation star selection and final fitting."""
        fraction_validation = self.config.get("fraction_validation_stars", 0)

        # Select validation stars from the outlier-cleaned catalog
        indices_validation = psf_utils.select_validation_stars(
            len(cat_clip), fraction_validation
        )
        cat_validation = cat_clip[indices_validation]

        # Flag validation stars in the full fitting catalog
        select_val_outer = np.in1d(cat_fit["NUMBER"], cat_validation["NUMBER"])
        set_flag_bit(
            flags=flags_fit,
            select=select_val_outer,
            field=star_sample_selection_cnn.FLAGBIT_VALIDATION_STAR,
        )

        # Final fit excluding validation stars
        select_final = flags_fit == 0
        LOGGER.info(
            f"Final fit: {len(cat_validation)} validation stars reserved, "
            f"{np.sum(select_final)} stars for training"
        )

        # Fit on non-validation stars
        regressor = self._fit_single_model(
            cat_fit[select_final],
            col_names_fit,
            position_weights_fit[select_final],
            settings_fit,
        )

        # Test on validation stars
        validation_metrics = self._test_validation_stars(
            regressor,
            cat_validation,
            col_names_fit,
            position_weights_fit[select_val_outer],
            settings_fit,
        )
        LOGGER.info(f"Validation test completed: {validation_metrics}")

        return regressor

    def _test_validation_stars(
        self,
        regressor,
        cat_validation,
        col_names_fit,
        position_weights_validation,
        settings_fit,
    ):
        """
        Test the fitted model on validation stars and compute metrics.

        :param regressor: Fitted polynomial regressor.
        :param cat_validation: Catalog of validation stars.
        :param col_names_fit: Names of parameters used in fitting.
        :param position_weights_validation: Position weights for validation stars.
        :param settings_fit: Fitting settings including scale parameters.
        :return: Dictionary with validation metrics.
        """
        if len(cat_validation) == 0:
            LOGGER.warning("No validation stars available for testing")
            return {"n_validation": 0}

        # Transform validation data
        position_xy = np.stack(
            (cat_validation["X_IMAGE"] - 0.5, cat_validation["Y_IMAGE"] - 0.5), axis=-1
        )
        position_par_true = np.stack(
            [cat_validation[p] for p in col_names_fit], axis=-1
        )

        position_xy_transformed = psf_utils.transform_forward(
            position_xy, settings_fit["scale_pos"]
        )
        position_xy_transformed_weights = np.concatenate(
            (position_xy_transformed, position_weights_validation), axis=1
        )
        position_par_true_transformed = psf_utils.transform_forward(
            position_par_true, settings_fit["scale_par"]
        )

        # Get model predictions
        position_par_pred_transformed = regressor.predict(
            position_xy_transformed_weights
        )

        # Calculate residuals in transformed space
        residuals = position_par_pred_transformed - position_par_true_transformed

        # Compute validation metrics
        metrics = {
            "n_validation": len(cat_validation),
            "mae_mean": np.mean(np.abs(residuals)),  # Mean absolute error
            "rmse_mean": np.sqrt(np.mean(residuals**2)),  # Root mean square error
            "bias_mean": np.mean(residuals),  # Systematic bias
        }

        # Per-parameter metrics
        for i, param in enumerate(col_names_fit):
            if i < residuals.shape[1]:
                metrics[f"mae_{param}"] = np.mean(np.abs(residuals[:, i]))
                metrics[f"rmse_{param}"] = np.sqrt(np.mean(residuals[:, i] ** 2))
                metrics[f"bias_{param}"] = np.mean(residuals[:, i])

        return metrics

    def _get_outlier_removal_columns(self, par_fit):
        """Get columns to use for outlier removal."""
        list_cols = []
        for ip, par in enumerate(par_fit):
            if ("fwhm" in par) or ("e1" in par) or ("e2" in par):
                list_cols.append(ip)
        LOGGER.info(f"Using columns {list_cols} for outlier removal")
        return list_cols

    def _colnames_cnn_fit_to_ipt(self, col_names_cnn_fit):
        """Convert CNN fit column names to interpolation column names."""
        return [p[:-4] + "_ipt" for p in col_names_cnn_fit]

    def _colnames_mom_fit_to_ipt(self, col_names_mom_fit):
        """Convert moment fit column names to interpolation column names."""
        return [p.replace("se_mom", "psf_mom") + "_ipt" for p in col_names_mom_fit]
