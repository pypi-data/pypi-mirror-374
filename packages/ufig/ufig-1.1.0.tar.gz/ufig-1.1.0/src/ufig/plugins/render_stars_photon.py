# Copyright (c) 2017 ETH Zurich, Cosmology Research Group
"""
Created on Jul 31, 2017
@author: Joerg Herbel
"""

import numba as nb
import numpy as np
from cosmic_toolbox.logger import get_logger
from ivy.plugin.base_plugin import BasePlugin

from ufig import rendering_util
from ufig.plugins import add_psf

LOGGER = get_logger(__file__)

NAME = "render stars photon-based"


@nb.jit(nopython=True, nogil=True)
def integrate_image_phot(
    buffer,
    image,
    x,
    y,
    nphot,
    psf_betas,
    ellip_matrices,
    flexion_tensors,
    kurtoses,
    dx_offset,
    dy_offset,
    flexion_suppression,
    sort_by_y,
):
    sin_table, cos_table = rendering_util.sin_cos_table()
    alpha_by_fwhm, beta_power = rendering_util.moffat_cdf_factors(psf_betas)

    ind_stars = np.argsort(y) if sort_by_y else np.arange(len(y))

    rng = 0

    for i_star in ind_stars:
        for i_beta in range(psf_betas.shape[1]):
            flexion_suppress = rendering_util.psf_flexion_suppression(
                psf_betas[i_star, i_beta], flexion_suppression
            )
            kurtosis_suppress = rendering_util.psf_kurtosis_suppression(
                psf_betas[i_star, i_beta]
            )

            for _ in range(nphot[i_star, i_beta]):
                dr, dx, dy = rendering_util.draw_photon_psf(
                    buffer,
                    sin_table,
                    cos_table,
                    alpha_by_fwhm[i_star, i_beta],
                    beta_power[i_star, i_beta],
                    rng,
                    ellip_matrices[i_star],
                    flexion_tensors[i_star],
                    kurtoses[i_star, i_beta],
                    flexion_suppress,
                    kurtosis_suppress,
                    dx_offset[i_star, i_beta],
                    dy_offset[i_star, i_beta],
                )

                rendering_util.add_photon(image, x[i_star], y[i_star], dx, dy)

                rng += 2
                if rng + 2 > 44497:
                    buffer[:21034] += buffer[(44497 - 21034) : 44497]
                    buffer[21034:44497] += buffer[: (44497 - 21034)]
                    rng = 0


@nb.jit(nopython=True)
def pixel_integration(
    seed,
    image,
    r_max,
    x,
    y,
    nphot,
    psf_beta,
    psf_r50,
    psf_e1,
    psf_e2,
    psf_dx_offset,
    psf_dy_offset,
):
    # Seed within numba-compiled code, otherwise this code won't be affected
    np.random.seed(seed)

    size_y, size_x = image.shape
    alpha_sq = 1.0 / (2.0 ** (1.0 / (psf_beta - 1.0)) - 1.0)

    # bounds for x axis
    center_x = x.astype(np.int_)
    offset_x = x - np.floor(x)
    min_x = -r_max
    idx = center_x < r_max
    min_x[idx] = -center_x[idx]
    max_x = (
        r_max.copy()
    )  # otherwise it will be a pointer, which overwritten and then re-used
    idx = size_x - r_max <= center_x
    max_x[idx] = size_x - 1 - center_x[idx]

    # bounds for y axis
    center_y = y.astype(np.int_)
    offset_y = y - np.floor(y)
    min_y = -r_max
    idy = center_y < r_max
    min_y[idy] = -center_y[idy]
    max_y = (
        r_max.copy()
    )  # otherwise it will be a pointer, which overwritten and then re-used
    idy = size_y - r_max <= center_y
    max_y[idy] = size_y - 1 - center_y[idy]

    for i in range(len(x)):
        star = np.zeros(
            (max_y[i] - min_y[i] + 1, max_x[i] - min_x[i] + 1), dtype=image.dtype
        )

        if star.shape == (1, 1):
            continue

        rendering_util.integrate_pixel_psf(
            alpha_sq[i],
            psf_beta[i],
            psf_r50[i],
            psf_e1[i],
            psf_e2[i],
            psf_dx_offset[i],
            psf_dy_offset[i],
            nphot[i],
            min_x[i],
            max_x[i],
            min_y[i],
            max_y[i],
            offset_x[i],
            offset_y[i],
            star,
        )

        image[
            min_y[i] + center_y[i] : max_y[i] + 1 + center_y[i],
            min_x[i] + center_x[i] : max_x[i] + 1 + center_x[i],
        ] += star


def integrate_image_pixel(
    seed,
    image,
    gain,
    render_stars_accuracy,
    x,
    y,
    nphot,
    psf_beta,
    psf_flux_ratio,
    psf_fwhm,
    psf_e1,
    psf_e2,
    psf_dx_offset,
    psf_dy_offset,
):
    # integrate a bigger radius for brighter stars
    index_min = np.argmin(psf_beta, axis=1)
    beta_min = psf_beta[np.arange(psf_beta.shape[0]), index_min]

    select = index_min > 0
    flux_ratio_min = psf_flux_ratio.copy()
    flux_ratio_min[select] = 1 - flux_ratio_min[select]

    alpha_min = add_psf.moffat_fwhm2alpha(psf_fwhm, beta_min)
    flux = (
        nphot
        * flux_ratio_min
        * (beta_min - 1)
        / (np.pi * gain)
        * alpha_min ** (2 * (beta_min - 1))
    )
    r_max = ((flux / render_stars_accuracy) ** (1.0 / (2 * beta_min))).astype(np.int_)
    r_max += 2

    # Distribute photons to individual Moffat profiles
    nphot_split = rendering_util.distribute_photons_psf_profiles(
        nphot, psf_beta.shape[1], psf_flux_ratio
    )

    # Get r50
    psf_r50 = np.empty_like(psf_beta)

    for beta_ind in range(psf_beta.shape[1]):
        psf_r50[:, beta_ind] = add_psf.moffat_fwhm2r50(
            psf_fwhm, psf_beta[:, beta_ind], psf_flux_ratio
        )

    pixel_integration(
        seed,
        image,
        r_max,
        x,
        y,
        nphot_split,
        psf_beta,
        psf_r50,
        psf_e1,
        psf_e2,
        psf_dx_offset,
        psf_dy_offset,
    )


@nb.jit(nopython=True)
def integrate_cube(
    buffer,
    cube,
    x,
    y,
    nphot,
    psf_betas,
    ellip_matrices,
    flexion_tensors,
    kurtoses,
    dx_offset,
    dy_offset,
    flexion_suppression,
    q_xx,
    q_yy,
    q_xy,
):
    sin_table, cos_table = rendering_util.sin_cos_table()
    alpha_by_fwhm, beta_power = rendering_util.moffat_cdf_factors(psf_betas)

    rng = 0
    cov_cutoff = 5

    for i_star in range(x.size):
        n_phot_cov = 0
        mean_phot_x = 0.0
        mean_phot_y = 0.0

        for i_beta in range(psf_betas.shape[1]):
            flexion_suppress = rendering_util.psf_flexion_suppression(
                psf_betas[i_star, i_beta], flexion_suppression
            )
            kurtosis_suppress = rendering_util.psf_kurtosis_suppression(
                psf_betas[i_star, i_beta]
            )

            for _ in range(nphot[i_star, i_beta]):
                dr, dx, dy = rendering_util.draw_photon_psf(
                    buffer,
                    sin_table,
                    cos_table,
                    alpha_by_fwhm[i_star, i_beta],
                    beta_power[i_star, i_beta],
                    rng,
                    ellip_matrices[i_star],
                    flexion_tensors[i_star],
                    kurtoses[i_star, i_beta],
                    flexion_suppress,
                    kurtosis_suppress,
                    dx_offset[i_star, i_beta],
                    dy_offset[i_star, i_beta],
                )

                rendering_util.add_photon(cube[i_star], x[i_star], y[i_star], dx, dy)

                rng += 2
                if rng + 2 > 44497:
                    buffer[:21034] += buffer[(44497 - 21034) : 44497]
                    buffer[21034:44497] += buffer[: (44497 - 21034)]
                    rng = 0

                # moments
                if dr < cov_cutoff:
                    n_phot_cov += 1
                    delta_x = dx - mean_phot_x
                    delta_y = dy - mean_phot_y
                    mean_phot_x += delta_x / n_phot_cov
                    mean_phot_y += delta_y / n_phot_cov
                    delta_y_2 = dy - mean_phot_y
                    q_xx[i_star] += delta_x * (dx - mean_phot_x)
                    q_yy[i_star] += delta_y * delta_y_2
                    q_xy[i_star] += delta_x * delta_y_2

        if n_phot_cov > 1:
            q_xx[i_star] /= n_phot_cov - 1
            q_yy[i_star] /= n_phot_cov - 1
            q_xy[i_star] /= n_phot_cov - 1


def integrate_threaded(
    ctx,
    x,
    y,
    nphot,
    psf_beta,
    psf_ellip_matrices,
    psf_flexion_tensors,
    psf_kurtoses,
    psf_dx_offset,
    psf_dy_offset,
    flexion_suppression,
):
    n_threads = ctx.parameters.n_threads_photon_rendering

    # Split workload between threads
    ind_split = rendering_util.split_array(x, n_threads)
    image = ctx.image
    ctx.image = None

    rendering_args_split = [
        [rendering_util.rng_buffer() for _ in range(n_threads)],
        [image for _ in range(n_threads)],
        [x[i_split] for i_split in ind_split],
        [y[i_split] for i_split in ind_split],
        [nphot[i_split] for i_split in ind_split],
        [psf_beta[i_split] for i_split in ind_split],
        [psf_ellip_matrices[i_split] for i_split in ind_split],
        [psf_flexion_tensors[i_split] for i_split in ind_split],
        [psf_kurtoses[i_split] for i_split in ind_split],
        [psf_dx_offset[i_split] for i_split in ind_split],
        [psf_dy_offset[i_split] for i_split in ind_split],
        [flexion_suppression for _ in range(n_threads)],
        [True for _ in range(n_threads)],
    ]

    # Run in threads
    # print('Number of threads used for rendering stars: {}'.format(n_threads))
    rendering_util.execute_threaded(
        integrate_image_phot, n_threads, *rendering_args_split
    )
    ctx.image = image


class Plugin(BasePlugin):
    """
    Render stellar profiles photon-by-photon onto a pixelated grid.
    """

    def __str__(self):
        return NAME

    def __call__(self):
        par = self.ctx.parameters

        LOGGER.info(f"Rendering {self.ctx.numstars} stars")

        # Seed
        current_seed = par.seed + par.star_render_seed_offset
        np.random.seed(par.seed + par.star_render_seed_offset)

        # PSF properties
        if self.ctx.stars.psf_beta.shape[1] == 1:
            self.ctx.stars.psf_flux_ratio = np.ones(self.ctx.numstars)

        psf_ellip_matrices = rendering_util.compute_ellip_matrices(
            self.ctx.stars.psf_fwhm, self.ctx.stars.psf_e1, self.ctx.stars.psf_e2
        )

        psf_flexion_tensors = rendering_util.compute_flexion_tensors(
            self.ctx.stars.psf_fwhm,
            self.ctx.stars.psf_f1,
            self.ctx.stars.psf_f2,
            self.ctx.stars.psf_g1,
            self.ctx.stars.psf_g2,
        )

        psf_kurtoses = rendering_util.compute_kurtoses(
            self.ctx.stars.psf_fwhm,
            self.ctx.stars.psf_kurtosis,
            self.ctx.stars.psf_beta,
        )

        # Calculate number of photons
        nphot = rendering_util.distribute_photons_psf_profiles(
            self.ctx.stars.nphot,
            self.ctx.stars.psf_beta.shape[1],
            self.ctx.stars.psf_flux_ratio,
        )

        if hasattr(self.ctx, "image"):
            if hasattr(par, "mag_pixel_rendering_stars"):
                mask_pix = self.ctx.stars.mag < par.mag_pixel_rendering_stars
                mask_phot = ~mask_pix

                if np.any(mask_phot):
                    if par.n_threads_photon_rendering > 1:
                        integrate_threaded(
                            self.ctx,
                            self.ctx.stars.x[mask_phot],
                            self.ctx.stars.y[mask_phot],
                            nphot[mask_phot],
                            self.ctx.stars.psf_beta[mask_phot],
                            psf_ellip_matrices[mask_phot],
                            psf_flexion_tensors[mask_phot],
                            psf_kurtoses[mask_phot],
                            self.ctx.stars.psf_dx_offset[mask_phot],
                            self.ctx.stars.psf_dy_offset[mask_phot],
                            par.psf_flexion_suppression,
                        )

                    else:
                        integrate_image_phot(
                            rendering_util.rng_buffer(),
                            self.ctx.image,
                            self.ctx.stars.x[mask_phot],
                            self.ctx.stars.y[mask_phot],
                            nphot[mask_phot],
                            self.ctx.stars.psf_beta[mask_phot],
                            psf_ellip_matrices[mask_phot],
                            psf_flexion_tensors[mask_phot],
                            psf_kurtoses[mask_phot],
                            self.ctx.stars.psf_dx_offset[mask_phot],
                            self.ctx.stars.psf_dy_offset[mask_phot],
                            par.psf_flexion_suppression,
                            False,
                        )

                if np.any(mask_pix):
                    integrate_image_pixel(
                        current_seed,
                        self.ctx.image,
                        par.gain,
                        par.render_stars_accuracy,
                        self.ctx.stars.x[mask_pix],
                        self.ctx.stars.y[mask_pix],
                        self.ctx.stars.nphot[mask_pix],
                        self.ctx.stars.psf_beta[mask_pix],
                        self.ctx.stars.psf_flux_ratio[mask_pix],
                        self.ctx.stars.psf_fwhm[mask_pix],
                        self.ctx.stars.psf_e1[mask_pix],
                        self.ctx.stars.psf_e2[mask_pix],
                        self.ctx.stars.psf_dx_offset[mask_pix],
                        self.ctx.stars.psf_dy_offset[mask_pix],
                    )

            else:
                if par.n_threads_photon_rendering > 1:
                    integrate_threaded(
                        self.ctx,
                        self.ctx.stars.x,
                        self.ctx.stars.y,
                        nphot,
                        self.ctx.stars.psf_beta,
                        psf_ellip_matrices,
                        psf_flexion_tensors,
                        psf_kurtoses,
                        self.ctx.stars.psf_dx_offset,
                        self.ctx.stars.psf_dy_offset,
                        par.psf_flexion_suppression,
                    )

                else:
                    integrate_image_phot(
                        rendering_util.rng_buffer(),
                        self.ctx.image,
                        self.ctx.stars.x,
                        self.ctx.stars.y,
                        nphot,
                        self.ctx.stars.psf_beta,
                        psf_ellip_matrices,
                        psf_flexion_tensors,
                        psf_kurtoses,
                        self.ctx.stars.psf_dx_offset,
                        self.ctx.stars.psf_dy_offset,
                        par.psf_flexion_suppression,
                        False,
                    )

        elif hasattr(self.ctx, "star_cube"):
            # Initialize moments
            self.ctx.stars.q_xx = np.zeros(self.ctx.numstars)
            self.ctx.stars.q_yy = np.zeros(self.ctx.numstars)
            self.ctx.stars.q_xy = np.zeros(self.ctx.numstars)

            integrate_cube(
                rendering_util.rng_buffer(),
                self.ctx.star_cube,
                self.ctx.stars.x,
                self.ctx.stars.y,
                nphot,
                self.ctx.stars.psf_beta,
                psf_ellip_matrices,
                psf_flexion_tensors,
                psf_kurtoses,
                self.ctx.stars.psf_dx_offset,
                self.ctx.stars.psf_dy_offset,
                par.psf_flexion_suppression,
                self.ctx.stars.q_xx,
                self.ctx.stars.q_yy,
                self.ctx.stars.q_xy,
            )

        else:
            raise RuntimeError(
                "No known photon container (image or star_cube) provided in ivy context"
            )
