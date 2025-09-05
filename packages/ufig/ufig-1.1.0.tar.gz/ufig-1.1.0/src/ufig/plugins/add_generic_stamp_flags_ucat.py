# Copyright (c) 2016 ETH Zurich, Institute of Astronomy, Tomasz Kacprzak
# <tomasz.kacprzak@phys.ethz.ch>
"""
Created on Aug 5, 2016
@author: Tomasz Kacprzak
adapted by Silvan Fischbacher, 2024
"""

import h5py
import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin

from ufig import mask_utils
from ufig.array_util import set_flag_bit
from ufig.plugins.add_generic_stamp_flags import (
    FLAGBIT_EDGE_DUPLICATE,
    FLAGBIT_NEARBY_BRIGHT_STAR,
    FLAGBIT_SURVEY_MASK,
    FLAGBIT_SYSMAP_DELTA_WEIGHT,
)

LOGGER = logger.get_logger(__file__)


class Plugin(BasePlugin):
    def __call__(self):
        par = self.ctx.parameters

        if hasattr(par, "det_clf_catalog_name"):
            add_all_stamp_flags(
                par.det_clf_catalog_name,
                par.filepath_overlapblock,
                par.sextractor_mask_name,
                3 * par.sextractor_catalog_off_mask_radius,
            )

    def __str__(self):
        return "tile overlap/coadd bounadry col for ucat catalog"


def add_all_stamp_flags(
    filename_cat,
    filename_overlapblock,
    filename_mask,
    off_mask_radius,
):
    add_edge_duplicate_flag(filename_cat, filename_overlapblock)
    add_pixel_based_masks(filename_cat, filename_mask, off_mask_radius)


def save_flags_stamp(filename_cat, flags_stamp):
    with h5py.File(filename_cat, "a") as f:
        cat = f["data"]
        del f["data"]
        if "FLAGS_STAMP" in cat.dtype.names:
            cat["FLAGS_STAMP"] = flags_stamp
        else:
            cat = at.add_cols(
                cat, ["FLAGS_STAMP"], data=flags_stamp, dtype=flags_stamp.dtype
            )
        f.create_dataset(name="data", data=cat, compression="lzf", shuffle=True)
    LOGGER.info(f"Saved flags to {filename_cat}")


def load_flags_stamp(filename_cat, len_cat):
    with h5py.File(filename_cat, "r") as f:
        cat = f["data"]
        if "FLAGS_STAMP" in cat.dtype.names:
            flags_stamp = cat["FLAGS_STAMP"]
        else:
            flags_stamp = np.zeros(len_cat, dtype=np.uint32)
    return flags_stamp


def add_pixel_based_masks(filename_cat, filename_mask, off_mask_radius):
    with h5py.File(filename_cat, "r") as f:
        cat = np.array(f["data"])
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
    # TODO: implement r50_offset as parameter
    select_sysmap_delta_weight = ~mask_utils.pixel_mask_to_ucat_catalog_mask(
        pixel_mask_sysmap_delta_weight, cat, off_mask_radius, r50_offset=5
    )
    select_mask_nearby_star = ~mask_utils.pixel_mask_to_ucat_catalog_mask(
        pixel_mask_nearby_star, cat, off_mask_radius, r50_offset=5
    )
    select_survey_mask = ~mask_utils.pixel_mask_to_ucat_catalog_mask(
        pixel_mask_survey_mask, cat, off_mask_radius, r50_offset=5
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
        x = np.int32(np.array(f["data"])["x"])
        y = np.int32(np.array(f["data"])["y"])

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
