# Copyright (c) 2013 ETH Zurich, Institute of Astronomy, Lukas Gamper
# <lukas.gamper@usystems.ch>

"""
Created on Oct 7, 2013
@author: Lukas Gamper
"""

import contextlib

from astropy.io import fits
from ivy.plugin.base_plugin import BasePlugin


def header_keys(ctx):
    """
    Initializes and fills a FITS header with all relevant keywords.

    :param par: Parameters in the context
    :return: List with tuples containing header entries
    """

    # Note: CRPIX1 and CRPIX2 are in the convention where the bottom left corner is
    # (0.5, 0.5) instead of (0, 0), how it is throughout UFig. Therefore, although the
    # FITS convention is used for the origin pixel (e.g. in wcs_pix2world), i.e. that
    # the first pixel center is (1, 1), the reference pixel is shifted by (-0.5, -0.5),
    # to account for this.

    par = ctx.parameters

    keys = [
        ("RADECSYS", "ICRS", "Astrometric system"),
        ("CTYPE1", "RA---TAN", "CS projection type for this axis"),
        ("CUNIT1", "deg", "Axis unit"),
        ("CRVAL1", par.ra0, "World coordinate on this axis"),
    ]

    try:
        keys += [("CRPIX1", par.crpix_ra, "Reference pixel on this axis")]

    except AttributeError:
        par.crpix_ra = par.size_x / 2.0 + 0.5
        keys += [("CRPIX1", par.crpix_ra, "Reference pixel on this axis")]

    keys += [
        ("CD1_1", -1 * par.pixscale / 60 / 60, "Linear projection matrix"),
        ("CD1_2", 0.00, "Linear projection matrix"),
        ("CTYPE2", "DEC--TAN", "WCS projection type for this axis"),
        ("CUNIT2", "deg", "Axis unit"),
        ("CRVAL2", par.dec0, "World coordinate on this axis"),
    ]

    try:
        keys += [("CRPIX2", par.crpix_dec, "Reference pixel on this axis")]

    except AttributeError:
        par.crpix_dec = par.size_y / 2.0 + 0.5
        keys += [("CRPIX2", par.crpix_dec, "Reference pixel on this axis")]

    keys += [
        ("CD2_1", 0.00, "Linear projection matrix"),
        ("CD2_2", par.pixscale / 60 / 60, "Linear projection matrix"),
        (
            "EXPTIME",
            par.n_exp * par.exposure_time,
            "Maximum equivalent exposure time (s)",
        ),
        ("GAIN", par.gain * par.n_exp, "Maximum equivalent gain (e-/ADU)"),
        ("SATURATE", par.saturation_level, "Saturation Level (ADU)"),
        ("SEXMGZPT", par.magzero, "Mag ZP"),
        ("PSF_FWHM", get_seeing_value(ctx), "Seeing in pixels"),
        ("SEED", par.seed, "General seed"),
        ("GDSEEDO", par.gal_dist_seed_offset, "Galaxy distribution seed offset"),
        (
            "GSSEEDO",
            par.gal_sersic_seed_offset,
            "Sersic indices of gals dist seed offset",
        ),
        (
            "GESEEDO",
            par.gal_ellipticities_seed_offset,
            "Ellipticities of gals dist seed offset",
        ),
        (
            "GNPSEEDO",
            par.gal_nphot_seed_offset,
            "Number of photons of gals seed offset",
        ),
        ("SDSEEDO", par.star_dist_seed_offset, "Star distribution seed offset"),
        (
            "SNPSEEDO",
            par.star_nphot_seed_offset,
            "Number of photons of stars seed offset",
        ),
        ("GRSEEDO", par.gal_render_seed_offset, "Gal rendering seed offset"),
        ("SRSEEDO", par.star_render_seed_offset, "Star rendering seed offset"),
        ("BKGSEEDO", par.background_seed_offset, "Background seed offset"),
    ]

    with contextlib.suppress(AttributeError):
        keys += [
            (
                "RESAMPT1",
                "LANCZOS" + str(par.lanczos_n),
                "RESAMPLING_TYPE config parameter",
            ),
            (
                "RESAMPT2",
                "LANCZOS" + str(par.lanczos_n),
                "RESAMPLING_TYPE config parameter",
            ),
        ]

    return keys


def get_seeing_value(ctx):
    """
    Returns the seeing value of the simulated image.

    :param ctx: Context
    :return: Seeing in pixels
    """

    try:
        seeing = ctx.average_seeing
    except AttributeError:
        try:
            seeing = ctx.parameters.seeing / ctx.parameters.pixscale
        except AttributeError:
            seeing = 0.001  # Small value for SExtractor to not crash

    return seeing


def write_image(path, image, keys, overwrite):
    """
    Writes the image to disk
    :param path: The path to write to (string)
    :param image: the 2d array image
    :param keys: list of header keys
    :param overwrite: whether to overwrite existing files
    """

    header = fits.header.Header()
    header["EQUINOX"] = (2000.00000000, "Mean equinox")
    header["MJD-OBS"] = (
        5.625609513605e04,
        "Modified Julian date at start (Arbitrary Value)",
    )
    header["AUTHOR"] = ("ETHZ    ", "Cosmology Research Group, ETH Zurich")
    header["CENTERT1"] = ("MANUAL  ", "CENTER_TYPE config parameter")
    header["PSCALET1"] = ("MANUAL  ", "PIXELSCALE_TYPE config parameter")
    header["CENTERT2"] = ("MANUAL  ", "CENTER_TYPE config parameter")
    header["PSCALET2"] = ("MANUAL  ", "PIXELSCALE_TYPE config parameter")
    header.extend(keys)

    fits.writeto(path, data=image, header=header, overwrite=overwrite)


class Plugin(BasePlugin):
    """
    Write a general ufig image into a FITS file with minimum basic header information.
    """

    def __call__(self):
        par = self.ctx.parameters

        write_image(
            par.image_name, self.ctx.image, header_keys(self.ctx), par.overwrite
        )

        del self.ctx.image

    def __str__(self):
        return "write image to fits"
