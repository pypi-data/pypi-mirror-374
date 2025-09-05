# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Mon Jul 21 2025


import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger

from . import cnn_util, psf_utils, star_sample_selection_cnn

LOGGER = logger.get_logger(__file__)
ERR_VAL = 999.0


class CNNPredictorPSF:
    """
    Handles CNN-based PSF parameter prediction.

    This class manages:
    - CNN model loading and configuration
    - Batch prediction on star stamp images
    - Post-processing and quality assessment of predictions
    - Application of systematic corrections
    """

    def __init__(self, config):
        """
        Initialize the PSF predictor with configuration parameters.

        :param config: Configuration dictionary with parameters for PSF prediction.
        """
        self.config = config
        self.cnn_pred = None

    def predict_psf_parameters(self, cat_gaia, cube_gaia, filepath_cnn):
        """
        Predict PSF parameters for a catalog of stars using a CNN model.

        :param cat_gaia: Input catalog of stars with GAIA matching.
        :param cube_gaia: Cube of star stamp images.
        :param filepath_cnn: Path to the CNN model file.
        :return: Dictionary with predicted PSF parameters and quality flags.
        """

        LOGGER.info("Starting CNN PSF parameter prediction")

        # Load CNN model
        self._load_cnn_model(filepath_cnn)

        # Select stars that pass quality cuts for CNN processing
        cat_cnn = cat_gaia
        cube_cnn = cube_gaia
        flags_cnn = np.zeros(len(cat_cnn), dtype=np.int32)

        # Run CNN predictions
        cnn_predictions = self._run_cnn_inference(cube_cnn)

        # Process and merge predictions
        cat_cnn = self._process_predictions(cat_cnn, cnn_predictions)

        # Apply corrections and additional quality cuts
        cat_cnn, flags_cnn = self._apply_corrections_and_cuts(cat_cnn, flags_cnn)

        LOGGER.info(
            f"CNN prediction complete. Valid predictions: {np.sum(flags_cnn == 0)}"
        )

        return {
            "cat_cnn": cat_cnn,
            "flags_cnn": flags_cnn,
            "cube_cnn": cube_cnn,
            "col_names_cnn": self.cnn_pred.config["param_names"],
        }

    def _load_cnn_model(self, filepath_cnn):
        """Load the CNN model for PSF parameter prediction."""
        LOGGER.debug(f"Loading CNN model: {filepath_cnn}")
        self.cnn_pred = cnn_util.CNNPredictor(filepath_cnn)
        LOGGER.info(
            f"CNN model loaded. Parameters: {self.cnn_pred.config['param_names']}"
        )

    def _run_cnn_inference(self, cube_cnn):
        """
        Run CNN inference on the star stamp images.

        :param cube_cnn: Cube of star stamp images.
        :return: Array of predicted PSF parameters.
        """
        LOGGER.info(f"Running CNN inference on {len(cube_cnn)} stars")

        # Run CNN prediction in batches
        cnn_predictions = self.cnn_pred(cube_cnn, batchsize=500)

        LOGGER.debug(f"CNN inference complete. Output shape: {cnn_predictions.shape}")

        return cnn_predictions

    def _process_predictions(self, cat_cnn, cnn_predictions):
        """
        Process and merge CNN predictions with catalog.

        :param cat_cnn: Catalog of stars with GAIA matching.
        :param cnn_predictions: Array of predicted PSF parameters.
        :return: Updated catalog with CNN predictions.
        """
        LOGGER.debug("Processing CNN predictions")

        # Get parameter names and create CNN column names
        col_names = self.cnn_pred.config["param_names"]
        col_names_cnn = [name + "_cnn" for name in col_names]

        # Convert predictions to structured array
        cnn_predictions_structured = np.core.records.fromarrays(
            cnn_predictions.T, names=",".join(col_names_cnn)
        )

        # Remove any existing CNN columns to avoid conflicts
        cat_cnn = at.delete_columns(cat_cnn, cnn_predictions_structured.dtype.names)

        # Merge predictions with catalog
        cat_cnn = np.lib.recfunctions.merge_arrays(
            (cat_cnn, cnn_predictions_structured), flatten=True
        )

        # Apply post-processing (unit conversions, etc.)
        psf_utils.postprocess_catalog(cat_cnn)

        return cat_cnn

    def _apply_corrections_and_cuts(self, cat_cnn, flags_cnn):
        """
        Apply corrections and quality cuts to the CNN predictions.

        :param cat_cnn: Catalog of stars with CNN predictions.
        :param flags_cnn: Flags for the CNN predictions.
        :return: Updated catalog and flags after corrections and cuts.
        """
        LOGGER.debug("Applying corrections and quality cuts")

        # Apply PSF measurement adjustments if specified
        psf_measurement_adjustment = self.config.get("psf_measurement_adjustment")
        if psf_measurement_adjustment is not None:
            LOGGER.info("Applying PSF measurement adjustments")
            psf_utils.adjust_psf_measurements(cat_cnn, psf_measurement_adjustment)

        # Apply Brighter-Fatter correction if specified
        psfmodel_corr_brighter_fatter = self.config.get("psfmodel_corr_brighter_fatter")
        if psfmodel_corr_brighter_fatter is not None:
            LOGGER.info("Applying Brighter-Fatter correction")
            psf_utils.apply_brighter_fatter_correction(
                cat_cnn, psfmodel_corr_brighter_fatter
            )

        # Apply CNN prediction quality cuts
        flags_cnn = star_sample_selection_cnn.select_cnn_predictions(
            flags_cnn,
            cat_cnn,
            beta_lim=self.config.get("beta_lim", (1.5, 10)),
            fwhm_lim=self.config.get("fwhm_lim", (1, 10)),
            ellipticity_lim=self.config.get("ellipticity_lim", (-0.3, 0.3)),
            flexion_lim=self.config.get("flexion_lim", (-0.3, 0.3)),
            kurtosis_lim=self.config.get("kurtosis_lim", (-1, 1)),
        )

        n_good = np.sum(flags_cnn == 0)
        LOGGER.info(f"After corrections and cuts: {n_good} valid predictions")

        return cat_cnn, flags_cnn
