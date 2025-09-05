"""
Created on Jul 26, 2018
@author: Joerg Herbel
"""

import os

import numpy as np
import pytest
from ivy import context

import ufig.config.common as common
from ufig.plugins import render_galaxies_flexion
from ufig.plugins.add_lensing import add_shear
from ufig.plugins.add_psf import sample_psf_moffat_constant


@pytest.mark.slow
def test_galaxy_profile1():
    inspect_image(
        int_e1=-0.1,
        int_e2=0.3,
        gamma1=-0.06,
        gamma2=-0.01,
        int_r50=4.0,
        sersic_n=0.2,
        seeing=4.0,
        psf_beta=[3.5],
        psf_e1=0.02,
        psf_e2=0.01,
        psf_flux_ratio=1.0,
        n_threads=1,
        hyperpigimage="HYPERPIGimage_Sersic0-2.txt",
    )


@pytest.mark.slow
def test_galaxy_profile2():
    inspect_image(
        int_e1=0.4,
        int_e2=-0.15,
        gamma1=-0.04,
        gamma2=0.03,
        int_r50=4.5,
        sersic_n=2.0,
        seeing=3.0,
        psf_beta=[3.0],
        psf_e1=0.01,
        psf_e2=0.02,
        psf_flux_ratio=1.0,
        n_threads=2,
        hyperpigimage="HYPERPIGimage_Sersic2-0.txt",
    )


@pytest.mark.slow
def test_galaxy_profile3():
    inspect_image(
        int_e1=0.4,
        int_e2=-0.15,
        gamma1=-0.04,
        gamma2=0.03,
        int_r50=3.1,
        sersic_n=1.2,
        seeing=1.5,
        psf_beta=[4.1, 1.9],
        psf_e1=0.01,
        psf_e2=0.02,
        psf_flux_ratio=0.7,
        n_threads=3,
        hyperpigimage="HYPERPIGimage_Sersic1-2_PSF1-5_PSFratio0-7_Beta1_4-1_Beta2_1-9.txt",
    )


def inspect_image(
    int_e1,
    int_e2,
    gamma1,
    gamma2,
    int_r50,
    sersic_n,
    seeing,
    psf_beta,
    psf_e1,
    psf_e2,
    psf_flux_ratio,
    n_threads,
    hyperpigimage,
):
    """
    Simulate an image with UFig and compare it to one simulated with HYPERPIG.
    The requirement is that the number of points below the curve expected from Poisson
    noise up to a radius where this noise is below the 1%-level is within a tolerance
    around 68.3%.

    """

    REQUIREMENT = 0.01
    NBINS = 5

    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        size_x=101,
        size_y=101,
        pixscale=1,
        sersicprecision=common.sersicprecision,
        gammaprecision=common.gammaprecision,
        gammaprecisionhigh=common.gammaprecisionhigh,
        psf_e1=psf_e1,
        psf_e2=psf_e2,
        seeing=seeing,
        psf_beta=psf_beta,
        psf_flux_ratio=psf_flux_ratio,
        psf_flexion_suppression=0.0,
        seed=102301239,
        gal_render_seed_offset=600,
        n_threads_photon_rendering=n_threads,
    )

    ctx.numgalaxies = 1
    ctx.galaxies = context.create_immutable_ctx(
        x=np.array([50.5]), y=np.array([50.5]), nphot=np.array([10000000000])
    )

    gals = ctx.galaxies
    sample_psf_moffat_constant("galaxies", ctx)
    gals.psf_flux_ratio = np.array([psf_flux_ratio])
    gals.psf_f1 = np.zeros_like(gals.psf_fwhm)
    gals.psf_f2 = np.zeros_like(gals.psf_fwhm)
    gals.psf_g1 = np.zeros_like(gals.psf_fwhm)
    gals.psf_g2 = np.zeros_like(gals.psf_fwhm)
    gals.psf_kurtosis = np.zeros_like(gals.psf_fwhm)
    gals.psf_dx_offset = np.zeros_like(gals.psf_beta)
    gals.psf_dy_offset = np.zeros_like(gals.psf_beta)
    gals.int_e1 = np.array([int_e1])
    gals.int_e2 = np.array([int_e2])
    gals.gamma1 = np.array([gamma1])
    gals.gamma2 = np.array([gamma2])
    gals.e1, gals.e2 = add_shear(
        ctx.galaxies.int_e1,
        ctx.galaxies.int_e2,
        ctx.galaxies.gamma1,
        ctx.galaxies.gamma2,
    )
    gals.sersic_n = np.array([sersic_n])
    gals.r50 = np.array([int_r50])

    ctx.timings = {}

    ctx.image = np.zeros(
        (ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
    )

    galaxy_plugin = render_galaxies_flexion.Plugin(ctx)
    galaxy_plugin()
    ctx.image = ctx.image.flatten()

    size_x = ctx.parameters.size_x
    size_y = ctx.parameters.size_y
    X = np.arange(0, size_x) + 0.5
    Y = np.arange(0, size_y) + 0.5
    x, y = np.meshgrid(X, Y)

    x -= ctx.galaxies.x
    y -= ctx.galaxies.y
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y.flatten(), x.flatten()).reshape((size_y, size_x))

    int_e1 = ctx.galaxies.int_e1
    int_e2 = ctx.galaxies.int_e2
    gamma1 = ctx.galaxies.gamma1
    gamma2 = ctx.galaxies.gamma2
    e1 = (
        ctx.galaxies.int_e1
        + 2 * gamma1 * (1 - int_e1**2)
        - 2 * gamma2 * int_e1 * int_e2
    )
    e2 = (
        ctx.galaxies.int_e2
        + 2 * gamma2 * (1 - int_e2**2)
        - 2 * gamma1 * int_e1 * int_e2
    )
    enorm = np.sqrt(e1**2 + e2**2)
    theta -= np.arctan2(e2, e1) / 2.0
    radius = r / np.sqrt(1.0 + enorm * (np.cos(theta) ** 2 - np.sin(theta) ** 2))
    radius = radius.flatten()

    if not os.path.isabs(hyperpigimage):
        dirname_tests = os.path.dirname(os.path.abspath(__file__))
        hyperpigimage = os.path.join(dirname_tests, hyperpigimage)
        hyperpig = np.loadtxt(hyperpigimage).flatten()

    poisson = 1.0 / np.sqrt(hyperpig)
    poissonmask = poisson >= REQUIREMENT
    rmax = np.min(radius[poissonmask])
    sortradius = np.argsort(radius)
    rmaxindex = np.where(radius[sortradius] == rmax)[0][-1]

    percentagebelowpoisson = np.zeros(NBINS)
    for i in range(NBINS - 1):
        mask = sortradius[
            int((rmaxindex / NBINS) * i) : int((rmaxindex / NBINS) * (i + 1))
        ]
        reldiff = np.abs(ctx.image[mask] - hyperpig[mask]) / hyperpig[mask]
        percentagebelowpoisson[i] = float(
            reldiff[reldiff <= poisson[mask]].size
        ) / float(reldiff.size)
    mask = sortradius[int((rmaxindex / NBINS) * (NBINS - 1)) : rmaxindex + 1]
    reldiff = np.abs(ctx.image[mask] - hyperpig[mask]) / hyperpig[mask]
    percentagebelowpoisson[-1] = float(reldiff[reldiff <= poisson[mask]].size) / float(
        reldiff.size
    )

    percentages = (
        np.sum(percentagebelowpoisson[:-1]) * (rmaxindex / NBINS)
        + percentagebelowpoisson[-1] * (rmaxindex / NBINS + rmaxindex % NBINS)
    ) / rmaxindex
    assert np.allclose(percentages, 0.683, atol=0.05)

    # NBINS - 1 as last bin is dropped (too close to cutoff for larger Sersics)
    assert np.allclose(percentagebelowpoisson[:-1], 0.683, atol=0.07)


def inspect_image_small_for_coverage(
    int_e1,
    int_e2,
    gamma1,
    gamma2,
    int_r50,
    sersic_n,
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

    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        size_x=10,
        size_y=10,
        pixscale=1,
        sersicprecision=common.sersicprecision,
        gammaprecision=common.gammaprecision,
        gammaprecisionhigh=common.gammaprecisionhigh,
        psf_e1=psf_e1,
        psf_e2=psf_e2,
        seeing=seeing,
        psf_beta=psf_beta,
        psf_flux_ratio=psf_flux_ratio,
        psf_flexion_suppression=0.0,
        seed=102301239,
        gal_render_seed_offset=600,
        n_threads_photon_rendering=n_threads,
    )

    ctx.numgalaxies = 1
    ctx.galaxies = context.create_immutable_ctx(
        x=np.array([5.5]), y=np.array([5.5]), nphot=np.array([10000])
    )

    gals = ctx.galaxies
    sample_psf_moffat_constant("galaxies", ctx)
    gals.psf_flux_ratio = np.array([psf_flux_ratio])
    gals.psf_f1 = np.zeros_like(gals.psf_fwhm)
    gals.psf_f2 = np.zeros_like(gals.psf_fwhm)
    gals.psf_g1 = np.zeros_like(gals.psf_fwhm)
    gals.psf_g2 = np.zeros_like(gals.psf_fwhm)
    gals.psf_kurtosis = np.zeros_like(gals.psf_fwhm)
    gals.psf_dx_offset = np.zeros_like(gals.psf_beta)
    gals.psf_dy_offset = np.zeros_like(gals.psf_beta)
    gals.int_e1 = np.array([int_e1])
    gals.int_e2 = np.array([int_e2])
    gals.gamma1 = np.array([gamma1])
    gals.gamma2 = np.array([gamma2])
    gals.e1, gals.e2 = add_shear(
        ctx.galaxies.int_e1,
        ctx.galaxies.int_e2,
        ctx.galaxies.gamma1,
        ctx.galaxies.gamma2,
    )
    gals.sersic_n = np.array([sersic_n])
    gals.r50 = np.array([int_r50])

    ctx.timings = {}

    ctx.image = np.zeros(
        (ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
    )

    galaxy_plugin = render_galaxies_flexion.Plugin(ctx)
    galaxy_plugin()


def test_galaxy_profile1_small_for_coverage():
    inspect_image_small_for_coverage(
        int_e1=-0.1,
        int_e2=0.3,
        gamma1=-0.06,
        gamma2=-0.01,
        int_r50=4.0,
        sersic_n=0.2,
        seeing=4.0,
        psf_beta=[3.5],
        psf_e1=0.02,
        psf_e2=0.01,
        psf_flux_ratio=1.0,
        n_threads=1,
    )


def test_galaxy_profile2_small_for_coverage():
    inspect_image_small_for_coverage(
        int_e1=0.4,
        int_e2=-0.15,
        gamma1=-0.04,
        gamma2=0.03,
        int_r50=4.5,
        sersic_n=2.0,
        seeing=3.0,
        psf_beta=[3.0],
        psf_e1=0.01,
        psf_e2=0.02,
        psf_flux_ratio=1.0,
        n_threads=2,
    )


def test_galaxy_profile3_small_for_coverage():
    inspect_image_small_for_coverage(
        int_e1=0.4,
        int_e2=-0.15,
        gamma1=-0.04,
        gamma2=0.03,
        int_r50=3.1,
        sersic_n=1.2,
        seeing=1.5,
        psf_beta=[4.1, 1.9],
        psf_e1=0.01,
        psf_e2=0.02,
        psf_flux_ratio=0.7,
        n_threads=3,
    )


@pytest.mark.slow
def test_galaxy_rough_shape():
    """
    Simulate an image with UFig of an elliptical galaxy (no PSF) and transform it back
    to a round shape (rotation + stretch). Testing that the resulting shape is
    approximately round (to 1 %), gives a rough test of the shape.
    """

    REQUIREMENT = 0.01

    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        size_x=101,
        size_y=101,
        pixscale=1,
        sersicprecision=common.sersicprecision,
        gammaprecision=common.gammaprecision,
        gammaprecisionhigh=common.gammaprecisionhigh,
        psf_e1=0.0,
        psf_e2=0.0,
        seeing=0.0001,
        psf_beta=3.5,
        psf_flexion_suppression=0.0,
        seed=142,
        gal_render_seed_offset=42,
        n_threads_photon_rendering=10,
    )
    par = ctx.parameters

    ctx.numgalaxies = 1
    ctx.galaxies = context.create_immutable_ctx(
        x=np.array([50.5]), y=np.array([50.5]), nphot=np.array([10000000])
    )
    gals = ctx.galaxies
    sample_psf_moffat_constant("galaxies", ctx)
    gals.psf_f1 = np.zeros_like(gals.psf_fwhm)
    gals.psf_f2 = np.zeros_like(gals.psf_fwhm)
    gals.psf_g1 = np.zeros_like(gals.psf_fwhm)
    gals.psf_g2 = np.zeros_like(gals.psf_fwhm)
    gals.psf_kurtosis = np.zeros_like(gals.psf_fwhm)
    gals.psf_dx_offset = np.zeros_like(gals.psf_beta)
    gals.psf_dy_offset = np.zeros_like(gals.psf_beta)
    gals.e1 = np.array([0.31])
    gals.e2 = np.array([-0.238])
    gals.sersic_n = np.array([1.5])
    gals.r50 = np.array([4.0])

    ctx.timings = {}

    ctx.image = np.zeros(
        (ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
    )

    galaxy_plugin = render_galaxies_flexion.Plugin(ctx)
    galaxy_plugin()

    x = np.arange(par.size_x) + 0.5 - gals.x
    y = np.arange(par.size_y) + 0.5 - gals.y
    x, y = np.meshgrid(x, y)

    alpha = np.arctan2(gals.e2, gals.e1) / 2
    e = np.sqrt(gals.e1**2 + gals.e2**2)
    stretch = np.sqrt((1 - e) / (1 + e))

    x_rot = (np.cos(alpha) * x + np.sin(alpha) * y) * stretch
    y_rot = -np.sin(alpha) * x + np.cos(alpha) * y
    r_rot = np.sqrt(x_rot**2 + y_rot**2)

    mask = 1 / np.sqrt(ctx.image) < REQUIREMENT
    maxradius = np.max(r_rot[mask])
    mask = r_rot < maxradius

    q11 = np.sum(ctx.image[mask] * x_rot[mask] ** 2)
    q12 = np.sum(ctx.image[mask] * x_rot[mask] * y_rot[mask])
    q22 = np.sum(ctx.image[mask] * y_rot[mask] ** 2)

    assert np.allclose((q11 - q22) / (q11 + q22), 0, atol=0.01)
    assert np.allclose(2 * q12 / (q11 + q22), 0, atol=0.01)


def test_galaxy_rough_shape_small_for_coverage():
    """
    This test is just for coverage. It calls the same plugins as the main test
    but with a smaller image size and number of objects such that the rendering
    also works without numba jit compilation.
    """

    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        size_x=10,
        size_y=10,
        pixscale=1,
        sersicprecision=common.sersicprecision,
        gammaprecision=common.gammaprecision,
        gammaprecisionhigh=common.gammaprecisionhigh,
        psf_e1=0.0,
        psf_e2=0.0,
        seeing=0.0001,
        psf_beta=3.5,
        psf_flexion_suppression=0.0,
        seed=142,
        gal_render_seed_offset=42,
        n_threads_photon_rendering=10,
    )

    ctx.numgalaxies = 1
    ctx.galaxies = context.create_immutable_ctx(
        x=np.array([5.5]), y=np.array([5.5]), nphot=np.array([10000])
    )
    gals = ctx.galaxies
    sample_psf_moffat_constant("galaxies", ctx)
    gals.psf_f1 = np.zeros_like(gals.psf_fwhm)
    gals.psf_f2 = np.zeros_like(gals.psf_fwhm)
    gals.psf_g1 = np.zeros_like(gals.psf_fwhm)
    gals.psf_g2 = np.zeros_like(gals.psf_fwhm)
    gals.psf_kurtosis = np.zeros_like(gals.psf_fwhm)
    gals.psf_dx_offset = np.zeros_like(gals.psf_beta)
    gals.psf_dy_offset = np.zeros_like(gals.psf_beta)
    gals.e1 = np.array([0.31])
    gals.e2 = np.array([-0.238])
    gals.sersic_n = np.array([1.5])
    gals.r50 = np.array([4.0])

    ctx.timings = {}

    ctx.image = np.zeros(
        (ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
    )

    galaxy_plugin = render_galaxies_flexion.Plugin(ctx)
    galaxy_plugin()
