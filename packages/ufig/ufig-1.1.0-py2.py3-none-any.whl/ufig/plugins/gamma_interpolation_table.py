# Copyright (c) 2014 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>
"""
Created on Nov 24, 2013
@author: Claudio Bruderer

"""

import os

import numpy as np
from astropy.io import fits
from cosmic_toolbox import file_utils
from ivy.plugin.base_plugin import BasePlugin
from pkg_resources import resource_filename
from scipy.special import gammaincinv

import ufig

NAME = "gamma interpolation table"


def load_intrinsicTable(
    sersicprecision, gammaprecision, gammaprecisionhigh, copy_to_cwd=False
):
    """
    Load the table containing values of the inverse gamma function.

    :param sersicprecision: 2**sersicpresicion points to interpolate the Sersic range
                            [0,10]
    :param gammaprecision: 2*(2**gammaprecision) to interpolate the range [0,1[ where
                            the inverse cdf is evaluated
    :param gammaprecisionhigh: Change of point density at 1-2**(-gammaprecisionhigh)
                               (increased precision close to 1)
    :param copy_to_cwd: Copy the table to the current working directory
    :return intrinsicTable: Table containing values
    """

    filename = (
        f"intrinsic_table_{sersicprecision}_{gammaprecision}_{gammaprecisionhigh}"
    )

    if np.__version__ >= "2.0":
        filename += "_np2"
    filename = filename + ".fits"
    resource_directory = resource_filename(ufig.__name__, "res/intrinsictables/")
    load_filename = os.path.join(resource_directory, filename)
    local_filename = os.path.join(os.getcwd(), filename)

    # copy to local directory (local scratch) if not already there
    if copy_to_cwd and (os.path.exists(local_filename) is False):
        src = os.path.join(resource_directory, filename)
        file_utils.robust_copy(src, local_filename)
        load_filename = local_filename
    elif copy_to_cwd:
        load_filename = local_filename

    try:
        intrinsicTable = fits.getdata(load_filename, ext=0).astype(np.float32)
    except OSError:
        raise OSError(
            "Include gamma_interpolation_table-module or provide matching parameter"
            " values to pre-computed tables"
        ) from None

    return intrinsicTable


def compute_intrinsictable(sersicprecision, gammaprecision, gammaprecisionhigh):
    """
    Compute the table containing values of the inverse gamma function.

    :param sersicprecision: 2**sersicpresicion points to interpolate the Sersic range
                            [0,10]
    :param gammaprecision: 2*(2**gammaprecision) to interpolate the range [0,1[ where
                           the inverse cdf is evaluated
    :param gammaprecisionhigh: Change of point density at 1-2**(-gammaprecisionhigh)
                               (increased precision close to 1)
    :return intrinsicTable: Table containing values
    """

    # gamma lookup has 1<<sersicprecision, and a more precise fit on 1-1/(1<<3) also
    # with 1<<sersicprecision elements
    intrinsicTable = np.empty(
        (
            (1 << sersicprecision) + 1,
            (1 << (gammaprecision + 1)) + 1,
        ),
        dtype=np.float32,
    )
    intrinsicTable[0, 0 : (1 << gammaprecision)] = (
        np.power(
            gammaincinv(
                2e-15,
                np.float32(range(0, 1 << gammaprecision))
                / np.float32(1 << gammaprecision),
            ),
            1e-15,
        )
        / 1e-15
    ).astype(np.float32)
    intrinsicTable[0, (1 << gammaprecision) : (1 << (gammaprecision + 1))] = (
        np.power(
            gammaincinv(
                2e-15,
                1.0
                - 1.0 / np.float32(1 << gammaprecisionhigh)
                + np.float32(range(0, 1 << gammaprecision))
                / np.float32(1 << (gammaprecision + gammaprecisionhigh)),
            ),
            1e-15,
        )
        / 1e-15
    ).astype(np.float32)
    intrinsicTable[0, 1 << (gammaprecision + 1)] = (
        np.power(gammaincinv(2e-15, 1.0 - 1e-6), 1e-15) / 1e-15
    ).astype(np.float32)

    for i in range(1, (1 << sersicprecision) + 1):
        n = 10.0 * np.float32(i << (32 - sersicprecision)) / (np.int64(1) << 32)
        k = gammaincinv(2.0 * n, 0.5)
        intrinsicTable[i, 0 : (1 << gammaprecision)] = (
            np.power(
                gammaincinv(
                    2.0 * n,
                    np.float32(range(0, 1 << gammaprecision))
                    / np.float32(1 << gammaprecision),
                ),
                n,
            )
            / np.power(k, n)
        ).astype(np.float32)
        intrinsicTable[i, (1 << gammaprecision) : (1 << (gammaprecision + 1))] = (
            np.power(
                gammaincinv(
                    2.0 * n,
                    1.0
                    - 1.0 / np.float32(1 << gammaprecisionhigh)
                    + np.float32(range(0, 1 << gammaprecision))
                    / np.float32(1 << (gammaprecision + gammaprecisionhigh)),
                ),
                n,
            )
            / np.power(k, n)
        ).astype(np.float32)
        intrinsicTable[i, 1 << (gammaprecision + 1)] = (
            np.power(gammaincinv(2.0 * n, 1.0 - 1e-6), n) / np.power(k, n)
        ).astype(np.float32)

    return intrinsicTable


class Plugin(BasePlugin):
    """
    Loads, or in case explicitly set or non-existent computes on-the-fly, the table with
    pre-computed values of the inverse gamma function in the range [0,1[ for different
    Sersic indexes in [0,10[ used in the render_galaxies.py-module to sample the radial
    cdf.

    Optionally a new intrinsic_table can furthermore be saved. Desirably not overwriting
    the ones in res/intrinsictables/ unless specifically stated.

    :param sersicprecision: 2**sersicpresicion points to interpolate the Sersic range
                            [0,10]
    :param gammaprecision: 2*(2**gammaprecision) to interpolate the range [0,1[ where
                            the inverse cdf is evaluated
    :param gammaprecisionhigh: Change of point density at 1-2**(-gammaprecisionhigh)
                                (increased precision close to 1)
    :param compute_gamma_table_onthefly: whether or not the interpolation table is
                                         computed on the fly

    :return: Table containing values of the inv gamma function for different Sersic
        values in [0,10] and values in [0,1[

    """

    def __call__(self):
        if self.ctx.parameters.compute_gamma_table_onthefly:
            self.ctx.intrinsicTable = compute_intrinsictable(
                self.ctx.parameters.sersicprecision,
                self.ctx.parameters.gammaprecision,
                self.ctx.parameters.gammaprecisionhigh,
            )
        else:
            self.ctx.intrinsicTable = load_intrinsicTable(
                self.ctx.parameters.sersicprecision,
                self.ctx.parameters.gammaprecision,
                self.ctx.parameters.gammaprecisionhigh,
                self.ctx.parameters.copy_gamma_table_to_cwd,
            )

    def __str__(self):
        return NAME

    def save_new_interpolation_table(self):
        filename = (
            f"intrinsic_table_{self.ctx.parameters.sersicprecision}"
            f"_{self.ctx.parameters.gammaprecision}"
            f"_{self.ctx.parameters.gammaprecisionhigh}"
        )
        if np.__version__ >= "2.0":
            filename += "_np2"
        resource_directory = resource_filename(ufig.__name__, "res/intrinsictables/")

        hdu = fits.PrimaryHDU(data=self.ctx.intrinsicTable)
        try:
            hdu.writeto(resource_directory + filename + ".fits")
        except OSError:
            os.remove(resource_directory + filename + ".fits")
            hdu.writeto(resource_directory + filename + ".fits")
