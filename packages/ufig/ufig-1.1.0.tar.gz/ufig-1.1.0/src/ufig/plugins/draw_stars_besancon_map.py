# Copyright (C) 2016 ETH Zurich, Institute for Astronomy

"""
Created on Jul 20, 2016
author: Tomasz Kacprzak
"""

import warnings

import h5py
import healpy as hp
import numpy as np
import six
from cosmic_toolbox import arraytools as at
from ivy.plugin.base_plugin import BasePlugin

from .. import coordinate_util, io_util, sampling_util
from ..sampling_util import sample_position_uniform

if six.PY2:  # pragma: no cover
    import cPickle as pickle
else:
    import pickle


NAME = "draw stars"


def get_interp_nearest(ra_new, dec_new, dict_besancon_info):
    ipix = coordinate_util.radec2pix(
        ra=ra_new, dec=dec_new, nside=dict_besancon_info["nside"]
    )
    if dict_besancon_info["healpix_list"][ipix] is None:
        warnings.warn(
            "Besancon model: queried position is outside the area covered by the model;"
            " falling back to default",
            stacklevel=1,
        )
        ipix = 10000

    closest_cat = dict_besancon_info["healpix_list"][ipix]

    return closest_cat


def load_besancon_map_info(ctx):
    par = ctx.parameters

    filepath_map = io_util.get_abs_path(par.besancon_map_path, par.maps_remote_dir)

    dict_besancon_info = {}

    with h5py.File(filepath_map, "r") as ff:
        dict_besancon_info["simulation_area"] = float(np.array(ff["simulation_area"]))
        dict_besancon_info["nside"] = int(np.array(ff["nside"]))

    return dict_besancon_info


def load_besancon_map_pixels(ctx, list_ipix):
    """
    Simply load the pickle with maps, from par.besancon_map_path

    return pickle with the Besancon simulation map model, with fields

    dict_besancon_info={'simulation_area': area_store, 'nside': nside,
                        'healpix_list': list_df, 'healpix_mask': hp_map}

    simulation_area - area in sq. deg corresponding to the simulation catalog covers

    nside - resolution of simulation sampling

    healpix_list - a list of numpy record arrays, each element corresponds to a pixel on
                   HEALPix grid with nside=nside

    hp_map - HEALPix map showing the coverage of simulations, ring=False
    """

    par = ctx.parameters

    filepath_map = io_util.get_abs_path(par.besancon_map_path, par.maps_remote_dir)

    dist_besancon_pix_cat = {}

    with h5py.File(filepath_map, "r") as ff:
        for ipix in list_ipix:
            if len(ff[f"healpix_list/{ipix:04d}"]) == 0:
                besancon_pix_cat = None
            else:
                besancon_pix_cat = np.array(ff[f"healpix_list/{ipix:04d}"])

            dist_besancon_pix_cat[f"{ipix:04d}"] = besancon_pix_cat

    return dist_besancon_pix_cat


def load_besancon_map(ctx):
    """
    Simply load the pickle with maps, from par.besancon_map_path
    return pickle with the Besancon simulation map model, with fields

    dict_besancon_info = {'simulation_area': area_store, 'nside': nside,
                          'healpix_list': list_df, 'healpix_mask': hp_map}

    simulation_area - area in sq. deg corresponding to the simulation catalog covers

    nside - resolution of simulation sampling

    healpix_list - a list of numpy record arrays, each element corresponds
                   to a pixel on HEALPix grid with nside=nside

    hp_map - HEALPix map showing the coverage of simulations, ring=False
    """

    par = ctx.parameters

    filepath_map = io_util.get_abs_path(par.besancon_map_path, par.maps_remote_dir)

    if ".pkl" in par.besancon_map_path:
        with open(filepath_map) as ff:
            dict_besancon_info = pickle.load(ff)

    elif ".h5" in par.besancon_map_path:
        dict_besancon_info = {}
        with h5py.File(filepath_map, "r") as ff:
            dict_besancon_info["healpix_mask"] = np.array(ff["healpix_mask"])
            dict_besancon_info["simulation_area"] = float(
                np.array(ff["simulation_area"])
            )
            dict_besancon_info["nside"] = int(np.array(ff["nside"]))
            n_pix = len(dict_besancon_info["healpix_mask"])
            dict_besancon_info["healpix_list"] = [None] * n_pix
            for ip in range(n_pix):
                if len(ff[f"healpix_list/{ip:04d}"]) == 0:
                    dict_besancon_info["healpix_list"][ip] = None
                else:
                    dict_besancon_info["healpix_list"][ip] = np.array(
                        ff[f"healpix_list/{ip:04d}"]
                    )

    return dict_besancon_info


def get_star_cat_besancon(ctx):
    par = ctx.parameters

    w = coordinate_util.tile_in_skycoords(
        pixscale=par.pixscale,
        ra0=par.ra0,
        dec0=par.dec0,
        crpix_ra=par.crpix_ra,
        crpix_dec=par.crpix_dec,
    )

    pixels = coordinate_util.get_healpix_pixels(
        par.nside_sampling, w, par.size_x, par.size_y
    )
    pixarea = hp.nside2pixarea(par.nside_sampling, degrees=True)

    dict_besancon_info = load_besancon_map(ctx)
    cat_stars = get_interp_nearest(
        ra_new=par.ra0, dec_new=par.dec0, dict_besancon_info=dict_besancon_info
    )
    simulation_area = dict_besancon_info["simulation_area"]

    # Choose stars randomly according to magnitude limits (including Poisson noise),
    # apply limits for detection band
    mask = (cat_stars[par.reference_band] >= par.stars_mag_min) & (
        cat_stars[par.reference_band] <= par.stars_mag_max
    )

    cat_stars_select = cat_stars[mask]

    max_numstars = np.count_nonzero(mask)

    # Mean number of stars within a Healpix pixel
    mean_numstars = np.int32(np.around(max_numstars * pixarea / simulation_area))

    # Loop over pixels
    for pixel in pixels:
        # Reseed random library
        np.random.seed(par.seed + pixel + par.star_num_seed_offset)
        nstars = np.random.poisson(mean_numstars)
        while (
            nstars > max_numstars
        ):  # in case drawn number of stars is larger than number of stars in catalog
            nstars = np.random.poisson(mean_numstars)

        # In case the Healpix pixel is empty
        if nstars == 0:
            continue

        # Reseed random library
        np.random.seed(par.seed + pixel + par.star_dist_seed_offset)

        # Positions
        x, y = sample_position_uniform(nstars, w, pixel, par.nside_sampling)
        ctx.stars.x = np.append(ctx.stars.x, x)
        ctx.stars.y = np.append(ctx.stars.y, y)

        # Set magnitudes according to catalog
        ind = np.random.choice(
            np.arange(len(cat_stars_select)), size=nstars, replace=False
        )

        # Set magnitudes according to catalog
        for f in par.filters:
            ctx.stars.magnitude_dict[f] = np.append(
                ctx.stars.magnitude_dict[f], cat_stars_select[f][ind]
            )


def transform_from_sdss_to_gaia_colours(cat):
    # https://www.aanda.org/articles/aa/pdf/2018/08/aa32756-18.pdf Table A.2
    colours = np.array(
        [
            np.ones(len(cat)),
            (cat["g"] - cat["i"]),
            (cat["g"] - cat["i"]) ** 2,
            (cat["g"] - cat["i"]) ** 3,
        ]
    ).T

    coeffs = np.array([-0.074189, -0.51409, -0.080607, 0.0016001])[np.newaxis, :]

    G_gaia_minus_g_sdss = np.sum((colours * coeffs), axis=1)

    gaia_G = cat["g"] + G_gaia_minus_g_sdss

    return gaia_G


def get_star_cat_besancon_gaia_splice(ctx):
    # load Besancon map

    par = ctx.parameters
    w = coordinate_util.wcs_from_parameters(par)
    pixels = coordinate_util.get_healpix_pixels(
        par.nside_sampling, w, par.size_x, par.size_y
    )
    pixarea = hp.nside2pixarea(par.nside_sampling, degrees=True)

    # get the scaling for star counts
    if hasattr(par, "stars_counts_scale"):
        stars_counts_scale = par.stars_counts_scale
    else:
        stars_counts_scale = 1

    # load besancon
    dict_besancon_info = load_besancon_map_info(ctx)
    list_ipix_besancon = []
    for pixel in pixels:
        theta, phi = hp.pix2ang(par.nside_sampling, pixel)
        ipix_besancon = hp.ang2pix(dict_besancon_info["nside"], theta, phi)
        list_ipix_besancon.append(ipix_besancon)

    besancon_pixels = np.unique(list_ipix_besancon)
    dict_cat_besancon = load_besancon_map_pixels(ctx, besancon_pixels)
    for key in dict_cat_besancon:
        cat = dict_cat_besancon[key]
        select = (cat[par.reference_band] > par.stars_mag_min) & (
            cat[par.reference_band] < par.stars_mag_max
        )
        cat = cat[select]

        cat = at.ensure_cols(
            cat, names=["index:i4", "index_gaia:i4", "pos_x", "pos_y", "gaia_G"]
        )
        cat["index"] = np.arange(len(cat))
        cat["gaia_G"] = transform_from_sdss_to_gaia_colours(cat)
        dict_cat_besancon[key] = cat

    # load GAIA
    with h5py.File(par.filepath_gaia, "r") as fh5:
        cat_gaia = np.array(fh5["data"])

    # get image coordinates for GAIA stars
    cat_gaia = at.ensure_cols(
        cat_gaia, names=["index:i4", "index_besancon:i4", "x", "y"]
    )

    wcs = coordinate_util.tile_in_skycoords(
        pixscale=par.pixscale,
        ra0=par.ra0,
        dec0=par.dec0,
        crpix_ra=par.crpix_ra,
        crpix_dec=par.crpix_dec,
    )

    cat_gaia["x"], cat_gaia["y"] = wcs.all_world2pix(cat_gaia["ra"], cat_gaia["dec"], 0)
    cat_gaia["index"] = np.arange(len(cat_gaia))

    # get areas for both catalogues
    besancon_area = dict_besancon_info["simulation_area"]

    # calculate healpix pixels for Gaia stars

    gaia_hppix = coordinate_util.radec2pix(
        ra=cat_gaia["ra"], dec=cat_gaia["dec"], nside=par.nside_sampling
    )

    list_pixel_besancon = []

    # Loop over pixels
    for pixel in pixels:
        # get the pixel index in the besancon catalogue

        theta, phi = hp.pix2ang(par.nside_sampling, pixel)
        ipix_besancon = hp.ang2pix(dict_besancon_info["nside"], theta, phi)
        cat_besancon = dict_cat_besancon[f"{ipix_besancon:04d}"]

        # current number of stars according to besancon

        n_stars_current = np.int32(
            np.around(len(cat_besancon) * pixarea / besancon_area)
        )
        np.random.seed(par.seed + pixel + par.star_num_seed_offset)
        stars_counts_scale = (
            par.stars_counts_scale if hasattr(par, "stars_counts_scale") else 1.0
        )
        n_stars_current_noise = np.random.poisson(n_stars_current * stars_counts_scale)
        indices_random = np.random.choice(
            len(cat_besancon), size=n_stars_current_noise, replace=True
        )
        current_besancon = cat_besancon[indices_random].copy()
        current_besancon = np.sort(current_besancon, order=["g"])
        np.random.seed(par.seed + pixel + par.star_dist_seed_offset)
        x, y = sample_position_uniform(
            n_stars_current_noise, w, pixel, par.nside_sampling
        )
        current_besancon["index_gaia"] = -99
        current_besancon["pos_x"] = x
        current_besancon["pos_y"] = y

        # select gaia stars in current pixel

        current_gaia = cat_gaia[gaia_hppix == pixel].copy()
        n_current_gaia = len(current_gaia)
        current_besancon_nogaia = current_besancon[n_current_gaia:]

        # match gaia and besancon
        indices_match_besancon = np.argmin(
            (
                (
                    current_gaia["phot_g_mean_mag"][:, np.newaxis]
                    - cat_besancon["gaia_G"][np.newaxis]
                )
                ** 2
            ),
            axis=1,
        )
        current_besancon_gaia = cat_besancon[indices_match_besancon].copy()
        current_besancon_gaia["index_gaia"] = current_gaia["index"]
        current_besancon_gaia["pos_x"] = current_gaia["x"]
        current_besancon_gaia["pos_y"] = current_gaia["y"]

        current_join_cat = np.concatenate(
            [current_besancon_gaia, current_besancon_nogaia]
        )
        list_pixel_besancon.append(current_join_cat)

    cat_full = np.concatenate(list_pixel_besancon)
    ctx.stars.x = np.append(ctx.stars.x, cat_full["pos_x"])
    ctx.stars.y = np.append(ctx.stars.y, cat_full["pos_y"])

    # Set magnitudes according to catalog
    for f in par.filters:
        ctx.stars.magnitude_dict[f] = np.append(
            ctx.stars.magnitude_dict[f], cat_full[f]
        )


STAR_GENERATOR = {
    "besancon_map": get_star_cat_besancon,
    "besancon_gaia_splice": get_star_cat_besancon_gaia_splice,
}


class Plugin(BasePlugin):
    """
    Draw stars for the r-band from a catalog created using the Besancon model of the
    Milky Way.

    :param besancon_cat_name: Path to the catalog of stars drawn from the model stored
        as fits-file. The catalog must contain a column called 'r' giving the magnitude
        of the stars in the r-band. Furthermore, the header of the HDU in which the
        catalog is stored must contain a field labeled 'AREA' which states the area (in
        sq. deg) the catalog covers.
    :param seed: General seed.
    :param star_num_seed_offset: Seed offset before number of stars is drawn.
    :param stars_mag_min: Minimum magnitude of stars in the r-band.
    :param stars_mag_max: Maximum magnitude of stars in the r-band.
    :param star_dist_seed_offset: Seed offset before positions of stars are drawn.
    :param star_nphot_seed_offset: Seed offset before numbers of photons are calculated
           for stars.
    :param n_exp: Number of single exposures in coadded image.
    :param magzero: Magnitude zeropoint.
    :param gain: Gain in electrons per ADU.
    :param exp_time_file_name: File name of an exposure time map.
    :param size_x: Size of the image in x-direction.
    :param size_y: Size of the image in y-direction.
    :param maps_remote_dir: Remote directory where maps are stored.
    """

    def __call__(self):
        par = self.ctx.parameters

        if not hasattr(par, "crpix_ra"):
            par.crpix_ra = par.size_x / 2 + 0.5
        if not hasattr(par, "crpix_dec"):
            par.crpix_dec = par.size_y / 2 + 0.5

        # Initialize star catalog
        self.ctx.stars = sampling_util.Catalog()
        self.ctx.stars.columns = ["id", "x", "y"]

        self.ctx.stars.x = np.zeros(0, dtype=np.float32)
        self.ctx.stars.y = np.zeros(0, dtype=np.float32)
        self.ctx.stars.magnitude_dict = {}
        for f in par.filters:
            self.ctx.stars.magnitude_dict[f] = np.zeros(0, dtype=np.float32)

        # Get magnitudes and position
        generator = STAR_GENERATOR[par.star_catalogue_type]
        generator(self.ctx)

        # Mask stars not on image
        mask = (
            (self.ctx.stars.x >= 0)
            & (self.ctx.stars.x < par.size_x)
            & (self.ctx.stars.y >= 0)
            & (self.ctx.stars.y < par.size_y)
        )

        self.ctx.numstars = np.sum(mask)
        self.ctx.stars.id = np.arange(self.ctx.numstars)

        self.ctx.stars.x = self.ctx.stars.x[mask]
        self.ctx.stars.y = self.ctx.stars.y[mask]

        for f in par.filters:
            self.ctx.stars.magnitude_dict[f] = self.ctx.stars.magnitude_dict[f][mask]

    def __str__(self):
        return NAME
