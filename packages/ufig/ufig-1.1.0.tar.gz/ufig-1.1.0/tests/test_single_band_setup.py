# Copyright (C) 2016 ETH Zurich, Institute for Astronomy

"""
Created on Feb 10, 2015
author: Joerg Herbel
adapted by Silvan Fischbacher, 2024
"""

import os
from unittest.mock import patch

import h5py
import numpy as np
import pytest
from ivy import context

from ufig.config import common
from ufig.plugins import single_band_setup, single_band_setup_intrinsic_only


@pytest.fixture
def ctx():
    seed = np.random.randint(low=0, high=int(1e8))
    gal_nphot_seed_offset = np.random.randint(low=0, high=int(1e8))
    star_nphot_seed_offset = np.random.randint(low=0, high=int(1e8))
    gal_render_seed_offset = np.random.randint(low=0, high=int(1e8))
    star_render_seed_offset = np.random.randint(low=0, high=int(1e8))
    background_seed_offset = np.random.randint(low=0, high=int(1e8))
    size_x = 10000
    size_y = 10000
    filters = ["g", "r", "i", "z", "Y"]
    tile_name = "tile_name"
    image_name_dict = {f: f"{tile_name}_{f}.fits" for f in filters}
    galaxy_catalog_name_dict = {f: f"{tile_name}_{f}.gal.cat" for f in filters}
    star_catalog_name_dict = {f: f"{tile_name}_{f}.star.cat" for f in filters}
    sextractor_catalog_name_dict = {f: f"{tile_name}_{f}.sexcat" for f in filters}
    filepath_sysmaps_dict = {f: f"{tile_name}_{f}_sysmap.h5" for f in filters}
    filepath_psfmodel_input_dict = {f: f"{tile_name}_{f}_psfmodel.h5" for f in filters}
    exp_time_type = "constant"
    n_exp = np.random.randint(low=2, high=5)
    saturation_level_dict = {
        f: np.random.uniform(low=40000, high=300000) for f in filters
    }
    gain_dict = {f: np.random.uniform(low=2, high=30) for f in filters}
    exposure_time_dict = {f: np.random.uniform(low=30, high=120) for f in filters}
    magzero_dict = {f: np.random.uniform(low=25, high=35) for f in filters}
    ctx = context.create_ctx(numgalaxies=10, numstars=5)
    ctx.parameters = context.create_ctx(
        seed=seed,
        gal_nphot_seed_offset=gal_nphot_seed_offset,
        star_nphot_seed_offset=star_nphot_seed_offset,
        gal_render_seed_offset=gal_render_seed_offset,
        star_render_seed_offset=star_render_seed_offset,
        background_seed_offset=background_seed_offset,
        size_x=size_x,
        size_y=size_y,
        filters=filters,
        image_name_dict=image_name_dict,
        galaxy_catalog_name_dict=galaxy_catalog_name_dict,
        star_catalog_name_dict=star_catalog_name_dict,
        sextractor_catalog_name_dict=sextractor_catalog_name_dict,
        filepath_sysmaps_dict=filepath_sysmaps_dict,
        filepath_psfmodel_input_dict=filepath_psfmodel_input_dict,
        exp_time_type=exp_time_type,
        n_exp=n_exp,
        saturation_level_dict=saturation_level_dict,
        gain_dict=gain_dict,
        exposure_time_dict=exposure_time_dict,
        magzero_dict=magzero_dict,
        n_phot_sum_gal_max=np.inf,
        image_precision=common.image_precision,
        catalog_precision=np.float32,
        seed_ngal=seed,
        sysmaps_type="sysmaps_hdf_combined",
        maps_remote_dir=os.getcwd() + "/",
    )

    ctx.current_filter = ctx.parameters.filters[0]
    ctx.galaxies = context.create_ctx(
        columns=["x", "y"],
        int_magnitude_dict={
            f: np.random.uniform(low=10, high=30, size=ctx.numgalaxies) for f in filters
        },
        magnitude_dict={
            f: np.random.uniform(low=10, high=30, size=ctx.numgalaxies) for f in filters
        },
        abs_magnitude_dict={
            f: np.random.uniform(low=10, high=30, size=ctx.numgalaxies) for f in filters
        },
        x=np.random.uniform(low=0, high=size_x, size=ctx.numgalaxies),
        y=np.random.uniform(low=0, high=size_y, size=ctx.numgalaxies),
        int_e1=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        int_e2=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        int_r50=np.random.uniform(low=2, high=5, size=ctx.numgalaxies),
    )
    ctx.stars = context.create_ctx(
        columns=["x", "y"],
        magnitude_dict={
            f: np.random.uniform(low=10, high=30, size=ctx.numstars) for f in filters
        },
        x=np.random.uniform(low=0, high=size_x, size=ctx.numstars),
        y=np.random.uniform(low=0, high=size_y, size=ctx.numstars),
    )

    return ctx


def test_single_band_setup(ctx):
    """
    Test setting up for rendering a single image from multi-band dictionaries.
    """

    par = ctx.parameters
    par_unchanged = par.copy()

    # Execute plugin
    plugin = single_band_setup.Plugin(ctx)
    plugin()

    # Tests
    par = ctx.parameters

    assert str(plugin) == "setup single-band"

    # Seeds
    assert par.gal_nphot_seed_offset == par_unchanged.gal_nphot_seed_offset + 1
    assert par.star_nphot_seed_offset == par_unchanged.star_nphot_seed_offset + 1
    assert par.gal_render_seed_offset == par_unchanged.gal_render_seed_offset + 1
    assert par.gal_render_seed_offset == par_unchanged.gal_render_seed_offset + 1
    assert par.background_seed_offset == par_unchanged.background_seed_offset + 1

    # Image
    assert np.array_equal(ctx.image, np.zeros((par.size_x, par.size_y)))

    # Quantities from dictionaries
    assert par.image_name == par.image_name_dict[ctx.current_filter]
    assert par.galaxy_catalog_name == par.galaxy_catalog_name_dict[ctx.current_filter]
    assert par.star_catalog_name == par.star_catalog_name_dict[ctx.current_filter]
    assert (
        par.sextractor_catalog_name
        == par.sextractor_catalog_name_dict[ctx.current_filter]
    )
    assert par.filepath_sysmaps == par.filepath_sysmaps_dict[ctx.current_filter]
    assert (
        par.filepath_psfmodel_input
        == par.filepath_psfmodel_input_dict[ctx.current_filter]
    )
    assert par.saturation_level == par.saturation_level_dict[ctx.current_filter]
    assert par.gain == par.gain_dict[ctx.current_filter]
    assert par.exposure_time == par.exposure_time_dict[ctx.current_filter]
    assert par.magzero == par.magzero_dict[ctx.current_filter]

    # Galaxy columns
    for col in ctx.galaxies.columns:
        assert len(getattr(ctx.galaxies, col)) == ctx.numgalaxies
    assert np.array_equal(
        ctx.galaxies.int_mag,
        ctx.galaxies.int_magnitude_dict[ctx.current_filter].astype(
            par.catalog_precision
        ),
    )
    assert np.array_equal(
        ctx.galaxies.mag,
        ctx.galaxies.magnitude_dict[ctx.current_filter].astype(par.catalog_precision),
    )

    # Star columns
    for col in ctx.stars.columns:
        assert len(getattr(ctx.stars, col)) == ctx.numstars

    assert np.array_equal(ctx.stars.mag, ctx.stars.magnitude_dict[ctx.current_filter])

    # Check that pre-set shear is not changed
    shear_col_dict = dict(
        gamma1=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        gamma2=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        kappa=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        e1=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        e2=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        r50=np.random.uniform(low=2, high=5, size=ctx.numgalaxies),
    )

    for col, val in shear_col_dict.items():
        setattr(ctx.galaxies, col, val.copy())

    single_band_setup.Plugin(ctx)()

    for col, val in shear_col_dict.items():
        assert np.array_equal(getattr(ctx.galaxies, col), val)


def test_nphot_conversion_constant():
    """
    Test the conversion from magnitude to the number of photons for constant exposure
    time.
    """

    ctx = context.create_ctx(
        parameters=context.create_ctx(gain=4.5, magzero=30.0, n_exp=3)
    )
    par = ctx.parameters

    mag = np.array([18.0, 21.3, 24.5])
    nphot_reference = np.round(10 ** (0.4 * (par.magzero - mag)) * par.gain)
    adu_reference = nphot_reference / par.gain
    nphot = np.empty((10000, mag.size))

    for i in range(nphot.shape[0]):
        nphot[i] = single_band_setup.convert_magnitude_to_nphot_const_texp(
            mag, par, n_exp=par.n_exp
        )

    nphot_mean = np.mean(nphot, axis=0)
    nphot_std = np.std(nphot, axis=0)
    nphot_mean_err = nphot_std / np.sqrt(nphot.shape[0]) / np.sqrt(par.n_exp)

    assert np.allclose(
        nphot_reference / nphot_mean_err, nphot_mean / nphot_mean_err, atol=5
    )
    assert np.all(nphot_reference != nphot_mean)
    assert np.all((nphot_mean / par.gain - adu_reference) / adu_reference < 0.001)


def test_nphot_conversion_variable():
    """
    Test the conversion from magnitude to the number of photons for variable exposure
    time.
    """

    ctx = context.create_ctx(
        parameters=context.create_ctx(
            gain=4.5,
            magzero=30.0,
            n_exp=1,
            exposure_time=1,
            sysmaps_type="sysmaps_hdf_combined",
            maps_remote_dir="",
        )
    )

    par = ctx.parameters

    mag = np.array([16.0, 18.0, 21.3, 24.5])
    nphot_reference = np.round(10 ** (0.4 * (par.magzero - mag)) * par.gain)
    nphot = np.empty((10000, mag.size))

    x = np.array([-1, 0, 1, 2])
    y = np.array(0)
    texp = par.exposure_time * np.array([np.full(3, par.n_exp)])

    with patch(
        "ufig.sysmaps_util.get_hdf_location_exptime"
    ) as get_hdf_location_exptime:
        get_hdf_location_exptime.return_value = None, None
        with patch("ufig.io_util.get_abs_path") as get_abs_path:
            get_abs_path.return_value = None
            with patch("ufig.io_util.load_from_hdf5") as load_from_hdf5:
                load_from_hdf5.return_value = texp

                for i in range(nphot.shape[0]):
                    nphot[
                        i
                    ] = single_band_setup.convert_magnitude_to_nphot_variable_texp(
                        mag, par, x, y, n_exp=par.n_exp
                    )

    nphot_mean = np.mean(nphot, axis=0)
    nphot_std = np.std(nphot, axis=0)
    nphot_mean_err = nphot_std / np.sqrt(nphot.shape[0]) / np.sqrt(par.n_exp)

    assert np.allclose(
        nphot_reference / nphot_mean_err, nphot_mean / nphot_mean_err, atol=5
    )
    assert np.all(nphot_reference != nphot_mean)


def test_single_band_intrinsic_only(ctx):
    par = ctx.parameters

    # Execute plugin
    plugin = single_band_setup_intrinsic_only.Plugin(ctx)
    plugin()

    # Tests
    par = ctx.parameters

    assert str(plugin) == "setup single-band (intrinsic only)"

    # Quantities from dictionaries
    assert par.galaxy_catalog_name == par.galaxy_catalog_name_dict[ctx.current_filter]
    assert par.star_catalog_name == par.star_catalog_name_dict[ctx.current_filter]
    assert (
        par.sextractor_catalog_name
        == par.sextractor_catalog_name_dict[ctx.current_filter]
    )
    assert par.filepath_sysmaps == par.filepath_sysmaps_dict[ctx.current_filter]
    assert (
        par.filepath_psfmodel_input
        == par.filepath_psfmodel_input_dict[ctx.current_filter]
    )
    assert par.saturation_level == par.saturation_level_dict[ctx.current_filter]
    assert par.gain == par.gain_dict[ctx.current_filter]
    assert par.exposure_time == par.exposure_time_dict[ctx.current_filter]
    assert par.magzero == par.magzero_dict[ctx.current_filter]

    # Galaxy columns
    for col in ctx.galaxies.columns:
        assert len(getattr(ctx.galaxies, col)) == ctx.numgalaxies
    assert np.array_equal(
        ctx.galaxies.int_mag,
        ctx.galaxies.int_magnitude_dict[ctx.current_filter].astype(
            par.catalog_precision
        ),
    )
    assert np.array_equal(
        ctx.galaxies.mag,
        ctx.galaxies.magnitude_dict[ctx.current_filter].astype(par.catalog_precision),
    )

    # Star columns
    for col in ctx.stars.columns:
        assert len(getattr(ctx.stars, col)) == ctx.numstars

    assert np.array_equal(ctx.stars.mag, ctx.stars.magnitude_dict[ctx.current_filter])

    # Check that pre-set shear is not changed
    shear_col_dict = dict(
        gamma1=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        gamma2=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        kappa=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        e1=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        e2=np.random.uniform(low=-0.1, high=0.1, size=ctx.numgalaxies),
        r50=np.random.uniform(low=2, high=5, size=ctx.numgalaxies),
    )

    for col, val in shear_col_dict.items():
        setattr(ctx.galaxies, col, val.copy())

    single_band_setup_intrinsic_only.Plugin(ctx)()

    for col, val in shear_col_dict.items():
        assert np.array_equal(getattr(ctx.galaxies, col), val)


def test_single_band_setup_nphot_generators(ctx):
    ctx.parameters.exp_time_type = "constant"
    plugin = single_band_setup.Plugin(ctx)
    plugin()

    nphot_const = ctx.galaxies.nphot.copy()

    with h5py.File(os.path.join(os.getcwd(), "tile_name_g_sysmap.h5"), "w") as f:
        f.create_dataset(
            "map_expt", data=np.random.uniform(low=100, high=400, size=(10000, 10000))
        )
        f.create_dataset(
            "map_gain", data=np.random.uniform(low=2, high=30, size=(10000, 10000))
        )

    ctx.parameters.exp_time_type = "variable"
    plugin = single_band_setup.Plugin(ctx)
    plugin()

    nphot_var = ctx.galaxies.nphot.copy()

    ctx.parameters.exp_time_type = "gain_map"
    plugin = single_band_setup.Plugin(ctx)
    plugin()

    nphot_gain_map = ctx.galaxies.nphot.copy()

    # TODO: make a better test
    assert np.all(nphot_const != nphot_var)
    assert np.all(nphot_const != nphot_gain_map)

    os.remove(os.path.join(os.getcwd(), "tile_name_g_sysmap.h5"))
