# Copyright (c) 2016 ETH Zurich, Institute of Astronomy, Tomasz Kacprzak
# <tomasz.kacprzak@phys.ethz.ch>
"""
Created on Aug 5, 2016
@author: Tomasz Kacprzak

"""

import os

import h5py
import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin

from ufig import mask_utils
from ufig.array_util import set_flag_bit

LOGGER = logger.get_logger(__file__)

FLAGBIT_EDGE_DUPLICATE = 1
FLAGBIT_COADD_BOUNDARY = 2
FLAGBIT_IMAGE_BOUNDARY = 3
FLAGBIT_SYSMAP_DELTA_WEIGHT = 4
FLAGBIT_NEARBY_BRIGHT_STAR = 5
FLAGBIT_SURVEY_MASK = 6


class Plugin(BasePlugin):
    def __call__(self):
        par = self.ctx.parameters

        sexcat_name = None
        if os.path.exists(par.sextractor_catalog_name):
            sexcat_name = par.sextractor_catalog_name
        elif os.path.exists(par.sextractor_forced_photo_catalog_name):
            sexcat_name = par.sextractor_forced_photo_catalog_name

        if sexcat_name is not None:
            add_all_stamp_flags(
                sexcat_name,
                par.filepath_overlapblock,
                par.sextractor_mask_name,
                par.sextractor_catalog_off_mask_radius,
            )
        else:
            LOGGER.info(
                "No SExtractor catalog found, skipping adding flags to the catalog."
            )

    def __str__(self):
        return "tile overlap/coadd bounadry col"


def add_all_stamp_flags(
    filename_cat,
    filename_overlapblock,
    filename_mask,
    off_mask_radius,
):
    add_edge_duplicate_flag(filename_cat, filename_overlapblock)
    add_pixel_based_masks(filename_cat, filename_mask, off_mask_radius)


def load_flags_stamp(filename_cat, len_cat):
    with h5py.File(filename_cat, "r") as f:
        if "FLAGS_STAMP" in f:
            flags_stamp = np.array(f["FLAGS_STAMP"])
        else:
            flags_stamp = np.zeros(len_cat, dtype=np.uint32)
    return flags_stamp


def save_flags_stamp(filename_cat, flags_stamp):
    with h5py.File(filename_cat, "a") as f:
        if "FLAGS_STAMP" in f:
            del f["FLAGS_STAMP"]
        f.create_dataset(name="FLAGS_STAMP", data=flags_stamp, compression="lzf")
        LOGGER.info(f"Saved flags to {filename_cat}")


def add_pixel_based_masks(filename_cat, filename_mask, off_mask_radius):
    cat = at.load_hdf_cols(
        filename_cat, columns=["XWIN_IMAGE", "YWIN_IMAGE", "FLUX_RADIUS"]
    )
    flags_stamp = load_flags_stamp(filename_cat, len(cat))

    # Pixel mask
    with h5py.File(filename_mask, mode="r") as fh5:
        pixel_mask = fh5["mask"][...]

    FLAGBITS = {"delta_weight": 0, "star": 1, "mask": 2}
    n_bits = len(FLAGBITS)

    # Get masked pixels
    pixel_mask_sysmap_delta_weight = mask_utils.set_masked_pixels(
        pixel_mask, [FLAGBITS["delta_weight"]], n_bits=n_bits
    )
    pixel_mask_nearby_star = mask_utils.set_masked_pixels(
        pixel_mask, [FLAGBITS["star"]], n_bits=n_bits
    )
    pixel_mask_survey_mask = mask_utils.set_masked_pixels(
        pixel_mask, [FLAGBITS["mask"]], n_bits=n_bits
    )

    # Transform to catalog mask
    select_sysmap_delta_weight = ~mask_utils.pixel_mask_to_catalog_mask(
        pixel_mask_sysmap_delta_weight, cat, off_mask_radius
    )
    select_mask_nearby_star = ~mask_utils.pixel_mask_to_catalog_mask(
        pixel_mask_nearby_star, cat, off_mask_radius
    )
    select_survey_mask = ~mask_utils.pixel_mask_to_catalog_mask(
        pixel_mask_survey_mask, cat, off_mask_radius
    )

    # Set FLAGS_STAMP
    set_flag_bit(
        flags=flags_stamp,
        select=select_sysmap_delta_weight,
        field=FLAGBIT_SYSMAP_DELTA_WEIGHT,
    )
    set_flag_bit(
        flags=flags_stamp,
        select=select_mask_nearby_star,
        field=FLAGBIT_NEARBY_BRIGHT_STAR,
    )
    set_flag_bit(
        flags=flags_stamp, select=select_survey_mask, field=FLAGBIT_SURVEY_MASK
    )

    save_flags_stamp(filename_cat, flags_stamp)


def add_edge_duplicate_flag(filename_cat, filename_overlapblock):
    with h5py.File(filename_cat, "r") as f:
        x = np.int32(np.array(f["X_IMAGE"])) - 1
        y = np.int32(np.array(f["Y_IMAGE"])) - 1

    with h5py.File(filename_overlapblock, "r") as f:
        img_mask = np.array(f["img_mask"], dtype=np.int8)

    x[x < 0] = 0
    y[y < 0] = 0
    x[x >= img_mask.shape[1]] = img_mask.shape[1]
    y[y >= img_mask.shape[0]] = img_mask.shape[0]

    is_duplicate = img_mask[y, x] == 1

    flags_stamp = load_flags_stamp(filename_cat, len(is_duplicate))
    set_flag_bit(flags=flags_stamp, select=is_duplicate, field=FLAGBIT_EDGE_DUPLICATE)

    save_flags_stamp(filename_cat, flags_stamp)
