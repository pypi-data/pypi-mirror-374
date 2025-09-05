# Copyright (c) 2016 ETH Zurich, Institute of Astronomy, Cosmology Research Group

"""
Created on Jul 12, 2016
@author: Joerg Herbel
"""

import os
import subprocess
import tempfile

import h5py
import numpy as np
from astropy.io import fits
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin
from pkg_resources import resource_filename

import ufig
from ufig import array_util, sysmaps_util
from ufig.plugins.write_image import get_seeing_value

LOGGER = logger.get_logger(__file__)

NAME = "run SourceExtractor (forced-photo)"
HDF5_COMPRESS = {"compression": "gzip", "compression_opts": 9, "shuffle": True}


def convert_fits_to_hdf(filepath_fits, fits_ext=2):
    try:
        cat = np.array(fits.getdata(filepath_fits, ext=fits_ext))
        cat = cat.byteswap()
        cat = cat.view(cat.dtype.newbyteorder())
    except Exception as errmsg:  # pragma: no cover
        LOGGER.error(f"failed to fits-open {filepath_fits}, already hdf?")
        LOGGER.error(errmsg)

    os.remove(filepath_fits)

    cat = array_util.rec_float64_to_float32(cat)

    at.save_hdf_cols(filepath_fits, cat, compression=HDF5_COMPRESS)

    LOGGER.info(f"converted to hdf: {filepath_fits}")


def checkimages_to_hdf(
    checkimage_type,
    checkimages_names_fits,
    checkimages_names_hdf5,
    kw_dataset=None,
):
    if kw_dataset is None:
        kw_dataset = {
            "compression": "gzip",
            "compression_opts": 9,
            "shuffle": True,
        }
    if len(checkimages_names_hdf5) > 0:
        for c, f_fits, f_hdf5 in zip(
            checkimage_type, checkimages_names_fits, checkimages_names_hdf5
        ):
            img = np.array(fits.getdata(f_fits))
            with h5py.File(f_hdf5, "w") as f:
                f.create_dataset(name=c, data=img, **kw_dataset)
            os.remove(f_fits)
            LOGGER.info(
                f"converted checkimage={c} dtype={str(img.dtype)} {f_fits} -> {f_hdf5}"
            )


def enforce_abs_path(path):
    """
    Build an absolute path using the path of the SExtractor directory in UFig. In case
    the input is already a path (and not only a filename), it is left unchanged.

    :param path: Input path
    :return: Absolute path
    """

    if path == os.path.basename(path):
        path = resource_filename(ufig.__name__, "res/sextractor/" + path)

    return path


def kwarg_to_sextractor_arg(key, value):
    """
    Construct a SExtractor command line argument from a keyword argument. The key of the
    keyword argument must be a valid SExtractor parameter (modulo upper cases). The
    value must convertible to a string. It can also be an iterable containing only
    objects that can be converted to a string.

    :param key: Key
    :param value: Value

    :return: SExtractor command line argument as a list in the form
            [-<PARAM_NAME>, VALUE]
    """

    path_keys = ("starnnw_name", "parameters_name", "filter_name")

    if str(value) != value:
        try:
            value = map(str, value)
        except TypeError:
            value = [str(value)]
        value = ",".join(value)

    if key in path_keys:
        value = enforce_abs_path(value)

    sextractor_arg = ["-" + key.upper(), value]

    return sextractor_arg


def build_sextractor_cmd(binary_name, image_name, config_name, **kwargs):
    """
    Construct a list of strings which make up a valid command line argument to call
    SExtractor.

    :param binary_name: Path of SExtractor executable
    :param image_name: Path(s) of image(s) on which SExtractor will run
    :param config_name: Path of SExtractor configuration file
    :param kwargs: Keyword arguments that can be converted to SExtractor command line
                   arguments

    :return: Command to call SExtractor as a list of strings
    """

    config_name = enforce_abs_path(config_name)

    if str(image_name) != image_name:
        image_name = ",".join(image_name)

    cmd = [binary_name, image_name, "-c", config_name]

    for key in kwargs:
        cmd += kwarg_to_sextractor_arg(key, kwargs[key])

    return cmd


def get_checkimages(
    sextractor_catalog_name, sextractor_checkimages, sextractor_checkimages_suffixes
):
    catalog_name_short = sextractor_catalog_name.rsplit(".", 1)[0]
    checkimages_names = []
    checkimages_names_hdf5 = []
    checkimages = sextractor_checkimages

    for suffix in sextractor_checkimages_suffixes:
        checkimage_name = catalog_name_short + suffix
        checkimage_name_hdf5 = checkimage_name.replace(".fits", ".h5")
        checkimages_names += [checkimage_name]
        checkimages_names_hdf5 += [checkimage_name_hdf5]

    if len(checkimages_names) == 0:
        checkimages_names = ["NONE"]
        checkimages = ["NONE"]

    return checkimages, checkimages_names, checkimages_names_hdf5


def run_sextractor(binary_name, image_name, config_name, **kwargs):
    """
    Run SExtractor by spawning a subprocess.

    :param binary_name: Path of SExtractor executable
    :param image_name: Path(s) of image(s) on which SExtractor will run
    :param config_name: Path of SExtractor configuration file
    :param kwargs: Keyword arguments that can be converted to SExtractor command line
                   arguments
    """
    cmd = build_sextractor_cmd(binary_name, image_name, config_name, **kwargs)
    LOGGER.info(" ".join(cmd))
    subprocess.check_call(cmd, stderr=subprocess.STDOUT)


class Plugin(BasePlugin):
    """
    Run SExtractor in forced-photometry mode.
    """

    def __call__(self):
        par = self.ctx.parameters

        sextractor_catalog_name = par.sextractor_forced_photo_catalog_name_dict[
            self.ctx.current_filter
        ]

        if self.ctx.parameters.sextractor_use_temp:
            sextractor_catalog_name = os.path.join(
                tempfile.mkdtemp("sextractor"),
                os.path.split(sextractor_catalog_name)[-1],
            )
        (
            path_detection_image,
            path_detection_weight,
            detection_weight_type,
        ) = sysmaps_util.get_detection_image(par)
        remove_detection_image = (self.ctx.current_filter == par.filters[-1]) & (
            len(par.sextractor_forced_photo_detection_bands) > 1
        )
        if par.weight_type != "NONE":
            # write weights for photometry band
            path_photometry_weight = sysmaps_util.get_path_temp_sextractor_weight(
                par, self.ctx.current_filter
            )
            sysmaps_util.write_temp_sextractor_weight(par, path_photometry_weight)

            # check if written weights can be removed after running SourceExtractor
            remove_photo_weights = path_detection_weight != path_photometry_weight
            remove_detection_weights = (self.ctx.current_filter == par.filters[-1]) & (
                path_detection_weight != "NONE"
            )

        else:
            detection_weight_type = par.weight_type
            path_detection_weight = "NONE"
            path_photometry_weight = "NONE"
            remove_photo_weights = False
            remove_detection_weights = False

        checkimages, checkimages_names, checkimages_names_hdf5 = get_checkimages(
            sextractor_catalog_name,
            par.sextractor_checkimages,
            par.sextractor_checkimages_suffixes,
        )

        if par.flag_gain_times_nexp:
            run_sextractor(
                par.sextractor_binary,
                (path_detection_image, par.image_name),
                par.sextractor_config,
                seeing_fwhm=get_seeing_value(self.ctx) * par.pixscale,
                satur_key="NONE",
                satur_level=par.saturation_level,
                mag_zeropoint=par.magzero,
                gain_key="NONE",
                gain=par.n_exp * par.gain,
                pixel_scale=par.pixscale,
                starnnw_name=par.sextractor_nnw,
                filter_name=par.sextractor_filter,
                parameters_name=par.sextractor_params,
                catalog_name=sextractor_catalog_name,
                checkimage_type=",".join(checkimages),
                checkimage_name=",".join(checkimages_names),
                weight_type=f"{detection_weight_type},{par.weight_type}",
                weight_gain=",".join([par.weight_gain] * 2),
                weight_image=(path_detection_weight, path_photometry_weight),
                catalog_type="FITS_LDAC",
                verbose_type="QUIET",
            )

        else:
            run_sextractor(
                par.sextractor_binary,
                (path_detection_image, par.image_name),
                par.sextractor_config,
                seeing_fwhm=get_seeing_value(self.ctx) * par.pixscale,
                satur_key="NONE",
                satur_level=par.saturation_level,
                mag_zeropoint=par.magzero,
                gain_key="NONE",
                gain=par.gain,
                pixel_scale=par.pixscale,
                starnnw_name=par.sextractor_nnw,
                filter_name=par.sextractor_filter,
                parameters_name=par.sextractor_params,
                catalog_name=sextractor_catalog_name,
                checkimage_type=",".join(checkimages),
                checkimage_name=",".join(checkimages_names),
                weight_type=f"{detection_weight_type},{par.weight_type}",
                weight_gain=",".join([par.weight_gain] * 2),
                catalog_type="FITS_LDAC",
                verbose_type="QUIET",
            )

        convert_fits_to_hdf(filepath_fits=sextractor_catalog_name)

        checkimages_to_hdf(
            checkimage_type=checkimages,
            checkimages_names_fits=checkimages_names,
            checkimages_names_hdf5=checkimages_names_hdf5,
        )

        # Check whether detection and photo weight image should be removed
        if remove_photo_weights:
            os.remove(path_photometry_weight)

        if remove_detection_weights:
            os.remove(path_detection_weight)

        # Check if detection image should be removed
        if remove_detection_image:
            os.remove(path_detection_image)

    def __str__(self):
        return NAME
