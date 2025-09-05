# Copyright (c) 2013 ETH Zurich, Institute of Astronomy, Lukas Gamper
# <lukas.gamper@usystems.ch>
"""
Created on Oct 7, 2013
@author: Lukas Gamper
"""

import h5py
import numpy as np
from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin

from ufig import io_util, sysmaps_util

LOGGER = logger.get_logger(__file__)


def get_effective_bkg_noise_scale_factor(par):
    bkg_noise_factor = par.gain if par.bkg_noise_multiply_gain else 1
    return bkg_noise_factor


def add_from_gaussian(ctx):
    """
    Adds noise to the image assuming a Gaussian background model.
    The noise in every pixel is randomly drawn from a Gaussian

    :param ctx.image: Simulated image
    :param ctx.parameters.bkg_noise_amp: Center of the Gaussian distribution
    :param ctx.parameters.background_sigma: RMS of the Gaussian distribution
    """
    par = ctx.parameters
    bkg_noise_factor = get_effective_bkg_noise_scale_factor(ctx.parameters)
    amp_variations = np.random.normal(
        0, par.bkg_amp_variation_sigma, size=ctx.image.shape
    )
    noise_variations = np.random.normal(
        0, par.bkg_noise_variation_sigma, size=ctx.image.shape
    )
    par.bkg_noise_std = bkg_noise_factor * par.background_sigma + noise_variations
    select = par.bkg_noise_std < 0
    if np.any(select):
        LOGGER.warning("Negative noise std values detected, setting to 0")
        par.bkg_noise_std[select] = 0
    ctx.image += np.random.normal(
        par.bkg_noise_amp + amp_variations,
        par.bkg_noise_std,
        size=ctx.image.shape,
    )
    ctx.image_mask = np.ones((par.size_y, par.size_x), dtype=bool)


def add_from_map(ctx):
    """
    Adds noise to the image using a rms map

    :param ctx.image: Simulated image
    :param ctx.params.maps_remote_dir: Path to fits-image containing the RMS of the
                                       noise in every pixel of the image
    :param ctx.params.bkg_rms_file_name: Path to fits-image containing the RMS of the
                                         noise in every pixel of the image :param
                                         ctx.params.bkg_noise_scale: Scale factor
                                         applied to the map
    :param ctx.params.bkg_noise_amp: Amplitude factor applied to the map
    """

    par = ctx.parameters
    img_shape = ctx.image.shape

    filename_h5, dataset = sysmaps_util.get_hdf_location_bgrms(par)
    filepath_h5 = io_util.get_abs_path(filename_h5, par.maps_remote_dir)

    bkg_rms = io_util.load_from_hdf5(
        file_name=filepath_h5,
        hdf5_keys=dataset,
        hdf5_path="",
        root_path=par.maps_remote_dir,
    )

    # Variable systematics
    variable_amp = np.random.normal(0, par.bkg_amp_variation_sigma, size=img_shape)
    variable_noise = np.random.normal(0, par.bkg_noise_variation_sigma, size=img_shape)

    bkg_noise_factor = get_effective_bkg_noise_scale_factor(par)
    noise_draw = np.random.normal(0, 1.0, size=img_shape)
    par.bkg_noise_std = (
        bkg_rms * bkg_noise_factor * par.bkg_noise_scale + variable_noise
    )
    select = par.bkg_noise_std < 0
    if np.any(select):
        LOGGER.warning("Negative noise std values detected, setting to 0")
        par.bkg_noise_std[select] = 0
    noise_draw *= par.bkg_noise_std
    noise_draw += par.bkg_noise_amp + variable_amp
    ctx.image += noise_draw
    ctx.image_mask = bkg_rms != 0


def add_from_chunked_map(ctx):
    """
    Adds noise to the image using a rms map. The map is memmapped and only read out in
    quadratic chunks to reduce the memory footprint.

    :param ctx.image: Simulated image
    :param ctx.params.maps_remote_dir: Path to fits-image containing the RMS of the
                                       noise in every pixel of the image
    :param ctx.params.bkg_rms_file_name: Path to fits-image containing the RMS of the
                                         noise in every pixel of the image
    :param ctx.params.bkg_noise_scale: Scale factor applied to the map
    :param ctx.params.bkg_noise_amp: Amplitude factor applied to the map
    """
    par = ctx.parameters
    img_shape = ctx.image.shape

    chunk = (par.chunksize, par.chunksize)  # quadratic chunks for now

    filename_h5, dataset = sysmaps_util.get_hdf_location_bgrms(par)
    filepath_h5 = io_util.get_abs_path(filename_h5, par.maps_remote_dir)

    bkg_noise_factor = get_effective_bkg_noise_scale_factor(par)

    with h5py.File(filepath_h5, "r") as file_bkgrms:
        bkg_rms = file_bkgrms[dataset]
        for i in range(img_shape[0] // chunk[0]):
            idx0 = slice(i * chunk[0], (i + 1) * chunk[0])
            for j in range(img_shape[1] // chunk[1]):
                idx1 = slice(j * chunk[1], (j + 1) * chunk[1])
                # TODO: implement variable systematics
                ctx.image[idx0, idx1] += (
                    par.bkg_noise_amp
                    + bkg_noise_factor
                    * par.bkg_noise_scale
                    * np.random.normal(0, 1.0, size=chunk)
                    * bkg_rms[idx0, idx1]
                )

                ctx.image_mask[idx0, idx1] = bkg_rms[idx0, idx1] != 0


BACKGROUND_GENERATOR = {
    "gaussian": add_from_gaussian,
    "map": add_from_map,
    "chunked_map": add_from_chunked_map,
}


class Plugin(BasePlugin):
    """
    Generating random Gaussian background noise for each pixel and adding the noise onto
    the image.

    :param background_sigma: rms spread of (zero mean) Gaussian background noise
    :param background_seed_offset: seed of the rng used to generate the background noies
                                   (optional)

    :return: Image with noise added
    """

    def __call__(self):
        # Reseed random library
        np.random.seed(
            self.ctx.parameters.seed + self.ctx.parameters.background_seed_offset
        )

        # generate background noise
        generator = BACKGROUND_GENERATOR[self.ctx.parameters.background_type]
        generator(self.ctx)

    def __str__(self):
        return "add background noise"
