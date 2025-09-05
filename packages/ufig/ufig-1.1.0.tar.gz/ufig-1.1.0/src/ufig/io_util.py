# Copyright (C) 2015 ETH Zurich, Institute for Astronomy

"""
Created on Nov 3, 2015

author: jakeret
"""

import os

import h5py
import healpy as hp
import numpy as np
from astropy.io import fits
from pkg_resources import resource_filename

DEFAULT_ROOT_PATH = "res/maps/"


def get_local_abs_path(path):
    if ("@" in path and ":/" in path) or os.path.isabs(path):
        abs_path = path
    else:
        parent = os.environ.get("SUBMIT_DIR", os.getcwd())
        abs_path = os.path.join(parent, path)
    return abs_path


def get_abs_path(
    file_name,
    root_path=DEFAULT_ROOT_PATH,
    is_file=True,
    package_name="ufig",
):
    """
    Resolves the absolute path for a file or a directory.

    In case the input is treated as a file (is_file=True), the function tries the
    following steps:
    1) if file_name is already an absolute path, then just return it
    2) if root_path is an absolute path the path is simply concatenated
    3) checking in the ufig package structure
    4) using DarkSkySync

    In case the input should be treated as a directory (is_file=False), the function
    tries the following steps:
    1) if file_name is already an absolute path, then just return it
    2) if root_path is an absolute path the path is simply concatenated
    3) checking in the ufig package structure

    :returns path: local absolute path to the file or directory if possible
    """

    if os.path.isabs(file_name):
        if os.path.exists(file_name):
            return file_name
        else:
            raise OSError(f"Absolute file path not found: {file_name}")

    if os.path.isabs(root_path):
        path = os.path.join(root_path, file_name)

    else:
        resource_directory = resource_filename(package_name, root_path)
        path = os.path.join(resource_directory, file_name)

    if os.path.exists(path):
        return path

    if is_file:
        try:
            from darkskysync import DarkSkySync

            dssync = DarkSkySync()
            path = dssync.load(root_path + file_name)[0]
        except Exception as errmsg:
            raise RuntimeError(
                f"DarkSkySync failed for path {root_path + file_name} \n {errmsg}"
            ) from None

    else:
        raise ValueError(
            f"Unable to construct absolute, existing directory path from {file_name}"
        )

    return path


def load_from_hdf5(file_name, hdf5_keys, hdf5_path="", root_path=DEFAULT_ROOT_PATH):
    """
    Load data stored in a HDF5-file.

    :param file_name: Name of the file.
    :param hdf5_keys: Keys of arrays to be loaded.
    :param hdf5_path: Path within HDF5-file appended to all keys.
    :param root_path: Relative or absolute root path.
    :return: Loaded arrays.
    """

    if str(hdf5_keys) == hdf5_keys:
        hdf5_keys = [hdf5_keys]
        return_null_entry = True
    else:
        return_null_entry = False

    hdf5_keys = [hdf5_path + hdf5_key for hdf5_key in hdf5_keys]

    path = get_abs_path(file_name, root_path=root_path)

    with h5py.File(path, mode="r") as hdf5_file:
        hdf5_data = [hdf5_file[hdf5_key][...] for hdf5_key in hdf5_keys]

    if return_null_entry:
        hdf5_data = hdf5_data[0]

    return hdf5_data


def load_image_chunks(file_name, ext=0, dtype=np.float64, n_pix_per_row=100):
    with fits.open(file_name, memmap=True) as hdul:
        img = np.empty(hdul[ext].shape, dtype=dtype)
        n_chunks = int(np.ceil(hdul[ext].shape[0] / float(n_pix_per_row)))
        for ci in range(n_chunks):
            si, ei = ci * n_pix_per_row, (ci + 1) * n_pix_per_row
            img[si:ei, :] = hdul[ext].data[si:ei, :]

        return img


def load_image(file_name, size_x, size_y, root_path=DEFAULT_ROOT_PATH, ext=0, **kwargs):
    """
    Loads an image from stored in a fits file

    :param file_name: name of the file
    :param size_x: max x size
    :param size_y: max y size
    :param root_path: relative root path
    :param ext: fits extention
    """
    path = get_abs_path(file_name, root_path)
    img = fits.getdata(filename=path, ext=ext, **kwargs)
    shape = img.shape

    if shape[0] > size_y and shape[1] > size_x:
        img = img[:size_y, :size_x]
    elif shape[0] < size_y and shape[1] < size_x:
        raise ValueError("Loaded image is smaller than rendered image")

    return img


def load_hpmap(file_name, root_path, ext=1):
    """
    Loads a healpix map and returns it in the ring-scheme

    :param file_name: name of the file
    :param root_path: relative root path
    :param ext: Extension of Healpix-maps (by default = 1)

    """
    path = get_abs_path(file_name, root_path)

    header = fits.getheader(path, ext=ext)
    tfields = header["TFIELDS"]
    ttypes = [header["TTYPE" + str(i)] for i in range(1, tfields + 1)]

    list_maps = fits.getdata(path, ext=ext)
    maps = [list_maps[ttype] for ttype in ttypes]

    if header["ORDERING"] == "NESTED":
        nside = hp.get_nside(maps[0])
        ring2nest_pixels = hp.ring2nest(nside, np.arange(12 * nside**2))
        maps = [maps[i][ring2nest_pixels] for i in range(len(maps))]

    if tfields == 1:
        return maps[0]
    else:
        return maps


def write_hpmap(maps, file_path, **kwargs):
    """
    Writes Healpix maps ensuring a format that can be loaded easily with fits.getdata()
    and displayed properly with Aladin.

    :param maps: 1 or 3 (given as a list) Healpix maps
    :param file_path: path where maps need to be stored
    """

    hp.write_map(file_path, maps, fits_IDL=False, nest=False, coord="C", **kwargs)
