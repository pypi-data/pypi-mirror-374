# Copyright (c) 2014 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>
"""
Created on Nov 4, 2014
@author: Claudio Bruderer

"""

import healpy as hp
import numpy as np
from ivy.plugin.base_plugin import BasePlugin

from ufig import io_util

from .. import coordinate_util

NAME = "add shear"


def shear_constant(numgalaxies, par):
    """
    Generates a constant shear field at the location of each galaxy

    :param numgalaxies: number of galaxies, i.e. number of samples
    :param par: ctx.parameters; part of ctx containing parameters
    :return: Shear 1-component
    :return: Shear 2-component
    """

    gamma1 = np.ones(numgalaxies) * par.g1_constant
    gamma2 = np.ones(numgalaxies) * par.g2_constant
    return gamma1, gamma2


def load_shear_skymaps(shear_maps, g1_prefactor, maps_remote_dir=""):
    """
    Load the map containing a realization on the whole sphere of a given input angular
    power spectrum for the shear

    :param shear_maps: File name of the shear maps
    :param g1_prefactor: Prefactor to account for a potential flipping of the shear
                         g1-map
    :param maps_remote_dir: Root directory where maps are stored
    :return gamma1_map: Realization of a shear-cl, 1-component
    :return gamma2_map: Realization of a shear-cl, 2-component
    """

    if shear_maps == "zeros":
        npix = hp.nside2npix(1)
        g1_map = np.zeros(npix, dtype=np.float32)
        g2_map = np.zeros(npix, dtype=np.float32)

    else:
        maps = io_util.load_hpmap(shear_maps, maps_remote_dir)
        g1_map = g1_prefactor * maps[1].astype(
            np.float32
        )  # Minus sign is HEALPix convention
        g2_map = maps[2].astype(np.float32)

    return g1_map, g2_map


def shear_from_sky_map(gamma1_map, gamma2_map, w, x, y):
    """
    Given an input gamma1 and gamma2 map, sample it at positions (x, y) to get input
    shear

    :param gamma1_map: Map containing gamma1 information
    :param gamma2_map: Map containing gamma2 information
    :param w: wcs-object containing all the relevant wcs-transformation information
    :param x: pixel x-coordinate
    :param y: pixel y-coordinate
    :return gamma1: Array containing the sampled gamma1 values
    :return gamma2: Array containing the sampled gamma2 values
    """

    theta, phi = coordinate_util.xy2thetaphi(w, x, y)

    # gamma1 = hp.get_interp_val(gamma1_map, theta=theta, phi=phi, nest=False)
    # gamma2 = hp.get_interp_val(gamma2_map, theta=theta, phi=phi, nest=False)
    nside = hp.get_nside(gamma1_map)

    pix_indices = hp.ang2pix(nside=nside, theta=theta, phi=phi, nest=False)
    gamma1 = gamma1_map[pix_indices]
    gamma2 = gamma2_map[pix_indices]

    return gamma1, gamma2


def add_shear(int_e1, int_e2, gamma1, gamma2):
    """
    Function that adds shear and the intrinsic ellipticity in the weak shear regime
    (small values of gamma1 and gamma2) for the ellipticity definition
    (a**2 - b**2) / (a**2 + b**2)

    :param int_e1: Intrinsic ellipticity 1-component
    :param int_e2: Intrinsic ellipticity 2-component
    :param gamma1: Shear 1-component
    :param gamma2: Shear 1-component
    :return e1: Effective ellipticity 1-component
    :return e2: Effective ellipticity 2-component
    """

    int_e1_e2 = int_e1 * int_e2
    e1 = int_e1 + 2 * gamma1 * (1 - int_e1**2) - 2 * gamma2 * int_e1_e2
    e2 = int_e2 + 2 * gamma2 * (1 - int_e2**2) - 2 * gamma1 * int_e1_e2
    return e1, e2


class Plugin(BasePlugin):
    """
    Shear and magnification are applied to the input galaxy catalog and
    combined into an effective ellipticity, magnitude, and size

    :param numgalaxies: number of galaxies
    :param shear_type: whether a constant or variable shear is added
    :param int_e1: Intrinsic ellipticity 1-component
    :param int_e2: Intrinsic ellipticity 2-component
    :param int_mag: Intrinsic magnitude
    :param int_r50: Intrinsic r50-radius

    :return gamma1: Shear 1-component at every galaxy location
    :return gamma2: Shear 2-component at every galaxy location
    :return e1: Effective ellipticity 1-component at every galaxy location
    :return e2: Effective ellipticity 1-component at every galaxy location
    :return kappa: Kappa at every galaxy location
    :return mag: Effective magnitude of every galaxy
    :return r50: Effective size of every galaxy
    """

    def __str__(self):
        return NAME

    def __call__(self):
        par = self.ctx.parameters

        if par.shear_type == "constant":
            self.ctx.galaxies.gamma1, self.ctx.galaxies.gamma2 = shear_constant(
                self.ctx.numgalaxies, par
            )
        elif par.shear_type == "grf_sky":
            gamma1_map, gamma2_map = load_shear_skymaps(
                par.shear_maps, par.g1_prefactor, par.maps_remote_dir
            )
            try:
                w = coordinate_util.tile_in_skycoords(
                    pixscale=par.pixscale,
                    ra0=par.ra0,
                    dec0=par.dec0,
                    crpix_ra=par.crpix_ra,
                    crpix_dec=par.crpix_dec,
                )
            except (
                AttributeError
            ):  # TODO: This is only here as transition! Remove at some point
                par.crpix_ra = par.size_x / 2 + 0.5
                par.crpix_dec = par.size_y / 2 + 0.5

                w = coordinate_util.tile_in_skycoords(
                    pixscale=par.pixscale,
                    ra0=par.ra0,
                    dec0=par.dec0,
                    crpix_ra=par.crpix_ra,
                    crpix_dec=par.crpix_dec,
                )

            self.ctx.galaxies.gamma1, self.ctx.galaxies.gamma2 = shear_from_sky_map(
                gamma1_map=gamma1_map,
                gamma2_map=gamma2_map,
                w=w,
                x=self.ctx.galaxies.x,
                y=self.ctx.galaxies.y,
            )
        elif par.shear_type == "zero":
            self.ctx.galaxies.gamma1, self.ctx.galaxies.gamma2 = (
                np.zeros_like(self.ctx.galaxies.int_e1),
                np.zeros_like(self.ctx.galaxies.int_e1),
            )

        else:
            raise ValueError(f"unknown shear_type={par.shear_type}")

        self.ctx.galaxies.e1, self.ctx.galaxies.e2 = add_shear(
            self.ctx.galaxies.int_e1,
            self.ctx.galaxies.int_e2,
            self.ctx.galaxies.gamma1,
            self.ctx.galaxies.gamma2,
        )

        # TODO: implement magnification; placeholder at the moment
        self.ctx.galaxies.kappa = np.zeros(self.ctx.numgalaxies, dtype=np.float32)
        self.ctx.galaxies.r50 = self.ctx.galaxies.int_r50 * 1.0
        self.ctx.galaxies.mag = self.ctx.galaxies.int_mag * 1.0
