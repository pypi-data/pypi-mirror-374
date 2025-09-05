# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Mon Jul 21 2025


import h5py
import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger

from ufig.psf_estimation import psf_utils

LOGGER = logger.get_logger(__file__)
HDF5_COMPRESS = {"compression": "gzip", "compression_opts": 9, "shuffle": True}
ERR_VAL = 999.0


class PSFSave:
    """
    Saves PSF models and predictions to HDF5 format.

    This class manages:

    - Saving PSF models to HDF5 format
    - Writing output catalogs with PSF predictions
    - Storing diagnostic data and star cubes
    - Creating grid predictions for visualization
    """

    def __init__(self, config):
        """
        Initialize the PSF save utility with configuration parameters.
        """
        self.config = config

    def save_psf_model(
        self,
        filepath_out,
        processed_data,
        cnn_results,
        model_results,
        filepath_sysmaps=None,
        filepath_cat_out=None,
    ):
        """
        Save the PSF model and predictions to an HDF5 file.
        """
        LOGGER.info(f"Saving PSF model to: {filepath_out}")
        # Create the main HDF5 model file
        self._save_hdf5_model(filepath_out, filepath_sysmaps, model_results)

        # Generate and save predictions
        predictions = self._generate_predictions(
            filepath_out, processed_data, model_results
        )

        # Update HDF5 file with predictions
        self._save_predictions_to_hdf5(filepath_out, predictions)

        if filepath_cat_out is not None:
            self._save_catalog_output(
                filepath_cat_out,
                processed_data,
                cnn_results,
                model_results,
                predictions,
            )

        # Save star cube if requested
        if self.config.get("save_star_cube", False):
            self._save_star_cube(filepath_cat_out, cnn_results)

        LOGGER.info("PSF model saving complete")

    def _save_hdf5_model(self, filepath_out, filepath_sysmaps, model_results):
        """Save the core PSF model to HDF5 format."""
        LOGGER.debug("Creating HDF5 PSF model file")

        with h5py.File(filepath_out, mode="w") as fh5_out:
            # Copy systematics maps from input file
            if filepath_sysmaps is not None:
                self._copy_systematics_maps(fh5_out, filepath_sysmaps)

            # Save fitting settings
            settings_fit = model_results["settings_fit"]
            for key in settings_fit:
                at.replace_hdf5_dataset(
                    fobj=fh5_out, name=f"settings/{key}", data=settings_fit[key]
                )

            # Save polynomial model components
            regressor = model_results["regressor"]
            col_names_ipt = model_results["col_names_ipt"]

            at.replace_hdf5_dataset(
                fobj=fh5_out, name="par_names", data=col_names_ipt, **HDF5_COMPRESS
            )
            at.replace_hdf5_dataset(
                fobj=fh5_out,
                name="arr_pointings_polycoeffs",
                data=regressor.arr_pointings_polycoeffs,
                **HDF5_COMPRESS,
            )
            at.replace_hdf5_dataset(
                fobj=fh5_out,
                name="unseen_pointings",
                data=regressor.unseen_pointings,
                **HDF5_COMPRESS,
            )
            at.replace_hdf5_dataset(
                fobj=fh5_out,
                name="set_unseen_to_mean",
                data=regressor.set_unseen_to_mean,
            )

    def _copy_systematics_maps(self, fh5_out, filepath_sys):
        """Copy systematics maps from input file."""
        LOGGER.debug("Copying systematics maps")

        with h5py.File(filepath_sys, mode="r") as fh5_sys:
            for key in fh5_sys:
                try:
                    fh5_out.create_dataset(name=key, data=fh5_sys[key], **HDF5_COMPRESS)
                except Exception as err:
                    LOGGER.debug(
                        f"Failed to compress {key}: {err}, copying uncompressed"
                    )
                    fh5_sys.copy(key, fh5_out)

            # Copy pointing attributes
            if "map_pointings" in fh5_sys:
                fh5_out["map_pointings"].attrs["n_pointings"] = fh5_sys[
                    "map_pointings"
                ].attrs["n_pointings"]

    def _generate_predictions(self, filepath_out, processed_data, model_results):
        """Generate PSF predictions for various data sets."""
        LOGGER.debug("Generating PSF predictions")

        predictions = {}
        psfmodel_corr_brighter_fatter = self.config.get("psfmodel_corr_brighter_fatter")

        # Predict for training stars
        cat_fit = model_results["cat_fit"]
        predictions["star_train_psf"], _ = self._predict_for_catalog(
            cat_fit, filepath_out, psfmodel_corr_brighter_fatter
        )

        # Predict for full input catalog
        cat_full = processed_data.get("cat_original", processed_data["cat_gaia"])
        predictions["cat_psf"], predictions["n_exposures"] = self._predict_for_catalog(
            cat_full, filepath_out, psfmodel_corr_brighter_fatter
        )

        # Generate grid predictions
        predictions["grid_psf"] = self._generate_grid_predictions(
            filepath_out,
            processed_data["image_shape"],
        )

        # Add astrometric derivatives if requested
        if self.config.get("astrometry_errors", False):
            col_names_astrometry_ipt = [
                f"{col}_ipt" for col in ["astrometry_diff_x", "astrometry_diff_y"]
            ]
            predictions["star_train_psf"] = self._add_model_derivatives(
                predictions["star_train_psf"],
                filepath_out,
                col_names_astrometry_ipt,
                psfmodel_corr_brighter_fatter,
            )
            predictions["cat_psf"] = self._add_model_derivatives(
                predictions["cat_psf"],
                filepath_out,
                col_names_astrometry_ipt,
                psfmodel_corr_brighter_fatter,
            )

        return predictions

    def _predict_for_catalog(self, cat, filepath_out, psfmodel_corr_brighter_fatter):
        """Generate PSF predictions for a catalog."""
        # Import here to avoid circular dependencies
        from .psf_predictions import predict_psf_for_catalogue_storing

        return predict_psf_for_catalogue_storing(
            cat, filepath_out, psfmodel_corr_brighter_fatter
        )

    def _generate_grid_predictions(self, filepath_out, img_shape):
        """
        Generate PSF predictions on a regular grid.
        Brighter-fatter correction can not be applied here as it requires
        specific magnitudes and ellipticities which are not available for grid points.
        """
        LOGGER.debug("Generating grid predictions")

        # Create regular grid across image
        x_grid, y_grid = np.meshgrid(
            np.arange(0, img_shape[1], 100), np.arange(0, img_shape[0], 100)
        )
        x_grid = x_grid.ravel() + 0.5
        y_grid = y_grid.ravel() + 0.5

        # Create catalog for grid points
        grid_cat = np.empty(len(x_grid), dtype=at.get_dtype(["X_IMAGE", "Y_IMAGE"]))
        grid_cat["X_IMAGE"] = x_grid
        grid_cat["Y_IMAGE"] = y_grid

        # Generate predictions
        grid_psf, _ = self._predict_for_catalog(
            grid_cat, filepath_out, psfmodel_corr_brighter_fatter=None
        )

        return grid_psf

    def _add_model_derivatives(
        self, cat, filepath_out, cols, psfmodel_corr_brighter_fatter, delta=1e-2
    ):
        """Add spatial derivative predictions."""
        # Import here to avoid circular dependencies
        from .psf_predictions import get_model_derivatives

        return get_model_derivatives(
            cat, filepath_out, cols, psfmodel_corr_brighter_fatter, delta
        )

    def _save_predictions_to_hdf5(self, filepath_out, predictions):
        """Save predictions to the HDF5 model file."""
        LOGGER.debug("Saving predictions to HDF5 file")

        with h5py.File(filepath_out, mode="r+") as fh5_out:
            # Save full catalog predictions
            at.replace_hdf5_dataset(
                fobj=fh5_out,
                name="predictions",
                data=at.set_storing_dtypes(predictions["cat_psf"]),
                **HDF5_COMPRESS,
            )

            # Save training star data and predictions
            if "star_train_psf" in predictions:
                data = predictions["star_train_psf"]

                at.replace_hdf5_dataset(
                    fobj=fh5_out,
                    name="star_train_prediction",
                    data=at.set_storing_dtypes(data),
                    **HDF5_COMPRESS,
                )

            # Save grid predictions
            at.replace_hdf5_dataset(
                fobj=fh5_out,
                name="grid_psf",
                data=at.set_storing_dtypes(predictions["grid_psf"]),
                **HDF5_COMPRESS,
            )

    def _save_catalog_output(
        self, filepath_cat_out, processed_data, cnn_results, model_results, predictions
    ):
        """Save catalog output with PSF predictions."""
        LOGGER.debug(f"Saving catalog output: {filepath_cat_out}")

        # Get original catalog
        cat = processed_data.get("cat_original", processed_data["cat_gaia"])

        # Define output columns
        col_names_cnn_fit = [
            col for col in model_results["col_names_fit"] if col.endswith("_cnn")
        ]
        col_names_ipt = model_results["col_names_ipt"]

        cols_new = (
            col_names_cnn_fit
            + col_names_ipt
            + [
                "FLAGS_STARS:i4",
                "N_EXPOSURES:i2",
                "gaia_ra_match",
                "gaia_dec_match",
                "gaia_id_match:i8",
            ]
        )

        # Create output catalog
        cat_save_psf = at.ensure_cols(cat, names=cols_new)

        # Fill with predictions and metadata
        self._fill_catalog_output(
            cat_save_psf, processed_data, cnn_results, model_results, predictions
        )

        # Convert precision if requested
        precision = self.config.get("precision", float)
        if precision == np.float32:
            cat_save_psf = at.rec_float64_to_float32(cat_save_psf)
            LOGGER.info("Converted catalog to float32 precision")

        # Save catalog
        at.save_hdf_cols(filepath_cat_out, cat_save_psf)
        LOGGER.info(f"Catalog saved with {len(cat_save_psf)} sources")

    def _fill_catalog_output(
        self, cat_save_psf, processed_data, cnn_results, model_results, predictions
    ):
        """Fill catalog output with predictions and metadata."""
        # Get masks and data
        cat_gaia = processed_data.get("cat_gaia", None)
        flags_gaia = processed_data.get("flags_gaia", None)
        flags_all = processed_data.get("flags_all", None)
        cat_cnn = cnn_results.get("cat_cnn", None)
        flags_cnn = cnn_results.get("flags_cnn", None)
        select_gaia = flags_gaia == 0
        select_cnn = flags_cnn == 0
        select_all = flags_all == 0

        # Fill interpolated PSF parameters
        col_names_ipt = model_results["col_names_ipt"]
        for col_name in col_names_ipt:
            if col_name in predictions["cat_psf"].dtype.names:
                cat_save_psf[col_name] = predictions["cat_psf"][col_name]

        # Fill CNN predicted parameters for stars used in fitting
        if cat_cnn is not None and flags_cnn is not None:
            col_names_cnn_fit = [
                col for col in model_results["col_names_fit"] if col.endswith("_cnn")
            ]
            for col_name in col_names_cnn_fit:
                if col_name in cat_cnn.dtype.names:
                    # Initialize with ERR_VAL
                    cat_save_psf[col_name] = ERR_VAL

                    # Fill values for stars that were used in CNN
                    if flags_gaia is not None:
                        # Map from CNN indices to full catalog indices
                        idx_full = np.where(select_gaia)[0][select_cnn]
                        cat_save_psf[col_name][idx_full] = cat_cnn[col_name][select_cnn]

        # Fill GAIA match information
        if cat_gaia is not None and flags_gaia is not None:
            cat_save_psf["gaia_ra_match"][select_all] = cat_gaia["gaia_ra_match"]
            cat_save_psf["gaia_dec_match"][select_all] = cat_gaia["gaia_dec_match"]
            cat_save_psf["gaia_id_match"][select_all] = cat_gaia["gaia_id_match"]
        else:
            cat_save_psf["FLAGS_STARS"] = 0

        # Fill exposure information
        cat_save_psf["N_EXPOSURES"] = predictions.get("n_exposures", 1)

    def _save_star_cube(self, filepath_cat_out, cnn_results):
        """Save star stamp cube for detailed analysis."""
        LOGGER.debug("Saving star cube")

        # Check if we have the necessary data
        if "cube_cnn" not in cnn_results:
            LOGGER.warning("No cube data to save")
            return

        cube = cnn_results["cube_cnn"]
        cat_cnn = cnn_results["cat_cnn"]

        psf_utils.write_star_cube(
            star_cube=cube, cat=cat_cnn, filepath_cat_out=filepath_cat_out
        )
