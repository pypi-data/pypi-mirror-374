# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Wed Aug 07 2024


import os

import numpy as np
import pytest
from cosmic_toolbox import arraytools as at
from ivy import context

from ufig.plugins import (
    run_detection_classifier,
    run_emulator,
    run_nflow,
    write_catalog_for_emu,
)


class dummy_clf:
    """
    Dummy classifier for testing purposes.
    Accepts all odd objects.
    """

    def __init__(self, params=("mag_r", "mag_i", "r50", "galaxy_type", "z")):
        self.params = params

    def predict(self, X):
        return np.arange(X.shape[0]) % 2 == 1

    __call__ = predict


class dummy_nflow:
    """
    Dummy normalizing flow for testing purposes.
    Outputs mags and sizes the same way as the input.
    """

    def __init__(
        self,
        filters=None,
        input_band_dep=None,
        input_band_indep=None,
        output=None,
    ):
        if filters is None:
            filters = ["r", "i"]
        if input_band_dep is None:
            input_band_dep = ["mag"]
        if input_band_indep is None:
            input_band_indep = ["r50", "galaxy_type", "z"]
        if output is None:
            output = ["MAG_AUTO", "FLUX_AUTO"]
        self.filters = filters
        self.input_band_dep = input_band_dep
        self.input_band_indep = input_band_indep
        self.output = output

    def sample(self, X):
        out = {}
        if not self.filters:
            for p in self.input_band_dep:
                out[p] = X[p]
            for p in self.input_band_indep:
                out[p] = X[p]
            for p in self.output:
                if p == "MAG_AUTO":
                    out[p] = X["mag"]
                elif p == "FLUX_AUTO":
                    out[p] = X["r50"]
                else:
                    raise ValueError(f"Unknown output parameter {p}, change test")
        else:
            for f in self.filters:
                for p in self.input_band_dep:
                    out[f"{p}_{f}"] = X[f"{p}_{f}"]
                for p in self.input_band_indep:
                    out[p] = X[p]
                for p in self.output:
                    if p == "MAG_AUTO":
                        out[f"{p}_{f}"] = X[f"mag_{f}"]
                    elif p == "FLUX_AUTO":
                        out[f"{p}_{f}"] = X["r50"]
                    else:
                        raise ValueError(f"Unknown output parameter {p}, change test")
        return at.dict2rec(out)

    __call__ = sample


@pytest.fixture
def create_context():
    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        emu_conf={
            "input_band_dep": ["mag"],
            "input_band_indep": ["r50", "galaxy_type", "z"],
            "output": ["MAG_AUTO", "FLUX_AUTO"],
        },
        clf=dummy_clf(),
        nflow=dummy_nflow(),
        emu_filters=["r", "i"],
        filters=["r", "i"],
        det_clf_catalog_name_dict={
            "r": "r.ucat",
            "i": "i.ucat",
        },
        sextractor_forced_photo_catalog_name_dict={
            "r": "r.cat",
            "i": "i.cat",
        },
        galaxy_catalog_name_dict={
            "r": "r_galaxy_ucat.cat",
            "i": "i_galaxy_ucat.cat",
        },
        catalog_precision=np.float32,
    )
    return ctx


def create_catalogs(filters):
    for f in filters:
        cat_gal = {}
        cat_gal["x"] = np.array([10, 20, 30, 40, 50, 60])
        cat_gal["y"] = np.array([10, 20, 30, 40, 50, 60])
        cat_gal["size"] = np.array([1, 1, 1, 1, 1, 1])
        cat_gal["mag"] = np.array([20, 21, 22, 23, 24, 25])
        cat_gal["r50"] = np.array([1, 1, 1, 1, 1, 1])
        cat_gal["id"] = np.arange(6)
        cat_gal["galaxy_type"] = np.array([0, 0, -1, 0, 0, 0])
        cat_gal["z"] = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        cat_gal = at.dict2rec(cat_gal)
        at.write_to_hdf(f"{f}.ucat", cat_gal)


def create_catalogs_radec(filters):
    for f in filters:
        cat_gal = {}
        cat_gal["ra"] = np.array([10, 20, 30, 40, 50, 60])
        cat_gal["dec"] = np.array([10, 20, 30, 40, 50, 60])
        cat_gal["size"] = np.array([1, 1, 1, 1, 1, 1])
        cat_gal["mag"] = np.array([20, 21, 22, 23, 24, 25])
        cat_gal["r50"] = np.array([1, 1, 1, 1, 1, 1])
        cat_gal["id"] = np.arange(6)
        cat_gal["galaxy_type"] = np.array([0, 0, -1, 0, 0, 0])
        cat_gal["z"] = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        cat_gal = at.dict2rec(cat_gal)
        at.write_to_hdf(f"{f}.ucat", cat_gal)


def test_emulator(create_context):
    ctx = create_context
    create_catalogs(ctx.parameters.filters)

    plugin = run_emulator.Plugin(ctx)
    plugin()

    for f in ctx.parameters.filters:
        cat = at.load_hdf_cols(
            ctx.parameters.sextractor_forced_photo_catalog_name_dict[f]
        )
        assert np.all(cat["MAG_AUTO".format()][:] == cat["mag"][:])
        assert np.all(cat["FLUX_AUTO".format()][:] == cat["r50"][:])

    os.remove("r.ucat")
    os.remove("i.ucat")
    os.remove("r.cat")
    os.remove("i.cat")


def test_emulator_radec(create_context):
    ctx = create_context
    create_catalogs_radec(ctx.parameters.filters)

    plugin = run_emulator.Plugin(ctx)
    plugin()

    for f in ctx.parameters.filters:
        cat = at.load_hdf_cols(
            ctx.parameters.sextractor_forced_photo_catalog_name_dict[f]
        )
        assert np.all(cat["MAG_AUTO".format()][:] == cat["mag"][:])
        assert np.all(cat["FLUX_AUTO".format()][:] == cat["r50"][:])

    os.remove("r.ucat")
    os.remove("i.ucat")
    os.remove("r.cat")
    os.remove("i.cat")


def test_detection_classifier(create_context):
    ctx = create_context
    create_catalogs(ctx.parameters.filters)

    plugin = run_detection_classifier.Plugin(ctx)
    plugin()

    for f in ctx.parameters.filters:
        cat = at.load_hdf(ctx.parameters.galaxy_catalog_name_dict[f])
        assert len(cat) == 3

    os.remove("r.ucat")
    os.remove("i.ucat")
    os.remove("r_galaxy_ucat.cat")
    os.remove("i_galaxy_ucat.cat")


def test_nflow(create_context):
    ctx = create_context
    ctx.parameters.nflow = {}
    for f in ctx.parameters.filters:
        ctx.parameters.nflow[f] = dummy_nflow(filters=[])
    create_catalogs(ctx.parameters.filters)

    ctx.parameters.galaxy_catalog_name_dict = ctx.parameters.det_clf_catalog_name_dict

    for f in ctx.parameters.filters:
        ctx.current_filter = f
        plugin = run_nflow.Plugin(ctx)
        plugin()

    for f in ctx.parameters.filters:
        cat = at.load_hdf_cols(
            ctx.parameters.sextractor_forced_photo_catalog_name_dict[f]
        )
        assert np.all(cat["MAG_AUTO".format()][:] == cat["mag"][:])
        assert np.all(cat["FLUX_AUTO".format()][:] == cat["r50"][:])

    os.remove("r.ucat")
    os.remove("i.ucat")
    os.remove("r.cat")
    os.remove("i.cat")


def enrich_context_for_write(ctx, star=True, galaxy=True):
    if galaxy:
        ctx.galaxies = context.create_immutable_ctx(
            columns=[
                "x",
                "y",
                "mag",
                "r50",
                "id",
                "galaxy_type",
                "z",
                "e1",
                "e2",
                "psf_fwhm",
                "sersic_n",
            ],
            x=np.array([10, 10, 30, 40, 50, 60]),
            y=np.array([10, 10, 30, 40, 50, 60]),
            mag=np.array([20, 21, 22, 23, 24, 25]),
            r50=np.array([1, 1, 1, 1, 1, 1]),
            id=np.arange(6),
            galaxy_type=np.array([0, 0, 1, 0, 0, 0]),
            z=np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            e1=np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            e2=np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            psf_fwhm=np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            sersic_n=np.array([1, 2, 3, 4, 5, 6]),
        )
    if star:
        ctx.stars = context.create_immutable_ctx(
            columns=["x", "y", "mag", "id", "psf_fwhm"],
            x=np.array([10, 20, 30, 40, 50, 60]),
            y=np.array([10, 20, 30, 40, 50, 60]),
            mag=np.array([20, 21, 22, 23, 24, 25]),
            id=np.arange(6),
            z=np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            psf_fwhm=np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
        )
    ctx.parameters.bkg_noise_amp = 1.0
    ctx.parameters.bkg_noise_std = np.ones((100, 100))
    ctx.current_filter = "i"
    ctx.parameters.emu_mini = False
    ctx.parameters.star_catalog_name_dict = {
        "i": "i_star_ucat.cat",
    }
    ctx.parameters.size_x = 97
    ctx.parameters.size_y = 97
    return ctx


def test_write_catalog_for_emu_ngal(create_context):
    ctx = create_context
    ctx = enrich_context_for_write(ctx)
    ctx.parameters.flux_estimation_type = "ngal"
    ctx.parameters.mag_for_scaling = [23, 24]

    plugin = write_catalog_for_emu.Plugin(ctx)
    plugin()

    cat_gal = at.load_hdf(ctx.parameters.galaxy_catalog_name_dict[ctx.current_filter])
    cat_star = at.load_hdf(ctx.parameters.star_catalog_name_dict[ctx.current_filter])
    assert np.all(cat_gal["ngal_23"] == 6)
    assert np.all(cat_gal["ngal_24"] == 8)
    assert np.all(cat_star["ngal_23"] == 6)
    assert np.all(cat_star["ngal_24"] == 8)

    os.remove("i.ucat")
    os.remove("i_star_ucat.cat")
    os.remove("i_galaxy_ucat.cat")


def test_write_catalog_for_emu_binned_integrated(create_context):
    ctx = create_context
    ctx = enrich_context_for_write(ctx, star=False)
    ctx.parameters.flux_estimation_type = "binned_integrated"
    ctx.parameters.mag_for_scaling = 20
    ctx.parameters.n_r50_for_flux_estimation = 1
    ctx.parameters.n_bins_for_flux_estimation = 2

    plugin = write_catalog_for_emu.Plugin(ctx)
    plugin()

    cat_gal = at.load_hdf(ctx.parameters.galaxy_catalog_name_dict[ctx.current_filter])

    mag_w1 = cat_gal["density_mag_weighted"][0]
    mag_w2 = cat_gal["density_mag_weighted"][-1]
    assert np.all(cat_gal["density_mag_weighted"][:4] == mag_w1)
    assert np.all(cat_gal["density_mag_weighted"][4:] == mag_w2)

    size_w1 = cat_gal["density_size_weighted"][0]
    size_w2 = cat_gal["density_size_weighted"][-1]
    assert np.all(cat_gal["density_size_weighted"][:4] == size_w1)
    assert np.all(cat_gal["density_size_weighted"][4:] == size_w2)

    assert mag_w1 > mag_w2
    assert size_w1 > size_w2

    os.remove("i.ucat")
    os.remove("i_galaxy_ucat.cat")
    os.remove("i_star_ucat.cat")


def test_write_catalog_for_emu_integrated(create_context):
    ctx = create_context
    ctx = enrich_context_for_write(ctx)
    ctx.parameters.flux_estimation_type = "integrated"
    ctx.parameters.mag_for_scaling = 20
    ctx.parameters.n_r50_for_flux_estimation = 1

    plugin = write_catalog_for_emu.Plugin(ctx)
    plugin()

    cat_gal = at.load_hdf(ctx.parameters.galaxy_catalog_name_dict[ctx.current_filter])
    cat_star = at.load_hdf(ctx.parameters.star_catalog_name_dict[ctx.current_filter])
    mag_w = cat_gal["density_mag_weighted"][0]
    size_w = cat_gal["density_size_weighted"][0]
    assert np.all(cat_gal["density_mag_weighted"] == mag_w)
    assert np.all(cat_gal["density_size_weighted"] == size_w)
    assert np.all(cat_star["density_mag_weighted"] == mag_w)
    assert np.all(cat_star["density_size_weighted"] == size_w)

    os.remove("i.ucat")
    os.remove("i_galaxy_ucat.cat")
    os.remove("i_star_ucat.cat")


def test_write_catalog_for_emu_image(create_context):
    ctx = create_context
    ctx = enrich_context_for_write(ctx, star=False)
    ctx.parameters.flux_estimation_type = "full_image"
    ctx.parameters.mag_for_scaling = 30
    ctx.parameters.n_r50_for_flux_estimation = 1

    plugin = write_catalog_for_emu.Plugin(ctx)
    plugin()

    cat_gal = at.load_hdf(ctx.parameters.galaxy_catalog_name_dict[ctx.current_filter])
    flux_full = cat_gal["estimated_flux"]
    # first two galaxies should have much higher flux than the others
    first = flux_full[0]
    second = flux_full[1]
    assert np.all(flux_full[2:] < first)
    assert np.all(flux_full[2:] < second)

    ctx.parameters.flux_estimation_type = "points"
    ctx.parameters.mag_for_scaling = 30
    ctx.parameters.n_r50_for_flux_estimation = 1

    plugin = write_catalog_for_emu.Plugin(ctx)
    plugin()

    cat_gal = at.load_hdf(ctx.parameters.galaxy_catalog_name_dict[ctx.current_filter])
    flux_points = cat_gal["estimated_flux"]
    # first two galaxies should have much higher flux than the others
    first = flux_points[0]
    second = flux_points[1]
    assert np.all(flux_points[2:] < first)
    assert np.all(flux_points[2:] < second)

    # the two methods should give the same results
    assert np.allclose(flux_full, flux_points)
    os.remove("i.ucat")
    os.remove("i_galaxy_ucat.cat")
    os.remove("i_star_ucat.cat")


def test_write_catalog_for_emu_without_flux_estimator(create_context):
    ctx = create_context
    ctx.parameters.emu_conf = {
        "input_band_dep": ["mag", "ngal"],
        "input_band_indep": ["r50", "galaxy_type", "z"],
        "output": ["MAG_AUTO", "FLUX_AUTO"],
    }
    ctx = enrich_context_for_write(ctx)
    ctx.parameters.flux_estimation_type = "none"
    plugin = write_catalog_for_emu.Plugin(ctx)
    plugin()


def test_write_catalog_for_emu_radec(create_context):
    ctx = create_context
    ctx = enrich_context_for_write(ctx)
    x = ctx.galaxies.x
    y = ctx.galaxies.y

    del ctx.galaxies.x
    del ctx.galaxies.y
    ctx.galaxies.ra = x
    ctx.galaxies.dec = y
    ctx.galaxies.columns = ctx.galaxies.columns[2:]
    ctx.galaxies.columns = ["ra", "dec"] + ctx.galaxies.columns

    del ctx.stars.x
    del ctx.stars.y
    ctx.stars.ra = x
    ctx.stars.dec = y
    ctx.stars.columns = ctx.stars.columns[2:]
    ctx.stars.columns = ["ra", "dec"] + ctx.stars.columns

    ctx.parameters.flux_estimation_type = "none"

    plugin = write_catalog_for_emu.Plugin(ctx)
    plugin()

    cat_gal = at.load_hdf(ctx.parameters.galaxy_catalog_name_dict[ctx.current_filter])
    assert np.all(cat_gal["ra"] == ctx.galaxies.ra)
    assert np.all(cat_gal["dec"] == ctx.galaxies.dec)

    os.remove("i.ucat")
    os.remove("i_galaxy_ucat.cat")
    os.remove("i_star_ucat.cat")
