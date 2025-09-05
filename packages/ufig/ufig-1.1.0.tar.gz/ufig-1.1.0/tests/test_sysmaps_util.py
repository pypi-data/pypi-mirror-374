# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Wed Aug 21 2024


import os

import h5py
import numpy as np
import pytest
from astropy.io import fits
from ivy import context
from pkg_resources import resource_filename

import ufig
from ufig import sysmaps_util


def test_get_hdf_location_exptime():
    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf",
        exp_time_file_name="exp_time.hdf",
        exp_time_file_name_dict={"g": "g_exp_time.hdf", "r": "r_exp_time.hdf"},
    )
    filepath, dataset = sysmaps_util.get_hdf_location_exptime(par, "g")
    assert filepath == "g_exp_time.hdf"
    assert dataset == "data"

    filepath, dataset = sysmaps_util.get_hdf_location_exptime(par)
    assert filepath == "exp_time.hdf"
    assert dataset == "data"

    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf_combined",
        filepath_sysmaps="sysmaps.hdf",
        filepath_sysmaps_dict={"g": "g_sysmaps.hdf", "r": "r_sysmaps.hdf"},
    )
    filepath, dataset = sysmaps_util.get_hdf_location_exptime(par, "g")
    assert filepath == "g_sysmaps.hdf"
    assert dataset == "map_expt"

    filepath, dataset = sysmaps_util.get_hdf_location_exptime(par)
    assert filepath == "sysmaps.hdf"
    assert dataset == "map_expt"

    with pytest.raises(ValueError):
        par.sysmaps_type = "unknown"
        sysmaps_util.get_hdf_location_exptime(par)


def test_get_hdf_location_bgrms():
    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf",
        bkg_rms_file_name="bgrms.hdf",
        bkg_rms_file_name_dict={"g": "g_bgrms.hdf", "r": "r_bgrms.hdf"},
    )
    filepath, dataset = sysmaps_util.get_hdf_location_bgrms(par, "g")
    assert filepath == "g_bgrms.hdf"
    assert dataset == "data"

    filepath, dataset = sysmaps_util.get_hdf_location_bgrms(par)
    assert filepath == "bgrms.hdf"
    assert dataset == "data"

    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf_combined",
        filepath_sysmaps="sysmaps.hdf",
        filepath_sysmaps_dict={"g": "g_sysmaps.hdf", "r": "r_sysmaps.hdf"},
    )
    filepath, dataset = sysmaps_util.get_hdf_location_bgrms(par, "g")
    assert filepath == "g_sysmaps.hdf"
    assert dataset == "map_bsig"

    filepath, dataset = sysmaps_util.get_hdf_location_bgrms(par)
    assert filepath == "sysmaps.hdf"
    assert dataset == "map_bsig"

    with pytest.raises(ValueError):
        par.sysmaps_type = "unknown"
        sysmaps_util.get_hdf_location_bgrms(par)


def test_get_hdf_location_gain():
    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf",
        gain_map_file_name="gain.hdf",
        gain_map_file_name_dict={"g": "g_gain.hdf", "r": "r_gain.hdf"},
    )
    filepath, dataset = sysmaps_util.get_hdf_location_gain(par, "g")
    assert filepath == "g_gain.hdf"
    assert dataset == "data"

    filepath, dataset = sysmaps_util.get_hdf_location_gain(par)
    assert filepath == "gain.hdf"
    assert dataset == "data"

    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf_combined",
        filepath_sysmaps="sysmaps.hdf",
        filepath_sysmaps_dict={"g": "g_sysmaps.hdf", "r": "r_sysmaps.hdf"},
    )
    filepath, dataset = sysmaps_util.get_hdf_location_gain(par, "g")
    assert filepath == "g_sysmaps.hdf"
    assert dataset == "map_gain"

    filepath, dataset = sysmaps_util.get_hdf_location_gain(par)
    assert filepath == "sysmaps.hdf"
    assert dataset == "map_gain"

    with pytest.raises(ValueError):
        par.sysmaps_type = "unknown"
        sysmaps_util.get_hdf_location_gain(par)


def test_get_hdf_location_invvar():
    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf",
        weight_image="invvar.hdf",
        weight_image_dict={"g": "g_invvar.hdf", "r": "r_invvar.hdf"},
    )

    filepath, dataset = sysmaps_util.get_hdf_location_invvar(par, "g")
    assert filepath == "g_invvar.hdf"
    assert dataset == "data"

    filepath, dataset = sysmaps_util.get_hdf_location_invvar(par)
    assert filepath == "invvar.hdf"
    assert dataset == "data"

    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf_combined",
        filepath_sysmaps="sysmaps.hdf",
        filepath_sysmaps_dict={"g": "g_sysmaps.hdf", "r": "r_sysmaps.hdf"},
    )

    filepath, dataset = sysmaps_util.get_hdf_location_invvar(par, "g")
    assert filepath == "g_sysmaps.hdf"
    assert dataset == "map_invv"

    filepath, dataset = sysmaps_util.get_hdf_location_invvar(par)
    assert filepath == "sysmaps.hdf"
    assert dataset == "map_invv"

    with pytest.raises(ValueError):
        par.sysmaps_type = "unknown"
        sysmaps_util.get_hdf_location_invvar(par)


def test_get_path_temp_sextractor_weight():
    par = context.create_ctx(
        tempdir_weight_fits="",
        image_name_dict={"g": "g_image.fits", "r": "r_image.fits"},
    )
    path = sysmaps_util.get_path_temp_sextractor_weight(par, "g")
    assert path == os.path.join(
        resource_filename(ufig.__name__, ""), "g_image.fits__temp_invvar.fits"
    )


def test_write_temp_sextractor_weight():
    par = context.create_ctx(
        sysmaps_type="sysmaps_hdf",
        weight_image="invvar.hdf",
        maps_remote_dir=os.getcwd(),
    )
    with h5py.File(os.path.join(os.getcwd(), "invvar.hdf"), "w") as f:
        f.create_dataset("data", data=np.ones((100, 100)))
    sysmaps_util.write_temp_sextractor_weight(par, "invvar.fits")
    file = fits.open("invvar.fits")
    file_data = file[0].data
    assert np.all(file_data == 1)
    assert file_data.shape == (100, 100)
    file.close()
    os.remove("invvar.fits")
    os.remove("invvar.hdf")


def test_write_temp_sextractor_weights():
    par = context.create_ctx(
        image_name="image.fits",
        sysmaps_type="sysmaps_hdf",
        weight_image="invvar.hdf",
        maps_remote_dir=os.getcwd(),
        sextractor_use_forced_photo=True,
        sextractor_forced_photo_detection_band="r",
        image_name_dict={"g": "g_image.fits", "r": "r_image.fits"},
        weight_image_dict={"g": "g_invvar.hdf", "r": "r_invvar.hdf"},
        filters=["g", "r"],
    )

    with h5py.File(os.path.join(os.getcwd(), "invvar.hdf"), "w") as f:
        f.create_dataset("data", data=np.ones((100, 100)))

    filepath_photo, filepath_detection = sysmaps_util.write_temp_sextractor_weights(
        par, ""
    )
    assert filepath_photo == os.path.join(
        resource_filename(ufig.__name__, ""), "image.fits__temp_invvar.fits"
    )
    assert filepath_detection is None
    os.remove(filepath_photo)

    par.weight_image = "invvar.fits"
    filepath_photo, filepath_detection = sysmaps_util.write_temp_sextractor_weights(
        par, ""
    )
    assert filepath_photo == "invvar.fits"

    os.remove("invvar.hdf")
