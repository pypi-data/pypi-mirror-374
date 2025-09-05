# Copyright (C) 2019 ETH Zurich, Institute for Particle Physics and Astrophysics

"""
Created 2024
author: Silvan Fischbacher
"""

import itertools

import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import file_utils, logger
from cosmic_toolbox.utils import is_between
from ivy.plugin.base_plugin import BasePlugin

from ufig.plugins.write_catalog import catalog_to_rec

LOGGER = logger.get_logger(__file__)


def ensure_valid_cats(cat_gals, cat_stars):
    if cat_gals is None and cat_stars is None:
        raise ValueError("No catalogs provided")
    if cat_gals is None:
        cat_gals = np.empty(0, dtype=cat_stars.dtype)
    if cat_stars is None:
        cat_stars = np.empty(0, dtype=cat_gals.dtype)
    return cat_gals, cat_stars


def get_elliptical_indices(
    x,
    y,
    r50,
    e1,
    e2,
    imshape=(4200, 4200),
    n_half_light_radius=5,
    pre_selected_indices=None,
):
    """
    Get the indices of the pixels within an elliptical region
    and their distances from the center.
    The distance is normalized to true pixel distance in the elliptical coordinate
    system. If the radius is too small to include any pixel, the center pixel is
    returned.

    :param x: x coordinate of the center of the ellipse
    :param y: y coordinate of the center of the ellipse
    :param r50: (half light) radius of the ellipse
    :param e1: ellipticity component 1
    :param e2: ellipticity component 2
    :param imshape: shape of the image
    :param n_half_light_radius: number of half light radii to consider
    :param pre_selected_indices: pre-selected indices of the image where the distance
    should be calculated, tuple of (x, y) indices
    :return: indices of the pixels within the elliptical region
    and their distances from the center
    """

    # choose indices withing n times the half light radius
    r = n_half_light_radius * r50

    # Grid dimensions
    grid_width = imshape[1]
    grid_height = imshape[0]

    # Get the absolute ellipticity
    e_abs = np.sqrt(e1**2 + e2**2)

    # Calculate the semi-major and semi-minor axes of the ellipse
    a = np.sqrt(1 / (1 - e_abs)) * r
    b = np.sqrt(1 / (1 + e_abs)) * r

    # Calculate the rotation angle of the ellipse
    theta = 0.5 * np.arctan2(e2, e1)

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    if pre_selected_indices is None:
        # Calculate the bounding box of the ellipse
        rx = a * np.abs(cos_theta) + b * np.abs(sin_theta)
        ry = a * np.abs(sin_theta) + b * np.abs(cos_theta)

        left = max(0, int(x - rx))
        right = min(grid_width - 1, int(x + rx))
        top = max(0, int(y - ry))
        bottom = min(grid_height - 1, int(y + ry))

        # Generate a meshgrid within the bounding box
        # xx, yy = np.meshgrid(np.arange(left, right + 1), np.arange(top, bottom + 1))
        yy, xx = np.indices((bottom - top + 1, right - left + 1))
        yy += top
        xx += left

        # Rotate the coordinates back to the original frame
        x_rot = (xx - x) * cos_theta + (yy - y) * sin_theta
        y_rot = -(xx - x) * sin_theta + (yy - y) * cos_theta

        # Check if each coordinate is within the elliptical region
        distances = (x_rot**2 / a**2) + (y_rot**2 / b**2)
        # indices = np.stack((xx, yy), axis=-1)

        good_indices = distances <= 1
        if not np.any(good_indices):
            good_indices = distances <= np.min(distances)
        return xx[good_indices], yy[good_indices], np.sqrt(distances[good_indices]) * r

    # Subtract x and y from the pre-selected indices
    diff_x = pre_selected_indices[0] - x
    diff_y = pre_selected_indices[1] - y

    # Calculate the rotated coordinates
    x_rot = diff_x * cos_theta + diff_y * sin_theta
    y_rot = -diff_x * sin_theta + diff_y * cos_theta

    # Check if each coordinate is within the elliptical region
    distances = (x_rot**2 / a**2) + (y_rot**2 / b**2)
    within_region = distances <= 1

    return within_region, np.sqrt(distances[within_region]) * r


def sersic_brightness(magnitude, r50, n, r):
    """
    Calculate the surface brightness of a Sersic profile.

    :param magnitude: magnitude of the object
    :param r50: half light radius
    :param n: Sersic index
    :param r: radius
    :return: surface brightness at radius r
    """
    b = sersic_b(n)
    I_r50 = np.exp(-0.4 * magnitude)
    ratio = (r / r50) ** (1 / n)
    surface_brightness = I_r50 * np.exp(-b * (ratio - 1))
    return surface_brightness


def sersic_b(n):
    """
    Calculate the b parameter of a Sersic profile.

    :param n: Sersic index
    :return: b parameter
    """
    return 2 * n - 0.324


def estimate_flux_of_points(
    cat, imshape=(4200, 4200), max_mag=26, n_half_light_radius=5
):
    """
    Estimates the flux of the points of the image where the galaxies are located.

    :param cat: catalog
    :return: estimated flux at the points of the galaxies
    """

    # Magnitude cut
    objects = cat[cat["mag"] < max_mag]

    # Setup the indices
    index_x = cat["x"].astype(int)
    index_y = cat["y"].astype(int)

    # Setup the flux
    flux = np.zeros(len(cat))

    for obj in objects:
        r = obj["r50"]
        x = int(obj["x"])
        y = int(obj["y"])

        # select = ((cat["x"]-x)**2 + (cat["y"]-y)**2) < (n_half_light_radius*r)**2

        good_ind, distance = get_elliptical_indices(
            x,
            y,
            r,
            obj["e1"],
            obj["e2"],
            imshape=imshape,
            n_half_light_radius=n_half_light_radius,
            pre_selected_indices=(index_x, index_y),
        )

        # subtract by distance of main pixel to avoid negative values
        # when subtracting the object's flux
        flux[good_ind] += sersic_brightness(obj["mag"], r, obj["sersic_n"], distance)
    return flux


def estimate_flux_full_image(
    cat, imshape=(4200, 4200), max_mag=26, n_half_light_radius=5
):
    """
    Estimates the flux of the image from catalog (with magnitude cut)

    :param cat: catalog
    :param imshape: shape of the image
    :param max_mag: maximum magnitude that is considered for blending
    :param n_half_light_radius: number of half light radii to consider for each galaxy
    :return: estimated flux of the image
    """

    # Magnitude cut
    objects = cat[cat["mag"] < max_mag]

    # Setup the image grid
    image = np.zeros(imshape)

    # Accumulate the object indices and mask values
    for obj in objects:
        r = obj["r50"]
        x = int(obj["x"])
        y = int(obj["y"])
        x_ind, y_ind, distance = get_elliptical_indices(
            x,
            y,
            r,
            obj["e1"],
            obj["e2"],
            imshape=imshape,
            n_half_light_radius=n_half_light_radius,
        )
        image[y_ind, x_ind] += sersic_brightness(
            obj["mag"], r, obj["sersic_n"], distance
        )
    return image


def add_blending_points(cat, par):
    """
    Add blending information to catalog estimating only the flux at the position
    of the objects.

    :param cat: catalog
    :param par: context parameters
    :return: catalog with blending information
    """
    imshape = (par.size_y, par.size_x)
    max_mag = par.mag_for_scaling
    n_half_light_radius = par.n_r50_for_flux_estimation

    new_names = ["estimated_flux"]
    cat = at.add_cols(cat, new_names, dtype=par.catalog_precision)
    flux = estimate_flux_of_points(
        cat,
        imshape=imshape,
        max_mag=max_mag,
        n_half_light_radius=n_half_light_radius,
    )
    mag = cat["mag"]
    sersic_n = cat["sersic_n"]
    r50 = cat["r50"]
    stars = cat["r50"] == 0
    r50[stars] = cat["psf_fwhm"][stars] / 2
    sersic_n[stars] = 1

    select = mag <= max_mag
    # subtract flux of object itself
    object_flux = sersic_brightness(mag[select], r50[select], sersic_n[select], 0)
    flux[select] = flux[select] - object_flux
    cat["estimated_flux"] = flux
    return cat


def add_blending_full_image(cat, par):
    """
    Add blending information to catalog estimating the flux at all positions.

    :param cat: catalog
    :param par: context parameters
    :return: catalog with blending information
    """
    imshape = (par.size_y, par.size_x)
    max_mag = par.mag_for_scaling
    n_half_light_radius = par.n_r50_for_flux_estimation

    new_names = ["estimated_flux"]

    cat = at.add_cols(cat, new_names, dtype=par.catalog_precision)
    estimated_flux = estimate_flux_full_image(
        cat,
        imshape=imshape,
        max_mag=max_mag,
        n_half_light_radius=n_half_light_radius,
    )
    x = cat["x"]
    y = cat["y"]
    mag = cat["mag"]
    sersic_n = cat["sersic_n"]
    r50 = cat["r50"]
    stars = cat["r50"] == 0
    r50[stars] = cat["psf_fwhm"][stars] / 2
    sersic_n[stars] = 1

    flux = estimated_flux[y.astype(int), x.astype(int)]
    select = mag <= max_mag
    object_flux = sersic_brightness(mag[select], r50[select], sersic_n[select], 0)
    flux[select] = flux[select] - object_flux
    cat["estimated_flux"] = flux
    return cat


def add_blending_integrated(cat, par):
    """
    Computes the average galaxy density weighted by magnitude and sizes to estimate the
    blending risk. The value is the same for all objects in the image.

    :param cat: catalog
    :param par: context parameters
    :return: catalog with additional column
    "density_mag_weighted" and "density_size_weighted"
    """
    mag_for_scaling = par.mag_for_scaling
    r50_for_scaling = par.n_r50_for_flux_estimation

    new_names = ["density_mag_weighted", "density_size_weighted"]
    cat = at.add_cols(cat, new_names, dtype=par.catalog_precision)

    mag = cat["mag"]
    r50 = cat["r50"]

    # Calculate the density
    cat["density_mag_weighted"] = np.sum(
        np.exp(-0.4 * mag) / np.exp(-0.4 * mag_for_scaling)
    )
    cat["density_size_weighted"] = np.sum(r50 / r50_for_scaling)

    return cat


def add_blending_binned_integrated(cat, par):
    """
    Computes the average galaxy density weighted by magnitude and sizes to estimate the
    blending risk. The image is divided into bins and the value is computed for each
    bin.

    :param cat: catalog
    :param par: context parameters
    :return: catalog with additional column
    "density_mag_weighted" and "density_size_weighted"
    """
    mag_for_scaling = par.mag_for_scaling
    r50_for_scaling = par.n_r50_for_flux_estimation
    n_bins = par.n_bins_for_flux_estimation

    new_names = ["density_mag_weighted", "density_size_weighted"]
    cat = at.add_cols(cat, new_names, dtype=par.catalog_precision)

    # Calculate the flux and size of the objects and scale them
    mag = cat["mag"]
    r50 = cat["r50"]
    flux = np.exp(-0.4 * mag) / np.exp(-0.4 * mag_for_scaling)
    r50 = r50 / r50_for_scaling

    pixels_per_bin_x = int(np.ceil(par.size_x / n_bins))
    pixels_per_bin_y = int(np.ceil(par.size_y / n_bins))

    for x, y in itertools.product(range(n_bins), range(n_bins)):
        # Select the objects in the bin
        select = is_between(cat["x"], x * pixels_per_bin_x, (x + 1) * pixels_per_bin_x)
        select &= is_between(cat["y"], y * pixels_per_bin_y, (y + 1) * pixels_per_bin_y)
        # Calculate the density in the bin
        cat["density_mag_weighted"][select] = np.sum(flux[select])
        cat["density_size_weighted"][select] = np.sum(r50[select])
    return cat


def add_blending_ngal(cat, par):
    """
    Computes the number of galaxies for different magnitude cuts. This can later be used
    to estimate the blending risk.

    :param cat: catalog
    :param par: context parameters
    :return: catalog with additional column "ngal_{}".format(mag_cuts)
    """
    mag_cuts = par.mag_for_scaling
    if not isinstance(mag_cuts, list):
        mag_cuts = [mag_cuts]

    new_names = []
    for cut in mag_cuts:
        new_names.append(f"ngal_{cut}")

    cat = at.add_cols(cat, new_names, dtype=par.catalog_precision)

    for cut in mag_cuts:
        cat[f"ngal_{cut}"] = np.sum(cat["mag"] < cut)

    return cat


def add_no_blending(cat, par):
    """
    Add no blending information to the catalog.

    :param cat: catalog
    :param par: context parameters
    :return: catalog with no blending information
    """
    return cat


def enrich_star_catalog(cat, par):
    """
    Add additional columns to the star catalog such that it can be used the same way as
    the galaxy catalog

    :param cat: catalog of stars
    :param par: ctx parameters
    :param catalog_precision: precision of the catalog
    :return: catalog of stars with additional columns and a list of the new column names
    """
    new_names = ["r50", "sersic_n", "e1", "e2", "z", "galaxy_type", "excess_b_v"]
    if cat is None:
        # to just get the names of the columns later
        return cat, new_names
    cat = at.add_cols(cat, new_names, dtype=par.catalog_precision)

    # set values that make sense for stars
    cat["r50"] = 0
    cat["sersic_n"] = 0
    cat["e1"] = 0
    cat["e2"] = 0
    cat["z"] = 0
    cat["galaxy_type"] = -1
    cat["excess_b_v"] = 0

    cat, _ = enrich_catalog(cat, par)
    return cat, new_names


def enrich_catalog(cat, par):
    """
    Enrich the catalog with computed columns: absolute ellipticity, noise levels

    :param cat: catalog
    :param par: ctx parameters
    :param catalog_precision: precision of the catalog
    :return: catalog with additional columns
    """
    cat = at.add_cols(
        cat,
        ["e_abs"],
        data=np.sqrt(cat["e1"] ** 2 + cat["e2"] ** 2),
        dtype=par.catalog_precision,
    )
    # add noise levels if used in the emulator
    if not par.emu_mini:
        cat = at.add_cols(
            cat,
            ["bkg_noise_amp"],
            data=(np.ones(len(cat)) * par.bkg_noise_amp),
            dtype=par.catalog_precision,
        )
        try:
            y = cat["y"].astype(int)
            x = cat["x"].astype(int)
            cat = at.add_cols(
                cat,
                ["bkg_noise_std"],
                data=par.bkg_noise_std[y, x],
                dtype=par.catalog_precision,
            )
            return cat, ["e_abs", "bkg_noise_amp", "bkg_noise_std"]
        except ValueError:
            pass
    return cat, ["e_abs"]


FLUX_ESTIMATOR = {
    "full_image": add_blending_full_image,
    "points": add_blending_points,
    "integrated": add_blending_integrated,
    "binned_integrated": add_blending_binned_integrated,
    "ngal": add_blending_ngal,
    "none": add_no_blending,
}


class Plugin(BasePlugin):
    def __call__(self):
        par = self.ctx.parameters

        f = self.ctx.current_filter

        LOGGER.info(f"Writing catalog for filter {f}")

        # write the classic catalogs
        cat_gals = catalog_to_rec(self.ctx.galaxies) if "galaxies" in self.ctx else None
        cat_stars = catalog_to_rec(self.ctx.stars) if "stars" in self.ctx else None
        # Create the catalogs for the emulators
        filepath_det = par.det_clf_catalog_name_dict[f]
        conf = par.emu_conf
        cat_stars, _ = enrich_star_catalog(cat_stars, par)
        cat_gals, _ = enrich_catalog(cat_gals, par)

        cat_gals, cat_stars = ensure_valid_cats(cat_gals, cat_stars)

        cat = {}
        for p in conf["input_band_dep"]:
            try:
                cat[p] = np.concatenate([cat_gals[p], cat_stars[p]], axis=0).astype(
                    par.catalog_precision
                )
            except Exception:
                acceptable_params = [
                    "ngal",
                    "estimated_flux",
                    "density_mag_weighted",
                    "density_size_weighted",
                ]
                # if p starts with any of the acceptable params, it is fine
                if any([p.startswith(ap) for ap in acceptable_params]):
                    LOGGER.debug(
                        f"Could not concatenate param {p}"
                        " (if this is a flux estimator, this is expected)"
                    )
                    continue
                LOGGER.warning(f"Could not concatenate param {p}")
        for p in conf["input_band_indep"]:
            cat[p] = np.concatenate([cat_gals[p], cat_stars[p]], axis=0).astype(
                par.catalog_precision
            )
        if "x" in cat_gals.dtype.names:
            params = ["x", "y", "id"]
        else:
            params = ["ra", "dec", "id"]
        for p in params:
            cat[p] = np.concatenate([cat_gals[p], cat_stars[p]], axis=0)

        for p in ["psf_fwhm"]:
            # add parameters that are not part of the emulator but are needed
            # for the sample selection and matching, mainly used for training data
            if p not in cat and not par.emu_mini:
                cat[p] = np.concatenate([cat_gals[p], cat_stars[p]], axis=0)

        if (par.flux_estimation_type == "full_image") or (
            par.flux_estimation_type == "points"
        ):
            # add ellipticities and sersic param
            for p in ["e1", "e2", "sersic_n"]:
                if p not in cat:
                    cat[p] = np.concatenate([cat_gals[p], cat_stars[p]], axis=0)

        cat = at.dict2rec(cat)

        # add blending risk parameters
        add_blending = FLUX_ESTIMATOR[par.flux_estimation_type]
        cat = add_blending(cat, par)
        file_utils.write_to_hdf(filepath_det, cat)

        # save galaxy and star catalog
        gals = cat["galaxy_type"] != -1
        stars = cat["galaxy_type"] == -1
        file_utils.write_to_hdf(par.galaxy_catalog_name_dict[f], cat[gals])
        file_utils.write_to_hdf(par.star_catalog_name_dict[f], cat[stars])

    def __str__(self):
        return "write emu-opt ucat catalog"
