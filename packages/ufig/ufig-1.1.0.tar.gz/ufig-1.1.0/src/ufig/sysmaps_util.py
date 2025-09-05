# Copyright (C) 2016 ETH Zurich, Institute for Astronomy

"""
Created on Nov 16, 2016
author: Tomasz Kacprzak
"""

import os

import numba as nb
import numpy as np
from astropy.io import fits
from cosmic_toolbox import logger
from scipy.special import gamma

from ufig import io_util

# from memory_profiler import profile

LOGGER = logger.get_logger(__file__)


@nb.jit(nopython=True)
def chi_mean_loop(detect_image, n_contribute, arange_mu):
    for i in range(detect_image.shape[0]):
        for j in range(detect_image.shape[1]):
            if n_contribute[i, j] == 0:
                detect_image[i, j] = 0.0
            else:
                detect_image[i, j] = (
                    np.sqrt(detect_image[i, j]) - arange_mu[n_contribute[i, j]]
                ) / np.sqrt(n_contribute[i, j] - arange_mu[n_contribute[i, j]] ** 2)


@nb.jit(nopython=True)
def stack_detect_image(detect_image, n_contribute, image, weights):
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if (image[i, j] != 0.0) & (weights[i, j] != 0.0):
                detect_image[i, j] += image[i, j] ** 2 * weights[i, j]
                n_contribute[i, j] += 1.0


def get_hdf_location_exptime(par, band=None):
    """
    Get the filename and dataset for the exposure time map

    :param par: ctx().parameters structure
    :param band: which band to use (if None, use the single-band parameter values)
    :return: filepath, dataset: path and dataset index in hdf file
    """

    if par.sysmaps_type == "sysmaps_hdf":
        if band is None:
            filepath_h5 = par.exp_time_file_name
        else:
            filepath_h5 = par.exp_time_file_name_dict[band]

        dataset = "data"

    elif par.sysmaps_type == "sysmaps_hdf_combined":
        if band is None:
            filepath_h5 = par.filepath_sysmaps
        else:
            filepath_h5 = par.filepath_sysmaps_dict[band]

        dataset = "map_expt"

    else:
        raise ValueError(
            f"unknown sysmaps_type {par.sysmaps_type}"
            " (see common.py for available types)"
        )

    return filepath_h5, dataset


def get_hdf_location_bgrms(par, band=None):
    """
    Get the filename and dataset for the background noise map

    :param par: ctx().parameters structure
    :param band: which band to use (if None, use the single-band parameter values)
    :return: filepath, dataset: path and dataset index in hdf file
    """

    if par.sysmaps_type == "sysmaps_hdf":
        if band is None:
            filepath_h5 = par.bkg_rms_file_name
        else:
            filepath_h5 = par.bkg_rms_file_name_dict[band]

        dataset = "data"

    elif par.sysmaps_type == "sysmaps_hdf_combined":
        if band is None:
            filepath_h5 = par.filepath_sysmaps
        else:
            filepath_h5 = par.filepath_sysmaps_dict[band]

        dataset = "map_bsig"

    else:
        raise ValueError(
            f"unknown sysmaps_type {par.sysmaps_type}"
            " (see common.py for available types)"
        )

    return filepath_h5, dataset


def get_hdf_location_invvar(par, band=None):
    """
    Get the filename and dataset for the inverse variance map

    :param par: ctx().parameters structure
    :param band: which band to use (if None, use the single-band parameter values)
    :return: filepath, dataset: path and dataset index in hdf file
    """

    if par.sysmaps_type == "sysmaps_hdf":
        filepath_h5 = par.weight_image if band is None else par.weight_image_dict[band]
        dataset = "data"

    elif par.sysmaps_type == "sysmaps_hdf_combined":
        if band is None:
            filepath_h5 = par.filepath_sysmaps
        else:
            filepath_h5 = par.filepath_sysmaps_dict[band]

        dataset = "map_invv"

    else:
        raise ValueError(
            f"unknown sysmaps_type {par.sysmaps_type}"
            " (see common.py for available types)"
        )

    return filepath_h5, dataset


def get_hdf_location_gain(par, band=None):
    """
    Get the filename and dataset for the background noise map

    :param par: ctx().parameters structure
    :param band: which band to use (if None, use the single-band parameter values)
    :return: filepath, dataset: path and dataset index in hdf file
    """

    if par.sysmaps_type == "sysmaps_hdf":
        if band is None:
            filepath_h5 = par.gain_map_file_name
        else:
            filepath_h5 = par.gain_map_file_name_dict[band]

        dataset = "data"

    elif par.sysmaps_type == "sysmaps_hdf_combined":
        if band is None:
            filepath_h5 = par.filepath_sysmaps
        else:
            filepath_h5 = par.filepath_sysmaps_dict[band]

        dataset = "map_gain"

    else:
        raise ValueError(
            f"unknown sysmaps_type {par.sysmaps_type}"
            " (see common.py for available types)"
        )

    return filepath_h5, dataset


def chi_mean_combination_lowmem(par):
    """
    This creates a CHI-MEAN detection image, as is done by the DES pipeline, see
    https://iopscience.iop.org/article/10.3847/1538-4365/aab4f5/pdf
    (DOI: 10.3847/1538-4365/aab4f5), appendix B.

    Copy of chi_mean_combination made to run with low memory

    :param images_and_weights: iterable yielding images with weights to be combined
    :return: chi-mean detection image
    """

    for i, band in enumerate(par.sextractor_forced_photo_detection_bands):
        # load image
        image = io_util.load_image_chunks(
            file_name=par.image_name_dict[band], ext=0, dtype=np.float32
        )

        # load weight map
        filepath, dataset = get_hdf_location_invvar(par, band=band)
        weights = io_util.load_from_hdf5(
            file_name=filepath, hdf5_keys=dataset, root_path=par.maps_remote_dir
        )

        if i == 0:
            detect_image = np.zeros_like(image, dtype=np.float32)
            n_contribute = np.zeros_like(image, dtype=np.uint8)

        stack_detect_image(detect_image, n_contribute, image, weights)
        del image
        del weights

    n_contribute_unique = np.arange(50, dtype=np.float32)
    arange_mu = (
        np.sqrt(2)
        * gamma((n_contribute_unique + 1) / 2)
        / gamma(n_contribute_unique / 2)
    )

    chi_mean_loop(detect_image, n_contribute, arange_mu)

    return detect_image


def get_path_temp_sextractor_weight(par, band):
    """
    Constructs the path to the temporary fits-file with the weights for SExtractor

    :param par: ctx.parameters
    :param band: filter band
    :return: path
    """
    dirpath_temp = io_util.get_abs_path(
        par.tempdir_weight_fits, root_path=par.tempdir_weight_fits, is_file=False
    )
    path = os.path.join(dirpath_temp, par.image_name_dict[band] + "__temp_invvar.fits")
    return path


def write_temp_sextractor_weight(par, path_out, band=None, dtype=np.float32):
    """
    Reads out the weight map (inverse variance) from hdf5 and writes it to fits, s.t. it
    can be used by SExtractor

    :param par: ctx.parameters
    :param path_out: path where weight map will be stored
    :param band: filter band
    """
    filepath, dataset = get_hdf_location_invvar(par, band=band)
    map_invv_photometry = io_util.load_from_hdf5(
        file_name=filepath, hdf5_keys=dataset, root_path=par.maps_remote_dir
    ).astype(dtype)
    fits.writeto(path_out, map_invv_photometry, overwrite=True)


# @profile
def get_detection_image(par):
    """
    Constructs the detection image for SExtractor. In case of a single-band detection
    image, simply writes the weight map of the detection band to a fits file. For
    multi-band detection, the function computes the CHI-MEAN combination of the
    detection band images and their weights.
    :param par: ctx.parameters
    :return: path to detection image (fits), path to detection weights (fits or 'NONE'),
             weight type of detection image for SExtractor, either according to input
             parameters (single-band) or 'NONE' (multi-band detection image)
    """

    if len(par.sextractor_forced_photo_detection_bands) == 1:
        path_detection_image = par.image_name_dict[
            par.sextractor_forced_photo_detection_bands[0]
        ]
        if par.weight_type == "NONE":
            path_detection_weight = "NONE"
            detection_weight_type = "NONE"

        else:
            path_detection_weight = get_path_temp_sextractor_weight(
                par, par.sextractor_forced_photo_detection_bands[0]
            )
            detection_weight_type = par.weight_type
            if not os.path.isfile(path_detection_weight):
                write_temp_sextractor_weight(
                    par,
                    path_detection_weight,
                    band=par.sextractor_forced_photo_detection_bands[0],
                )

    else:
        dirpath_temp = io_util.get_abs_path(
            par.tempdir_weight_fits, root_path=par.tempdir_weight_fits, is_file=False
        )
        filename_detection_image = "temp_detection_image_{}.fits".format(
            "".join(par.sextractor_forced_photo_detection_bands)
        )
        path_detection_image = os.path.join(dirpath_temp, filename_detection_image)
        path_detection_weight = "NONE"
        detection_weight_type = "NONE"

        if not os.path.isfile(path_detection_image):
            detection_image = chi_mean_combination_lowmem(par)
            header = fits.getheader(par.image_name_dict[par.filters[0]])
            fits.writeto(
                path_detection_image, detection_image, header=header, overwrite=True
            )
    return path_detection_image, path_detection_weight, detection_weight_type


def write_temp_sextractor_weights(
    par, dirpath_temp, overwrite_photo=True, overwrite_det=True, dtype=np.float32
):
    """
    Write fits weight maps for SExtractor in the temp folder.

    :param par: ctx().parameters structure
    :param dirpath_temp: temp dir where to write files
    :param overwrite_photo: if to overwrite photometry weight if exists
    :param overwrite_det: if to overwrite detection weight if exists

    :return: filepath_fits_photometry, filepath_fits_detection: paths to decompressed
            weights
    """

    # ==========
    # Photometry
    # ==========

    dirpath_temp = io_util.get_abs_path(
        dirpath_temp, root_path=dirpath_temp, is_file=False
    )
    filepath_fits_photometry = os.path.join(
        dirpath_temp, par.image_name + "__temp_invvar.fits"
    )
    filepath, dataset = get_hdf_location_invvar(par)

    if filepath.endswith(".fits"):
        filepath_fits_photometry = filepath

    elif (not os.path.isfile(filepath_fits_photometry)) or overwrite_photo:
        map_invv_photometry = io_util.load_from_hdf5(
            file_name=filepath, hdf5_keys=dataset, root_path=par.maps_remote_dir
        )

        fits.writeto(
            filepath_fits_photometry, map_invv_photometry.astype(dtype), overwrite=True
        )

    # =========
    # Detection
    # =========

    if par.sextractor_use_forced_photo:
        LOGGER.warning(
            "This line should not be executed, use the force photometry plugin instead"
        )
        filepath_fits_detection = None
    else:
        filepath_fits_detection = None

    return filepath_fits_photometry, filepath_fits_detection
