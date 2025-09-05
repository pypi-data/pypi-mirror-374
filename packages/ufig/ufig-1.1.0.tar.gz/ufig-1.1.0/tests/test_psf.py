# Copyright (c) 2014 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>

"""
Created on Nov 10, 2014
@author: Claudio Bruderer
adapted by Silvan Fischbacher, 2024
"""

import os
from unittest.mock import patch

import h5py
import healpy as hp
import numpy as np
import pytest
from cosmic_toolbox import arraytools as at
from ivy import context

from ufig import coordinate_util
from ufig.plugins import add_psf
from ufig.psf_estimation.correct_brighter_fatter import (
    brighter_fatter_add,
    brighter_fatter_remove,
)


@pytest.fixture
def ctx():
    ctx = context.create_ctx(
        current_filter="i",
    )
    ctx.parameters = context.create_ctx(
        ra0=30,
        dec0=-10,
        nside_sampling=256,
        pixscale=0.25,
        size_x=100,
        size_y=100,
        crpix_ra=50.5,
        crpix_dec=50.5,
        seeing=1.2,
        psf_beta=3.2,
        psf_e1=0.06,
        psf_e2=0.07,
        maps_remote_dir="map_remote_dir/",
        psf_maps="psf_maps.fits",
        psf_r50_factor=1.1,
        psf_r50_shift=0.7,
        psf_e1_factor=2,
        psf_e1_shift=0,
        psf_e2_factor=0.6,
        psf_e2_shift=-0.004,
        psf_e1_prefactor=1,
        catalog_precision=np.float32,
        psf_fwhm_variation_sigma=0,
    )

    return ctx


def test_psf_constant(ctx):
    """
    Test properties of the constant Moffat PSF field.
    """

    par = ctx.parameters
    par.psf_type = "constant_moffat"

    ctx.galaxies = context.create_ctx(x=np.array([1.2]), y=np.array([1.2]))
    ctx.numgalaxies = 1

    ctx.stars = context.create_ctx(x=np.array([2.2]), y=np.array([2.2]))
    ctx.numstars = 1

    psf_plugin = add_psf.Plugin(ctx)
    psf_plugin()

    psf_r50 = ctx.galaxies.psf_r50
    psf_r50_indiv = ctx.galaxies.psf_r50_indiv
    psf_fwhm = ctx.galaxies.psf_fwhm
    psf_beta = ctx.galaxies.psf_beta
    psf_e1 = ctx.galaxies.psf_e1
    psf_e2 = ctx.galaxies.psf_e2
    alpha = par.seeing / par.pixscale / (2 * np.sqrt(2 ** (1 / par.psf_beta[0]) - 1))
    reference_r50 = alpha * np.sqrt(2 ** (1 / (par.psf_beta[0] - 1)) - 1)
    assert np.allclose(psf_r50, reference_r50, rtol=0.001)
    assert np.allclose(psf_r50_indiv[0], reference_r50, rtol=0.001)
    assert np.shape(psf_r50_indiv) == (1, reference_r50.size)
    assert np.allclose(psf_fwhm, par.seeing / par.pixscale, rtol=0.001)
    assert np.allclose(psf_beta, par.psf_beta, rtol=0.001)
    assert np.allclose(psf_e1, par.psf_e1, rtol=0.001)
    assert np.allclose(psf_e2, par.psf_e2, rtol=0.001)

    psf_r50 = ctx.stars.psf_r50
    psf_r50_indiv = ctx.stars.psf_r50_indiv
    psf_fwhm = ctx.stars.psf_fwhm
    psf_beta = ctx.stars.psf_beta
    psf_e1 = ctx.stars.psf_e1
    psf_e2 = ctx.stars.psf_e2
    alpha = par.seeing / par.pixscale / (2 * np.sqrt(2 ** (1 / par.psf_beta[0]) - 1))
    reference_r50 = alpha * np.sqrt(2 ** (1 / (par.psf_beta[0] - 1)) - 1)
    assert np.allclose(psf_r50, reference_r50, rtol=0.001)
    assert np.allclose(psf_r50_indiv[0], reference_r50, rtol=0.001)
    assert np.shape(psf_r50_indiv) == (1, reference_r50.size)
    assert np.allclose(psf_fwhm, par.seeing / par.pixscale, rtol=0.001)
    assert np.allclose(psf_beta, par.psf_beta, rtol=0.001)
    assert np.allclose(psf_e1, par.psf_e1, rtol=0.001)
    assert np.allclose(psf_e2, par.psf_e2, rtol=0.001)

    assert np.allclose(ctx.average_seeing, par.seeing / par.pixscale)


def test_psf_variable(ctx):
    """
    Test properties of a variable Moffat PSF field generated from maps. The test creates
    mock maps and compares their values to PSF sizes and ellipticities generated using
    the maps.
    """

    # Create mock PSF maps
    nside = 1024
    npix = hp.nside2npix(nside)
    r50_map = np.random.uniform(low=1, high=2, size=npix).astype(np.float32)
    e1_map = np.random.uniform(low=0.05, high=0.06, size=npix).astype(np.float32)
    e2_map = np.random.uniform(low=0.03, high=0.04, size=npix).astype(np.float32)

    # Setup context to run plugin
    ctx.numgalaxies = 10
    ctx.numstars = 10
    par = ctx.parameters
    par.psf_type = "maps_moffat"
    ctx.galaxies = context.create_ctx(
        x=np.random.uniform(0, par.size_x, size=ctx.numgalaxies).astype(np.float32),
        y=np.random.uniform(0, par.size_y, size=ctx.numgalaxies).astype(np.float32),
    )
    ctx.stars = context.create_ctx(
        x=np.random.uniform(0, par.size_x, size=ctx.numstars).astype(np.float32),
        y=np.random.uniform(0, par.size_y, size=ctx.numstars).astype(np.float32),
    )

    # Run plugin
    with patch("ufig.io_util.load_hpmap") as mock_load_hpmap:
        mock_load_hpmap.return_value = (r50_map, e1_map, e2_map)
        plugin = add_psf.Plugin(ctx)
        plugin()

    # Test beta parameter (constant)
    assert np.allclose(ctx.galaxies.psf_beta[:, 0], par.psf_beta, atol=1e-6)
    assert np.shape(ctx.galaxies.psf_beta) == (ctx.galaxies.x.size, 1)
    assert np.allclose(ctx.stars.psf_beta[:, 0], par.psf_beta, atol=1e-6)
    assert np.shape(ctx.stars.psf_beta) == (ctx.stars.x.size, 1)

    # Test variable parameters
    w = coordinate_util.tile_in_skycoords(
        pixscale=par.pixscale,
        ra0=par.ra0,
        dec0=par.dec0,
        crpix_ra=par.crpix_ra,
        crpix_dec=par.crpix_dec,
    )
    theta, phi = coordinate_util.xy2thetaphi(
        w,
        np.append(ctx.galaxies.x, ctx.stars.x),
        np.append(ctx.galaxies.y, ctx.stars.y),
    )

    # Get indices of pixels corresponding to the positions of objects
    central_ind = hp.ang2pix(nside, theta, phi, nest=False)

    # Get bounds on the PSF size, i.e. the pixels the objects lie in as well as the
    # surrounding pixel values
    r50_values = r50_map[central_ind]
    r50_values = par.psf_r50_factor * r50_values + par.psf_r50_shift
    e1_values = e1_map[central_ind]
    e1_values = par.psf_e1_prefactor * (
        par.psf_e1_factor * e1_values + par.psf_e1_shift
    )
    e2_values = e2_map[central_ind]
    e2_values = par.psf_e2_factor * e2_values + par.psf_e2_shift

    # Check the evaluated values
    psf_r50 = np.append(ctx.galaxies.psf_r50, ctx.stars.psf_r50)
    assert np.allclose(psf_r50, r50_values, rtol=1e-6)

    psf_e1 = np.append(ctx.galaxies.psf_e1, ctx.stars.psf_e1)
    assert np.allclose(psf_e1, e1_values, rtol=1e-6)

    psf_e2 = np.append(ctx.galaxies.psf_e2, ctx.stars.psf_e2)
    assert np.allclose(psf_e2, e2_values, rtol=1e-6)


def test_alpha_fwhm_r50_transformations():
    # Single beta
    psf_beta = 2.32
    psf_flux_ratio = 1

    psf_r50_ref = 3.8
    alpha_ref = psf_r50_ref / np.sqrt(2 ** (1 / (psf_beta - 1)) - 1)
    psf_fwhm_ref = 2 * alpha_ref * np.sqrt(2 ** (1 / psf_beta) - 1)

    assert np.allclose(
        psf_fwhm_ref,
        add_psf.moffat_r502fwhm(psf_r50_ref, [psf_beta], psf_flux_ratio),
        rtol=1e-6,
    )
    assert np.allclose(
        alpha_ref, add_psf.moffat_r502alpha(psf_r50_ref, [psf_beta]), rtol=1e-6
    )

    assert np.allclose(
        alpha_ref, add_psf.moffat_fwhm2alpha(psf_fwhm_ref, [psf_beta]), rtol=1e-6
    )
    assert np.allclose(
        psf_r50_ref,
        add_psf.moffat_fwhm2r50(psf_fwhm_ref, [psf_beta], psf_flux_ratio),
        rtol=1e-6,
    )

    assert np.allclose(
        psf_fwhm_ref, add_psf.moffat_alpha2fwhm(alpha_ref, [psf_beta]), rtol=1e-6
    )
    assert np.allclose(
        psf_r50_ref, add_psf.moffat_alpha2r50(alpha_ref, [psf_beta]), rtol=1e-6
    )

    # Test inverse transformations
    assert np.allclose(
        alpha_ref,
        add_psf.moffat_r502alpha(
            add_psf.moffat_alpha2r50(alpha_ref, psf_beta), psf_beta
        ),
        rtol=1e-6,
    )
    assert np.allclose(
        alpha_ref,
        add_psf.moffat_fwhm2alpha(
            add_psf.moffat_alpha2fwhm(alpha_ref, psf_beta), psf_beta
        ),
        rtol=1e-6,
    )
    assert np.allclose(
        psf_r50_ref,
        add_psf.moffat_fwhm2r50(
            add_psf.moffat_r502fwhm(psf_r50_ref, psf_beta, psf_flux_ratio),
            psf_beta,
            psf_flux_ratio,
        ),
        rtol=1e-6,
    )

    radii = np.linspace(0.1, 1000 * psf_r50_ref, 1000)
    fluxes = 1 - add_psf.moffat_profile_integrated(radii, psf_beta, psf_flux_ratio)
    assert np.all(np.argsort(fluxes) == np.arange(1000))
    assert np.allclose(fluxes[-1], 1, atol=1e-8)
    assert np.allclose(
        0.5,
        add_psf.moffat_profile_integrated(
            psf_r50_ref / alpha_ref, psf_beta, psf_flux_ratio
        ),
        rtol=1e-6,
    )

    # Multiple betas
    psf_beta = [8.2, 2.32]
    psf_flux_ratio = 0.7
    psf_fwhm_ref = 3.8

    psf_r50_1 = add_psf.moffat_fwhm2r50(psf_fwhm_ref, psf_beta[0], psf_flux_ratio)
    psf_r50_2 = add_psf.moffat_fwhm2r50(psf_fwhm_ref, psf_beta[1], psf_flux_ratio)
    psf_r50_0 = add_psf.moffat_fwhm2r50(psf_fwhm_ref, psf_beta, psf_flux_ratio)

    assert psf_r50_0 > psf_r50_1
    assert psf_r50_0 < psf_r50_2
    assert np.allclose(
        psf_r50_ref,
        add_psf.moffat_r502fwhm(
            add_psf.moffat_fwhm2r50(psf_fwhm_ref, psf_beta, psf_flux_ratio),
            psf_beta,
            psf_flux_ratio,
        ),
        rtol=1e-6,
    )

    radii = np.linspace(0.1, 1000 * psf_r50_0, 1000)
    fluxes = 1 - add_psf.moffat_profile_integrated(radii, psf_beta, psf_flux_ratio)
    assert np.all(np.argsort(fluxes) == np.arange(1000))
    assert np.allclose(fluxes[-1], 1, atol=1e-8)
    alpha_tmp = add_psf.moffat_fwhm2alpha(psf_fwhm_ref, psf_beta[0])
    alpha_1 = add_psf.moffat_fwhm2alpha(
        psf_fwhm_ref, psf_beta
    )  # Gives alpha corresponding to the first component
    assert alpha_1 == alpha_tmp
    assert np.allclose(
        0.5,
        add_psf.moffat_profile_integrated(
            psf_r50_0 / alpha_1, psf_beta, psf_flux_ratio
        ),
        rtol=1e-6,
    )

    psf_beta = np.array([2, 3, 4, 5])
    psf_fwhm = np.array([1, 2, 3, 4])
    psf_r50 = add_psf.moffat_fwhm2r50(psf_fwhm, psf_beta, 1)
    assert np.allclose(
        psf_fwhm, add_psf.moffat_r502fwhm(psf_r50, psf_beta, 1), rtol=1e-6
    )


def create_psf_file(filename):
    n_grid = 100
    y = np.arange(0, int(np.sqrt(n_grid)))
    x = np.arange(0, int(np.sqrt(n_grid)))
    x, y = np.meshgrid(x, y)
    x = x.ravel()
    y = y.ravel()

    grid = dict()
    grid["X_IMAGE"] = x
    grid["Y_IMAGE"] = y
    grid["psf_flux_ratio_ipt"] = np.ones(n_grid) * 0.75 + np.random.normal(
        0, 0.01, n_grid
    )
    grid["psf_fwhm_ipt"] = np.ones(n_grid) * 3.5 + np.random.normal(0, 0.1, n_grid)
    grid["psf_e1_ipt"] = np.ones(n_grid) * -0.01 + np.random.normal(0, 0.003, n_grid)
    grid["psf_e2_ipt"] = np.ones(n_grid) * -0.02 + np.random.normal(0, 0.003, n_grid)
    grid["psf_f1_ipt"] = np.ones(n_grid) * 0.04 + np.random.normal(0, 0.003, n_grid)
    grid["psf_f2_ipt"] = np.ones(n_grid) * -0.07 + np.random.normal(0, 0.003, n_grid)
    grid["psf_g1_ipt"] = np.ones(n_grid) * 0.01 + np.random.normal(0, 0.003, n_grid)
    grid["psf_g2_ipt"] = np.ones(n_grid) * -0.03 + np.random.normal(0, 0.003, n_grid)

    grid = at.dict2rec(grid)

    dtype = np.dtype(
        [
            ("bit1", "<u8"),
            ("bit2", "<u8"),
            ("bit3", "<u8"),
            ("bit4", "<u8"),
            ("bit5", "<u8"),
        ]
    )
    map_pointings = np.zeros((4200, 4200), dtype=dtype)

    map_pointings[:, :2100]["bit1"] = 491893876059824
    map_pointings[:, 2100:]["bit1"] = 517869943128059
    map_pointings[-2100:, :2100]["bit1"] = 491893876059824
    map_pointings[-2100:, 2100:]["bit1"] = 446813865770993

    unseen_pointings = np.array(
        [27, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
    )

    arr_pointings_polycoeffs = np.random.randn(8, 1600) * 0.1
    arr_pointings_polycoeffs[:, 1200:] = 0

    settings_dict = {
        "n_max_refit": 10,
        "n_sigma_clip": 3,
        "poly_order": 4,
        "polynomial_type": b"chebyshev",
        "raise_underdetermined": False,
        "ridge_alpha": np.array(
            [
                2.10634454,
                0.12252799,
                0.5080218,
                0.5080218,
                2.10634454,
                2.10634454,
                1.31113394,
                1.31113394,
            ]
        ),
        "scale_par": np.array(
            [
                [0.8207056, 0.07974097],
                [4.111996, 0.49206895],
                [0.00685191, 0.06655788],
                [0.02508005, 0.03823495],
                [0.00999626, 0.01315519],
                [-0.03712298, 0.02376803],
                [0.01073337, 0.01203464],
                [-0.01422904, 0.01210075],
            ]
        ),
        "scale_pos": np.array([[2100, 2100], [2100, 2100]]),
    }

    par_names = np.array(
        [
            b"psf_flux_ratio_ipt",
            b"psf_fwhm_ipt",
            b"psf_e1_ipt",
            b"psf_e2_ipt",
            b"psf_f1_ipt",
            b"psf_f2_ipt",
            b"psf_g1_ipt",
            b"psf_g2_ipt",
        ],
        dtype=object,
    )
    with h5py.File(filename, "w") as f:
        f.create_dataset("grid_psf", data=grid)
        mp = f.create_dataset("map_pointings", data=map_pointings)
        mp.attrs["n_pointings"] = 49
        f.create_dataset("unseen_pointings", data=unseen_pointings)
        f.create_dataset("arr_pointings_polycoeffs", data=arr_pointings_polycoeffs)
        f.create_dataset("par_names", data=par_names)

        group = f.create_group("settings")
        for key, value in settings_dict.items():
            group.create_dataset(key, data=value)


def test_psf_coadd_cnn_read():
    ctx = context.create_ctx()
    ctx.parameters = context.create_ctx(
        psf_type="coadd_moffat_cnn_read",
        filepath_psfmodel_input="test_psfmodel_input.h5",
        psf_beta=[2, 5],
        psf_kurtosis=0,
        psfmodel_corr_brighter_fatter={
            "c1r": 0.0,
            "c1e1": 0.0,
            "c1e2": 0.0,
            "mag_ref": 22,
            "apply_to_galaxies": False,
        },
        catalog_precision=np.float32,
        psf_fwhm_variation_sigma=0,
    )
    ctx.current_filter = "i"

    ctx.galaxies = context.create_ctx(
        x=np.array([1.2]), y=np.array([1.2]), mag=np.array([22])
    )
    ctx.numgalaxies = 1
    ctx.stars = context.create_ctx(
        x=np.array([2.2]), y=np.array([2.2]), mag=np.array([22])
    )
    ctx.numstars = 1

    create_psf_file(ctx.parameters.filepath_psfmodel_input)

    psf_plugin = add_psf.Plugin(ctx)
    psf_plugin()

    assert np.allclose(ctx.galaxies.psf_beta, ctx.parameters.psf_beta)
    assert np.allclose(ctx.stars.psf_beta, ctx.parameters.psf_beta)

    for p in ctx.psf_column_names:
        assert p in ctx.galaxies
        assert p in ctx.stars

    os.remove(ctx.parameters.filepath_psfmodel_input)


def test_psf_cnn():
    ctx = context.create_ctx()
    ctx.parameters = context.create_ctx(
        psf_type="coadd_moffat_cnn",
        filepath_psfmodel_input="test_psfmodel_input.h5",
        maps_remote_dir=os.getcwd(),
        psf_beta=[2, 5],
        psf_kurtosis=0,
        psfmodel_corr_brighter_fatter={
            "c1r": 0.0,
            "c1e1": 0.0,
            "c1e2": 0.0,
            "mag_ref": 22,
            "apply_to_galaxies": False,
        },
        catalog_precision=np.float32,
        psf_cnn_factors={
            "psf_fwhm_cnn": [0.0, 1.0],
            "psf_e1_cnn": [0.0, 1.0],
            "psf_e2_cnn": [0.0, 1.0],
            "psf_f1_cnn": [0.0, 1.0],
            "psf_f2_cnn": [0.0, 1.0],
            "psf_g1_cnn": [0.0, 1.0],
            "psf_g2_cnn": [0.0, 1.0],
            "psf_kurtosis_cnn": [0.0, 1.0],
            "psf_flux_ratio_cnn": [0, 1.0],
        },
        psf_fwhm_variation_sigma=0,
    )
    ctx.current_filter = "i"

    ctx.galaxies = context.create_ctx(
        x=np.array([1.2]), y=np.array([1.2]), mag=np.array([22])
    )
    ctx.numgalaxies = 1
    ctx.stars = context.create_ctx(
        x=np.array([2.2]), y=np.array([2.2]), mag=np.array([22])
    )
    ctx.numstars = 1
    filename = os.path.join(os.getcwd(), ctx.parameters.filepath_psfmodel_input)
    create_psf_file(filename)

    psf_plugin = add_psf.Plugin(ctx)
    psf_plugin()

    assert np.allclose(ctx.galaxies.psf_beta, ctx.parameters.psf_beta)
    assert np.allclose(ctx.stars.psf_beta, ctx.parameters.psf_beta)

    for p in ctx.psf_column_names:
        assert p in ctx.galaxies
        assert p in ctx.stars

    os.remove(filename)


def test_brighter_fatter():
    col_mag = 22
    col_fwhm = 1.2
    col_e1 = 0.06
    col_e2 = 0.07
    dict_corr = {
        "c1r": 0.1,
        "c1e1": 0.02,
        "c1e2": 0.03,
        "mag_ref": 22,
    }
    col_fwhm_add, col_e1_add, col_e2_add = brighter_fatter_add(
        col_mag, col_fwhm, col_e1, col_e2, dict_corr
    )
    col_fwhm_rem, col_e1_rem, col_e2_rem = brighter_fatter_remove(
        col_mag, col_fwhm_add, col_e1_add, col_e2_add, dict_corr
    )
    assert np.allclose(col_fwhm, col_fwhm_rem)
    assert np.allclose(col_e1, col_e1_rem)
    assert np.allclose(col_e2, col_e2_rem)


def test_psf_variations(ctx):
    par = ctx.parameters
    par.psf_type = "constant_moffat"

    ctx.galaxies = context.create_ctx(
        x=np.random.uniform(0, par.size_x, size=1000).astype(np.float32),
        y=np.random.uniform(0, par.size_y, size=1000).astype(np.float32),
    )
    ctx.numgalaxies = 1000

    psf_plugin = add_psf.Plugin(ctx)
    psf_plugin()

    psf_fwhm = ctx.galaxies.psf_fwhm

    ctx.parameters.psf_fwhm_variation_sigma = 1

    psf_plugin()
    assert not np.allclose(psf_fwhm, ctx.galaxies.psf_fwhm, atol=1)
    assert np.allclose(np.mean(psf_fwhm - ctx.galaxies.psf_fwhm), 0, atol=1e-1)
    assert np.allclose(np.std(ctx.galaxies.psf_fwhm), 1, atol=1e-1)


def test_psf_variations_negative(ctx):
    par = ctx.parameters
    par.psf_type = "constant_moffat"

    ctx.galaxies = context.create_ctx(
        x=np.random.uniform(0, par.size_x, size=1000).astype(np.float32),
        y=np.random.uniform(0, par.size_y, size=1000).astype(np.float32),
    )
    ctx.numgalaxies = 1000

    ctx.stars = context.create_ctx(
        x=np.random.uniform(0, par.size_x, size=1000).astype(np.float32),
        y=np.random.uniform(0, par.size_y, size=1000).astype(np.float32),
    )
    ctx.numstars = 1000

    ctx.parameters.psf_fwhm_variation_sigma = 10
    psf_plugin = add_psf.Plugin(ctx)
    psf_plugin()

    assert np.all(ctx.galaxies.psf_fwhm >= 0)
    assert np.all(ctx.stars.psf_fwhm >= 0)
