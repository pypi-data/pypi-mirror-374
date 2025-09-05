# Copyright (c) 2014 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>

"""
Created on Nov 10, 2014
@author: Claudio Bruderer
"""

from unittest.mock import patch

import healpy as hp
import numpy as np
from ivy import context

from ufig import coordinate_util
from ufig.plugins import add_lensing


def test_grf():
    """
    Test properties of a variable shear field. The test creates mock maps and compares
    their values to shear values generated using the maps.
    """

    # Create mock shear maps
    nside = 1024
    npix = hp.nside2npix(nside)
    random_map = np.random.uniform(low=1, high=2, size=npix).astype(np.float32)
    g1_map = np.random.uniform(low=-0.03, high=0.03, size=npix).astype(np.float32)
    g2_map = np.random.uniform(low=-0.03, high=0.03, size=npix).astype(np.float32)

    # Setup context to run plugin
    ctx = context.create_ctx(numgalaxies=100, numstars=0)
    ctx.parameters = context.create_ctx(
        ra0=30,
        dec0=-10,
        pixscale=0.263,
        size_x=1000,
        size_y=1000,
        crpix_ra=500.5,
        crpix_dec=500.5,
        maps_remote_dir="",
        shear_maps="shear_maps.fits",
        shear_type="grf_sky",
        g1_prefactor=1,
        nside_sampling=256,
    )

    par = ctx.parameters

    ctx.galaxies = context.create_ctx(
        x=np.random.uniform(0, par.size_x, size=ctx.numgalaxies).astype(np.float32),
        y=np.random.uniform(0, par.size_y, size=ctx.numgalaxies).astype(np.float32),
        int_e1=np.random.normal(0.0, 0.15, ctx.numgalaxies),
        int_e2=np.random.normal(0.0, 0.25, ctx.numgalaxies),
        int_r50=np.ones(ctx.numgalaxies) * 3.85,
        int_mag=np.ones(ctx.numgalaxies) * 19.4,
    )

    gal = ctx.galaxies

    # Run plugin
    with patch("ufig.io_util.load_hpmap") as mock_load_hpmap:
        mock_load_hpmap.return_value = (random_map, g1_map, g2_map)
        plugin = add_lensing.Plugin(ctx)
        plugin()

    # Test variable parameters
    w = coordinate_util.tile_in_skycoords(
        pixscale=par.pixscale,
        ra0=par.ra0,
        dec0=par.dec0,
        crpix_ra=par.crpix_ra,
        crpix_dec=par.crpix_dec,
    )
    theta, phi = coordinate_util.xy2thetaphi(w, gal.x, gal.y)
    pix_indices = hp.ang2pix(nside, theta, phi)

    # Test shear components
    assert np.allclose(gal.gamma1, g1_map[pix_indices], atol=0.0001)
    assert np.allclose(gal.gamma2, g2_map[pix_indices], atol=0.0001)

    # Test addition of shear components
    trace = g1_map[pix_indices] * gal.int_e1 + g2_map[pix_indices] * gal.int_e2
    ref_e1 = gal.int_e1 + 2 * g1_map[pix_indices] - 2 * gal.int_e1 * trace
    ref_e2 = gal.int_e2 + 2 * g2_map[pix_indices] - 2 * gal.int_e2 * trace

    assert np.allclose(ref_e1, gal.e1, rtol=0.001)
    assert np.allclose(ref_e2, gal.e2, rtol=0.001)

    # Test that other quantities are not affected
    assert np.allclose(gal.kappa, 0, atol=0.001)
    assert np.allclose(gal.r50, gal.int_r50, rtol=0.001)
    assert np.allclose(gal.mag, gal.int_mag, rtol=0.001)


def test_constant_shear():
    """
    Test how shear is added to the effective ellipticity at catalog-level and the
    properties of the shear field"""

    ctx = context.create_ctx()
    ctx.parameters = context.create_ctx(
        shear_type="constant", g1_constant=0.02, g2_constant=-0.03
    )
    ctx.numgalaxies = 1
    ctx.galaxies = context.create_ctx(
        int_e1=np.array([0.3]),
        int_e2=np.array([-0.25]),
        int_r50=np.array([4.3]),
        int_mag=np.array([23]),
    )

    lensing_plugin = add_lensing.Plugin(ctx)
    lensing_plugin()

    par = ctx.parameters
    gal = ctx.galaxies
    trace = par.g1_constant * gal.int_e1 + par.g2_constant * gal.int_e2
    ref_e1 = gal.int_e1 + 2 * par.g1_constant - 2 * gal.int_e1 * trace
    ref_e2 = gal.int_e2 + 2 * par.g2_constant - 2 * gal.int_e2 * trace

    assert np.allclose(ref_e1, gal.e1, rtol=0.001)
    assert np.allclose(ref_e2, gal.e2, rtol=0.001)
    assert np.allclose(gal.gamma1, par.g1_constant, rtol=0.001)
    assert np.allclose(gal.gamma2, par.g2_constant, rtol=0.001)
    assert np.allclose(gal.kappa, 0, atol=0.001)
    assert np.allclose(gal.r50, gal.int_r50, rtol=0.001)
    assert np.allclose(gal.mag, gal.int_mag, rtol=0.001)


def test_zero_shear_map():
    """
    Test specific case of user defined zero shear map
    """

    ctx = context.create_ctx()
    ctx.parameters = context.create_ctx(
        ra0=30,
        dec0=-10,
        pixscale=0.263,
        size_x=1000,
        size_y=1000,
        shear_type="grf_sky",
        shear_maps="zeros",
        g1_prefactor=1,
        maps_remote_dir=None,
    )
    ctx.numgalaxies = 1
    ctx.galaxies = context.create_ctx(
        x=np.array([10.0]),
        y=np.array([10.0]),
        int_e1=np.array([0.3]),
        int_e2=np.array([-0.25]),
        int_r50=np.array([4.3]),
        int_mag=np.array([23]),
    )

    add_lensing.Plugin(ctx)()

    assert np.all(ctx.galaxies.gamma1 == 0)
    assert np.all(ctx.galaxies.gamma2 == 0)
