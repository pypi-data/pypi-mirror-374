# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Wed Jul 23 2025

import os

from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin

from ufig.psf_estimation import PSFEstimationPipeline

LOGGER = logger.get_logger(__file__)


class Plugin(BasePlugin):
    def __call__(self):
        par = self.ctx.parameters

        psf_est = PSFEstimationPipeline(
            astrometry_errors=par.psfmodel_astrometry_errors,
            max_dist_gaia_arcsec=par.psfmodel_max_dist_gaia_arcsec,
            cnn_variance_type=par.psfmodel_cnn_variance_type,
            filepath_cnn_info=getattr(par, "filepath_cnn_info", None),
            poly_order=par.psfmodel_poly_order,
            polynomial_type=par.psfmodel_polynomial_type,
            star_mag_range=par.psfmodel_star_mag_range,
            min_n_exposures=par.psfmodel_min_n_exposures,
            n_sigma_clip=par.psfmodel_n_sigma_clip,
            fraction_validation_stars=par.psfmodel_fraction_validation_stars,
            save_star_cube=par.psfmodel_save_star_cube,
            psfmodel_raise_underdetermined_error=par.psfmodel_raise_underdetermined_error,
            star_stamp_shape=par.psfmodel_star_stamp_shape,
            sextractor_flags=par.psfmodel_sextractor_flags,
            flag_coadd_boundaries=par.psfmodel_flag_coadd_boundaries,
            moments_lim=par.psfmodel_moments_lim,
            beta_lim=par.psfmodel_beta_lim,
            fwhm_lim=par.psfmodel_fwhm_lim,
            ellipticity_lim=par.psfmodel_ellipticity_lim,
            flexion_lim=par.psfmodel_flexion_lim,
            kurtosis_lim=par.psfmodel_kurtosis_lim,
            n_max_refit=par.psfmodel_n_max_refit,
            psf_measurement_adjustment=par.psf_measurement_adjustment,
            psfmodel_corr_brighter_fatter=par.psfmodel_corr_brighter_fatter,
            psfmodel_ridge_alpha=par.psfmodel_ridge_alpha,
            image_shape=(par.size_y, par.size_x),
            precision=par.catalog_precision,
        )

        sexcat_name = None
        if os.path.exists(par.sextractor_catalog_name):
            sexcat_name = par.sextractor_catalog_name
        elif os.path.exists(par.sextractor_forced_photo_catalog_name):
            sexcat_name = par.sextractor_forced_photo_catalog_name

        psf_est.create_psf_model(
            filepath_image=par.image_name,
            filepath_sexcat=sexcat_name,
            filepath_sysmaps=par.filepath_sysmaps,
            filepath_gaia=par.filepath_gaia,
            filepath_cnn=par.filepath_cnn,
            filepath_out_model=par.filepath_psfmodel_output,
            filepath_out_cat=par.filepath_psfmodel_output_catalog,
        )

    def __str__(self):
        return "estimate PSF"
