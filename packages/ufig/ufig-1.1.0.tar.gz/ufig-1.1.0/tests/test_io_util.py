# Copyright (C) 2015 ETH Zurich, Institute for Astronomy

"""
Created on Nov 3, 2015
author: jakeret
"""

import os
import random
import string
import tempfile
from unittest.mock import patch

import h5py
import healpy as hp
import numpy as np
import pytest
from darkskysync.DarkSkySync import DarkSkySync
from darkskysync.DataSourceFactory import DataSourceFactory
from pkg_resources import resource_filename

import ufig
from ufig import io_util

FILE_NAME = "Cls_smail.txt"


def test_get_abs_path_local():
    # Absolute file name input for existing file
    resource_directory = resource_filename(ufig.__name__, io_util.DEFAULT_ROOT_PATH)
    abspath = os.path.join(resource_directory, FILE_NAME)
    path = io_util.get_abs_path(abspath)
    assert path == abspath

    # Absolute file name input for non-existing file
    abspath = "/" + random.choice(string.ascii_letters + string.digits)
    while os.path.exists(abspath):
        abspath += random.choice(string.ascii_letters + string.digits)

    with pytest.raises(OSError):
        io_util.get_abs_path(abspath)

    # Relative file name input
    path = io_util.get_abs_path(FILE_NAME, io_util.DEFAULT_ROOT_PATH)
    assert path.find(io_util.DEFAULT_ROOT_PATH) >= 0
    assert os.path.basename(path) == FILE_NAME


@patch.object(DataSourceFactory, "fromConfig", autospec=False)
@patch.object(DarkSkySync, "load", autospec=True, side_effect=[[FILE_NAME]])
def test_get_abs_path_remote(dss_object, load_object):
    path = io_util.get_abs_path(FILE_NAME, "test")
    assert path.find(FILE_NAME) >= 0


def test_load_image():
    image = np.ones((10, 10))

    with (
        patch("ufig.io_util.get_abs_path") as _,
        patch("astropy.io.fits.getdata") as getdata_mock,
    ):
        getdata_mock.return_value = np.ones_like(image)

        img = io_util.load_image("dummy", image.shape[1], image.shape[0])
        assert img.shape == image.shape

        getdata_mock.return_value = np.ones((image.shape[1] * 2, image.shape[0] * 2))
        img = io_util.load_image("dummy", image.shape[1], image.shape[0])
        assert img.shape == image.shape

        getdata_mock.return_value = np.ones((image.shape[1] // 2, image.shape[0] // 2))
        with pytest.raises(ValueError):
            _ = io_util.load_image("dummy", image.shape[1], image.shape[0])


def test_write_load_hpmap():
    nside = 16
    path = os.path.join(os.getcwd(), "map.fits")

    # Write dummy map
    hp_map = np.random.uniform(size=hp.nside2npix(nside)).astype(np.float32)
    io_util.write_hpmap(hp_map, path, overwrite=True)

    # Load dummy
    hp_map_load = io_util.load_hpmap(path, None)

    assert np.array_equal(hp_map, hp_map_load)

    os.remove(path)


def test_load_from_hdf5():
    """
    Test the loading of numpy-arrays from a HDF5-file.
    """

    data = np.random.uniform(size=10)
    path = tempfile.mkstemp()[1]

    with h5py.File(path, "w") as f:
        f.create_dataset("data", data=data)
        f.create_group("data2")
        f["data2"].create_dataset("data", data=data)

    x = io_util.load_from_hdf5(path, "data")

    assert np.array_equal(x, data)

    x = io_util.load_from_hdf5(path, "data", hdf5_path="data2/")

    assert np.array_equal(x, data)

    x = io_util.load_from_hdf5(path, ["data"])

    assert np.array_equal(x[0], data)

    x, y = io_util.load_from_hdf5(path, ("data", "data2/data"))

    assert np.array_equal(x, data)
    assert np.array_equal(y, data)


def test_get_local_abs_path_with_remote_path():
    # Test a path with "@" and ":/" in it
    path = "user@server:/path/to/file"
    assert io_util.get_local_abs_path(path) == path


def test_get_local_abs_path_with_absolute_path():
    # Test an absolute path
    path = "/absolute/path/to/file"
    assert io_util.get_local_abs_path(path) == path


def test_get_local_abs_path_with_relative_path_and_submit_dir():
    # Test a relative path with SUBMIT_DIR set in the environment
    relative_path = "relative/path/to/file"
    submit_dir = "/submit/dir"

    with patch.dict(os.environ, {"SUBMIT_DIR": submit_dir}):
        expected_path = os.path.join(submit_dir, relative_path)
        assert io_util.get_local_abs_path(relative_path) == expected_path


def test_get_local_abs_path_with_relative_path_and_no_submit_dir():
    # Test a relative path without SUBMIT_DIR, should use os.getcwd()
    relative_path = "relative/path/to/file"
    current_dir = "/current/working/dir"

    with patch("os.getcwd", return_value=current_dir):
        expected_path = os.path.join(current_dir, relative_path)
        assert io_util.get_local_abs_path(relative_path) == expected_path
