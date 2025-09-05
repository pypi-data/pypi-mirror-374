# Copyright (c) 2014 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>

"""
Created on Sep 15, 2014
@author: Claudio Bruderer
"""

import healpy as hp
import ivy
import numpy as np

from ufig import coordinate_util


def test_tile_on_sky():
    pixscale = 0.263
    size_x = 3
    size_y = 3
    nside = 256
    ra0 = 59.94140624999999
    dec0 = 0.0

    theta, phi = coordinate_util.radec2thetaphi(ra0, dec0)

    w = coordinate_util.tile_in_skycoords(
        pixscale, ra0, dec0, size_x / 2 + 0.5, size_y / 2 + 0.5
    )
    pixels = coordinate_util.get_healpix_pixels(
        nside, w, size_x, size_y, margin=0, npoints=300
    )

    assert pixels.size == 1
    assert pixels[0] == hp.ang2pix(nside, theta, phi)


def test_coord_transformations():
    pixscale = 0.263
    size_x = 3
    size_y = 3
    ra0 = 59.94140624999999
    dec0 = 0.0

    w = coordinate_util.tile_in_skycoords(
        pixscale, ra0, dec0, size_x / 2 + 0.5, size_y / 2 + 0.5
    )

    # Set up test set
    x_ref = np.random.uniform(0, 3, 10)
    y_ref = np.random.uniform(0, 3, 10)

    pixelcoords = np.transpose(np.array([x_ref, y_ref])) + 0.5
    skycoords = np.transpose(w.wcs_pix2world(pixelcoords, 1))
    ra_ref, dec_ref = skycoords[0], skycoords[1]
    theta_ref = np.pi / 2 - dec_ref * np.pi / 180
    phi_ref = ra_ref * np.pi / 180

    # Test operations
    ra, dec = coordinate_util.xy2radec(w, x_ref, y_ref)
    theta, phi = coordinate_util.xy2thetaphi(w, x_ref, y_ref)
    assert np.allclose(ra, ra_ref, rtol=1e-6)
    assert np.allclose(dec, dec_ref, rtol=1e-6)
    assert np.allclose(theta, theta_ref, rtol=1e-6)
    assert np.allclose(phi, phi_ref, rtol=1e-6)

    theta, phi = coordinate_util.radec2thetaphi(ra, dec)
    assert np.allclose(theta, theta_ref, rtol=1e-6)
    assert np.allclose(phi, phi_ref, rtol=1e-6)

    # Inverse operations
    x, y = coordinate_util.radec2xy(w, ra, dec)
    assert np.allclose(x, x_ref, rtol=1e-6)
    assert np.allclose(y, y_ref, rtol=1e-6)

    x, y = coordinate_util.thetaphi2xy(w, theta, phi)
    assert np.allclose(x, x_ref, rtol=1e-6)
    assert np.allclose(y, y_ref, rtol=1e-6)

    ra, dec = coordinate_util.thetaphi2radec(theta, phi)
    assert np.allclose(ra, ra_ref, rtol=1e-6)
    assert np.allclose(dec, dec_ref, rtol=1e-6)

    # Test with floats
    x_ref = 1.23
    y_ref = 2.76

    pixelcoords = np.array([x_ref, y_ref])[np.newaxis] + 0.5
    skycoords = np.transpose(w.wcs_pix2world(pixelcoords, 1))
    ra_ref, dec_ref = skycoords[0], skycoords[1]
    theta_ref = np.pi / 2 - dec_ref * np.pi / 180
    phi_ref = ra_ref * np.pi / 180

    # Test operations
    ra, dec = coordinate_util.xy2radec(w, x_ref, y_ref)
    theta, phi = coordinate_util.xy2thetaphi(w, x_ref, y_ref)
    assert np.allclose(ra, ra_ref, rtol=1e-6)
    assert np.allclose(dec, dec_ref, rtol=1e-6)
    assert np.allclose(theta, theta_ref, rtol=1e-6)
    assert np.allclose(phi, phi_ref, rtol=1e-6)

    theta, phi = coordinate_util.radec2thetaphi(ra, dec)
    assert np.allclose(theta, theta_ref, rtol=1e-6)
    assert np.allclose(phi, phi_ref, rtol=1e-6)

    # Inverse operations
    x, y = coordinate_util.radec2xy(w, ra, dec)
    assert np.allclose(x, x_ref, rtol=1e-6)
    assert np.allclose(y, y_ref, rtol=1e-6)

    x, y = coordinate_util.thetaphi2xy(w, theta, phi)
    assert np.allclose(x, x_ref, rtol=1e-6)
    assert np.allclose(y, y_ref, rtol=1e-6)

    ra, dec = coordinate_util.thetaphi2radec(theta, phi)
    assert np.allclose(ra, ra_ref, rtol=1e-6)
    assert np.allclose(dec, dec_ref, rtol=1e-6)

    # check empty arrays
    ra, dec = coordinate_util.xy2radec(w, np.array([]), np.array([]))
    assert ra.size == 0
    assert dec.size == 0

    ra, dec = coordinate_util.xy2thetaphi(w, np.array([]), np.array([]))
    assert ra.size == 0
    assert dec.size == 0


def test_conversion_to_healpix_pixels():
    pixscale = 0.263
    size_x = 3
    size_y = 3
    ra0 = 59.94140624999999
    dec0 = 0.0
    nside = 32

    w = coordinate_util.tile_in_skycoords(
        pixscale, ra0, dec0, size_x / 2 + 0.5, size_y / 2 + 0.5
    )

    # Set up test set (arrays)
    x_ref = np.random.uniform(0, 3, 10)
    y_ref = np.random.uniform(0, 3, 10)
    ra_ref, dec_ref = coordinate_util.xy2radec(w, x_ref, y_ref)
    theta_ref, phi_ref = coordinate_util.xy2thetaphi(w, x_ref, y_ref)

    ipix = hp.ang2pix(theta=theta_ref, phi=phi_ref, nside=nside, nest=False)
    assert np.all(ipix == coordinate_util.xy2pix(w, x_ref, y_ref, nside, nest=False))
    assert np.all(ipix == coordinate_util.radec2pix(ra_ref, dec_ref, nside, nest=False))
    assert np.all(
        ipix == coordinate_util.thetaphi2pix(theta_ref, phi_ref, nside, nest=False)
    )

    ipix = hp.ang2pix(theta=theta_ref, phi=phi_ref, nside=nside, nest=True)
    assert np.all(ipix == coordinate_util.xy2pix(w, x_ref, y_ref, nside, nest=True))
    assert np.all(ipix == coordinate_util.radec2pix(ra_ref, dec_ref, nside, nest=True))
    assert np.all(
        ipix == coordinate_util.thetaphi2pix(theta_ref, phi_ref, nside, nest=True)
    )

    # Set up test set (scalar)
    x_ref = 1.75
    y_ref = 0.25
    ra_ref, dec_ref = coordinate_util.xy2radec(w, x_ref, y_ref)
    theta_ref, phi_ref = coordinate_util.xy2thetaphi(w, x_ref, y_ref)

    ipix = hp.ang2pix(theta=theta_ref, phi=phi_ref, nside=nside, nest=False)
    assert np.all(ipix == coordinate_util.xy2pix(w, x_ref, y_ref, nside, nest=False))
    assert np.all(ipix == coordinate_util.radec2pix(ra_ref, dec_ref, nside, nest=False))
    assert np.all(
        ipix == coordinate_util.thetaphi2pix(theta_ref, phi_ref, nside, nest=False)
    )

    ipix = hp.ang2pix(theta=theta_ref, phi=phi_ref, nside=nside, nest=True)
    assert np.all(ipix == coordinate_util.xy2pix(w, x_ref, y_ref, nside, nest=True))
    assert np.all(ipix == coordinate_util.radec2pix(ra_ref, dec_ref, nside, nest=True))
    assert np.all(
        ipix == coordinate_util.thetaphi2pix(theta_ref, phi_ref, nside, nest=True)
    )


def test_wcs_from_parameters():
    """
    Test the creation of an astropy WCS object from the parameters in stored in the
    context.
    """

    par = ivy.context.create_ctx()
    par.pixscale = 0.263
    par.ra0 = 0.0
    par.dec0 = 0.0
    par.size_x = 1000
    par.size_y = 1000

    # first test without specifying crpix_ra and crxpix_dec
    wcs = coordinate_util.wcs_from_parameters(par)
    assert wcs.wcs.crpix[0] == par.size_x / 2.0 + 0.5
    assert wcs.wcs.crpix[1] == par.size_y / 2.0 + 0.5

    # now test specifying crpix_ra and crxpix_dec
    par.crpix_ra = 70.4356
    par.crpix_dec = -300
    wcs = coordinate_util.wcs_from_parameters(par)
    assert wcs.wcs.crpix[0] == par.crpix_ra
    assert wcs.wcs.crpix[1] == par.crpix_dec


def test_get_healpix_from_map():
    par = ivy.context.create_ctx()
    par.nside_sampling = 64
    npix = hp.nside2npix(par.nside_sampling)
    par.healpix_map = np.zeros(npix, dtype=bool)
    par.healpix_map[0] = True

    pixels = coordinate_util.get_healpix_pixels_from_map(par)
    assert pixels.size == 1
    assert pixels[0] == 0
