# Copyright (c) 2016 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>

"""
Created on Jul 5, 2016
@author: Claudio Bruderer
"""

import contextlib

import healpy as hp
import numpy as np
from astropy import wcs
from cosmic_toolbox import logger

LOGGER = logger.get_logger(__file__)


def thetaphi2pix(theta, phi, nside, **kwargs):
    """
    Convert (RA, DEC) to HEALPix pixel number.

    :param theta: Theta angle on the sphere following the HEALPix convention (in
                  radians)
    :param phi: Phi angle on the sphere following the HEALPix convention (in radians)
    :param nside: nside of HEALPix map
    :param kwargs: additional keyword arguments for healpy.ang2pix-function; e.g. nest
    :return: pixel number position lies in
    """

    pix = hp.ang2pix(nside=nside, theta=theta, phi=phi, **kwargs)

    return pix


def radec2pix(ra, dec, nside, **kwargs):
    """
    Convert (RA, DEC) to HEALPix pixel number.

    :param ra: RA coordinate (in degrees)
    :param dec: DEC coordinate (in degrees)
    :param nside: nside of HEALPix map
    :param kwargs: additional keyword arguments for healpy.ang2pix-function; e.g. nest
    :return: pixel number position lies in
    """

    theta, phi = radec2thetaphi(ra, dec)
    pix = thetaphi2pix(theta, phi, nside, **kwargs)

    return pix


def xy2pix(w, x, y, nside, **kwargs):
    """
    Convert (RA, DEC) to HEALPix pixel number.

    :param w: wcs-object containing all the relevant wcs-information
    :param x: x coordinate (in pixels)
    :param y: y coordinate (in pixels)
    :param nside: nside of HEALPix map
    :param kwargs: additional keyword arguments for healpy.ang2pix-function; e.g. nest
    :return: pixel number position lies in
    """

    theta, phi = xy2thetaphi(w, x, y)
    pix = thetaphi2pix(theta, phi, nside, **kwargs)

    return pix


def radec2xy(w, ra, dec):
    """
    Convert (RA, DEC) to (x, y).

    :param w: wcs-object containing all the relevant wcs-information
    :param ra: RA coordinate (in degrees)
    :param dec: DEC coordinate (in degrees)
    :return: x coordinate (in pixels)
    :return: y coordinate (in pixels)
    """

    # Check if ra and dec are empty arrays and treat this case special, since astropy
    # cannot handle this case. The try-statement is necessary to handle single numbers
    # as input
    with contextlib.suppress(TypeError):
        if len(ra) == 0:
            x = np.array([], dtype=ra.dtype)
            y = np.array([], dtype=dec.dtype)
            return x, y

    skycoords = np.array([ra, dec])
    if np.shape(skycoords)[0] == skycoords.size:
        skycoords = skycoords.reshape((1, skycoords.size))
    else:
        skycoords = skycoords.transpose()

    x, y = np.transpose(w.wcs_world2pix(skycoords, 1))

    # Bottom left corner is (0, 0) in UFig instead of (0.5, 0.5) as required by the
    # WCS-transformation
    x -= 0.5
    y -= 0.5

    return x, y


def radec2thetaphi(ra, dec):
    """
    Convert (RA, DEC) to (theta, phi).

    :param ra: RA coordinate (in degrees)
    :param dec: DEC coordinate (in degrees)
    :return: Theta angle on the sphere following the HEALPix convention (in radians)
    :return: Phi angle on the sphere following the HEALPix convention (in radians)
    """

    theta = np.pi / 2 - np.pi / 180 * dec
    phi = np.pi / 180 * ra

    return theta, phi


def xy2radec(w, x, y):
    """
    Convert (x, y) to (RA, DEC).

    :param w: wcs-object containing all the relevant wcs-information
    :param x: x coordinate (in pixels)
    :param y: y coordinate (in pixels)
    :return: RA coordinate (in degrees)
    :return: DEC coordinate (in degrees)
    """

    # Check if x and y are empty arrays and treat this case special, since astropy
    # cannot handle this case The try-statement is necessary to handle single numbers as
    # input
    with contextlib.suppress(TypeError):
        if len(x) == 0:
            ra = np.array([], dtype=x.dtype)
            dec = np.array([], dtype=y.dtype)
            return ra, dec

    pixelcoords = (
        np.array([x, y]) + 0.5
    )  # +0.5 is to convert it into origin-1 convention
    if np.shape(pixelcoords)[0] == pixelcoords.size:
        pixelcoords = pixelcoords.reshape((1, pixelcoords.size))
    else:
        pixelcoords = pixelcoords.transpose()

    ra, dec = np.transpose(w.wcs_pix2world(pixelcoords, 1))

    return ra, dec


def xy2thetaphi(w, x, y):
    """
    Convert (x, y) to (theta, phi).

    :param w: wcs-object containing all the relevant wcs-information
    :param x: x coordinate (in pixels)
    :param y: y coordinate (in pixels)
    :return: Theta angle on the sphere following the HEALPix convention (in radians)
    :return: Phi angle on the sphere following the HEALPix convention (in radians)
    """

    ra, dec = xy2radec(w, x, y)
    return radec2thetaphi(ra, dec)


def thetaphi2radec(theta, phi):
    """
    Convert (theta, phi) to (RA, DEC).

    :param theta: Theta angle on the sphere following the HEALPix convention (in
                  radians)
    :param phi: Phi angle on the sphere following the HEALPix convention (in radians)
    :return: RA coordinate (in degrees)
    :return: DEC coordinate (in degrees)
    """

    ra = phi * 180.0 / np.pi
    dec = 90.0 - theta * 180.0 / np.pi

    return ra, dec


def thetaphi2xy(w, theta, phi):
    """
    Convert (theta, phi) to (x, y).

    :param w: wcs-object containing all the relevant wcs-information
    :param theta: Theta angle on the sphere following the HEALPix convention (in
                  radians)
    :param phi: Phi angle on the sphere following the HEALPix convention (in radians)
    :return: x coordinate (in pixels)
    :return: y coordinate (in pixels)
    """

    ra, dec = thetaphi2radec(theta, phi)
    return radec2xy(w, ra, dec)


def tile_in_skycoords(pixscale, ra0, dec0, crpix_ra, crpix_dec):
    """
    Maps a pixel tile onto the sky. The tile, which has pixels with width pixscale, is
    defined around a center point (ra0, dec0). The projection employed is a tangent
    plane gnonomic projection.

    :param pixscale: Pixelscale of the image
    :param size_x: size of image in x-direction (pixel)
    :param size_y: size of image in x-direction (pixel)
    :param ra0: Right ascension of the center of the tile
    :param dec0: Declination of the center of the tile
    :param crpix_ra: RA axis reference pixel (x-axis)
    :param crpix_dec: DEC axis reference pixel (y-axis)
    :return wcs_trans: wcs-object containing all the relevant wcs-transformation
                       information
    """

    c1_1 = -1 * pixscale / 60.0 / 60.0  # pixelscale in degrees
    c1_2 = 0.0
    c2_1 = 0.0
    c2_2 = pixscale / 60.0 / 60.0  # pixelscale in degrees

    # DES uses Gnonomic tangent projection as standard
    w = wcs.WCS(naxis=2)
    # Note, throughout UFig use convention that bottom left corner
    # is (0, 0) --> Center is Size_x / 2
    w.wcs.crpix = [crpix_ra, crpix_dec]
    if c1_2 == c2_1 == 0.0:
        w.wcs.cdelt = [c1_1, c2_2]
    else:
        raise AssertionError(
            "WCS transformation only implemented for a vanishing rotation at the moment"
        )
    w.wcs.crval = [ra0, dec0]
    w.wcs.ctype = [b"RA---TAN", b"DEC--TAN"]

    return w


def get_healpix_pixels(nside, w, size_x, size_y, margin=50, npoints=300, nest=False):
    """
    For a given wcs-information of a tile find overlapping HEALPix pixels.
    These pixels are found, by setting up a grid of npoints x npoints points, finding
    the corresponding HEALPix pixels of these gridpoints and computing the unique pixel
    IDs.

    Note: Pixels are in RING-ordering

    :param nside: NSIDE of the HEALPix map
    :param w: wcs-object containing all the relevant wcs-information
    :param size_x: size of image in x-direction (pixel)
    :param size_y: size of image in x-direction (pixel)
    :param margin: Number of pixels margin to ensure that the whole tile is covered
    :param npoints: Number of points in one dimension sampled
    :param nest: whether the HEALPix map is ordered in the NESTED-format or not;
                 default = False
    :return pixels: HEALPix pixels overlapping a given tile
    """

    # The image-corners are in the origin-1 convention
    img_corners_x = np.array([-margin, size_x + margin, -margin, size_x + margin])
    img_corners_y = np.array([-margin, -margin, size_y + margin, size_y + margin])
    x_vec = np.linspace(np.min(img_corners_x), np.max(img_corners_x), npoints)
    y_vec = np.linspace(np.min(img_corners_y), np.max(img_corners_y), npoints)

    X, Y = np.meshgrid(x_vec, y_vec)
    x, y = X.flatten(), Y.flatten()

    pixels = xy2pix(w, x, y, nside, nest=nest)
    unique_pixels = np.unique(pixels)

    return unique_pixels


def wcs_from_parameters(par):
    """
    Creates an astropy WCS objects from the parameters in stored in the context.
    This is a wrapper for tile_in_skycoords
    to avoid code duplicates when getting crpix_ra and crpix_dec.
    :param par: parameters, type: ivy.utils.struct.Struct
    :return: wcs object created by tile_in_skycoords
    """

    try:
        crpix_ra = par.crpix_ra
    except AttributeError:
        crpix_ra = par.size_x / 2 + 0.5
        LOGGER.debug("Setting RA reference pixel to the center of the field")

    try:
        crpix_dec = par.crpix_dec
    except AttributeError:
        crpix_dec = par.size_y / 2 + 0.5
        LOGGER.debug("Setting DEC reference pixel to the center of the field")

    w = tile_in_skycoords(
        pixscale=par.pixscale,
        ra0=par.ra0,
        dec0=par.dec0,
        crpix_ra=crpix_ra,
        crpix_dec=crpix_dec,
    )

    return w


def get_healpix_pixels_from_map(par):
    """
    Returns the pixels of a boolean HEALPix map that are True.
    Also adapts the nside_sampling parameter if it is not set to the same value as
    the nside of the map.
    """
    if par.healpix_map is None:
        raise ValueError(
            "The healpix_map parameter is not set."
            " Use sampling_mode=wcs or define a healpix_map."
        )

    pixels = np.where(par.healpix_map)[0]

    nside_sampling = hp.get_nside(par.healpix_map)
    if nside_sampling != par.nside_sampling:
        LOGGER.warning(
            "The nside_sampling parameter is different from the nside of the map. "
            "Setting nside_sampling to the nside of the map."
        )
        par.nside_sampling = nside_sampling

    return pixels
