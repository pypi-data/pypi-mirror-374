"""
Created on Jan 14, 2014
@author: jakeret, cchang
"""

import os

import numpy as np
import pytest
from astropy.io import fits
from ivy import context

from ufig.plugins import write_image


@pytest.fixture
def ctx():
    ctx = context.create_ctx()
    ctx.parameters = context.create_ctx()

    ctx.parameters.size_x = 2
    ctx.parameters.size_y = 3
    ctx.parameters.pixscale = 0.1
    ctx.parameters.ra0 = 11.3
    ctx.parameters.dec0 = 2.0
    ctx.parameters.n_exp = 3
    ctx.parameters.exposure_time = 10
    ctx.parameters.gain = 13.2
    ctx.parameters.saturation_level = 102
    ctx.parameters.lanczos_n = 2
    ctx.parameters.magzero = 30.21
    ctx.parameters.seeing = 1.02
    ctx.parameters.seed = 102301242
    ctx.parameters.gal_dist_seed_offset = 101
    ctx.parameters.gal_sersic_seed_offset = 201
    ctx.parameters.gal_ellipticities_seed_offset = 301
    ctx.parameters.gal_nphot_seed_offset = 401
    ctx.parameters.star_dist_seed_offset = 501
    ctx.parameters.star_nphot_seed_offset = 601
    ctx.parameters.gal_render_seed_offset = 701
    ctx.parameters.star_render_seed_offset = 801
    ctx.parameters.background_seed_offset = 901

    add_image(ctx)

    return ctx


def add_image(ctx):
    ctx.image = np.zeros(
        (ctx.parameters.size_y, ctx.parameters.size_x), dtype=np.float64
    )


def test_write(ctx):
    plugin = write_image.Plugin(ctx)

    image_name = "image.fits"
    ctx.parameters.image_name = image_name
    ctx.parameters.overwrite = False
    plugin()
    assert os.path.isfile(image_name)

    # test overwriting
    add_image(ctx)
    with pytest.raises(IOError):
        plugin()

    ctx.parameters.overwrite = True
    plugin()
    assert os.path.isfile(image_name)

    # test written data
    add_image(ctx)
    header = fits.getheader(image_name)
    img = fits.getdata(image_name)

    assert np.array_equal(img, ctx.image)
    assert header["NAXIS1"] == ctx.parameters.size_x
    assert header["NAXIS2"] == ctx.parameters.size_y
    assert header["CRVAL1"] == ctx.parameters.ra0
    assert header["CRVAL2"] == ctx.parameters.dec0
    assert header["EXPTIME"] == ctx.parameters.n_exp * ctx.parameters.exposure_time
    assert np.allclose(
        header["GAIN"], ctx.parameters.gain * ctx.parameters.n_exp, atol=1e-5
    )
    assert header["SATURATE"] == ctx.parameters.saturation_level
    assert header["SEED"] == ctx.parameters.seed
    assert header["RESAMPT1"] == f"LANCZOS{ctx.parameters.lanczos_n}"
    assert header["RESAMPT2"] == f"LANCZOS{ctx.parameters.lanczos_n}"
    assert header["SEXMGZPT"] == ctx.parameters.magzero
    assert np.allclose(
        header["PSF_FWHM"], ctx.parameters.seeing / ctx.parameters.pixscale, atol=1e-5
    )

    assert header["SEED"] == ctx.parameters.seed
    assert header["GDSEEDO"] == ctx.parameters.gal_dist_seed_offset
    assert header["GSSEEDO"] == ctx.parameters.gal_sersic_seed_offset
    assert header["GESEEDO"] == ctx.parameters.gal_ellipticities_seed_offset
    assert header["GNPSEEDO"] == ctx.parameters.gal_nphot_seed_offset
    assert header["SDSEEDO"] == ctx.parameters.star_dist_seed_offset
    assert header["SNPSEEDO"] == ctx.parameters.star_nphot_seed_offset
    assert header["GRSEEDO"] == ctx.parameters.gal_render_seed_offset
    assert header["SRSEEDO"] == ctx.parameters.star_render_seed_offset
    assert header["BKGSEEDO"] == ctx.parameters.background_seed_offset

    # remove written image
    os.remove(image_name)
