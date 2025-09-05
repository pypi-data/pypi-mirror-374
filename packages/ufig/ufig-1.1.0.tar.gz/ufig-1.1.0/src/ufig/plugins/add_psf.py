# Copyright (c) 2015 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>

"""
Created on Mar 20, 2015
@author: Claudio Bruderer
adapted by Silvan Fischbacher, 2024
"""

import h5py
import healpy as hp
import numba as nb
import numpy as np
from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin
from scipy import optimize

from ufig import io_util
from ufig.psf_estimation import correct_brighter_fatter

from .. import coordinate_util

LOGGER = logger.get_logger(__file__)

NAME = "add psf"


@nb.njit(nb.types.int32[:](nb.types.float32[:, :], nb.types.float32[:, :]), cache=True)
def numba_min_dist(X, Y):
    """
    Finds the index of the closest point in Y for each point in X
    """
    m = X.shape[0]
    D = np.zeros((m,), dtype=np.int32)
    for i in nb.prange(m):
        arg_min = np.argmin(np.sum((X[i] - Y) ** 2, axis=1))
        D[i] = arg_min

    return D


def load_psf_skymaps(psf_maps, par):
    """
    Load maps of the PSF across the sky.

    :param psf_maps: File name of the psf maps (0: r50-map, 1: e1-map, 2: e2-map)
    :param par: ctx.parameters containing potential fudge factors for PSF maps

    :return r50_map: r50-map containing flux radius (50%)-variations across the survey
                    area
    :return e1_map: Ellipticity 1-component-map containing variations across the survey
                    area
    :return e2_map: Ellipticity 2-component-map containing variations across the survey
                    area
    """

    maps = io_util.load_hpmap(psf_maps, par.maps_remote_dir)
    r50_map = par.psf_r50_factor * maps[0].astype(np.float32) + par.psf_r50_shift
    r50_map[r50_map < 0] = 0.0
    e1_map = par.psf_e1_prefactor * (
        par.psf_e1_factor * maps[1].astype(np.float32) + par.psf_e1_shift
    )
    e2_map = par.psf_e2_factor * maps[2].astype(np.float32) + par.psf_e2_shift
    return r50_map, e1_map, e2_map


def psf_from_sky_maps(r50_map, e1_map, e2_map, psf_beta, w, x, y, psf_flux_ratio):
    """
    Evaluate PSF maps at input positions.

    :param r50_map: r50-map containing flux radius (50%)-variations across the survey
                    area
    :param e1_map: Ellipticity 1-component-map containing variations across the survey
                   area
    :param e2_map: Ellipticity 2-component-map containing variations across the survey
                   area
    :param psf_beta: PSF beta parameter evaluated at every object's position
    :param w: wcs-object containing all the relevant wcs-transformation information
    :param x: pixel x-coordinate
    :param y: pixel y-coordinate
    :param psf_flux_ratio: Flux ratio of the different PSF Moffat component(s) relative
                           to the total flux

    :return r50: PSF r50 (flux radius 50%) evaluated at the input positions
    :return beta: PSF beta parameter evaluated at the input positions
    :return e1: PSF ellipticity 1-component evaluated at the input positions
    :return e2: PSF ellipticity 2-component evaluated at the input positions
    """

    # +0.5 is to convert it into origin-1 convention
    theta, phi = coordinate_util.xy2thetaphi(w, x, y)

    beta = np.full((x.size, len(psf_beta)), psf_beta, np.float32)

    # PSF interpolation
    nside = hp.get_nside(r50_map)

    pix_indices = hp.ang2pix(nside=nside, theta=theta, phi=phi, nest=False)

    r50 = r50_map[pix_indices]
    e1 = e1_map[pix_indices]
    e2 = e2_map[pix_indices]

    # Convert psf_r50 to psf_fwhm (multiple betas)
    psf_fwhm = moffat_r502fwhm(r50, psf_beta, psf_flux_ratio)

    psf_r50_indiv = np.empty((len(psf_beta), x.size), dtype=np.float32)
    for i in range(len(psf_beta)):
        psf_r50_indiv[i] = moffat_fwhm2r50(psf_fwhm, psf_beta[i], psf_flux_ratio)

    return r50, beta, e1, e2, psf_r50_indiv, psf_fwhm


def get_moffat_maps_psf(obj_name, ctx):
    """
    Set the PSF for objects (stars or galaxies) using maps of the PSF across the sky.

    :param obj_name: Name of the objects the PSF is evaluated for
    :param ctx: Ivy-context containing the catalog of the object properties

    :return r50: PSF r50 (flux radius 50%) evaluated at the positions of the input
                 objects
    :return beta: PSF beta parameter evaluated at the positions of the input objects
    :return e1: PSF ellipticity 1-component evaluated at the positions of the input
                objects
    :return e2: PSF ellipticity 2-component evaluated at the positions of the input
                objects
    """

    par = ctx.parameters

    obj = getattr(ctx, obj_name)

    if not isinstance(par.psf_beta, list):
        par.psf_beta = [par.psf_beta]

    if len(par.psf_beta) == 1:
        par.psf_flux_ratio = 1

    if not hasattr(ctx, "psf_r50_map"):
        ctx.psf_r50_map, ctx.psf_e1_map, ctx.psf_e2_map = load_psf_skymaps(
            par.psf_maps, par
        )

    w = coordinate_util.tile_in_skycoords(
        pixscale=par.pixscale,
        ra0=par.ra0,
        dec0=par.dec0,
        crpix_ra=par.crpix_ra,
        crpix_dec=par.crpix_dec,
    )

    x = obj.x
    y = obj.y

    psf_r50, psf_beta, psf_e1, psf_e2, psf_r50_indiv, psf_fwhm = psf_from_sky_maps(
        r50_map=ctx.psf_r50_map,
        e1_map=ctx.psf_e1_map,
        e2_map=ctx.psf_e2_map,
        psf_beta=par.psf_beta,
        w=w,
        x=x,
        y=y,
        psf_flux_ratio=par.psf_flux_ratio,
    )
    ctx.psf_column_names = [
        "psf_r50",
        "psf_beta",
        "psf_e1",
        "psf_e2",
        "psf_r50_indiv",
        "psf_fwhm",
    ]

    obj.psf_r50 = psf_r50
    obj.psf_beta = psf_beta
    obj.psf_e1 = psf_e1
    obj.psf_e2 = psf_e2
    obj.psf_r50_indiv = psf_r50_indiv
    obj.psf_fwhm = psf_fwhm


def apply_psf_parameter_scalings(psf_par, par):
    for name in psf_par.dtype.names:
        if name in par.psf_cnn_factors:
            psf_par[name] = (
                par.psf_cnn_factors[name][0]
                + par.psf_cnn_factors[name][1] * psf_par[name]
            )


def ensure_valid_psf_beta(psf_beta):
    psf_beta[:] = np.clip(psf_beta, a_min=1.2, a_max=np.inf)


def ensure_valid_psf_flux_ratio(psf_flux_ratio):
    psf_flux_ratio[:] = np.clip(psf_flux_ratio, a_min=0.0, a_max=1.0)
    psf_flux_ratio[:] = np.nan_to_num(psf_flux_ratio, nan=1.0)


def ensure_valid_psf_fwhm(psf_fwhm):
    select = psf_fwhm <= 0
    psf_fwhm[select] = 0.0001


def ensure_valid_psf_ellip(psf_e1, psf_e2):
    psf_ellip = np.sqrt(psf_e1**2 + psf_e2**2)
    select = psf_ellip > 1
    psf_e1[select] /= 1.01 * psf_ellip[select]
    psf_e2[select] /= 1.01 * psf_ellip[select]


def get_moffat_coadd_psf_cnn(obj_name, ctx):
    # Parameters
    par = ctx.parameters

    # Objects
    obj = getattr(ctx, obj_name)

    # Predict PSF at object position
    predict_args = dict(
        position_xy=np.stack((obj.x, obj.y), axis=-1),
        filepath_psfmodel=io_util.get_abs_path(
            par.filepath_psfmodel_input, par.maps_remote_dir
        ),
    )

    if par.psf_type == "coadd_moffat_cnn_robust" or par.psf_type == "coadd_moffat_cnn":
        if par.psf_type == "coadd_moffat_cnn_robust":  # pragma: no cover
            LOGGER.warning("Using deprecated PSF type name 'coadd_moffat_cnn_robust'")
            LOGGER.warning("Please use 'coadd_moffat_cnn' instead")

        from ufig.psf_estimation import psf_predictions as psf_pred

        col_ending = "_ipt"

    psf_par_pred = next(psf_pred.predict_psf_with_file(**predict_args))[0]

    # Scale predictions
    apply_psf_parameter_scalings(psf_par_pred, par)

    # Set PSF beta
    n_beta = len(
        list(
            filter(
                lambda col: col.startswith("psf_beta_") and col.endswith(col_ending),
                psf_par_pred.dtype.names,
            )
        )
    )

    if n_beta > 0:
        obj.psf_beta = np.empty((len(psf_par_pred), n_beta), dtype=np.float32)

        for i_beta in range(n_beta):
            obj.psf_beta[:, i_beta] = psf_par_pred[f"psf_beta_{i_beta + 1}{col_ending}"]

    else:
        obj.psf_beta = np.full(
            (len(psf_par_pred), len(par.psf_beta)), par.psf_beta, dtype=np.float32
        )

    # Set other PSF parameters
    psf_par_names = [
        "psf_flux_ratio",
        "psf_fwhm",
        "psf_e1",
        "psf_e2",
        "psf_f1",
        "psf_f2",
        "psf_g1",
        "psf_g2",
        "psf_kurtosis",
    ]

    for psf_par_name in psf_par_names:
        psf_par_name_ipt = psf_par_name + col_ending

        if psf_par_name_ipt in psf_par_pred.dtype.names:
            psf_par_col = psf_par_pred[psf_par_name_ipt]

        else:
            psf_par_col = np.full(
                len(psf_par_pred),
                getattr(ctx.parameters, psf_par_name),
                dtype=np.float32,
            )

        setattr(obj, psf_par_name, psf_par_col)

    # Ensure valid beta, flux ratio, size and ellipticity
    ensure_valid_psf_beta(obj.psf_beta)
    ensure_valid_psf_flux_ratio(obj.psf_flux_ratio)
    ensure_valid_psf_fwhm(obj.psf_fwhm)
    ensure_valid_psf_ellip(obj.psf_e1, obj.psf_e2)

    # Set half-light radii and offsets between profiles
    obj.psf_r50_indiv = (
        obj.psf_fwhm[:, np.newaxis]
        * np.sqrt((2 ** (1 / (obj.psf_beta - 1)) - 1) / (2 ** (1 / obj.psf_beta) - 1))
        / 2
    )
    obj.psf_r50_indiv = obj.psf_r50_indiv.T
    obj.psf_dx_offset = np.zeros_like(obj.psf_r50_indiv).T
    obj.psf_dy_offset = np.zeros_like(obj.psf_r50_indiv).T

    # Apply brighter-fatter corrections
    if ctx.parameters.psfmodel_corr_brighter_fatter is not None:
        apply_brighter_fatter = False

        if obj_name == "stars":
            apply_brighter_fatter = True

        if (obj_name == "galaxies") and (
            "apply_to_galaxies" in ctx.parameters.psfmodel_corr_brighter_fatter
        ):
            apply_brighter_fatter = ctx.parameters.psfmodel_corr_brighter_fatter[
                "apply_to_galaxies"
            ]

        if apply_brighter_fatter:
            (
                obj.psf_fwhm,
                obj.psf_e1,
                obj.psf_e2,
            ) = correct_brighter_fatter.brighter_fatter_add(
                col_mag=obj.mag,
                col_fwhm=obj.psf_fwhm,
                col_e1=obj.psf_e1,
                col_e2=obj.psf_e2,
                dict_corr=ctx.parameters.psfmodel_corr_brighter_fatter,
            )

    ctx.psf_column_names = [
        "psf_flux_ratio",
        "psf_fwhm",
        "psf_e1",
        "psf_e2",
        "psf_f1",
        "psf_f2",
        "psf_g1",
        "psf_g2",
        "psf_kurtosis",
        "psf_r50_indiv",
        "psf_dy_offset",
        "psf_dx_offset",
    ]


def get_moffat_coadd_psf_cnn_from_file(obj_name, ctx):
    # Parameters
    par = ctx.parameters

    # Objects
    obj = getattr(ctx, obj_name)

    # Predict PSF at object position
    predict_args = dict(
        position_xy=np.stack((obj.x, obj.y), axis=-1),
        filepath_psfmodel=par.filepath_psfmodel_input,
    )

    col_ending = "_ipt"

    psfcat = h5py.File(predict_args["filepath_psfmodel"])

    xy_ucat = np.stack((obj.x, obj.y)).T
    xy_ucat += 0.5
    xy_psf = np.stack((psfcat["grid_psf"]["X_IMAGE"], psfcat["grid_psf"]["Y_IMAGE"])).T
    min_dist = numba_min_dist(xy_ucat.astype(np.float32), xy_psf.astype(np.float32))
    psf_params = [
        "psf_flux_ratio_ipt",
        "psf_fwhm_ipt",
        "psf_e1_ipt",
        "psf_e2_ipt",
        "psf_f1_ipt",
        "psf_f2_ipt",
        "psf_g1_ipt",
        "psf_g2_ipt",
    ]
    psf_par_pred = psfcat["grid_psf"][:][psf_params][min_dist]

    # Set PSF beta
    n_beta = len(
        list(
            filter(
                lambda col: col.startswith("psf_beta_") and col.endswith(col_ending),
                psf_par_pred.dtype.names,
            )
        )
    )

    if n_beta > 0:
        obj.psf_beta = np.empty((len(psf_par_pred), n_beta), dtype=np.float32)

        for i_beta in range(n_beta):
            obj.psf_beta[:, i_beta] = psf_par_pred[f"psf_beta_{i_beta + 1}{col_ending}"]

    else:
        obj.psf_beta = np.full(
            (len(psf_par_pred), len(par.psf_beta)), par.psf_beta, dtype=np.float32
        )

    # Set other PSF parameters
    psf_par_names = [
        "psf_flux_ratio",
        "psf_fwhm",
        "psf_e1",
        "psf_e2",
        "psf_f1",
        "psf_f2",
        "psf_g1",
        "psf_g2",
        "psf_kurtosis",
    ]

    for psf_par_name in psf_par_names:
        psf_par_name_ipt = psf_par_name + col_ending

        if psf_par_name_ipt in psf_par_pred.dtype.names:
            psf_par_col = psf_par_pred[psf_par_name_ipt]

        else:
            psf_par_col = np.full(
                len(psf_par_pred),
                getattr(ctx.parameters, psf_par_name),
                dtype=np.float32,
            )

        setattr(obj, psf_par_name, psf_par_col)

    # Ensure valid beta, flux ratio, size and ellipticity
    ensure_valid_psf_beta(obj.psf_beta)
    ensure_valid_psf_flux_ratio(obj.psf_flux_ratio)
    ensure_valid_psf_fwhm(obj.psf_fwhm)
    ensure_valid_psf_ellip(obj.psf_e1, obj.psf_e2)

    # Set half-light radii and offsets between profiles
    obj.psf_r50_indiv = (
        obj.psf_fwhm[:, np.newaxis]
        * np.sqrt((2 ** (1 / (obj.psf_beta - 1)) - 1) / (2 ** (1 / obj.psf_beta) - 1))
        / 2
    )
    obj.psf_r50_indiv = obj.psf_r50_indiv.T
    obj.psf_dx_offset = np.zeros_like(obj.psf_r50_indiv).T
    obj.psf_dy_offset = np.zeros_like(obj.psf_r50_indiv).T

    # Apply brighter-fatter corrections
    if ctx.parameters.psfmodel_corr_brighter_fatter is not None:
        apply_brighter_fatter = False

        if obj_name == "stars":
            apply_brighter_fatter = True

        if (obj_name == "galaxies") and (
            "apply_to_galaxies" in ctx.parameters.psfmodel_corr_brighter_fatter
        ):
            apply_brighter_fatter = ctx.parameters.psfmodel_corr_brighter_fatter[
                "apply_to_galaxies"
            ]

        if apply_brighter_fatter:
            (
                obj.psf_fwhm,
                obj.psf_e1,
                obj.psf_e2,
            ) = correct_brighter_fatter.brighter_fatter_add(
                col_mag=obj.mag,
                col_fwhm=obj.psf_fwhm,
                col_e1=obj.psf_e1,
                col_e2=obj.psf_e2,
                dict_corr=ctx.parameters.psfmodel_corr_brighter_fatter,
            )

    ctx.psf_column_names = [
        "psf_flux_ratio",
        "psf_fwhm",
        "psf_e1",
        "psf_e2",
        "psf_f1",
        "psf_f2",
        "psf_g1",
        "psf_g2",
        "psf_kurtosis",
        "psf_r50_indiv",
        "psf_dy_offset",
        "psf_dx_offset",
    ]


def sample_psf_moffat_constant(obj_name, ctx):
    """
    Evaluate a constant, Moffat-PSF field at the positions of different objects (stars
    or galaxies).

    :param obj: Name of the objects the PSF is evaluated for
    :param ctx: Ivy-context containing the catalog of the object properties
    :return r50: PSF r50 (flux radius 50%) evaluated at the positions of the input
                 objects
    :return beta: PSF beta parameter evaluated at the positions of the input objects
    :return e1: PSF ellipticity 1-component evaluated at the positions of the input
                objects
    :return e2: PSF ellipticity 2-component evaluated at the positions of the input
                objects
    """

    par = ctx.parameters

    # Objects
    obj = getattr(ctx, obj_name)

    if not isinstance(par.psf_beta, list):
        par.psf_beta = [par.psf_beta]

    if len(par.psf_beta) == 1:
        par.psf_flux_ratio = 1

    numobj = obj.x.size

    psf_fwhm = np.full(numobj, par.seeing / par.pixscale, dtype=np.float32)
    psf_r50 = moffat_fwhm2r50(psf_fwhm, par.psf_beta, par.psf_flux_ratio)
    psf_beta = np.full((numobj, len(par.psf_beta)), par.psf_beta, dtype=np.float32)
    psf_e1 = np.full(numobj, par.psf_e1, dtype=np.float32)
    psf_e2 = np.full(numobj, par.psf_e2, dtype=np.float32)

    psf_r50_indiv = np.empty((len(par.psf_beta), numobj))
    for i in range(len(par.psf_beta)):
        psf_r50_indiv[i] = moffat_fwhm2r50(
            psf_fwhm, par.psf_beta[i], par.psf_flux_ratio
        )

    obj.psf_dx_offset = np.zeros([len(obj.x), 2])
    obj.psf_dy_offset = np.zeros([len(obj.y), 2])

    ctx.psf_column_names = [
        "psf_r50",
        "psf_beta",
        "psf_e1",
        "psf_e2",
        "psf_r50_indiv",
        "psf_fwhm",
    ]

    obj.psf_r50 = psf_r50
    obj.psf_beta = psf_beta
    obj.psf_e1 = psf_e1
    obj.psf_e2 = psf_e2
    obj.psf_r50_indiv = psf_r50_indiv
    obj.psf_fwhm = psf_fwhm


def moffat_r502fwhm(psf_r50, psf_beta, psf_flux_ratio):
    """
    Computes the FWHM for a given r50 and beta parameter for the PSF assuming a Moffat
    distribution

    :param psf_r50: r50 of the PSF in units of pixels
    :param psf_beta: beta parameter for a Moffat distribution
    :return: FWHM of the PSF (assuming a Moffat distribution) in units of pixels
    """

    def convert(r50, beta):
        return 2 * r50 * np.sqrt((2 ** (1 / beta) - 1) / (2 ** (1 / (beta - 1)) - 1))

    if isinstance(psf_beta, np.ndarray):
        psf_fwhm = convert(psf_r50, psf_beta)

    else:
        if not isinstance(psf_beta, list):
            psf_beta = [psf_beta]

        if len(psf_beta) == 1:
            psf_fwhm = convert(psf_r50, psf_beta[0])
        else:
            psf_fwhm = multiple_moffat_fwhm(psf_r50, psf_beta, psf_flux_ratio)

    return psf_fwhm


def moffat_fwhm2r50(psf_fwhm, psf_beta, psf_flux_ratio):
    """
    Computes the r50 for a given FWHM and beta parameter for the PSF assuming a Moffat
    distribution

    :param psf_fwhm: FWHM of the PSF in units of pixels
    :param psf_beta: beta parameter for a Moffat distribution
    :return: r50 of the PSF (assuming a Moffat distribution) in units of pixels
    """

    def convert(fwhm, beta):
        return fwhm / 2 * np.sqrt((2 ** (1 / (beta - 1)) - 1) / (2 ** (1 / beta) - 1))

    if isinstance(psf_beta, np.ndarray):
        psf_r50 = convert(psf_fwhm, psf_beta)

    else:
        if not isinstance(psf_beta, list):
            psf_beta = [psf_beta]

        if len(psf_beta) == 1:
            psf_r50 = convert(psf_fwhm, psf_beta[0])
        else:
            psf_r50 = multiple_moffat_r50(psf_fwhm, psf_beta, psf_flux_ratio)

    return psf_r50


def moffat_fwhm2alpha(psf_fwhm, psf_beta):
    """
    Computes the alpha parameter for a given FWHM and beta parameter for a Moffat
    distribution

    :param psf_fwhm: FWHM of the PSF in units of pixels
    :param psf_beta: beta parameter for a Moffat distribution
    :return: alpha of the Moffat profile in units of pixels
    """

    if isinstance(psf_beta, list):
        psf_beta = psf_beta[0]

    alpha = psf_fwhm / 2 / np.sqrt(2 ** (1 / psf_beta) - 1)
    return alpha


def moffat_r502alpha(psf_r50, psf_beta):
    """
    Computes the alpha parameter for a given r50 and beta parameter for a Moffat
    distribution

    :param psf_r50: r50 of the PSF in units of pixels
    :param psf_beta: beta parameter for a Moffat distribution
    :return: alpha of the Moffat profile in units of pixels
    """

    if isinstance(psf_beta, list):
        psf_beta = psf_beta[0]

    alpha = psf_r50 / np.sqrt(2 ** (1 / (psf_beta - 1)) - 1)
    return alpha


def moffat_alpha2fwhm(psf_alpha, psf_beta):
    """
    Computes the fwhm (in the units alpha is in) for a given alpha and beta parameter
    for a Moffat distribution

    :param psf_alpha: alpha of the PSF in units of pixels
    :param psf_beta: beta parameter for a Moffat distribution
    :return: alpha of the Moffat profile in units of pixels
    """

    if isinstance(psf_beta, list):
        psf_beta = psf_beta[0]

    psf_fwhm = 2 * psf_alpha * np.sqrt(2 ** (1 / psf_beta) - 1)

    return psf_fwhm


def moffat_alpha2r50(psf_alpha, psf_beta):
    """
    Computes the r50 (in units of alpha) for a given alpha and beta parameter for a
    Moffat distribution

    :param psf_alpha: alpha of the PSF in units of pixels
    :param psf_beta: beta parameter for a Moffat distribution
    :return: alpha of the Moffat profile in units of pixels
    """

    if isinstance(psf_beta, list):
        psf_beta = psf_beta[0]

    psf_r50 = psf_alpha * np.sqrt(2 ** (1 / (psf_beta - 1)) - 1)

    return psf_r50


def moffat_profile_integrated(r, psf_beta, psf_flux_ratio):
    """
    Evaluates the integrated "1 - Moffat profile" within a radius r (in units of Moffat
    alpha), which potentially can consist of multiple components, and returns the flux
    in units of the total flux.

    :param x: Radius in units of Moffat alpha
    :param psf_beta: Moffat beta parameter(s)
    :param psf_flux_ratio: Fraction of flux in the first component
    :return: Flux within a radius r in units of the total flux
    """

    if not isinstance(psf_beta, list):
        psf_beta = [psf_beta]

    if len(psf_beta) == 1:
        psf_flux_ratio = 1

    value = 0.0
    for i in range(len(psf_beta)):
        value += psf_flux_ratio / (1 + r**2) ** (psf_beta[i] - 1)
        psf_flux_ratio = 1 - psf_flux_ratio

    return value


def _moffat_subtracted(x, ppsf_beta, ppsf_flux_ratio):
    return moffat_profile_integrated(x, ppsf_beta, ppsf_flux_ratio) - 0.5


def multiple_moffat_r50(psf_fwhm, psf_beta, psf_flux_ratio):
    """
    Solve the nonlinear equation to recover an effective r50 of a PSF profile
    consisting of potentially multiple Moffat profiles.

    :param psf_fwhm: FWHM of the Moffat profile in pixels
    :param psf_beta: Moffat beta parameter(s)
    :param psf_flux_ratio: Fraction of flux in the first component
    :return: r50 of the total PSF profile
    """

    r50 = optimize.brentq(
        _moffat_subtracted, 0.0, 10 * np.mean(psf_fwhm), args=(psf_beta, psf_flux_ratio)
    )

    alpha = moffat_fwhm2alpha(psf_fwhm, psf_beta[0])
    r50 = r50 * alpha

    return r50


def multiple_moffat_fwhm(psf_r50, psf_beta, psf_flux_ratio):
    """
    Solve the nonlinear equation to recover an effective fwhm of a PSF profile
    consisting of potentially multiple Moffat profiles.
    This function is similar to ufig.plugins.add_psf.multiple_moffat_r50().

    :param psf_fwhm: FWHM of the Moffat profile in pixels
    :param psf_beta: Moffat beta parameter(s)
    :param psf_flux_ratio: Fraction of flux in the first component
    :return: r50 of the total PSF profile
    """

    r50_reduced = optimize.brentq(
        _moffat_subtracted, 0.0, 10 * np.mean(psf_r50), args=(psf_beta, psf_flux_ratio)
    )

    alpha = psf_r50 / r50_reduced
    fwhm = moffat_alpha2fwhm(alpha, psf_beta[0])

    return fwhm


def update_psf_for_current_filter(obj, ctx):
    for col in ctx.psf_column_names:
        col_bands = f"{col}_dict"
        if not hasattr(obj, col_bands):
            col_dict = setattr(obj, col_bands, {})

        col_dict = getattr(obj, col_bands)
        col_dict[ctx.current_filter] = getattr(obj, col)


PSF_GENERATOR = {
    "constant_moffat": sample_psf_moffat_constant,
    "maps_moffat": get_moffat_maps_psf,
    "coadd_moffat_cnn": get_moffat_coadd_psf_cnn,
    "coadd_moffat_cnn_robust": get_moffat_coadd_psf_cnn,  # backwards compatibility
    "coadd_moffat_cnn_read": get_moffat_coadd_psf_cnn_from_file,  # keep
}


class Plugin(BasePlugin):
    """
    The PSF is applied to the input galaxy and star catalogs by evaluating the PSF size
    and ellipticity fields at every objects position

    :param psf_type: whether a constant or variable psf is added
    :param psf_beta: beta parameter for Moffat PSF profile
    :param seeing: seeing (arcsec)
    :param psf_e1: e1 for the PSF
    :param psf_e2: e2 for the PSF
    :param psf_maps: File name of the psf maps (0: r50-map, 1: e1-map, 2: e2-map)
    :param maps_remote_dir: Remote directory used in case the file name of the psf maps
                            is not absolute
    :param pixscale: pixel scale (arcsec/pixel)
    :param size_x: size of image in x-direction (pixel)
    :param size_y: size of image in y-direction (pixel)
    :param ra0: right ascension at the center of the image in degree
    :param dec0: declination at the center of the image in degree

    :return psf_r50: PSF r50 (flux radius 50%) evaluated at every object's position
    :return psf_beta: PSF beta parameter evaluated at every object's position
    :return psf_e1: PSF ellipticity 1-component evaluated at every object's position
    :return psf_e2: PSF ellipticity 2-component evaluated at every object's position
    """

    def __str__(self):
        return NAME

    def __call__(self):
        generator = PSF_GENERATOR[self.ctx.parameters.psf_type]
        LOGGER.info(f"Generating PSF with {self.ctx.parameters.psf_type}")

        psf_fwhm = np.array([])

        def add_psf_to_objects(obj, ctx, name_str):
            par = ctx.parameters

            generator(name_str, ctx)

            for p in ctx.psf_column_names:
                # set catalog precision
                arr = getattr(obj, p).astype(par.catalog_precision)
                setattr(obj, p, arr)

        if hasattr(self.ctx, "galaxies"):
            add_psf_to_objects(self.ctx.galaxies, self.ctx, "galaxies")
            update_psf_for_current_filter(self.ctx.galaxies, self.ctx)

            self.ctx.galaxies.psf_fwhm = np.random.normal(
                self.ctx.galaxies.psf_fwhm, self.ctx.parameters.psf_fwhm_variation_sigma
            )
            select = self.ctx.galaxies.psf_fwhm < 0
            if np.any(select):
                LOGGER.warning("Negative PSF FWHM detected. Setting to 0.")
                self.ctx.galaxies.psf_fwhm[select] = 0.0

            psf_fwhm = np.append(psf_fwhm, self.ctx.galaxies.psf_fwhm)

        if hasattr(self.ctx, "stars"):
            add_psf_to_objects(self.ctx.stars, self.ctx, "stars")
            update_psf_for_current_filter(self.ctx.stars, self.ctx)

            self.ctx.stars.psf_fwhm = np.random.normal(
                self.ctx.stars.psf_fwhm, self.ctx.parameters.psf_fwhm_variation_sigma
            )
            select = self.ctx.stars.psf_fwhm < 0
            if np.any(select):
                LOGGER.warning("Negative PSF FWHM detected. Setting to 0.")
                self.ctx.stars.psf_fwhm[select] = 0.0
            psf_fwhm = np.append(psf_fwhm, self.ctx.stars.psf_fwhm)

        if psf_fwhm.size > 0:
            self.ctx.average_seeing = np.mean(psf_fwhm)
            if not np.isfinite(self.ctx.average_seeing):  # pragma: no cover
                raise ValueError("Average seeing is not finite")

        try:
            del self.ctx.psf_r50_map
            del self.ctx.psf_e1_map
            del self.ctx.psf_e2_map
        except AttributeError:
            pass
