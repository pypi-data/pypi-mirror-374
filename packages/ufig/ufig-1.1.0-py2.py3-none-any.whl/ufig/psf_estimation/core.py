# Copyright (C) 2024 ETH Zurich, Institute for Astronomy

"""
Core PSF estimation pipeline functionality.

This module contains the main PSF estimation pipeline that orchestrates
the complete process from image loading to model creation.
"""

from cosmic_toolbox import logger

from . import psf_utils

LOGGER = logger.get_logger(__file__)
ERR_VAL = 999.0


class PSFEstimationPipeline:
    """
    Main PSF estimation pipeline orchestrator.

    This class coordinates the complete PSF estimation process:
    1. Data loading and preparation
    2. Star selection and quality cuts
    3. CNN-based PSF parameter prediction
    4. Polynomial interpolation model fitting
    5. Model validation and output generation
    """

    def __init__(self, **kwargs):
        """
        Initialize the PSF estimation pipeline.

        Args:
            config (dict): Configuration parameters for the pipeline
        """
        self._setup_config(**kwargs)
        self.position_weights = None

    def create_psf_model(
        self,
        filepath_image,
        filepath_sexcat,
        filepath_sysmaps,
        filepath_gaia,
        filepath_cnn,
        filepath_out_model,
        filepath_out_cat=None,
    ):
        """
        Estimates the PSF of the image and saves all necessary files for a later image
        simulation.

        :param filepath_image: Path to the input image file to estimate the PSF from.
        :param filepath_sexcat: Path to the SExtractor catalog file of the image.
        :param filepath_sysmaps: Path to the systematics maps file.
        :param filepath_gaia: Path to the Gaia catalog file.
        :param filepath_cnn: Path to the pretrained CNN model
        :param filepath_out_model: Path to save the output PSF model file.
        :param filepath_cat_out: Path to save the enriched sextractor catalog,
            if None, the catalog at filepath_sexcat will be enriched
        """
        try:
            # Import dependent modules inside the method to avoid circular imports
            from .cnn_predictions import CNNPredictorPSF
            from .data_preparation import PSFDataPreparator
            from .polynomial_fitting import PolynomialPSFModel
            from .save_model import PSFSave

            # Step 1: Prepare input data
            LOGGER.info("Starting PSF model creation pipeline")
            data_prep = PSFDataPreparator(self.config)
            processed_data = data_prep.prepare_data(
                filepath_image=filepath_image,
                filepath_sexcat=filepath_sexcat,
                filepath_sysmaps=filepath_sysmaps,
                filepath_gaia=filepath_gaia,
            )

            # Step 2: Run CNN predictions
            # Filter to only include stars that passed CNN quality cuts
            select_cnn = processed_data["flags_gaia"] == 0
            cat_cnn_input = processed_data["cat_gaia"][select_cnn]
            cube_cnn_input = processed_data["cube_gaia"][select_cnn]
            self.config["image_shape"] = processed_data["image_shape"]

            LOGGER.info(
                f"Running CNN predictions on {len(cat_cnn_input)} selected stars"
            )
            predictor = CNNPredictorPSF(self.config)
            cnn_results = predictor.predict_psf_parameters(
                cat_gaia=cat_cnn_input,
                cube_gaia=cube_cnn_input,
                filepath_cnn=filepath_cnn,
            )

            # Step 3: Fit polynomial interpolation model
            # Extract position weights for the CNN-selected stars
            position_weights_cnn = processed_data["position_weights"][select_cnn]

            poly_model = PolynomialPSFModel(self.config)
            model_results = poly_model.fit_model(
                cat=cnn_results["cat_cnn"],
                position_weights=position_weights_cnn,
            )

            # Step 4: Generate predictions and save model
            io_handler = PSFSave(self.config)
            io_handler.save_psf_model(
                filepath_out=filepath_out_model,
                processed_data=processed_data,
                cnn_results=cnn_results,
                model_results=model_results,
                filepath_sysmaps=filepath_sysmaps,
                filepath_cat_out=filepath_out_cat,
            )

            LOGGER.info(f"PSF model successfully created: {filepath_out_model}")

        except Exception as e:
            LOGGER.error(f"PSF model creation failed: {str(e)}")
            self._handle_failure(filepath_out_model, filepath_out_cat)
            raise

    def _setup_config(self, **kwargs):
        """
        Creates a configuration dictionary for the pipeline from the kwargs provided.
        Additionally, sets default values if arguments are not provided.

        :param kwargs: Configuration parameters for the pipeline.
        """
        default_ridge_alpha = dict(
            psf_flux_ratio_cnn=2.10634454232412,
            psf_fwhm_cnn=0.12252798573828638,
            psf_e1_cnn=0.5080218046913018,
            psf_e2_cnn=0.5080218046913018,
            psf_f1_cnn=2.10634454232412,
            psf_f2_cnn=2.10634454232412,
            psf_g1_cnn=1.311133937421563,
            psf_g2_cnn=1.311133937421563,
            se_mom_fwhm=0.12,
            se_mom_win=0.12,
            se_mom_e1=0.51,
            se_mom_e2=0.51,
            astrometry_diff_x=0.5,
            astrometry_diff_y=0.5,
        )

        default_corr_bf = {
            "c1r": 0.0,
            "c1e1": 0.0,
            "c1e2": 0.0,
            "mag_ref": 22,
            "apply_to_galaxies": False,
        }
        user_corr_bf = kwargs.get("psfmodel_corr_brighter_fatter", {})
        if not isinstance(user_corr_bf, dict):
            raise ValueError("psfmodel_corr_brighter_fatter must be a dictionary")
        default_corr_bf.update(user_corr_bf)

        user_ridge_alpha = kwargs.get("psfmodel_ridge_alpha", {})
        if not isinstance(user_ridge_alpha, dict):
            raise ValueError("psfmodel_ridge_alpha must be a dictionary")
        default_ridge_alpha.update(user_ridge_alpha)

        self.config = {
            "astrometry_errors": kwargs.get("astrometry_errors", False),
            "max_dist_gaia_arcsec": kwargs.get("max_dist_gaia_arcsec", 0.1),
            "cnn_variance_type": kwargs.get("cnn_variance_type", "constant"),
            "filepath_cnn_info": kwargs.get("filepath_cnn_info"),
            "poly_order": kwargs.get("poly_order", 4),
            "polynomial_type": kwargs.get("polynomial_type", "chebyshev"),
            "star_mag_range": kwargs.get("star_mag_range", (18, 22)),
            "min_n_exposures": kwargs.get("min_n_exposures", 0),
            "n_sigma_clip": kwargs.get("n_sigma_clip", 3),
            "fraction_validation_stars": kwargs.get("fraction_validation_stars", 0.15),
            "save_star_cube": kwargs.get("save_star_cube", False),
            "psfmodel_raise_undetermined_error": kwargs.get(
                "psfmodel_raise_undetermined_error", False
            ),
            "star_stamp_shape": kwargs.get("star_stamp_shape", (19, 19)),
            "sextractor_flags": kwargs.get("sextractor_flags", [0, 16]),
            "flag_coadd_boundaries": kwargs.get("flag_coadd_boundaries", True),
            "moments_lim": kwargs.get("moments_lim", (-99, 99)),
            "beta_lim": kwargs.get("beta_lim", (1.5, 10)),
            "fwhm_lim": kwargs.get("fwhm_lim", (1, 10)),
            "ellipticity_lim": kwargs.get("ellipticity_lim", (-0.3, 0.3)),
            "flexion_lim": kwargs.get("flexion_lim", (-0.3, 0.3)),
            "kurtosis_lim": kwargs.get("kurtosis_lim", (-1, 1)),
            "n_max_refit": kwargs.get("n_max_refit", 10),
            "psf_measurement_adjustment": kwargs.get("psf_measurement_adjustment"),
            "psfmodel_corr_brighter_fatter": default_corr_bf,
            "psfmodel_ridge_alpha": default_ridge_alpha,
            "precision": kwargs.get("precision", float),
        }

    def _handle_failure(self, filepath_out, filepath_cat_out=None):
        """Handle pipeline failures by creating empty output files."""
        try:
            psf_utils.write_empty_output(
                filepath_out,
                filepath_cat_out=filepath_cat_out,
                save_star_cube=self.config.get("save_star_cube", False),
            )
        except Exception as cleanup_error:
            LOGGER.error(f"Failed to write empty output: {cleanup_error}")
