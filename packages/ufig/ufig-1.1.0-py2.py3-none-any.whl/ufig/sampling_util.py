# Copyright (C) 2018 ETH Zurich, Institute for Particle Physics and Astrophysics

"""
Created on Mar 6, 2018
author: Joerg Herbel
"""

import warnings

import healpy as hp
import numpy as np

from . import coordinate_util

warnings.filterwarnings("once")


class Catalog:
    pass


def sample_position_uniform(numobj, w, pixel_index, nside):
    """
    Sample a Healpix pixel uniformly

    :param numobj: Number of uniform samples
    :param w: wcs-object containing all the relevant wcs-information
    :param pixel_index: Index of the Healpix pixels sampled
    :param nside: NSIDE of the Healpix map
    :return: Uniformly drawn x-coordinate (in pixels)
    :return: Uniformly drawn y-coordinate (in pixels)
    """

    corners = hp.boundaries(nside, pixel_index, 1)
    theta, phi = hp.vec2ang(np.transpose(corners))

    # removing this as it will cause sampling uniform to sample over too big range and
    # the while loop to take forever the subsequent code should handle this
    phi[phi > np.pi] -= 2 * np.pi  # To deal with periodic boundaries

    cos_theta_sample = np.random.uniform(
        low=np.min(np.cos(theta)), high=np.max(np.cos(theta)), size=numobj
    )
    phi_sample = np.random.uniform(low=np.min(phi), high=np.max(phi), size=numobj)

    n_reps = 0

    while True:
        mask = hp.ang2pix(nside, np.arccos(cos_theta_sample), phi_sample) != pixel_index

        if np.sum(mask) == 0:
            break

        cos_theta_sample[mask] = np.random.uniform(
            low=np.min(np.cos(theta)), high=np.max(np.cos(theta)), size=np.sum(mask)
        )

        phi_sample[mask] = np.random.uniform(
            low=np.min(phi), high=np.max(phi), size=np.sum(mask)
        )

        n_reps += 1

        if n_reps > 10_000:
            raise RuntimeError("more than 10_000 many iterations")
    if w is None:
        # If no wcs is provided, ra and dec are returned
        return coordinate_util.thetaphi2radec(np.arccos(cos_theta_sample), phi_sample)
    else:
        # If a wcs is provided, x and y are returned
        return coordinate_util.thetaphi2xy(w, np.arccos(cos_theta_sample), phi_sample)
