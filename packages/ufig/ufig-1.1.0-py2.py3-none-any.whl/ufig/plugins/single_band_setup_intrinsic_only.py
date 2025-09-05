# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Thu Aug 08 2024


import numpy as np
from ivy.plugin.base_plugin import BasePlugin

from ufig.plugins.single_band_setup import initialize_shape_size_columns

NAME = "setup single-band (intrinsic only)"


class Plugin(BasePlugin):
    """
    Set parameters for catalogs of only intrisic properties (no image simulation)
    """

    def __call__(self):
        par = self.ctx.parameters

        np.random.seed(par.seed)

        filter_band_params = [
            param_name for param_name in par if param_name.endswith("_dict")
        ]
        for param_name in filter_band_params:
            try:
                param_name_stripped = param_name[:-5]
                setattr(
                    par,
                    param_name_stripped,
                    getattr(par, param_name)[self.ctx.current_filter],
                )
            except KeyError:
                pass

        if "galaxies" in self.ctx:
            add_galaxy_col = [
                "gamma1",
                "gamma2",
                "kappa",
                "e1",
                "e2",
                "r50",
                "int_mag",
                "mag",
                "abs_mag",
            ]

            self.ctx.galaxies.columns = list(
                set(self.ctx.galaxies.columns) | set(add_galaxy_col)
            )

            # Initial values for galaxy shapes
            initialize_shape_size_columns(
                self.ctx.galaxies, self.ctx.numgalaxies, precision=par.catalog_precision
            )

            # Magnitudes and numbers of photons
            self.ctx.galaxies.int_mag = self.ctx.galaxies.int_magnitude_dict[
                self.ctx.current_filter
            ].astype(par.catalog_precision)
            self.ctx.galaxies.abs_mag = self.ctx.galaxies.abs_magnitude_dict[
                self.ctx.current_filter
            ].astype(par.catalog_precision)
            self.ctx.galaxies.mag = self.ctx.galaxies.magnitude_dict[
                self.ctx.current_filter
            ].astype(par.catalog_precision)

        if "stars" in self.ctx:
            add_star_col = [
                "mag",
            ]

            self.ctx.stars.columns = list(
                set(self.ctx.stars.columns) | set(add_star_col)
            )

            # Magnitudes and numbers of photons
            self.ctx.stars.mag = self.ctx.stars.magnitude_dict[self.ctx.current_filter]

    def __str__(self):
        return NAME
