# Copyright (C) 2018 ETH Zurich, Institute for Particle Physics and Astrophysics

"""
Created on Aug 16, 2018
author: Joerg Herbel
"""

import io
import sys

import numpy as np
import pytest
from ivy import context

from ufig.plugins import render_galaxies_flexion, render_stars_photon

# TODO: Fix import in ucat by adding init file
# from galsbi.ucat.galaxy_sampling_util import Catalog


class Catalog:
    pass


def create_ctx(n_threads):
    """
    Creates an ivy-context that can be used to execute the galaxy and the star rendering
    plugin.
    :return: ivy-context
    """

    np.random.seed(654)  # s.t. objects are always in the same positions

    ctx = context.create_ctx(image=np.zeros((1000, 1000)))

    par = context.create_ctx(
        seed=102301239,
        gal_render_seed_offset=900,
        star_render_seed_offset=1000,
        size_x=ctx.image.shape[1],
        size_y=ctx.image.shape[0],
        sersicprecision=9,
        gammaprecision=13,
        gammaprecisionhigh=4,
        n_threads_photon_rendering=n_threads,
        psf_flexion_suppression=0.0,
    )
    ctx.parameters = par

    ctx.numgalaxies = 100
    ctx.galaxies = Catalog()
    ctx.galaxies.x = np.random.uniform(low=0, high=par.size_x, size=ctx.numgalaxies)
    ctx.galaxies.y = np.random.uniform(low=0, high=par.size_y, size=ctx.numgalaxies)
    ctx.galaxies.sersic_n = np.full(ctx.numgalaxies, 2)
    ctx.galaxies.nphot = np.full(ctx.numgalaxies, 1000, dtype=int)
    ctx.galaxies.r50 = np.full(ctx.numgalaxies, 3)
    ctx.galaxies.e1 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.e2 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_beta = np.full((ctx.numgalaxies, 1), 3.5)
    ctx.galaxies.psf_fwhm = np.full(ctx.numgalaxies, 2)
    ctx.galaxies.psf_e1 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_e2 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_f1 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_f2 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_g1 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_g2 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_kurtosis = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_dx_offset = np.zeros((ctx.numgalaxies, 1))
    ctx.galaxies.psf_dy_offset = np.zeros((ctx.numgalaxies, 1))

    ctx.numstars = 100
    ctx.stars = Catalog()
    ctx.stars.x = np.random.uniform(low=0, high=par.size_x, size=ctx.numstars)
    ctx.stars.y = np.random.uniform(low=0, high=par.size_y, size=ctx.numstars)
    ctx.stars.nphot = np.full(ctx.numstars, 1000, dtype=int)
    ctx.stars.psf_beta = np.full((ctx.numstars, 1), 3.5)
    ctx.stars.psf_fwhm = np.full(ctx.numstars, 2)
    ctx.stars.psf_e1 = np.zeros(ctx.numstars)
    ctx.stars.psf_e2 = np.zeros(ctx.numstars)
    ctx.stars.psf_f1 = np.zeros(ctx.numstars)
    ctx.stars.psf_f2 = np.zeros(ctx.numstars)
    ctx.stars.psf_g1 = np.zeros(ctx.numstars)
    ctx.stars.psf_g2 = np.zeros(ctx.numstars)
    ctx.stars.psf_kurtosis = np.zeros(ctx.numstars)
    ctx.stars.psf_dx_offset = np.zeros((ctx.numstars, 1))
    ctx.stars.psf_dy_offset = np.zeros((ctx.numstars, 1))

    return ctx


@pytest.mark.slow
def test_threaded_rendering():
    """
    Test the threaded photon rendering of objects. The test compares the average chi^2
    between an image rendered with no threads and and image rendered using threads with
    the average chi^2 obtained from using no threads at all.
    """

    # Suppress print statements concerning number of threads
    sys.stdout = io.StringIO()

    # Render reference image without threads
    ctx_no_threads = create_ctx(1)
    render_galaxies_flexion.Plugin(ctx_no_threads)()
    render_stars_photon.Plugin(ctx_no_threads)()

    # Render images with and without threads
    n_renderings = 100

    images_no_threads = np.empty((n_renderings,) + ctx_no_threads.image.shape)
    images_2_threads = np.empty((n_renderings,) + ctx_no_threads.image.shape)

    for i in range(n_renderings):
        ctx_no_threads_ = create_ctx(1)
        ctx_no_threads_.parameters.seed = i

        ctx_2_threads = create_ctx(2)
        ctx_2_threads.parameters.seed = i + n_renderings

        render_galaxies_flexion.Plugin(ctx_no_threads_)()
        render_stars_photon.Plugin(ctx_no_threads_)()
        render_galaxies_flexion.Plugin(ctx_2_threads)()
        render_stars_photon.Plugin(ctx_2_threads)()

        images_no_threads[i] = ctx_no_threads_.image
        images_2_threads[i] = ctx_2_threads.image

    # Compute average chi^2 and errors for both cases
    chi_sq_0_0 = np.sum((images_no_threads - ctx_no_threads.image) ** 2, axis=(1, 2))
    chi_sq_0_2 = np.sum((images_2_threads - ctx_no_threads.image) ** 2, axis=(1, 2))
    mean_chi_sq_0_0 = np.mean(chi_sq_0_0)
    stdvar_chi_sq_0_0 = np.var(chi_sq_0_0, ddof=1) / n_renderings
    mean_chi_sq_0_2 = np.mean(chi_sq_0_2)
    stdvar_chi_sq_0_2 = np.var(chi_sq_0_2, ddof=1) / n_renderings

    # Check if the two average chi^2 are compatible
    delta_chi_sq = abs(mean_chi_sq_0_0 - mean_chi_sq_0_2)
    assert delta_chi_sq / np.sqrt(stdvar_chi_sq_0_0 + stdvar_chi_sq_0_2) < 1


def create_ctx_small(n_threads):
    """
    Creates an ivy-context that can be used to execute the galaxy and the star rendering
    plugin.
    :return: ivy-context
    """

    np.random.seed(654)  # s.t. objects are always in the same positions

    ctx = context.create_ctx(image=np.zeros((10, 10)))

    par = context.create_ctx(
        seed=102301239,
        gal_render_seed_offset=900,
        star_render_seed_offset=1000,
        size_x=ctx.image.shape[1],
        size_y=ctx.image.shape[0],
        sersicprecision=9,
        gammaprecision=13,
        gammaprecisionhigh=4,
        n_threads_photon_rendering=n_threads,
        psf_flexion_suppression=0.0,
    )
    ctx.parameters = par

    ctx.numgalaxies = 3
    ctx.galaxies = Catalog()
    ctx.galaxies.x = np.random.uniform(low=0, high=par.size_x, size=ctx.numgalaxies)
    ctx.galaxies.y = np.random.uniform(low=0, high=par.size_y, size=ctx.numgalaxies)
    ctx.galaxies.sersic_n = np.full(ctx.numgalaxies, 2)
    ctx.galaxies.nphot = np.full(ctx.numgalaxies, 1000, dtype=int)
    ctx.galaxies.r50 = np.full(ctx.numgalaxies, 3)
    ctx.galaxies.e1 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.e2 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_beta = np.full((ctx.numgalaxies, 1), 3.5)
    ctx.galaxies.psf_fwhm = np.full(ctx.numgalaxies, 2)
    ctx.galaxies.psf_e1 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_e2 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_f1 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_f2 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_g1 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_g2 = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_kurtosis = np.zeros(ctx.numgalaxies)
    ctx.galaxies.psf_dx_offset = np.zeros((ctx.numgalaxies, 1))
    ctx.galaxies.psf_dy_offset = np.zeros((ctx.numgalaxies, 1))

    ctx.numstars = 3
    ctx.stars = Catalog()
    ctx.stars.x = np.random.uniform(low=0, high=par.size_x, size=ctx.numstars)
    ctx.stars.y = np.random.uniform(low=0, high=par.size_y, size=ctx.numstars)
    ctx.stars.nphot = np.full(ctx.numstars, 1000, dtype=int)
    ctx.stars.psf_beta = np.full((ctx.numstars, 1), 3.5)
    ctx.stars.psf_fwhm = np.full(ctx.numstars, 2)
    ctx.stars.psf_e1 = np.zeros(ctx.numstars)
    ctx.stars.psf_e2 = np.zeros(ctx.numstars)
    ctx.stars.psf_f1 = np.zeros(ctx.numstars)
    ctx.stars.psf_f2 = np.zeros(ctx.numstars)
    ctx.stars.psf_g1 = np.zeros(ctx.numstars)
    ctx.stars.psf_g2 = np.zeros(ctx.numstars)
    ctx.stars.psf_kurtosis = np.zeros(ctx.numstars)
    ctx.stars.psf_dx_offset = np.zeros((ctx.numstars, 1))
    ctx.stars.psf_dy_offset = np.zeros((ctx.numstars, 1))

    return ctx


def test_threaded_rendering_small_for_cov():
    """
    This test is just for coverage. It calls the same plugins as the main test
    but with a smaller image size and number of objects such that the rendering
    also works without numba jit compilation.
    """

    # Suppress print statements concerning number of threads
    sys.stdout = io.StringIO()

    # Render reference image without threads
    ctx_no_threads = create_ctx_small(1)
    render_galaxies_flexion.Plugin(ctx_no_threads)()
    render_stars_photon.Plugin(ctx_no_threads)()

    # Render images with and without threads
    n_renderings = 2

    for i in range(n_renderings):
        ctx_no_threads_ = create_ctx(1)
        ctx_no_threads_.parameters.seed = i

        ctx_2_threads = create_ctx(2)
        ctx_2_threads.parameters.seed = i + n_renderings

        render_galaxies_flexion.Plugin(ctx_no_threads_)()
        render_stars_photon.Plugin(ctx_no_threads_)()
        render_galaxies_flexion.Plugin(ctx_2_threads)()
        render_stars_photon.Plugin(ctx_2_threads)()
