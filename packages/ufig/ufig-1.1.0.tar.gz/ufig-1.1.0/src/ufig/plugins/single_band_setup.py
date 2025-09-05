# Copyright (C) 2016 ETH Zurich, Institute for Astronomy

"""
Created on Feb 09, 2016
author: Joerg Herbel
"""

import numpy as np
from ivy.plugin.base_plugin import BasePlugin

from ufig import io_util, sysmaps_util

NAME = "setup single-band"


def initialize_shape_size_columns(galaxies, numgalaxies, precision):
    # Shear
    for col in ["gamma1", "gamma2", "kappa"]:
        if not hasattr(galaxies, col):
            setattr(galaxies, col, np.zeros(numgalaxies, dtype=precision))

    # Size and shape after shear
    for col in ("e1", "e2", "r50"):
        if not hasattr(galaxies, col):
            setattr(galaxies, col, getattr(galaxies, f"int_{col}").copy())


def initialize_psf_columns(obj, n_obj, band, precision=np.float32):
    """
    Adds a negligible PSF to simulated objects (stars or galaxies)
    :param obj: object catalog (stars or galaxies)
    :param n_obj: number of objects
    """

    # set defaults
    cols_init = {}
    cols_init["psf_beta"] = lambda: np.full((n_obj, 1), 2.0, dtype=precision)
    cols_init["psf_flux_ratio"] = lambda: np.ones(n_obj, dtype=precision)
    cols_init["psf_fwhm"] = lambda: np.full(n_obj, 0.0001, dtype=precision)
    cols_init["psf_r50"] = lambda: np.full(n_obj, 0.0001, dtype=precision)
    cols_init["psf_r50_indiv"] = lambda: np.full(n_obj, 0.0001, dtype=precision).T
    cols_init["psf_e1"] = lambda: np.zeros(n_obj, dtype=precision)
    cols_init["psf_e2"] = lambda: np.zeros(n_obj, dtype=precision)
    cols_init["psf_f1"] = lambda: np.zeros(n_obj, dtype=precision)
    cols_init["psf_f2"] = lambda: np.zeros(n_obj, dtype=precision)
    cols_init["psf_g1"] = lambda: np.zeros(n_obj, dtype=precision)
    cols_init["psf_g2"] = lambda: np.zeros(n_obj, dtype=precision)
    cols_init["psf_kurtosis"] = lambda: np.zeros(n_obj, dtype=precision)
    cols_init["psf_dx_offset"] = lambda: np.zeros(n_obj, dtype=precision).T
    cols_init["psf_dy_offset"] = lambda: np.zeros(n_obj, dtype=precision).T

    for col in cols_init:
        dict_col_name = f"{col}_dict"

        # initialize dict if does not exist
        if not hasattr(obj, dict_col_name):
            setattr(obj, dict_col_name, {})

        # assign PSF column to band
        dict_col = getattr(obj, dict_col_name)

        # initialize values if fdo not exist
        if band not in dict_col:
            dict_col[band] = cols_init[col]()

        # set the column to the current filter
        setattr(obj, col, dict_col[band])


class UFigNumPhotError(ValueError):
    """
    Raised when more photons (for galaxies) than allowed by the input parameters are
    sampled
    """


def convert_magnitude_to_nphot_const_texp(
    mag, par, x=None, y=None, texp_img=None, n_exp=None
):
    """
    Convert the magnitude into a number of photons to be sampled later on

    :param mag: magnitude of the objects
    :param par: Container of ctx.parameters parameters (magzero & gain)
    :param x: x-coordinate of objects (in pixels) (not used here)
    :param y: y-coordinate of objects (in pixels) (not used here)
    :param texp_img: Image contining the exposure times at each position (not used here)
    :param n_exp: number of exposures
    :return: Number of photons
    """
    nphot_mean = np.power(10.0, 0.4 * (par.magzero - mag)) * par.gain * n_exp
    nphot = np.round(np.random.poisson(nphot_mean) / n_exp)

    return nphot


def convert_magnitude_to_nphot_const_gain(
    mag, par, gain, x=None, y=None, texp_img=None, n_exp=None
):
    """
    Convert the magnitude into a number of photons to be sampled later on

    :param mag: magnitude of the objects
    :param par: Container of ctx.parameters parameters (magzero & gain)
    :param x: x-coordinate of objects (in pixels) (not used here)
    :param y: y-coordinate of objects (in pixels) (not used here)
    :param texp_img: Image contining the exposure times at each position (not used here)
    :param n_exp: number of exposures
    :return: Number of photons
    """
    nphot_mean = np.power(10.0, 0.4 * (par.magzero - mag)) * gain
    nphot = np.random.poisson(nphot_mean)

    return nphot


def get_texp_per_object(par, x, y, texp_img=None):
    if texp_img is None:
        filename_h5, dataset = sysmaps_util.get_hdf_location_exptime(par)
        filepath_h5 = io_util.get_abs_path(filename_h5, par.maps_remote_dir)
        texp_img = io_util.load_from_hdf5(
            file_name=filepath_h5,
            hdf5_keys=dataset,
            hdf5_path="",
            root_path=par.maps_remote_dir,
        )

    # proof in case of position of of image
    obj_x = x.astype(np.int32)
    obj_x[obj_x > texp_img.shape[1] - 1] = texp_img.shape[1] - 1
    obj_x[obj_x < 0] = 0

    obj_y = y.astype(np.int32)
    obj_y[obj_y > texp_img.shape[0] - 1] = texp_img.shape[0] - 1
    obj_y[obj_y < 0] = 0

    texp_obj = texp_img[obj_y, obj_x]

    return texp_obj


def get_gain_per_object(par, x, y, gain_img=None):
    if gain_img is None:
        filename_h5, dataset = sysmaps_util.get_hdf_location_gain(par)
        filepath_h5 = io_util.get_abs_path(filename_h5, par.maps_remote_dir)
        gain_img = io_util.load_from_hdf5(
            file_name=filepath_h5,
            hdf5_keys=dataset,
            hdf5_path="",
            root_path=par.maps_remote_dir,
        )

    # proof in case of position of image
    obj_x = x.astype(np.int32)
    obj_x[obj_x > gain_img.shape[1] - 1] = gain_img.shape[1] - 1
    obj_x[obj_x < 0] = 0

    obj_y = y.astype(np.int32)
    obj_y[obj_y > gain_img.shape[0] - 1] = gain_img.shape[0] - 1
    obj_y[obj_y < 0] = 0

    gain_obj = gain_img[obj_y, obj_x]

    return gain_obj


def convert_magnitude_to_nphot_variable_texp(mag, par, x, y, texp_img=None, n_exp=None):
    """
    Convert the magnitude into a number of photons to be sampled later on

    :param mag: magnitude of the objects
    :param par: self.ctx.parameters; must contain:
        magzero: magnitude zero point of target image
        gain: gain of the target image
        exp_time_file_name: file name of the exposure time image
        maps_remote_dir: Remote directory images and maps are stored in if not at
        'res/maps/'
    :param x: x-coordinate of objects (in pixels)
    :param y: y-coordinate of objects (in pixels)
    :param texp_img: Image contining the exposure times at each position
    :param n_exp: number of exposures (not used here)
    :return: Number of photons
    """

    texp_obj = get_texp_per_object(par, x, y)

    nphot = np.zeros_like(texp_obj, dtype=np.int32)
    mask_texp = (texp_obj > 0) & (texp_obj >= par.exposure_time)
    nphot[mask_texp] = convert_magnitude_to_nphot_const_texp(
        mag=mag[mask_texp], par=par, n_exp=texp_obj[mask_texp] // par.exposure_time
    )

    return nphot


def convert_magnitude_to_nphot_with_gain_map(mag, par, x, y, **args):
    """
    Convert the magnitude into a number of photons to be sampled later on

    :param mag: magnitude of the objects
    :param par: self.ctx.parameters; must contain:
        magzero: magnitude zero point of target image
        gain: gain of the target image
        exp_time_file_name: file name of the exposure time image
        maps_remote_dir: Remote directory images and maps are stored in if not at
        'res/maps/'
    :param x: x-coordinate of objects (in pixels)
    :param y: y-coordinate of objects (in pixels)
    :param texp_img: Image contining the exposure times at each position
    :param n_exp: number of exposures (not used here)
    :return: Number of photons
    """

    gain_obj = get_gain_per_object(par, x, y)

    nphot = np.zeros_like(gain_obj, dtype=np.int32)
    nphot = convert_magnitude_to_nphot_const_gain(mag=mag, par=par, gain=gain_obj)

    return nphot


NPHOT_GENERATOR = {
    "constant": convert_magnitude_to_nphot_const_texp,
    "variable": convert_magnitude_to_nphot_variable_texp,
    "gain_map": convert_magnitude_to_nphot_with_gain_map,
}


class Plugin(BasePlugin):
    """
    Set parameters to render an image according to the current filter band and
    multi-band dictionaries. The number of photons is also calculated here.
    """

    def __call__(self):
        par = self.ctx.parameters
        nphot_generator = NPHOT_GENERATOR[par.exp_time_type]

        # Image and general seed
        np.random.seed(par.seed)
        self.ctx.image = np.zeros((par.size_y, par.size_x), dtype=par.image_precision)
        self.ctx.image_mask = np.zeros((par.size_y, par.size_x), dtype=bool)

        # Specific seeds
        for seed_name in [
            "gal_nphot_seed_offset",
            "star_nphot_seed_offset",
            "gal_render_seed_offset",
            "star_render_seed_offset",
            "background_seed_offset",
            "seed_ngal",
        ]:
            setattr(par, seed_name, getattr(par, seed_name) + 1)

        # Set quantities from corresponding dictionaries
        filter_band_params = [
            param_name for param_name in par if param_name.endswith("_dict")
        ]
        for param_name in filter_band_params:
            try:
                param_name_stripped = param_name[:-5]
                setattr(
                    par,
                    param_name_stripped,
                    getattr(par, param_name)[self.ctx.current_filter],
                )
            except KeyError:
                pass

        if "galaxies" in self.ctx:
            add_galaxy_col = [
                "nphot",
                "gamma1",
                "gamma2",
                "kappa",
                "e1",
                "e2",
                "r50",
                "int_mag",
                "mag",
                "abs_mag",
                "psf_beta",
                "psf_flux_ratio",
                "psf_fwhm",
                "psf_r50",
                "psf_e1",
                "psf_e2",
                "psf_f1",
                "psf_f2",
                "psf_g1",
                "psf_g2",
                "psf_kurtosis",
            ]

            self.ctx.galaxies.columns = list(
                set(self.ctx.galaxies.columns) | set(add_galaxy_col)
            )

            # Initial values for galaxy shapes
            initialize_shape_size_columns(
                self.ctx.galaxies, self.ctx.numgalaxies, precision=par.catalog_precision
            )

            # Values emulating a negligible PSF effect (overwritten by add_psf-module)
            initialize_psf_columns(
                self.ctx.galaxies,
                self.ctx.numgalaxies,
                band=self.ctx.current_filter,
                precision=par.catalog_precision,
            )

            #

            # Magnitudes and numbers of photons
            self.ctx.galaxies.int_mag = self.ctx.galaxies.int_magnitude_dict[
                self.ctx.current_filter
            ].astype(par.catalog_precision)
            self.ctx.galaxies.abs_mag = self.ctx.galaxies.abs_magnitude_dict[
                self.ctx.current_filter
            ].astype(par.catalog_precision)
            self.ctx.galaxies.mag = self.ctx.galaxies.magnitude_dict[
                self.ctx.current_filter
            ].astype(par.catalog_precision)
            np.random.seed(par.seed + par.gal_nphot_seed_offset)
            self.ctx.galaxies.nphot = nphot_generator(
                self.ctx.galaxies.mag,
                par=par,
                x=self.ctx.galaxies.x,
                y=self.ctx.galaxies.y,
                n_exp=par.n_exp,
            )

            sum_nphot = np.sum(self.ctx.galaxies.nphot)

            if sum_nphot > par.n_phot_sum_gal_max:
                raise UFigNumPhotError(
                    f"Maximum number of photons: {par.n_phot_sum_gal_max}"
                    f" Computed number: {sum_nphot}"
                )

        if "stars" in self.ctx:
            add_star_col = [
                "nphot",
                "mag",
                "psf_flux_ratio",
                "psf_fwhm",
                "psf_r50",
                "psf_e1",
                "psf_e2",
                "psf_f1",
                "psf_f2",
                "psf_g1",
                "psf_g2",
                "psf_kurtosis",
            ]

            self.ctx.stars.columns = list(
                set(self.ctx.stars.columns) | set(add_star_col)
            )

            # Values emulating a negligible PSF effect (overwritten by add_psf-module)
            initialize_psf_columns(
                self.ctx.stars,
                self.ctx.numstars,
                band=self.ctx.current_filter,
                precision=par.catalog_precision,
            )

            # Magnitudes and numbers of photons
            self.ctx.stars.mag = self.ctx.stars.magnitude_dict[self.ctx.current_filter]
            np.random.seed(par.seed + par.star_nphot_seed_offset)
            self.ctx.stars.nphot = nphot_generator(
                self.ctx.stars.mag,
                par=par,
                x=self.ctx.stars.x,
                y=self.ctx.stars.y,
                n_exp=par.n_exp,
            )

    def __str__(self):
        return NAME
