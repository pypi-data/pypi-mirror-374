# Copyright (c) 2014 ETH Zurich, Institute of Astronomy, Lukas Gamper
# <lukas.gamper@usystems.ch>
"""
Created on Jun 3, 2014
@author: Lukas Gamper

"""

import contextlib
import os
import subprocess
import tempfile

from ivy.plugin.base_plugin import BasePlugin
from pkg_resources import resource_filename

import ufig
from ufig import io_util, sysmaps_util
from ufig.plugins.write_image import get_seeing_value


def get_sextractor_cmd(ctx):
    par = ctx.parameters

    catalog_name_short = par.sextractor_catalog_name.rsplit(".", 1)[0]
    checkimages_names = []
    checkimages = par.sextractor_checkimages
    for suffix in par.sextractor_checkimages_suffixes:
        checkimages_names += [catalog_name_short + suffix]
    if len(checkimages_names) == 0:
        checkimages_names = ["NONE"]
        checkimages = ["NONE"]

    if not os.path.isabs(par.sextractor_config):
        par.sextractor_config = resource_filename(
            ufig.__name__, "res/sextractor/" + par.sextractor_config
        )
    if not os.path.isabs(par.sextractor_params):
        par.sextractor_params = resource_filename(
            ufig.__name__, "res/sextractor/" + par.sextractor_params
        )
    if not os.path.isabs(par.sextractor_filter):
        par.sextractor_filter = resource_filename(
            ufig.__name__, "res/sextractor/" + par.sextractor_filter
        )
    if not os.path.isabs(par.sextractor_nnw):
        par.sextractor_nnw = resource_filename(
            ufig.__name__, "res/sextractor/" + par.sextractor_nnw
        )

    seeing = get_seeing_value(ctx)

    cmd = [
        par.sextractor_binary,
        par.image_name,
        "-c",
        par.sextractor_config,
        "-SEEING_FWHM",
        str(seeing * par.pixscale),  # Seeing value in arcsec
        "-SATUR_KEY",
        "NONE",
        "-SATUR_LEVEL",
        str(par.saturation_level),
        "-MAG_ZEROPOINT",
        str(par.magzero),
        "-GAIN_KEY",
        "NONE",
        "-GAIN",
        str(par.n_exp * par.gain),
        "-PIXEL_SCALE",
        str(par.pixscale),
        "-STARNNW_NAME",
        par.sextractor_nnw,
        "-FILTER_NAME",
        par.sextractor_filter,
        "-PARAMETERS_NAME",
        par.sextractor_params,
        "-CATALOG_NAME",
        par.sextractor_catalog_name,
        "-CHECKIMAGE_TYPE",
        ",".join(checkimages),
        "-CHECKIMAGE_NAME",
        ",".join(checkimages_names),
        "-CATALOG_TYPE",
        "FITS_LDAC",
        "-VERBOSE_TYPE",
        "QUIET",
    ]

    if par.weight_type != "NONE":
        path = io_util.get_abs_path(par.filepath_weight_fits, par.maps_remote_dir)
        cmd += [
            "-WEIGHT_IMAGE",
            path,
            "-WEIGHT_TYPE",
            par.weight_type,
            "-WEIGHT_GAIN",
            par.weight_gain,
        ]

    return cmd, checkimages_names


class Plugin(BasePlugin):
    """
    Executes sextractor by spawning a subprocess.

    :param image_name of image
    :param sextractor_binary: path to sextractor binary
    :param sextractor_config: c
    :param saturation_level: SATUR_LEVEL
    :param magzero_point: MAG_ZEROPOINT
    :param gain: GAIN
    :param sextractor_nnw: STARNNW_NAME
    :param sextractor_filter: FILTER_NAME
    :param sextractor_params: PARAMETERS_NAME
    :param sextractor_catalog_name: CATALOG_NAME
    :param sextractor_checkimages: CHECKIMAGE_TYPE
    :param sextractor_checkimages_suffixes: Suffixes to construct CHECKIMAGE_NAME from
                                            sextractor_catalog_name
    """

    def __call__(self):
        par = self.ctx.parameters

        if self.ctx.parameters.sextractor_use_temp:
            catalog_name = os.path.join(
                tempfile.mkdtemp("sextractor"),
                par.sextractor_catalog_name.split("/")[-1],
            )
            par.sextractor_catalog_name = catalog_name

        if par.weight_type != "NONE":
            # par.filepath_weight_fits, weight_image_converted = \
            # io_util.handle_sextractor_weight_image(par.weight_image,
            # par.tempdir_weight_fits,
            # overwrite=True,
            # root_path=par.maps_remote_dir)

            overwrite_photo = True
            remove_photo = True
            (
                filepath_photometry_weight,
                filepath_detection_weight,
            ) = sysmaps_util.write_temp_sextractor_weights(
                par,
                dirpath_temp=par.tempdir_weight_fits,
                overwrite_photo=overwrite_photo,
            )
            par.filepath_weight_fits = filepath_photometry_weight

        else:
            remove_photo = False

        cmd, checkimages_names = get_sextractor_cmd(self.ctx)

        if self.ctx.parameters.overwrite:
            with contextlib.suppress(OSError):
                os.remove(par.sextractor_catalog_name)

            for name in checkimages_names:
                with contextlib.suppress(OSError):
                    os.remove(name)

        subprocess.check_call(cmd, stderr=subprocess.STDOUT)

        if remove_photo and os.path.isfile(filepath_photometry_weight):
            os.remove(par.filepath_weight_fits)

    def __str__(self):
        return "run sextractor"
