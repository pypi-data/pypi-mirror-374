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

from ufig.plugins import (
    match_sextractor_catalog_multiband_read,
    match_sextractor_seg_catalog_multiband_read,
)
from ufig.plugins.match_sextractor_seg_catalog_multiband_read import NO_MATCH_VAL


@pytest.fixture
def create_context():
    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        galaxy_catalog_name_dict={
            "g": "g_galaxy_ucat.cat",
            "r": "r_galaxy_ucat.cat",
            "i": "i_galaxy_ucat.cat",
            "z": "z_galaxy_ucat.cat",
            "y": "y_galaxy_ucat.cat",
        },
        star_catalog_name_dict={
            "g": "g_star_ucat.cat",
            "r": "r_star_ucat.cat",
            "i": "i_star_ucat.cat",
            "z": "z_star_ucat.cat",
            "y": "y_star_ucat.cat",
        },
        sextractor_forced_photo_catalog_name_dict={
            "g": "g.cat",
            "r": "r.cat",
            "i": "i.cat",
            "z": "z.cat",
            "y": "y.cat",
        },
        matching_x="XWIN_IMAGE",
        matching_y="YWIN_IMAGE",
        matching_mag="MAG_AUTO",
        filters=["g", "r", "i", "z", "y"],
        max_radius=2.0,
        mag_diff=2,
    )

    return ctx


def create_catalogs_and_segmentation_map():
    """
    The image has 3 galaxies and 2 stars.
    The segmentation map has 3 real objects and one artefact.
    At 10,10 there is a faint galaxy and a bright star (only star detected).
    At 20,20 there is a bright galaxy (detected).
    At 30,30 there is a faint galaxy (not detected).
    At 40,40 there is a bright star (detected, but with bad magnitude match).
    At 45,45 there is an artefact (detected).
    """
    for band in ["g", "r", "i", "z", "y"]:
        cat_gal = {}
        cat_gal["x"] = [10.0, 20.0, 30.0]
        cat_gal["y"] = [10.0, 20.0, 30.0]
        cat_gal["mag"] = [25.0, 20.0, 30.0]
        cat_gal = at.dict2rec(cat_gal)
        at.write_to_hdf(f"{band}_galaxy_ucat.cat", cat_gal)

        cat_star = {}
        cat_star["x"] = [10.0, 40.0]
        cat_star["y"] = [10.0, 40.0]
        cat_star["mag"] = [20.0, 20.0]
        cat_star = at.dict2rec(cat_star)
        at.write_to_hdf(f"{band}_star_ucat.cat", cat_star)

        cat_forced_photometry = {}
        cat_forced_photometry["XWIN_IMAGE"] = [10.0, 20.0, 40.0, 45.0]
        cat_forced_photometry["YWIN_IMAGE"] = [10.0, 20.0, 40.0, 45.0]
        cat_forced_photometry["MAG_AUTO"] = [20.0, 20.0, 24.0, 15.0]
        cat_forced_photometry = at.dict2rec(cat_forced_photometry)
        at.save_hdf_cols(
            f"{band}.cat",
            cat_forced_photometry,
        )

    seg_map = np.zeros((50, 50), dtype=np.int32)
    seg_map[9:12, 9:12] = 1
    seg_map[19:22, 19:22] = 2
    seg_map[39:42, 39:42] = 3
    seg_map[44:47, 44:47] = 4

    with h5py.File("i_seg.h5", "w") as f:
        f.create_dataset("SEGMENTATION", data=seg_map)

    n_gals = len(cat_gal)
    return n_gals


def test_match_sextractor_seg_catalog_multiband_read(create_context):
    ctx = create_context
    ctx.numgalaxies = create_catalogs_and_segmentation_map()

    # dummy values
    ctx.galaxies = True
    ctx.stars = True

    plugin = match_sextractor_seg_catalog_multiband_read.Plugin(ctx)
    plugin()

    new_sexcat = at.load_hdf_cols("i.cat")
    assert np.all(new_sexcat["MAG_AUTO"] == np.array([20, 20, 24, 15]))
    assert np.all(new_sexcat["XWIN_IMAGE"] == np.array([10, 20, 40, 45]))
    assert np.all(new_sexcat["YWIN_IMAGE"] == np.array([10, 20, 40, 45]))
    assert np.all(new_sexcat["mag"] == np.array([20, 20, 20, NO_MATCH_VAL]))
    assert np.all(new_sexcat["x"] == np.array([10, 20, 40, NO_MATCH_VAL]))
    assert np.all(new_sexcat["y"] == np.array([10, 20, 40, NO_MATCH_VAL]))
    assert np.all(new_sexcat["star_gal"] == np.array([1, 0, 1, NO_MATCH_VAL]))

    for f in ctx.parameters.filters:
        os.remove(f"{f}_galaxy_ucat.cat")
        os.remove(f"{f}_star_ucat.cat")
        os.remove(f"{f}.cat")
    os.remove("i_seg.h5")


def create_catalogs_for_catalog_matching():
    """
    The image has 3 galaxies and 2 stars.
    At 10,10 there is a faint galaxy and a bright star (only star detected).
    At 20,20 there is a bright galaxy (detected).
    At 30,30 there is a faint galaxy (not detected).
    At 40,40 there is a bright star (detected, but with bad magnitude match).
    At 45,45 there is an artefact (detected).
    """

    for band in ["g", "r", "i", "z", "y"]:
        cat_gal = {}
        cat_gal["x"] = [10.0, 20.0, 30.0]
        cat_gal["y"] = [10.0, 20.0, 30.0]
        cat_gal["mag"] = [25.0, 20.0, 30.0]
        cat_gal = at.dict2rec(cat_gal)
        at.write_to_hdf(f"{band}_galaxy_ucat.cat", cat_gal)

        cat_star = {}
        cat_star["x"] = [10.0, 40.0]
        cat_star["y"] = [10.0, 40.0]
        cat_star["mag"] = [20.0, 20.0]
        cat_star = at.dict2rec(cat_star)
        at.write_to_hdf(f"{band}_star_ucat.cat", cat_star)

        cat_forced_photometry = {}
        cat_forced_photometry["XWIN_IMAGE"] = [10.0, 20.0, 40.0, 45.0]
        cat_forced_photometry["YWIN_IMAGE"] = [10.0, 20.0, 40.0, 45.0]
        cat_forced_photometry["MAG_AUTO"] = [20.0, 20.0, 24.0, 15.0]
        cat_forced_photometry = at.dict2rec(cat_forced_photometry)
        at.save_hdf_cols(
            f"{band}.cat",
            cat_forced_photometry,
        )

    n_gals = len(cat_gal)
    return n_gals


def test_match_sextractor_catalog_multiband(create_context):
    ctx = create_context
    ctx.numgalaxies = create_catalogs_for_catalog_matching()
    ctx.galaxies = True
    ctx.stars = True

    plugin = match_sextractor_catalog_multiband_read.Plugin(ctx)
    plugin()

    new_sexcat = at.load_hdf_cols("i.cat")

    assert np.all(new_sexcat["MAG_AUTO"] == np.array([20, 20, 24, 15]))
    assert np.all(new_sexcat["XWIN_IMAGE"] == np.array([10, 20, 40, 45]))
    assert np.all(new_sexcat["YWIN_IMAGE"] == np.array([10, 20, 40, 45]))

    # no matching for star with bad magnitude and the artefact
    assert np.all(new_sexcat["mag"] == np.array([20, 20, NO_MATCH_VAL, NO_MATCH_VAL]))
    assert np.all(new_sexcat["x"] == np.array([10, 20, NO_MATCH_VAL, NO_MATCH_VAL]))
    assert np.all(new_sexcat["y"] == np.array([10, 20, NO_MATCH_VAL, NO_MATCH_VAL]))
    assert np.all(
        new_sexcat["star_gal"] == np.array([1, 0, NO_MATCH_VAL, NO_MATCH_VAL])
    )

    for f in ctx.parameters.filters:
        os.remove(f"{f}_galaxy_ucat.cat")
        os.remove(f"{f}_star_ucat.cat")
        os.remove(f"{f}.cat")
