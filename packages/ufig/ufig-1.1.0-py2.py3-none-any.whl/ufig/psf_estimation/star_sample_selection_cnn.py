# Copyright (c) 2017 ETH Zurich, Cosmology Research Group
"""
Created on Aug 03, 2017
@author: Joerg Herbel
"""

import h5py
import numpy as np
import scipy.stats
from astropy import wcs
from astropy.io import fits
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger
from sklearn.neighbors import BallTree

from ufig.array_util import check_flag_bit, set_flag_bit
from ufig.plugins import add_generic_stamp_flags
from ufig.psf_estimation import psf_utils
from ufig.psf_estimation.cutouts_utils import get_cutouts

LOGGER = logger.get_logger(__file__)

FLAGBIT_GAIA = 1
FLAGBIT_MAG = 2
FLAGBIT_N_EXP = 3
FLAGBIT_SOURCEEXTRACTOR_FLAGS = 4
FLAGBIT_POSITION_WEIGHTS = 5
FLAGBIT_IMAGE_BOUNDARY = 6
FLAGBIT_COADD_BOUNDARY = 7
FLAGBIT_MAX_FLUX_CENTERED = 8
FLAGBIT_BETA = 9
FLAGBIT_FWHM = 10
FLAGBIT_ELLIPTICITY = 11
FLAGBIT_FLEXION = 12
FLAGBIT_KURTOSIS = 13
FLAGBIT_OUTLIER = 14
FLAGBIT_VALIDATION_STAR = 15
FLAGBIT_MOM_ERROR = 16
FLAGBIT_SYSMAP_DELTA_WEIGHT = 17
FLAGBIT_NEARBY_BRIGHT_STAR = 18
FLAGBIT_SURVEY_MASK = 19


def inlims(x, lims):
    """
    Check if values in x are within the specified limits.

    :param x: Array of values to check.
    :param lims: Tuple of (min, max) limits.
    :return: Boolean array indicating whether each value is within the limits.
    """

    return (x > lims[0]) & (x < lims[1])


def get_gaia_match(cat_in, filepath_gaia, max_dist_arcsec):
    """
    Match the objects from the SExtractor catalog with the GAIA catalog based on their
    sky coordinates with a maximum distance defined by max_dist_arcsec.
    The function returns a catalog with additional columns to flag the matches and
    the matched RA/Dec coordinates from GAIA.

    :param cat_in: SExtractor catalog data.
    :param filepath_gaia: Path to the GAIA catalog file.
    :param max_dist_arcsec: Maximum distance in arcseconds for matching.
    :return: Catalog enriched with GAIA matching information
    """

    with h5py.File(filepath_gaia, mode="r") as fh5:
        cat_gaia = np.array(fh5["data"])
        LOGGER.info(f"found {len(cat_gaia)} stars in the Gaia catalogue")

    match_vector = get_match_vector(cat_in, cat_gaia, max_dist_arcsec)

    cat_out = at.ensure_cols(
        cat_in,
        names=["match_gaia:i2", "gaia_ra_match", "gaia_dec_match", "gaia_id_match:i8"],
    )
    cat_out["gaia_id_match"] = match_vector[3]

    cat_out["match_gaia"] = match_vector[0]
    cat_out["gaia_ra_match"] = match_vector[1]
    cat_out["gaia_dec_match"] = match_vector[2]

    return cat_out


def get_gaia_image_coords(filepath_image, cat):
    """
    Convert GAIA coordinates (RA/Dec) to image pixel coordinates.

    :param filepath_image: Path to the image file for coordinate conversion.
    :param cat: Catalog containing GAIA coordinates.
    :return: Catalog with additional columns for GAIA pixel coordinates.
    """
    try:
        header = fits.getheader(filepath_image, ext=1)
    except IndexError:
        header = fits.getheader(filepath_image, ext=0)
    wcsobj = wcs.WCS(header)
    skycoords = np.vstack([cat["gaia_ra_match"], cat["gaia_dec_match"]]).T
    pixelcoords = wcsobj.all_world2pix(skycoords, 1)
    cat = at.ensure_cols(cat, names=["gaia_x_match", "gaia_y_match"])
    cat["gaia_x_match"] = pixelcoords[:, 0]
    cat["gaia_y_match"] = pixelcoords[:, 1]
    select = np.isnan(cat["gaia_x_match"])
    cat["gaia_x_match"][select] = cat["gaia_ra_match"][select]  # unmatched
    cat["gaia_y_match"][select] = cat["gaia_dec_match"][select]  # unmatched
    return cat


def cut_magnitude(cat, mag_min, mag_max):
    """
    Select stars based on their magnitude.

    :param cat: Catalog with SExtractor measurements.
    :param mag_min: Minimum magnitude for selection.
    :param mag_max: Maximum magnitude for selection.
    :return: Boolean array indicating which stars are within the magnitude range.
    """
    select = (cat["MAG_AUTO"] > mag_min) & (cat["MAG_AUTO"] < mag_max)
    return select


def cut_n_exp(weights, n_exp_min):
    """
    Select stars based on the number of exposures they are covered by.

    :param weights: Position weights for each star.
    :param n_exp_min: Minimum number of exposures required for selection.
    :return: Boolean array indicating which stars have enough exposures.
    """
    n_exp = psf_utils.position_weights_to_nexp(weights)
    select = n_exp >= n_exp_min
    return select


def cut_sextractor_flag(cat, flags=None):
    """
    Select stars based on SExtractor flags.

    :param cat: Catalog with SExtractor measurements.
    :param flags: list of flags to consider, if None, all flags are considered.
    :return: Boolean array indicating which stars have acceptable SExtractor flags.
    """
    if flags is None:
        return np.ones(len(cat), dtype=bool)
    if isinstance(flags, int):
        select = cat["FLAGS"] == flags
    elif isinstance(flags, (list, tuple, np.ndarray)):
        select = np.zeros(len(cat), dtype=bool)
        for flag in flags:
            select |= cat["FLAGS"] == flag
    else:
        raise ValueError("flags must be an int, list, tuple or numpy array")
    return select


def cut_position_weights(weights):
    """
    Select only stars with finite weights

    :param weights: Position weights for each star.
    :return: Boolean array indicating which stars have valid position weights.
    """
    select = np.all(np.isfinite(weights), axis=1)
    return select


def cut_nearby_bright_star(cat):
    if "FLAGS_STAMP" in cat.dtype.names:
        select = ~check_flag_bit(
            cat["FLAGS_STAMP"], add_generic_stamp_flags.FLAGBIT_NEARBY_BRIGHT_STAR
        )
    else:
        LOGGER.warning(
            "column FLAGS_STAMP not found, not cutting on FLAGBIT_NEARBY_BRIGHT_STAR"
        )
        select = np.ones(len(cat), dtype=bool)

    return select


def cut_sysmaps_delta_weight(cat):
    if "FLAGS_STAMP" in cat.dtype.names:
        select = ~check_flag_bit(
            cat["FLAGS_STAMP"], add_generic_stamp_flags.FLAGBIT_SYSMAP_DELTA_WEIGHT
        )
    else:
        LOGGER.warning(
            "column FLAGS_STAMP not found, not cutting on FLAGBIT_SYSMAP_DELTA_WEIGHT"
        )
        select = np.ones(len(cat), dtype=bool)

    return select


def cut_sysmaps_survey_mask(cat):
    if "FLAGS_STAMP" in cat.dtype.names:
        select = ~check_flag_bit(
            cat["FLAGS_STAMP"], add_generic_stamp_flags.FLAGBIT_SURVEY_MASK
        )
    else:
        LOGGER.warning(
            "column FLAGS_STAMP not found, not cutting on FLAGBIT_SURVEY_MASK"
        )
        select = np.ones(len(cat), dtype=bool)

    return select


def cut_boundaries(cat, image, pointings_maps, star_stamp_shape):
    """
    Checks the position of the star stamps within the image and returns boolean arrays
    indicating whether the stars are within the image boundaries, coadd boundaries and
    whether the cutout is centered on the maximum flux pixel.

    :param cat: Catalog with SExtractor measurements.
    :param image: Image data for cutout extraction.
    :param pointings_maps: Pointing maps for exposure coverage.
    :param star_stamp_shape: Shape of the cutout stamps for stars.
    """
    (
        cube,
        select_image_boundary,
        select_coadd_boundary,
        select_max_flux_centered,
    ) = get_cutouts(
        cat["XPEAK_IMAGE"] - 1,
        cat["YPEAK_IMAGE"] - 1,
        image,
        pointings_maps,
        star_stamp_shape,
    )
    return select_image_boundary, select_coadd_boundary, select_max_flux_centered, cube


def set_flag_bit_and_log(select, flags, flagbit, msg):
    set_flag_bit(flags=flags, select=select, field=flagbit)
    LOGGER.info(
        f"star cuts: found {np.count_nonzero(~select)}/{len(flags)} {msg}, "
        f"current n_star={np.count_nonzero(flags == 0)}"
    )


def get_stars_for_cnn(
    cat,
    image,
    star_stamp_shape,
    pointings_maps,
    position_weights,
    star_mag_range=(18, 22),
    min_n_exposures=1,
    sextractor_flags=None,
    flag_coadd_boundaries=False,
    moments_lim=(-99, 99),
):
    """
    Select the stars for the CNN model based on various quality cuts.

    :param cat: Catalog with SExtractor measurements.
    :param image: Image data for cutout extraction.
    :param star_stamp_shape: Shape of the cutout stamps for stars.
    :param pointings_maps: Pointing maps for exposure coverage.
    :param position_weights: Position weights for each star.
    :param star_mag_range: Tuple defining the magnitude range for star selection.
    :param min_n_exposures: Minimum number of exposures required for a star to be
                           selected.
    :param sextractor_flags: SExtractor flags to consider for quality cuts.
    :return: flags, cube: Flags indicating the quality of each star and the
        cutout cube of selected stars.
    """

    flags = np.zeros(len(cat), dtype=np.uint32)

    # Magnitude
    select_mag = cut_magnitude(cat, star_mag_range[0], star_mag_range[1])
    set_flag_bit_and_log(
        ~select_mag, flags, FLAGBIT_MAG, msg="stars in accepted mag range"
    )

    # Number of exposures
    select_n_exp = cut_n_exp(position_weights, min_n_exposures)
    set_flag_bit_and_log(
        ~select_n_exp,
        flags,
        FLAGBIT_N_EXP,
        msg="stars with accepted number of exposures",
    )

    # SExtractor flags
    if sextractor_flags is None:
        sextractor_flags = [0, 16]
    select_sourceextractor_flags = cut_sextractor_flag(cat, sextractor_flags)
    set_flag_bit_and_log(
        ~select_sourceextractor_flags,
        flags,
        FLAGBIT_SOURCEEXTRACTOR_FLAGS,
        msg="stars with accepted SourceExtractor flags",
    )

    # NaN weights
    select_position_weights = cut_position_weights(position_weights)
    set_flag_bit_and_log(
        ~select_position_weights,
        flags,
        FLAGBIT_POSITION_WEIGHTS,
        msg="stars without any NaN position weights",
    )

    # Get cutouts
    (
        select_image_boundary,
        select_coadd_boundary,
        select_max_flux_centered,
        cube,
    ) = cut_boundaries(cat, image, pointings_maps, star_stamp_shape)
    set_flag_bit_and_log(
        ~select_image_boundary,
        flags,
        FLAGBIT_IMAGE_BOUNDARY,
        msg="stars far enough from image boundary",
    )
    if flag_coadd_boundaries:
        set_flag_bit_and_log(
            ~select_coadd_boundary,
            flags,
            FLAGBIT_COADD_BOUNDARY,
            msg="stars far enough from coadd boundaries",
        )
    set_flag_bit_and_log(
        ~select_max_flux_centered,
        flags,
        FLAGBIT_MAX_FLUX_CENTERED,
        msg="stars centered on maximum flux",
    )

    select_moments = cut_moments(cat, moments_lim)
    set_flag_bit_and_log(
        ~select_moments, flags, FLAGBIT_MOM_ERROR, msg="stars with good moments"
    )

    select_ok_sysmap_delta_weight = cut_sysmaps_delta_weight(cat)
    set_flag_bit_and_log(
        ~select_ok_sysmap_delta_weight,
        flags,
        FLAGBIT_SYSMAP_DELTA_WEIGHT,
        msg="stars with matching sysmap delta weight",
    )

    select_no_bright_star = cut_nearby_bright_star(cat)
    set_flag_bit_and_log(
        ~select_no_bright_star,
        flags,
        FLAGBIT_NEARBY_BRIGHT_STAR,
        msg="stars far enough from bright stars",
    )

    select_ok_survey_mask = cut_sysmaps_survey_mask(cat)
    set_flag_bit_and_log(
        ~select_ok_survey_mask,
        flags,
        FLAGBIT_SURVEY_MASK,
        msg="stars with OK survey mask",
    )

    return flags, cube


def beta_cut(beta, beta_lim=(1.5, 10)):
    """
    Select stars based on their beta parameter.

    :param beta: Beta parameter for each star.
    :param beta_lim: Tuple defining the limits for beta selection.
    :return: Boolean array indicating which stars have beta within the specified limits.
    """
    select = inlims(beta, beta_lim)
    return select


def fwhm_cut(fwhm, fwhm_lim=(1, 10)):
    """
    Select stars based on their FWHM parameter.

    :param fwhm: FWHM parameter for each star.
    :param fwhm_lim: Tuple defining the limits for FWHM selection.
    :return: Boolean array indicating which stars have FWHM within the specified limits.
    """
    select = inlims(fwhm, fwhm_lim)
    return select


def ellipticity_cut(e1, e2, ellipticity_lim=(-0.3, 0.3)):
    """
    Select stars based on their ellipticity parameters.

    :param e1: First ellipticity component for each star.
    :param e2: Second ellipticity component for each star.
    :param ellipticity_lim: Tuple defining the limits for ellipticity selection.
    :return: Boolean array indicating which stars have ellipticity within the
             specified limits.
    """
    select = inlims(e1, ellipticity_lim) & inlims(e2, ellipticity_lim)
    return select


def flexion_cut(f1, f2, g1, g2, flexion_lim=(-0.3, 0.3)):
    """
    Select stars based on their flexion parameters.

    :param f1: First flexion component for each star.
    :param f2: Second flexion component for each star.
    :param g1: Third flexion component for each star.
    :param g2: Fourth flexion component for each star.
    :param flexion_lim: Tuple defining the limits for flexion selection.
    :return: Boolean array indicating which stars have flexion within the
             specified limits.
    """
    select = (
        inlims(f1, flexion_lim)
        & inlims(f2, flexion_lim)
        & inlims(g1, flexion_lim)
        & inlims(g2, flexion_lim)
    )
    return select


def kurtosis_cut(kurtosis, kurtosis_lim=(-1, 1)):
    """
    Select stars based on their kurtosis parameter.

    :param kurtosis: Kurtosis parameter for each star.
    :param kurtosis_lim: Tuple defining the limits for kurtosis selection.
    :return: Boolean array indicating which stars have kurtosis within the
             specified limits.
    """
    select = inlims(kurtosis, kurtosis_lim)
    return select


def cut_moments(cat, moments_lim):
    select = (
        inlims(cat["se_mom_fwhm"], moments_lim)
        & inlims(cat["se_mom_e1"], moments_lim)
        & inlims(cat["se_mom_e2"], moments_lim)
    )
    return select


def select_cnn_predictions(
    flags,
    pred,
    beta_lim=(1.5, 10),
    fwhm_lim=(1, 10),
    ellipticity_lim=(-0.3, 0.3),
    flexion_lim=(-0.3, 0.3),
    kurtosis_lim=(-1, 1),
):
    """
    Apply various cuts to the CNN predictions to select stars based on their
    PSF parameters.

    :param flags: Flags array indicating the quality of each star.
    :param pred: Predictions from the CNN model containing PSF parameters.
    :return: Updated flags after applying the cuts.
    """

    # Beta
    if "psf_beta_1_cnn" in pred.dtype.names:
        select_beta = beta_cut(pred["psf_beta_1_cnn"], beta_lim=beta_lim)

        if "psf_beta_2_cnn" in pred.dtype.names:
            select_beta &= beta_cut(pred["psf_beta_2_cnn"], beta_lim=beta_lim)

        set_flag_bit_and_log(
            ~select_beta, flags, FLAGBIT_BETA, "stars with accepted beta"
        )

    # FWHM
    select_fwhm = fwhm_cut(pred["psf_fwhm_cnn"], fwhm_lim=fwhm_lim)
    set_flag_bit_and_log(~select_fwhm, flags, FLAGBIT_FWHM, "stars with accepted FWHM")

    # Ellipticity
    select_ellip = ellipticity_cut(
        pred["psf_e1_cnn"], pred["psf_e2_cnn"], ellipticity_lim=ellipticity_lim
    )
    set_flag_bit_and_log(
        ~select_ellip, flags, FLAGBIT_ELLIPTICITY, "stars with accepted ellipticity"
    )

    # Flexion
    select_flexion = flexion_cut(
        pred["psf_f1_cnn"],
        pred["psf_f2_cnn"],
        pred["psf_g1_cnn"],
        pred["psf_g2_cnn"],
        flexion_lim=flexion_lim,
    )
    set_flag_bit_and_log(
        ~select_flexion, flags, FLAGBIT_FLEXION, "stars with accepted flexion"
    )

    # Kurtosis
    if "psf_kurtosis_cnn" in pred.dtype.names:
        select_kurtosis = kurtosis_cut(
            pred["psf_kurtosis_cnn"], kurtosis_lim=kurtosis_lim
        )
        set_flag_bit_and_log(
            ~select_kurtosis, flags, FLAGBIT_KURTOSIS, "stars with accepted kurtosis"
        )

    return flags


def remove_outliers(x, y, n_sigma, list_cols_use="all"):
    """
    Remove outliers based on the difference between predicted and actual values.

    :param x: Predicted values (e.g., CNN predictions).
    :param y: Actual values (e.g., SExtractor measurements).
    :param n_sigma: Number of standard deviations for clipping.
    :param list_cols_use: List of columns to use for outlier detection, or 'all'
                          to use all columns.
    :return: Boolean array indicating which samples are not outliers.
    """

    n_samples, n_dim = x.shape

    if list_cols_use == "all":
        list_cols_use = range(n_dim)

    select_clip = np.ones(n_samples, dtype=bool)

    res = y - x

    for i_dim in list_cols_use:
        _, lo, up = scipy.stats.sigmaclip(res[:, i_dim], low=n_sigma, high=n_sigma)
        select_clip &= (res[:, i_dim] < up) & (res[:, i_dim] > lo)

    return select_clip


def get_match_vector(cat, cat_gaia, max_dist_arcsec):
    """
    Match the SExtractor catalog with the GAIA catalog based on RA/Dec coordinates.
    The matching is done using a nearest neighbor search with a maximum distance
    defined by max_dist_arcsec.

    :param cat: SExtractor catalog data.
    :param cat_gaia: GAIA catalog data.
    :param max_dist_arcsec: Maximum distance in arcseconds for matching.
    :return: Tuple of boolean selection array and matched RA/Dec coordinates
             from GAIA."""

    gaia_ang = np.concatenate(
        [
            cat_gaia["dec"][:, np.newaxis] * np.pi / 180.0,
            cat_gaia["ra"][:, np.newaxis] * np.pi / 180.0,
        ],
        axis=1,
    )
    cat_ang = np.concatenate(
        [
            cat["DELTAWIN_J2000"][:, np.newaxis] * np.pi / 180.0,
            cat["ALPHAWIN_J2000"][:, np.newaxis] * np.pi / 180.0,
        ],
        axis=1,
    )

    # calculate nearest neighbours
    ball_tree = BallTree(gaia_ang, metric="haversine")
    dist, ind = ball_tree.query(cat_ang, k=1)
    dist_arcsec = dist[:, 0] / np.pi * 180.0 * 3600.0
    select_in_gaia = dist_arcsec < max_dist_arcsec

    # get matched
    ind_match = ind[:, 0][select_in_gaia]

    # remove those with conflicts
    un, ui, uc = np.unique(ind_match, return_counts=True, return_inverse=True)
    select_unique_matches = uc[ui] == 1
    select_in_gaia[select_in_gaia] &= select_unique_matches
    ind_match = ind_match[select_unique_matches]

    # assign
    gaia_ra_match = np.full_like(cat["ALPHAWIN_J2000"], -200)
    gaia_dec_match = np.full_like(cat["DELTAWIN_J2000"], -200)
    gaia_id_match = np.full(len(cat), -200, dtype=int)
    gaia_ra_match[select_in_gaia] = cat_gaia["ra"][ind_match]
    gaia_dec_match[select_in_gaia] = cat_gaia["dec"][ind_match]

    gaia_id_match[select_in_gaia] = cat_gaia["id"][ind_match]

    return select_in_gaia, gaia_ra_match, gaia_dec_match, gaia_id_match
