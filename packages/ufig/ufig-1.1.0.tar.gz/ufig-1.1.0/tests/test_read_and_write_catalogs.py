# Copyright (c) 2015 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>

"""
Created on Jun 01, 2015
@author: Claudio Bruderer
adapted by: Silvan Fischbacher (2024)
"""

import os

import numpy as np
import pytest
from ivy import context

from ufig.plugins import read_in_catalog, write_catalog


@pytest.fixture
def create_ctx():
    int_mag = np.array([2.0, 4.0, 5.0])
    r50 = np.array([1.0, 3.0, 6.0])
    kappa = np.array([0.0, 7.0, 8.0])

    psf_r50 = np.array([2.0, 4.0])
    psf_e1 = np.array([1.0, 3.0])

    ctx = context.create_ctx(current_filter="r", filters=["r", "i", "z"])
    catalog_name = "testcatalog"
    ctx.parameters = context.create_ctx(
        star_catalog_name=catalog_name + "star.cat",
        galaxy_catalog_name=catalog_name + "gal.cat",
        overwrite=True,
        size_x=20,
        size_y=33,
        pixscale=0.2,
        ra0=1.2,
        dec0=1.5,
        n_exp=3,
        exposure_time=10,
        gain=4.3,
        saturation_level=123.3,
        lanczos_n=2,
        magzero=30.21,
        seeing=1.02,
        seed=102301242,
        gal_dist_seed_offset=101,
        gal_sersic_seed_offset=201,
        gal_ellipticities_seed_offset=301,
        gal_nphot_seed_offset=401,
        star_dist_seed_offset=501,
        star_nphot_seed_offset=601,
        gal_render_seed_offset=701,
        star_render_seed_offset=801,
        background_seed_offset=901,
    )
    ctx.parameters.bkg_noise_std = np.random.uniform(
        0, 1, (ctx.parameters.size_x, ctx.parameters.size_y)
    )
    ctx.parameters["galaxy_catalog_name_dict"] = {
        "r": catalog_name + "gal.cat",
    }
    ctx.parameters["star_catalog_name_dict"] = {
        "r": catalog_name + "star.cat",
    }

    ctx.galaxies = context.create_ctx(
        int_mag=int_mag,
        r50_weird_name=r50,
        kappa=kappa,
        columns=["r50_weird_name", "kappa", "int_mag"],
    )
    ctx.stars = context.create_ctx(
        psf_r50=psf_r50,
        psf_e1=psf_e1,
        int_mag=int_mag[:-1],
        columns=["psf_r50", "psf_e1", "int_mag"],
    )
    return ctx, catalog_name, r50, kappa, int_mag, psf_r50, psf_e1


def test_read_in_catalog(create_ctx):
    """
    Test that star and galaxy catalogs are correctly read in
    """
    ctx, catalog_name, r50, kappa, int_mag, psf_r50, psf_e1 = create_ctx
    write_catalog_plugin = write_catalog.Plugin(ctx)
    write_catalog_plugin()

    del ctx

    ctx = context.create_ctx(current_filter="r", filters=["r", "i", "z"])
    ctx.parameters = context.create_ctx(
        star_catalog_name=catalog_name + "star.cat",
        galaxy_catalog_name=catalog_name + "gal.cat",
        overwrite=True,
    )
    ctx.parameters["galaxy_catalog_name_dict"] = {
        "r": catalog_name + "gal.cat",
    }
    ctx.parameters["star_catalog_name_dict"] = {"r": catalog_name + "star.cat"}

    read_in_catalog_plugin = read_in_catalog.Plugin(ctx)
    read_in_catalog_plugin()

    assert ctx.galaxies.columns == ["r50_weird_name", "kappa", "int_mag"]
    assert np.allclose(ctx.galaxies.r50_weird_name, r50)
    assert np.allclose(ctx.galaxies.kappa, kappa)
    assert np.allclose(ctx.galaxies.int_mag, int_mag)
    assert ctx.numgalaxies == int_mag.size

    assert ctx.stars.columns == ["psf_r50", "psf_e1", "int_mag"]
    assert np.allclose(ctx.stars.psf_r50, psf_r50)
    assert np.allclose(ctx.stars.psf_e1, psf_e1)
    assert np.allclose(ctx.stars.int_mag, int_mag[:-1])
    assert ctx.numstars == psf_r50.size

    os.remove(catalog_name + "star.cat")
    os.remove(catalog_name + "gal.cat")


def test_read_in_catalog_bkg_noise_map(create_ctx):
    """
    Test that star and galaxy catalogs are correctly read in
    """
    ctx, catalog_name, r50, kappa, int_mag, psf_r50, psf_e1 = create_ctx
    n_gals = len(ctx.galaxies.int_mag)
    n_stars = len(ctx.stars.int_mag)

    par = ctx.parameters
    ctx.parameters.bkg_noise_std = np.random.uniform(0, 1, (par.size_y, par.size_x))
    ctx.galaxies.x = np.random.uniform(0, par.size_x, n_gals)
    ctx.galaxies.y = np.random.uniform(0, par.size_y, n_gals)
    ctx.galaxies.columns.extend(["x", "y"])
    ctx.stars.x = np.random.uniform(0, par.size_x, n_stars)
    ctx.stars.y = np.random.uniform(0, par.size_y, n_stars)
    ctx.stars.columns.extend(["x", "y"])

    write_catalog_plugin = write_catalog.Plugin(ctx)
    write_catalog_plugin()

    del ctx

    ctx = context.create_ctx(current_filter="r", filters=["r", "i", "z"])
    ctx.parameters = context.create_ctx(
        star_catalog_name=catalog_name + "star.cat",
        galaxy_catalog_name=catalog_name + "gal.cat",
        overwrite=True,
    )
    ctx.parameters["galaxy_catalog_name_dict"] = {
        "r": catalog_name + "gal.cat",
    }
    ctx.parameters["star_catalog_name_dict"] = {"r": catalog_name + "star.cat"}

    read_in_catalog_plugin = read_in_catalog.Plugin(ctx)
    read_in_catalog_plugin()

    assert ctx.galaxies.columns == [
        "r50_weird_name",
        "kappa",
        "int_mag",
        "x",
        "y",
        "bkg_noise_std",
    ]
    assert np.allclose(ctx.galaxies.r50_weird_name, r50)
    assert np.allclose(ctx.galaxies.kappa, kappa)
    assert np.allclose(ctx.galaxies.int_mag, int_mag)
    assert ctx.numgalaxies == int_mag.size

    assert ctx.stars.columns == ["psf_r50", "psf_e1", "int_mag", "x", "y"]
    assert np.allclose(ctx.stars.psf_r50, psf_r50)
    assert np.allclose(ctx.stars.psf_e1, psf_e1)
    assert np.allclose(ctx.stars.int_mag, int_mag[:-1])
    assert ctx.numstars == psf_r50.size

    os.remove(catalog_name + "star.cat")
    os.remove(catalog_name + "gal.cat")


def test_read_in_catalog_bkg_noise_value(create_ctx):
    ctx, catalog_name, r50, kappa, int_mag, psf_r50, psf_e1 = create_ctx
    n_gals = len(ctx.galaxies.int_mag)
    n_stars = len(ctx.stars.int_mag)

    par = ctx.parameters
    ctx.parameters.bkg_noise_std = 0.1
    ctx.galaxies.x = np.random.uniform(0, par.size_x, n_gals)
    ctx.galaxies.y = np.random.uniform(0, par.size_y, n_gals)
    ctx.galaxies.columns.extend(["x", "y"])
    ctx.stars.x = np.random.uniform(0, par.size_x, n_stars)
    ctx.stars.y = np.random.uniform(0, par.size_y, n_stars)
    ctx.stars.columns.extend(["x", "y"])

    write_catalog_plugin = write_catalog.Plugin(ctx)
    write_catalog_plugin()

    del ctx

    ctx = context.create_ctx(current_filter="r", filters=["r", "i", "z"])
    ctx.parameters = context.create_ctx(
        star_catalog_name=catalog_name + "star.cat",
        galaxy_catalog_name=catalog_name + "gal.cat",
        overwrite=True,
    )
    ctx.parameters["galaxy_catalog_name_dict"] = {
        "r": catalog_name + "gal.cat",
    }
    ctx.parameters["star_catalog_name_dict"] = {"r": catalog_name + "star.cat"}

    read_in_catalog_plugin = read_in_catalog.Plugin(ctx)
    read_in_catalog_plugin()

    assert ctx.galaxies.columns == [
        "r50_weird_name",
        "kappa",
        "int_mag",
        "x",
        "y",
        "bkg_noise_std",
    ]
    assert np.allclose(ctx.galaxies.r50_weird_name, r50)
    assert np.allclose(ctx.galaxies.kappa, kappa)
    assert np.allclose(ctx.galaxies.int_mag, int_mag)
    assert ctx.numgalaxies == int_mag.size

    assert ctx.stars.columns == ["psf_r50", "psf_e1", "int_mag", "x", "y"]
    assert np.allclose(ctx.stars.psf_r50, psf_r50)
    assert np.allclose(ctx.stars.psf_e1, psf_e1)
    assert np.allclose(ctx.stars.int_mag, int_mag[:-1])
    assert ctx.numstars == psf_r50.size

    os.remove(catalog_name + "star.cat")
    os.remove(catalog_name + "gal.cat")
