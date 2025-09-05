# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Sep 17 2024

import os

import numpy as np
import pytest
from cosmic_toolbox import arraytools as at
from ivy import context

from ufig.plugins import cleanup_catalogs


@pytest.fixture
def ctx():
    ctx = context.create_ctx(
        parameters=context.create_ctx(
            det_clf_catalog_name_dict={
                "r": "det_clf_r.h5",
                "i": "det_clf_i.h5",
                "z": "det_clf_z.h5",
            },
            sextractor_forced_photo_catalog_name_dict={
                "r": "sextractor_forced_photo_r.h5",
                "i": "sextractor_forced_photo_i.h5",
                "z": "sextractor_forced_photo_z.h5",
            },
        )
    )
    return ctx


def test_cleanup_cats_nono(ctx):
    """
    Tests the plugin when neither det_clf catalogs nor sextractor catalogs exists.
    """
    cleanup_catalogs.Plugin(ctx)()


def test_cleanup_cats_yesno(ctx):
    """
    Tests the plugin when det_clf catalogs exist but sextractor catalogs do not exist.
    """
    for f in ctx.parameters["det_clf_catalog_name_dict"].values():
        open(f, "w").close()
    for f in ctx.parameters["det_clf_catalog_name_dict"].values():
        assert os.path.exists(f)
    cleanup_catalogs.Plugin(ctx)()
    for f in ctx.parameters["det_clf_catalog_name_dict"].values():
        assert not os.path.exists(f)


def test_cleanup_cats_noyes(ctx):
    """
    Tests the plugin when det_clf catalogs do not exist but sextractor catalogs exist.
    """
    cats = {}
    for f in ctx.parameters["sextractor_forced_photo_catalog_name_dict"].values():
        cat = {"mag": np.random.rand(10), "r50": np.random.rand(10)}
        cat = at.dict2rec(cat)
        cats[f] = cat
        at.save_hdf_cols(f, cat)
    for f in ctx.parameters["sextractor_forced_photo_catalog_name_dict"].values():
        assert os.path.exists(f)
    cleanup_catalogs.Plugin(ctx)()
    for f in ctx.parameters["sextractor_forced_photo_catalog_name_dict"].values():
        cat = at.load_hdf(f)
        assert np.all(cat["mag"] == cats[f]["mag"])
        assert np.all(cat["r50"] == cats[f]["r50"])

    for f in ctx.parameters["sextractor_forced_photo_catalog_name_dict"].values():
        os.remove(f)
