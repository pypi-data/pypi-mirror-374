# Copyright (c) 2013 ETH Zurich, Institute of Astronomy, Lukas Gamper
# <lukas.gamper@usystems.ch>
"""
Created on Oct 7, 2013
@author: Lukas Gamper

"""

import numba as nb
import numpy as np
from cosmic_toolbox.logger import get_logger
from ivy.plugin.base_plugin import BasePlugin

from ufig import rendering_util
from ufig.plugins.gamma_interpolation_table import load_intrinsicTable

LOGGER = get_logger(__file__)

NAME = "render galaxies (flexion)"
intrinsicTableCache = None


@nb.jit(nopython=True, nogil=True)
def integrate_image(
    buffer,
    gammaprecision,
    gammaprecisionhigh,
    sersicprecision,
    intrinsic_table,
    image,
    x,
    y,
    nphot,
    sersic_indices,
    gal_ellip_matrices,
    psf_betas,
    psf_ellip_matrices,
    psf_flexion_tensors,
    psf_kurtoses,
    psf_dx_offset,
    psf_dy_offset,
    psf_flexion_suppression,
    sort_by_y,
):
    sin_table, cos_table = rendering_util.sin_cos_table()
    alpha_by_fwhm, beta_power = rendering_util.moffat_cdf_factors(psf_betas)

    # sersic index lookup
    n = (sersic_indices * np.float64(np.int64(1) << 32) / 10.0).astype(np.uint32)
    sersic_table_l = (n >> np.uint32(32 - sersicprecision)).astype(np.uint32)
    sersic_table_b = (n - (sersic_table_l << np.uint32(32 - sersicprecision))).astype(
        np.float32
    )
    sersic_table_b /= np.float32(1 << (32 - sersicprecision))

    ind_galaxies = np.argsort(y) if sort_by_y else np.arange(len(y))

    rng = 0

    for i_gal in ind_galaxies:
        for i_beta in range(psf_betas.shape[1]):
            psf_flexion_suppress = rendering_util.psf_flexion_suppression(
                psf_betas[i_gal, i_beta], psf_flexion_suppression
            )
            psf_kurtosis_suppress = rendering_util.psf_kurtosis_suppression(
                psf_betas[i_gal, i_beta]
            )

            for _ in range(nphot[i_gal, i_beta]):
                dr_psf, dx_psf, dy_psf = rendering_util.draw_photon_psf(
                    buffer,
                    sin_table,
                    cos_table,
                    alpha_by_fwhm[i_gal, i_beta],
                    beta_power[i_gal, i_beta],
                    rng,
                    psf_ellip_matrices[i_gal],
                    psf_flexion_tensors[i_gal],
                    psf_kurtoses[i_gal, i_beta],
                    psf_flexion_suppress,
                    psf_kurtosis_suppress,
                    psf_dx_offset[i_gal, i_beta],
                    psf_dy_offset[i_gal, i_beta],
                )

                dx_gal, dy_gal = rendering_util.draw_photon_gal(
                    buffer,
                    sin_table,
                    cos_table,
                    gammaprecision,
                    gammaprecisionhigh,
                    sersic_table_l[i_gal],
                    sersic_table_b[i_gal],
                    intrinsic_table,
                    rng,
                    gal_ellip_matrices[i_gal],
                )

                dx = dx_psf + dx_gal
                dy = dy_psf + dy_gal

                rendering_util.add_photon(image, x[i_gal], y[i_gal], dx, dy)

                rng += 4

                if rng + 4 > 44497:
                    buffer[:21034] += buffer[(44497 - 21034) : 44497]
                    buffer[21034:44497] += buffer[: (44497 - 21034)]
                    rng = 0


class Plugin(BasePlugin):
    def __str__(self):
        return NAME

    def __call__(self):
        par = self.ctx.parameters

        LOGGER.info(f"Rendering {self.ctx.numgalaxies} galaxies")

        # Seed
        np.random.seed(par.seed + par.gal_render_seed_offset)

        # Intrinsic galaxy shapes
        gal_ellip_matrices = rendering_util.compute_ellip_matrices(
            self.ctx.galaxies.r50, self.ctx.galaxies.e1, self.ctx.galaxies.e2
        )

        # PSF properties
        if self.ctx.galaxies.psf_beta.shape[1] == 1:
            self.ctx.galaxies.psf_flux_ratio = np.ones(self.ctx.numgalaxies)

        psf_ellip_matrices = rendering_util.compute_ellip_matrices(
            self.ctx.galaxies.psf_fwhm,
            self.ctx.galaxies.psf_e1,
            self.ctx.galaxies.psf_e2,
        )

        psf_flexion_tensors = rendering_util.compute_flexion_tensors(
            self.ctx.galaxies.psf_fwhm,
            self.ctx.galaxies.psf_f1,
            self.ctx.galaxies.psf_f2,
            self.ctx.galaxies.psf_g1,
            self.ctx.galaxies.psf_g2,
        )

        psf_kurtoses = rendering_util.compute_kurtoses(
            self.ctx.galaxies.psf_fwhm,
            self.ctx.galaxies.psf_kurtosis,
            self.ctx.galaxies.psf_beta,
        )

        # Calculate number of photons
        nphot = rendering_util.distribute_photons_psf_profiles(
            self.ctx.galaxies.nphot,
            self.ctx.galaxies.psf_beta.shape[1],
            self.ctx.galaxies.psf_flux_ratio,
        )

        # By default, if intrinsicTable is not loaded/computed, a corresponding one in
        # res/intrinsictables/ is loaded
        if not hasattr(self.ctx, "intrinsicTable"):
            sersic_table = load_intrinsicTable(
                par.sersicprecision, par.gammaprecision, par.gammaprecisionhigh
            )
        else:
            sersic_table = self.ctx.intrinsicTable.copy()
            del self.ctx.intrinsicTable

        if par.n_threads_photon_rendering > 1:
            ind_split = rendering_util.split_array(
                self.ctx.galaxies.x, par.n_threads_photon_rendering
            )
            image = self.ctx.image
            self.ctx.image = None

            rendering_args_split = [
                [
                    rendering_util.rng_buffer()
                    for _ in range(par.n_threads_photon_rendering)
                ],
                [par.gammaprecision * 1 for _ in range(par.n_threads_photon_rendering)],
                [
                    par.gammaprecisionhigh * 1
                    for _ in range(par.n_threads_photon_rendering)
                ],
                [
                    par.sersicprecision * 1
                    for _ in range(par.n_threads_photon_rendering)
                ],
                [sersic_table for _ in range(par.n_threads_photon_rendering)],
                [image for _ in range(par.n_threads_photon_rendering)],
                [self.ctx.galaxies.x[i_split] for i_split in ind_split],
                [self.ctx.galaxies.y[i_split] for i_split in ind_split],
                [nphot[i_split] for i_split in ind_split],
                [self.ctx.galaxies.sersic_n[i_split] for i_split in ind_split],
                [gal_ellip_matrices[i_split] for i_split in ind_split],
                [self.ctx.galaxies.psf_beta[i_split] for i_split in ind_split],
                [psf_ellip_matrices[i_split] for i_split in ind_split],
                [psf_flexion_tensors[i_split] for i_split in ind_split],
                [psf_kurtoses[i_split] for i_split in ind_split],
                [self.ctx.galaxies.psf_dx_offset[i_split] for i_split in ind_split],
                [self.ctx.galaxies.psf_dy_offset[i_split] for i_split in ind_split],
                [
                    par.psf_flexion_suppression
                    for _ in range(par.n_threads_photon_rendering)
                ],
                [True for _ in range(par.n_threads_photon_rendering)],
            ]

            # Run in threads
            rendering_util.execute_threaded(
                integrate_image, par.n_threads_photon_rendering, *rendering_args_split
            )
            self.ctx.image = image

        else:
            integrate_image(
                rendering_util.rng_buffer(),
                par.gammaprecision,
                par.gammaprecisionhigh,
                par.sersicprecision,
                sersic_table,
                self.ctx.image,
                self.ctx.galaxies.x,
                self.ctx.galaxies.y,
                nphot,
                self.ctx.galaxies.sersic_n,
                gal_ellip_matrices,
                self.ctx.galaxies.psf_beta,
                psf_ellip_matrices,
                psf_flexion_tensors,
                psf_kurtoses,
                self.ctx.galaxies.psf_dx_offset,
                self.ctx.galaxies.psf_dy_offset,
                par.psf_flexion_suppression,
                False,
            )
