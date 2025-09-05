# Copyright (c) 2014 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>

"""
Created on Sep 15, 2014
@author: Claudio Bruderer

"""

import os

import numpy as np
import pytest
from ivy import context

from ufig.plugins import add_psf, render_stars_photon


@pytest.mark.slow
def test_star_profile1():
    inspect_image(
        seeing=4.0,
        psf_beta=2.5,
        psf_e1=0.3,
        psf_e2=-0.1,
        psf_flux_ratio=1,
        n_threads=1,
        path_hyperpig_img="HYPERPIGimage_Stars_PSF4-0_Beta2-5.txt",
    )


@pytest.mark.slow
def test_star_profile2():
    inspect_image(
        seeing=6.0,
        psf_beta=3.5,
        psf_e1=-0.15,
        psf_e2=-0.2,
        psf_flux_ratio=1,
        n_threads=2,
        path_hyperpig_img="HYPERPIGimage_Stars_PSF6-0_Beta3-5.txt",
    )


@pytest.mark.slow
def test_star_profile3():
    inspect_image(
        seeing=1.9,
        psf_beta=[4.1, 1.9],
        psf_e1=-0.15,
        psf_e2=-0.2,
        psf_flux_ratio=0.7,
        n_threads=1,
        path_hyperpig_img="HYPERPIGimage_Stars_PSF1-9_PSFratio0-7_Beta1_4-1_Beta2_1-9.txt",
    )


def inspect_image(
    seeing, psf_beta, psf_e1, psf_e2, psf_flux_ratio, n_threads, path_hyperpig_img
):
    """
    Simulate an image with UFig and compare it to one simulated with HYPERPIG.

    The requirement is that the number of points below the curve expected from Poisson
    noise up to a radius where this noise is below the 1%-level is within a tolerance
    around 68.3%.
    """

    REQUIREMENT = 0.01
    NBINS = 5

    def create_ctx():
        nonlocal psf_beta

        ctx = context.create_ctx()
        ctx.parameters = context.create_immutable_ctx(
            size_x=101,
            size_y=101,
            pixscale=1,
            gain=1.0,
            seed=102352 + 234,
            n_threads_photon_rendering=n_threads,
            render_stars_accuracy=0.3,
            psf_flexion_suppression=0.0,
        )
        ctx.parameters.seeing = seeing

        if not isinstance(psf_beta, list):
            psf_beta = [psf_beta]

        ctx.stars = context.create_immutable_ctx(
            x=np.array([50.7]),
            y=np.array([51.2]),
            mag=np.array([10]),
            nphot=np.array([10000000000]),
        )

        ctx.stars.psf_beta = np.array([psf_beta])
        ctx.stars.psf_flux_ratio = np.array([psf_flux_ratio])
        ctx.stars.psf_e1 = np.array([psf_e1])
        ctx.stars.psf_e2 = np.array([psf_e2])
        ctx.stars.psf_fwhm = np.full_like(
            ctx.stars.psf_e1, seeing / ctx.parameters.pixscale
        )

        ctx.stars.psf_f1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_f2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_kurtosis = np.zeros_like(ctx.stars.psf_fwhm)

        ctx.stars.psf_dx_offset = np.zeros_like(ctx.stars.psf_beta)
        ctx.stars.psf_dy_offset = np.zeros_like(ctx.stars.psf_beta)

        ctx.numstars = 1

        ctx.image = np.zeros(
            (ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
        )

        return ctx

    def compare_images(executed_ctx, hyperpig_img):
        img_flat = executed_ctx.image.flatten()
        hyperpig_img_flat = hyperpig_img.flatten()

        size_x = executed_ctx.parameters.size_x
        size_y = executed_ctx.parameters.size_y
        X = np.arange(0, size_x) + 0.5
        Y = np.arange(0, size_y) + 0.5
        x, y = np.meshgrid(X, Y)

        x -= executed_ctx.stars.x
        y -= executed_ctx.stars.y
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y.flatten(), x.flatten()).reshape((size_y, size_x))

        e1 = executed_ctx.stars.psf_e1
        e2 = executed_ctx.stars.psf_e2
        enorm = np.sqrt(e1**2 + e2**2)
        theta -= np.arctan2(e2, e1) / 2.0
        radius = r / np.sqrt(1.0 + enorm * (np.cos(theta) ** 2 - np.sin(theta) ** 2))
        radius = radius.flatten()

        poisson = 1.0 / np.sqrt(hyperpig_img_flat)
        poissonmask = poisson >= REQUIREMENT
        rmax = np.min(radius[poissonmask])
        sortradius = np.argsort(radius)
        rmaxindex = np.where(radius[sortradius] == rmax)[0][-1]

        percentagebelowpoisson = np.zeros(NBINS)
        for i in range(NBINS - 1):
            mask = sortradius[(rmaxindex // NBINS) * i : (rmaxindex // NBINS) * (i + 1)]
            reldiff = (
                np.abs(img_flat[mask] - hyperpig_img_flat[mask])
                / hyperpig_img_flat[mask]
            )
            percentagebelowpoisson[i] = float(
                reldiff[reldiff <= poisson[mask]].size
            ) / float(reldiff.size)
        mask = sortradius[(rmaxindex // NBINS) * (NBINS - 1) : rmaxindex + 1]
        reldiff = (
            np.abs(img_flat[mask] - hyperpig_img_flat[mask]) / hyperpig_img_flat[mask]
        )
        percentagebelowpoisson[-1] = float(
            reldiff[reldiff <= poisson[mask]].size
        ) / float(reldiff.size)

        percentages = (
            np.sum(percentagebelowpoisson[:-1]) * (rmaxindex / NBINS)
            + percentagebelowpoisson[-1] * (rmaxindex / NBINS + rmaxindex % NBINS)
        ) / rmaxindex

        assert np.allclose(percentages, 0.683, atol=0.05)
        assert np.allclose(percentagebelowpoisson, 0.683, atol=0.05)

    # Load hyperpig image
    if not os.path.isabs(path_hyperpig_img):
        dirname_tests = os.path.dirname(os.path.abspath(__file__))
        path_hyperpig_img = os.path.join(dirname_tests, path_hyperpig_img)

    hyperpig_image = np.loadtxt(path_hyperpig_img).flatten()

    # Test photon rendering
    ctx = create_ctx()
    ctx.parameters.star_render_seed_offset = 214
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()
    compare_images(ctx, hyperpig_image)

    # Test pixel rendering
    ctx = create_ctx()
    ctx.parameters.star_render_seed_offset = 213
    ctx.parameters.mag_pixel_rendering_stars = np.inf
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()

    compare_images(ctx, hyperpig_image)


def inspect_image_small_for_coverage(
    seeing,
    psf_beta,
    psf_e1,
    psf_e2,
    psf_flux_ratio,
    n_threads,
):
    """
    This test is just for coverage. It calls the same plugins as the main test
    but with a smaller image size and number of objects such that the rendering
    also works without numba jit compilation.
    """

    def create_ctx():
        nonlocal psf_beta

        ctx = context.create_ctx()
        ctx.parameters = context.create_immutable_ctx(
            size_x=10,
            size_y=10,
            pixscale=1,
            gain=1.0,
            seed=102352 + 234,
            n_threads_photon_rendering=n_threads,
            render_stars_accuracy=0.3,
            psf_flexion_suppression=0.0,
        )
        ctx.parameters.seeing = seeing

        if not isinstance(psf_beta, list):
            psf_beta = [psf_beta]

        ctx.stars = context.create_immutable_ctx(
            x=np.array([5.7]),
            y=np.array([5.2]),
            mag=np.array([24]),
            nphot=np.array([100000]),
        )

        ctx.stars.psf_beta = np.array([psf_beta])
        ctx.stars.psf_flux_ratio = np.array([psf_flux_ratio])
        ctx.stars.psf_e1 = np.array([psf_e1])
        ctx.stars.psf_e2 = np.array([psf_e2])
        ctx.stars.psf_fwhm = np.full_like(
            ctx.stars.psf_e1, seeing / ctx.parameters.pixscale
        )

        ctx.stars.psf_f1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_f2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_kurtosis = np.zeros_like(ctx.stars.psf_fwhm)

        ctx.stars.psf_dx_offset = np.zeros_like(ctx.stars.psf_beta)
        ctx.stars.psf_dy_offset = np.zeros_like(ctx.stars.psf_beta)

        ctx.numstars = 1

        ctx.image = np.zeros(
            (ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
        )

        return ctx

    # Test photon rendering
    ctx = create_ctx()
    ctx.parameters.star_render_seed_offset = 214
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()

    # Test pixel rendering
    ctx = create_ctx()
    ctx.parameters.star_render_seed_offset = 213
    ctx.parameters.mag_pixel_rendering_stars = np.inf
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()


def test_star_profile1_small_for_coverage():
    inspect_image_small_for_coverage(
        seeing=4.0,
        psf_beta=2.5,
        psf_e1=0.3,
        psf_e2=-0.1,
        psf_flux_ratio=1,
        n_threads=1,
    )


def test_star_profile2_small_for_coverage():
    inspect_image_small_for_coverage(
        seeing=6.0,
        psf_beta=3.5,
        psf_e1=-0.15,
        psf_e2=-0.2,
        psf_flux_ratio=1,
        n_threads=2,
    )


def test_star_profile3_small_for_coverage():
    inspect_image_small_for_coverage(
        seeing=1.9,
        psf_beta=[4.1, 1.9],
        psf_e1=-0.15,
        psf_e2=-0.2,
        psf_flux_ratio=0.7,
        n_threads=1,
    )


@pytest.mark.slow
def test_star_round():
    """
    Simulate an image with UFig of a round star and compare a slice of the radial
    profile with the analytical profile.
    The requirement is that the number of points below the curve expected from Poisson
    noise up to a radius where this noise is below the 1%-level is within a tolerance
    around 68.3%.
    """

    REQUIREMENT = 0.01

    def create_ctx():
        ctx = context.create_ctx()
        ctx.parameters = context.create_immutable_ctx(
            size_x=101,
            size_y=101,
            pixscale=1,
            gain=1.0,
            seed=102352 + 234,
            star_render_seed_offset=213,
            psf_e1=0.0,
            psf_e2=0.0,
            psf_beta=3.5,
            seeing=10.0,
            psf_flexion_suppression=0.0,
            n_threads_photon_rendering=1,
            render_stars_accuracy=0.3,
        )
        par = ctx.parameters

        ctx.stars = context.create_immutable_ctx(
            x=np.array([50.5]),
            y=np.array([50.5]),
            mag=np.array([10]),
            nphot=np.array([10000000000]),
        )

        add_psf.sample_psf_moffat_constant("stars", ctx)

        ctx.stars.psf_f1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_f2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_kurtosis = np.zeros_like(ctx.stars.psf_fwhm)

        ctx.stars.psf_dx_offset = np.zeros_like(ctx.stars.psf_beta)
        ctx.stars.psf_dy_offset = np.zeros_like(ctx.stars.psf_beta)

        ctx.numstars = 1

        ctx.image = np.zeros((par.size_y, par.size_x), dtype=np.float64)

        return ctx

    def check_image(exec_ctx):
        par = exec_ctx.parameters
        psf_beta = ctx.stars.psf_beta[0, 0]

        radial_slice = exec_ctx.image[par.size_y // 2, par.size_x // 2 :]

        r = np.arange(par.size_x // 2 + 1)
        alpha = par.seeing / 2 / np.sqrt(2 ** (1 / psf_beta) - 1)
        I0 = (psf_beta - 1) / np.pi / alpha**2
        i = ctx.stars.nphot[0] * I0 / (1 + (r / alpha) ** 2) ** psf_beta

        mask = 1 / np.sqrt(i) < REQUIREMENT
        assert np.allclose(radial_slice[mask], i[mask], rtol=0.05)

    # Test photon rendering
    ctx = create_ctx()
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()

    # Test pixel rendering
    ctx = create_ctx()
    ctx.parameters.mag_pixel_rendering_stars = np.inf
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()
    check_image(ctx)


def test_star_round_small_for_coverage():
    """
    This test is just for coverage. It calls the same plugins as the main test
    but with a smaller image size and number of objects such that the rendering
    also works without numba jit compilation.
    """

    def create_ctx():
        ctx = context.create_ctx()
        ctx.parameters = context.create_immutable_ctx(
            size_x=10,
            size_y=10,
            pixscale=1,
            gain=1.0,
            seed=102352 + 234,
            star_render_seed_offset=213,
            psf_e1=0.0,
            psf_e2=0.0,
            psf_beta=3.5,
            seeing=10.0,
            psf_flexion_suppression=0.0,
            n_threads_photon_rendering=1,
            render_stars_accuracy=0.3,
        )
        par = ctx.parameters

        ctx.stars = context.create_immutable_ctx(
            x=np.array([5.5]),
            y=np.array([5.5]),
            mag=np.array([24]),
            nphot=np.array([100000]),
        )

        add_psf.sample_psf_moffat_constant("stars", ctx)

        ctx.stars.psf_f1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_f2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_kurtosis = np.zeros_like(ctx.stars.psf_fwhm)

        ctx.stars.psf_dx_offset = np.zeros_like(ctx.stars.psf_beta)
        ctx.stars.psf_dy_offset = np.zeros_like(ctx.stars.psf_beta)

        ctx.numstars = 1

        ctx.image = np.zeros((par.size_y, par.size_x), dtype=np.float64)

        return ctx

    # Test photon rendering
    ctx = create_ctx()
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()

    # Test pixel rendering
    ctx = create_ctx()
    ctx.parameters.mag_pixel_rendering_stars = np.inf
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()


@pytest.mark.slow
def test_star_rough_shape():
    """
    Simulate an image with UFig of an elliptical star and transform it back to a round
    shape (rotation + stretch). Testing that the resulting shape is approximately round
    (to 0.5 %), gives a rough test of the shape.
    """

    REQUIREMENT = 0.01

    def create_ctx():
        ctx = context.create_ctx()
        ctx.parameters = context.create_immutable_ctx(
            size_x=101,
            size_y=101,
            pixscale=1,
            gain=1.0,
            seed=102352 + 234,
            star_render_seed_offset=213,
            psf_e1=-0.1,
            psf_e2=0.35,
            psf_beta=3.5,
            seeing=10.0,
            psf_flexion_suppression=0.0,
            n_threads_photon_rendering=10,
            render_stars_accuracy=0.3,
        )

        par = ctx.parameters

        ctx.stars = context.create_immutable_ctx(
            x=np.array([50.5]),
            y=np.array([50.5]),
            mag=np.array([10]),
            nphot=np.array([10000000000]),
        )

        add_psf.sample_psf_moffat_constant("stars", ctx)

        ctx.stars.psf_f1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_f2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_kurtosis = np.zeros_like(ctx.stars.psf_fwhm)

        ctx.stars.psf_dx_offset = np.zeros_like(ctx.stars.psf_beta)
        ctx.stars.psf_dy_offset = np.zeros_like(ctx.stars.psf_beta)

        ctx.numstars = (1,)
        ctx.timings = {}

        ctx.image = np.zeros((par.size_y, par.size_x), dtype=np.float64)

        return ctx

    def check_image(exec_ctx):
        par = exec_ctx.parameters

        x = np.arange(par.size_x) + 0.5 - exec_ctx.stars.x
        y = np.arange(par.size_y) + 0.5 - exec_ctx.stars.y
        x, y = np.meshgrid(x, y)

        alpha = np.arctan2(par.psf_e2, par.psf_e1) / 2
        psf_e = np.sqrt(par.psf_e1**2 + par.psf_e2**2)
        stretch = np.sqrt((1 - psf_e) / (1 + psf_e))

        x_rot = (np.cos(alpha) * x + np.sin(alpha) * y) * stretch
        y_rot = -np.sin(alpha) * x + np.cos(alpha) * y
        r_rot = np.sqrt(x_rot**2 + y_rot**2)

        mask = 1 / np.sqrt(exec_ctx.image) < REQUIREMENT
        maxradius = np.max(r_rot[mask])
        mask = r_rot < maxradius

        q11 = np.sum(exec_ctx.image[mask] * x_rot[mask] ** 2)
        q12 = np.sum(exec_ctx.image[mask] * x_rot[mask] * y_rot[mask])
        q22 = np.sum(exec_ctx.image[mask] * y_rot[mask] ** 2)

        assert np.allclose((q11 - q22) / (q11 + q22), 0, atol=0.005)
        assert np.allclose(2 * q12 / (q11 + q22), 0, atol=0.005)

    # Test photon rendering
    ctx = create_ctx()
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()

    # Test pixel rendering
    ctx = create_ctx()
    ctx.parameters.mag_pixel_rendering_stars = np.inf
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()
    check_image(ctx)


def test_star_rough_shape_small_for_coverage():
    """
    This test is just for coverage. It calls the same plugins as the main test
    but with a smaller image size and number of objects such that the rendering
    also works without numba jit compilation.
    """

    def create_ctx():
        ctx = context.create_ctx()
        ctx.parameters = context.create_immutable_ctx(
            size_x=10,
            size_y=10,
            pixscale=1,
            gain=1.0,
            seed=102352 + 234,
            star_render_seed_offset=213,
            psf_e1=-0.1,
            psf_e2=0.35,
            psf_beta=3.5,
            seeing=10.0,
            psf_flexion_suppression=0.0,
            n_threads_photon_rendering=10,
            render_stars_accuracy=0.3,
        )

        par = ctx.parameters

        ctx.stars = context.create_immutable_ctx(
            x=np.array([5.5]),
            y=np.array([5.5]),
            mag=np.array([24]),
            nphot=np.array([100000]),
        )

        add_psf.sample_psf_moffat_constant("stars", ctx)

        ctx.stars.psf_f1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_f2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g1 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_g2 = np.zeros_like(ctx.stars.psf_fwhm)
        ctx.stars.psf_kurtosis = np.zeros_like(ctx.stars.psf_fwhm)

        ctx.stars.psf_dx_offset = np.zeros_like(ctx.stars.psf_beta)
        ctx.stars.psf_dy_offset = np.zeros_like(ctx.stars.psf_beta)

        ctx.numstars = (1,)
        ctx.timings = {}

        ctx.image = np.zeros((par.size_y, par.size_x), dtype=np.float64)

        return ctx

    # Test photon rendering
    ctx = create_ctx()
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()

    # Test pixel rendering
    ctx = create_ctx()
    ctx.parameters.mag_pixel_rendering_stars = np.inf
    star_plugin = render_stars_photon.Plugin(ctx)
    star_plugin()
