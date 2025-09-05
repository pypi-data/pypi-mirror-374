# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Wed Aug 07 2024


import os

import h5py
import numpy as np
import pytest
from cosmic_toolbox import arraytools as at
from ivy import context

from ufig.plugins import add_generic_stamp_flags, add_generic_stamp_flags_ucat
from ufig.plugins.add_generic_stamp_flags import (
    FLAGBIT_EDGE_DUPLICATE,
    FLAGBIT_NEARBY_BRIGHT_STAR,
    FLAGBIT_SURVEY_MASK,
    FLAGBIT_SYSMAP_DELTA_WEIGHT,
)


@pytest.fixture
def create_context():
    ctx = context.create_ctx(current_filter="i")
    ctx.parameters = context.create_immutable_ctx(
        sextractor_forced_photo_catalog_name=True,  # dummy variable
        sextractor_catalog_name="i.cat",
        filepath_overlapblock="overlap.h5",
        sextractor_mask_name="i.mask",
        sextractor_catalog_off_mask_radius=1,
        det_clf_catalog_name="i.cat",
        filepath_sysmaps_dict={"i": "i.sysmaps"},
    )

    return ctx


def create_catalogs(ucat=False):
    """
    The catalog has 6 objects.
    At 10,10 there is a galaxy cut because of the overlap mask.
    At 20,20 there is a galaxy that is detected.
    At 30,30 there is a galaxy flagged because of the delta_weight
    At 40,40 there is a galaxy flagged because of a close by star
    At 50,50 there is a galaxy flagged because of the survey mask
    At 60,60 there is a galaxy flagged because of the survey mask and the delta_weight
    """
    cat_gal = {}
    x = np.array([10, 20, 30, 40, 50, 60])
    y = np.array([10, 20, 30, 40, 50, 60])
    size = np.array([1, 1, 1, 1, 1, 1])
    if ucat:
        cat_gal["x"] = x
        cat_gal["y"] = y
        cat_gal["r50"] = size
    else:
        cat_gal["X_IMAGE"] = x
        cat_gal["Y_IMAGE"] = y
        cat_gal["XWIN_IMAGE"] = x
        cat_gal["YWIN_IMAGE"] = y
        cat_gal["FLUX_RADIUS"] = size
    cat_gal = at.dict2rec(cat_gal)
    if ucat:
        at.write_to_hdf("i.cat", cat_gal)
    else:
        at.save_hdf_cols("i.cat", cat_gal)

    # overlap mask below 12
    overlap = np.zeros((70, 70), dtype=np.int8)
    overlap[0:12, :] = 1
    with h5py.File("overlap.h5", "w") as f:
        f.create_dataset("img_mask", data=overlap)

    FLAGBITS = {"delta_weight": 0, "star": 1, "mask": 2}
    mask = np.zeros((70, 70), dtype=np.int8)
    mask[29:32, 29:32] = 2 ** FLAGBITS["delta_weight"]
    mask[39:42, 39:42] = 2 ** FLAGBITS["star"]
    mask[49:52, 49:52] = 2 ** FLAGBITS["mask"]
    mask[59:62, 59:62] = 2 ** FLAGBITS["mask"] + 2 ** FLAGBITS["delta_weight"]
    with h5py.File("i.mask", "w") as f:
        f.create_dataset("mask", data=mask)

    return np.array(
        [
            2**FLAGBIT_EDGE_DUPLICATE,
            0,
            2**FLAGBIT_SYSMAP_DELTA_WEIGHT,
            2**FLAGBIT_NEARBY_BRIGHT_STAR,
            2**FLAGBIT_SURVEY_MASK,
            2**FLAGBIT_SURVEY_MASK + 2**FLAGBIT_SYSMAP_DELTA_WEIGHT,
        ]
    )


def test_add_generic_stamp_flags(create_context):
    ctx = create_context
    expected_flags = create_catalogs()
    add_generic_stamp_flags.Plugin(ctx)()
    flags = at.load_hdf_cols("i.cat")["FLAGS_STAMP"]
    assert np.all(flags == expected_flags)
    os.remove("i.cat")
    os.remove("overlap.h5")
    os.remove("i.mask")


def test_add_generic_stamp_flags_ucat(create_context):
    ctx = create_context
    expected_flags = create_catalogs(ucat=True)
    add_generic_stamp_flags_ucat.Plugin(ctx)()
    flags = at.load_hdf("i.cat")["FLAGS_STAMP"]
    assert np.all(flags == expected_flags)
    os.remove("i.cat")
    os.remove("overlap.h5")
    os.remove("i.mask")
