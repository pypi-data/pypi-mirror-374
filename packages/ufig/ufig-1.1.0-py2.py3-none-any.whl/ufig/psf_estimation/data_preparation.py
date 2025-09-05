# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Mon Jul 21 2025


import h5py
import numpy as np
from astropy.io import fits
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger

from ufig.array_util import set_flag_bit

from ..se_moment_util import get_se_cols
from . import psf_utils, star_sample_selection_cnn

LOGGER = logger.get_logger(__file__)


class PSFDataPreparator:
    """
    Handles data preparation for PSF estimation.

    This class is responsible for:
    - Loading and preprocessing image data
    - GAIA catalog matching for stellar sample selection
    - Initial quality cuts and flag management
    - Preparation of data structures for CNN processing
    """

    def __init__(self, config):
        """
        Initialize the data preparator with configuration parameters.

        :param config: Configuration dictionary with parameters for data preparation.
        """
        self.config = config

    def prepare_data(
        self,
        filepath_image,
        filepath_sexcat,
        filepath_sysmaps,
        filepath_gaia,
    ):
        """
        Prepare the data for the PSF estimation. This includes
        - loading the image and the SExtractor catalog,
        - matching with GAIA catalog,
        - applying initial quality cuts.

        :param filepath_image: Path to the input image file to estimate the PSF from.
        :param filepath_sexcat: Path to the SExtractor catalog file of the image.
        :param filepath_sysmaps: Path to the systematics maps file.
        :param filepath_gaia: Path to the GAIA catalog file.
        :param config: Configuration dictionary with parameters for data preparation.
        """
        LOGGER.info("Starting data preparation")

        # Load image data and catalog
        img = self._load_image(filepath_image)
        cat = at.load_hdf_cols(filepath_sexcat)

        # Match with GAIA and apply initial cuts
        cat_gaia, flags_all = self._select_gaia_stars(
            cat, filepath_gaia, filepath_image
        )

        # Get exposure information and position weights
        position_weights, pointings_maps = self._get_exposure_info(
            cat_gaia, filepath_sysmaps
        )

        # Apply moment measurements and quality cuts for CNN
        cat_gaia, flags_gaia, cube_gaia = self._prepare_cnn_sample(
            cat_gaia, img, position_weights, pointings_maps
        )

        LOGGER.info(
            f"Data preparation complete. Stars for CNN: {np.sum(flags_gaia == 0)}"
        )

        return {
            "cat_original": cat,  # Full SExtractor catalog for PSF predictions
            "cat_gaia": cat_gaia,
            "flags_all": flags_all,
            "flags_gaia": flags_gaia,
            "cube_gaia": cube_gaia,
            "position_weights": position_weights,
            "image_shape": img.shape,
        }

    def _load_image(self, filepath_image):
        """Load astronomical image from FITS file."""
        LOGGER.debug(f"Loading image: {filepath_image}")
        img = np.array(fits.getdata(filepath_image), dtype=float)
        LOGGER.info(f"Loaded image with shape: {img.shape}")
        return img

    def _select_gaia_stars(self, cat, filepath_gaia, filepath_image):
        """
        Select the objects from the SExtractor catalog that are in the GAIA catalog.

        :param cat: SExtractor catalog data.
        :param filepath_gaia: Path to the GAIA catalog file.
        :param filepath_image: Path to the image file for coordinate conversion.
        :param config: Configuration dictionary with parameters for data preparation.
        """
        LOGGER.info("Matching with GAIA catalog")

        # Initialize flags for all sources
        flags_all = np.zeros(len(cat), dtype=np.int32)

        # Cross-match with GAIA
        cat = star_sample_selection_cnn.get_gaia_match(
            cat, filepath_gaia, self.config["max_dist_gaia_arcsec"]
        )

        # Convert GAIA coordinates to image pixels
        cat = star_sample_selection_cnn.get_gaia_image_coords(filepath_image, cat)

        # Add astrometric differences if requested
        if self.config.get("astrometry_errors", False):
            cat = self._add_astrometry_diff(cat)

        # Select GAIA matches
        select_gaia = cat["match_gaia"].astype(bool)

        # Flag non-GAIA sources
        set_flag_bit(
            flags=flags_all,
            select=~select_gaia,
            field=star_sample_selection_cnn.FLAGBIT_GAIA,
        )

        LOGGER.info(
            f"GAIA matching: {np.count_nonzero(select_gaia)}/{len(flags_all)} "
            f"sources matched"
        )

        # Keep only GAIA-matched sources
        cat_gaia = cat[select_gaia]

        return cat_gaia, flags_all

    def _get_exposure_info(self, cat_gaia, filepath_sys):
        """
        Get exposure information and calculate position weights.

        Returns:
            tuple: (position_weights, pointings_maps)
        """
        LOGGER.debug("Getting exposure information")

        with h5py.File(filepath_sys, mode="r") as fh5_maps:
            pointings_maps = fh5_maps["map_pointings"]

            # Calculate position weights based on exposure coverage
            position_weights = psf_utils.get_position_weights(
                x=cat_gaia["XWIN_IMAGE"] - 0.5,  # Convert to 0-indexed
                y=cat_gaia["YWIN_IMAGE"] - 0.5,
                pointings_maps=pointings_maps,
            )

            # Copy pointing maps data for later use
            pointings_maps_data = pointings_maps[...]

        return position_weights, pointings_maps_data

    def _prepare_cnn_sample(self, cat_gaia, img, position_weights, pointings_maps):
        """
        Prepare the sample for CNN processing. Enrich catalog with moment measurements
        and apply quality cuts.

        :param cat_gaia: Catalog with GAIA matches.
        :param img: Image data for cutout extraction.
        :param position_weights: Position weights for each star.
        :param pointings_maps: Pointing maps for exposure coverage.

        """
        LOGGER.debug("Preparing CNN sample")

        # Add moment measurements
        cat_gaia = get_se_cols(cat_gaia)

        # Apply quality cuts and extract star stamps
        flags_gaia, cube_gaia = star_sample_selection_cnn.get_stars_for_cnn(
            cat=cat_gaia,
            image=img,
            star_stamp_shape=self.config.get("star_stamp_shape", (19, 19)),
            pointings_maps=pointings_maps,
            position_weights=position_weights,
            star_mag_range=self.config.get("star_mag_range", (18, 22)),
            min_n_exposures=self.config.get("min_n_exposures", 1),
            sextractor_flags=self.config.get("sextractor_flags", [0, 16]),
            flag_coadd_boundaries=self.config.get("flag_coadd_boundaries", True),
            moments_lim=self.config.get("moments_lim", (-99, 99)),
        )

        return cat_gaia, flags_gaia, cube_gaia

    def _add_astrometry_diff(self, cat):
        """
        Add astrometric difference measurements.
        """
        cat = at.ensure_cols(cat, names=["astrometry_diff_x", "astrometry_diff_y"])
        cat["astrometry_diff_x"] = cat["X_IMAGE"] - cat["gaia_x_match"]
        cat["astrometry_diff_y"] = cat["Y_IMAGE"] - cat["gaia_y_match"]
        return cat
