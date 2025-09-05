"""
Created on Mar 11, 2014
@author: Chihway Chang, Lukas Gamper
"""

from unittest import mock

import numpy as np
from ivy import context

from ufig.plugins import background_noise


def test_background_noise_gaussian():
    ctx = context.create_ctx(
        parameters=context.create_ctx(
            seed=0,
            background_seed_offset=2,
            background_sigma=1,
            background_type="gaussian",
            bkg_noise_amp=5,
            bkg_noise_multiply_gain=False,
            bkg_amp_variation_sigma=0,
            bkg_noise_variation_sigma=0,
            size_x=1000,
            size_y=1000,
        ),
        image=np.zeros((1000, 1000), dtype=np.float64),
    )
    plugin = background_noise.Plugin(ctx)
    assert plugin.__str__() == "add background noise"

    plugin()
    assert np.all(ctx.image != 0)
    assert np.allclose(np.mean(ctx.image), ctx.parameters.bkg_noise_amp, atol=1e-2)
    assert np.allclose(np.std(ctx.image), ctx.parameters.background_sigma, atol=1e-2)


def test_background_noise_map():
    background_sigma = 5
    bkg_noise_amp = 0
    size_x = 1000
    size_y = 1000

    ctx = context.create_ctx(
        parameters=context.create_ctx(
            seed=184,
            background_seed_offset=0,
            bkg_noise_scale=1,
            bkg_noise_amp=bkg_noise_amp,
            maps_remote_dir="",
            bkg_rms_file_name="",
            bkg_noise_multiply_gain=False,
            bkg_amp_variation_sigma=0,
            bkg_noise_variation_sigma=0,
            sysmaps_type="sysmaps_hdf",
            background_type="map",
        ),
        image=np.zeros((size_y, size_x), dtype=np.float64),
    )

    plugin = background_noise.Plugin(ctx)
    with mock.patch("ufig.io_util.load_from_hdf5") as getdata_mock:
        getdata_mock.return_value = background_sigma * np.ones_like(ctx.image)
        plugin()

    assert np.allclose(np.mean(ctx.image), bkg_noise_amp, atol=1e-2)
    assert np.allclose(np.std(ctx.image), background_sigma, atol=1e-2)


# @pytest.mark.skip(reason="something wrong, let's fix it later")
def test_background_chunked_map():
    background_sigma = 5
    bkg_noise_amp = 0
    size_x = 1000
    size_y = 1000

    ctx = context.create_ctx(
        parameters=context.create_ctx(
            seed=184,
            background_seed_offset=0,
            bkg_noise_scale=1,
            bkg_noise_amp=bkg_noise_amp,
            bkg_amp_variation_sigma=0,
            bkg_noise_variation_sigma=0,
            maps_remote_dir="",
            filepath_sysmaps="",
            bkg_noise_multiply_gain=False,
            sysmaps_type="sysmaps_hdf_combined",
            background_type="chunked_map",
            chunksize=250,
        ),
        image=np.zeros((size_y, size_x), dtype=np.float64),
        image_mask=np.ones((size_y, size_x), dtype=np.float64),
    )

    plugin = background_noise.Plugin(ctx)

    with mock.patch("h5py.File", autospec=True) as h5py_mock:
        file_mock = mock.MagicMock()
        file_mock.__enter__.return_value = {
            "map_bsig": background_sigma * np.ones_like(ctx.image)
        }
        h5py_mock.return_value = file_mock
        plugin()

    assert np.allclose(np.mean(ctx.image), bkg_noise_amp, atol=1e-2)
    assert np.allclose(np.std(ctx.image), background_sigma, atol=1e-2)


def test_background_noise_variations():
    ctx = context.create_ctx(
        parameters=context.create_ctx(
            seed=0,
            background_seed_offset=2,
            background_sigma=1,
            background_type="gaussian",
            bkg_noise_amp=5,
            bkg_noise_multiply_gain=False,
            bkg_amp_variation_sigma=0,
            bkg_noise_variation_sigma=0,
            size_x=1000,
            size_y=1000,
        ),
        image=np.zeros((1000, 1000), dtype=np.float64),
    )
    plugin = background_noise.Plugin(ctx)
    assert plugin.__str__() == "add background noise"

    plugin()
    image_1 = ctx.image.copy()

    ctx.parameters.bkg_amp_variation_sigma = 1
    ctx.parameters.bkg_noise_variation_sigma = 1
    plugin()

    assert np.all(ctx.image != 0)
    assert not np.allclose(image_1, ctx.image, atol=1e-2)


def test_background_noise_variations_map():
    background_sigma = 1
    bkg_noise_amp = 0
    size_x = 1000
    size_y = 1000

    ctx = context.create_ctx(
        parameters=context.create_ctx(
            seed=184,
            background_seed_offset=0,
            bkg_noise_scale=1,
            bkg_noise_amp=bkg_noise_amp,
            maps_remote_dir="",
            bkg_rms_file_name="",
            bkg_noise_multiply_gain=False,
            bkg_amp_variation_sigma=0,
            bkg_noise_variation_sigma=0,
            sysmaps_type="sysmaps_hdf",
            background_type="map",
        ),
        image=np.zeros((size_y, size_x), dtype=np.float64),
    )

    plugin = background_noise.Plugin(ctx)
    with mock.patch("ufig.io_util.load_from_hdf5") as getdata_mock:
        getdata_mock.return_value = background_sigma * np.ones_like(ctx.image)
        plugin()

    image_1 = ctx.image.copy()

    ctx.parameters.bkg_amp_variation_sigma = 1
    ctx.parameters.bkg_noise_variation_sigma = 1
    with mock.patch("ufig.io_util.load_from_hdf5") as getdata_mock:
        getdata_mock.return_value = background_sigma * np.ones_like(ctx.image)
        plugin()

    assert np.all(ctx.image != 0)
    assert not np.allclose(image_1, ctx.image, atol=1e-2)
