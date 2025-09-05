"""
Created on June 24, 2014

@author: Lukas Gamper
adapted by Silvan Fischbacher, 2024
"""


import numpy as np
import pytest
from ivy import context

from ufig.plugins import render_galaxies_flexion as render_galaxies
from ufig.plugins import saturate_pixels, saturate_pixels_x
from ufig.plugins.add_psf import sample_psf_moffat_constant

from .test_data import PointSourceGalaxyCatalog


@pytest.fixture
def create_context():
    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        psf_beta=3.5,
        seeing=0.0,
        psf_e1=0.0,
        psf_e2=0.0,
        psf_f1=0.0,
        psf_f2=0.0,
        psf_g1=0.0,
        psf_g2=0.0,
        size_x=51,
        size_y=51,
        queff=0.95,
        gain=1.0,
        pixscale=0.01,
        stars_mag_max=24.0,
        gals_mag_max=24.0,
        seed=100,
        gal_render_seed_offset=42,
        saturation_level=1000,
        sersicprecision=9,
        gammaprecision=13,
        gammaprecisionhigh=4,
        n_threads_photon_rendering=1,
        psf_flexion_suppression=0.0,
    )

    ctx.image = np.zeros(
        (ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
    )

    ctx.numgalaxies = 1
    ctx.galaxies = PointSourceGalaxyCatalog()

    sample_psf_moffat_constant("galaxies", ctx)

    ctx.galaxies.psf_f1 = np.zeros_like(ctx.galaxies.psf_fwhm)
    ctx.galaxies.psf_f2 = np.zeros_like(ctx.galaxies.psf_fwhm)
    ctx.galaxies.psf_g1 = np.zeros_like(ctx.galaxies.psf_fwhm)
    ctx.galaxies.psf_g2 = np.zeros_like(ctx.galaxies.psf_fwhm)
    ctx.galaxies.psf_kurtosis = np.zeros_like(ctx.galaxies.psf_fwhm)
    ctx.galaxies.psf_dx_offset = np.zeros_like(ctx.galaxies.psf_beta)
    ctx.galaxies.psf_dy_offset = np.zeros_like(ctx.galaxies.psf_beta)

    np.random.seed(ctx.parameters.seed)
    galaxy_plugin = render_galaxies.Plugin(ctx)
    galaxy_plugin()

    return ctx


def test_saturation(create_context):
    ctx = create_context

    center_y = int(ctx.galaxies.y[0])
    center_x = int(ctx.galaxies.x[0])

    saturate_plugin = saturate_pixels.Plugin(ctx)
    saturate_plugin()

    reference = np.zeros_like(ctx.image)
    saturation = ctx.parameters.saturation_level
    offset = int((ctx.galaxies.nphot[0] / saturation) / 2)
    rest = int((ctx.galaxies.nphot[0] % ((2 * offset - 1) * saturation)) / 2.0)
    reference[(center_y - offset + 1) : (center_y + offset), center_x] = saturation
    reference[center_y - offset, center_x] = rest
    reference[center_y + offset, center_x] = rest

    assert np.all(ctx.image <= saturation)
    assert np.sum(ctx.image) == ctx.galaxies.nphot[0]
    assert np.allclose(reference, ctx.image, rtol=0.005)


def test_saturation_x(create_context):
    ctx = create_context

    center_y = int(ctx.galaxies.y[0])
    center_x = int(ctx.galaxies.x[0])

    saturate_plugin = saturate_pixels_x.Plugin(ctx)
    saturate_plugin()

    reference = np.zeros_like(ctx.image)
    saturation = ctx.parameters.saturation_level
    offset = int((ctx.galaxies.nphot[0] / saturation) / 2)
    rest = int((ctx.galaxies.nphot[0] % ((2 * offset - 1) * saturation)) / 2.0)
    reference[center_y, (center_x - offset + 1) : (center_x + offset)] = saturation
    reference[center_y, center_x - offset] = rest
    reference[center_y, center_x + offset] = rest

    assert np.all(ctx.image <= saturation)
    assert np.sum(ctx.image) == ctx.galaxies.nphot[0]
    assert np.allclose(reference, ctx.image, rtol=0.005)
