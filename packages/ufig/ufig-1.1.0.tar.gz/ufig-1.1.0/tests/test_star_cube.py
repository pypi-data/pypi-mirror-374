# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Thu Aug 29 2024


import numpy as np
import pytest
from ivy import context

from ufig import sampling_util
from ufig.plugins import render_stars_photon


@pytest.fixture
def create_ctx():
    n_stars = 100
    ctx = context.create_ctx(
        numstars=n_stars,
    )
    ctx.parameters = context.create_immutable_ctx(
        seed=0,
        star_render_seed_offset=0,
        gain=np.random.uniform(1, 4, size=n_stars),
        magzero=np.random.uniform(10, 20, size=n_stars),
        n_exp=np.ones(n_stars, dtype=np.int32),
        size_x=10,
        size_y=10,
        psf_flexion_suppression=0,
        n_threads_photon_rendering=1,
    )

    ctx.stars = sampling_util.Catalog()
    ctx.stars.x = np.random.uniform(0, ctx.parameters.size_x, size=n_stars)
    ctx.stars.y = np.random.uniform(0, ctx.parameters.size_y, size=n_stars)
    ctx.stars.psf_fwhm = np.random.uniform(5, 7, size=n_stars)
    ctx.stars.psf_e1 = np.random.uniform(-0.5, 0.5, size=n_stars)
    ctx.stars.psf_e2 = np.random.uniform(-0.5, 0.5, size=n_stars)
    ctx.stars.psf_f1 = np.random.uniform(0.5, 2, size=n_stars)
    ctx.stars.psf_f2 = np.random.uniform(0.5, 2, size=n_stars)
    ctx.stars.psf_g1 = np.random.uniform(0.5, 2, size=n_stars)
    ctx.stars.psf_g2 = np.random.uniform(0.5, 2, size=n_stars)
    ctx.stars.psf_kurtosis = np.random.uniform(0.5, 2, size=n_stars)
    ctx.stars.psf_beta = np.array([[2.5]])
    ctx.stars.psf_beta = np.tile(ctx.stars.psf_beta, (n_stars, 1))
    ctx.stars.nphot = np.random.uniform(1, 100, size=n_stars)
    ctx.stars.psf_dx_offset = np.zeros((n_stars, 1))
    ctx.stars.psf_dy_offset = np.zeros((n_stars, 1))
    return ctx


def test_star_cube(create_ctx):
    ctx = create_ctx.copy()
    ctx.star_cube = np.zeros(
        (ctx.numstars, ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
    )
    plugin = render_stars_photon.Plugin(ctx)
    plugin()

    assert len(ctx.stars.q_xx) == ctx.numstars
    assert len(ctx.stars.q_yy) == ctx.numstars
    assert len(ctx.stars.q_xy) == ctx.numstars
    assert np.all(ctx.stars.q_xx != 0)
    assert np.all(ctx.stars.q_yy != 0)
    assert np.all(ctx.stars.q_xy != 0)

    # this is the the image of all stars of the star cube
    image = ctx.star_cube.sum(axis=0)

    ctx2 = create_ctx.copy()
    ctx2.image = np.zeros(
        (ctx2.parameters.size_y, ctx2.parameters.size_x), dtype=np.float64
    )

    plugin2 = render_stars_photon.Plugin(ctx2)
    plugin2()

    # the image of all stars of the star cube should be the same as the image of all
    # stars
    assert np.all(ctx2.image == image)
