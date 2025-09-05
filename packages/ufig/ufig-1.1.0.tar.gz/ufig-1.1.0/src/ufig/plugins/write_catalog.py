# Copyright (C) 2019 ETH Zurich, Institute for Particle Physics and Astrophysics

"""
Created on Aug 2021
author: Tomasz Kacprzak
"""

import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import file_utils, logger
from ivy.plugin.base_plugin import BasePlugin

LOGGER = logger.get_logger(__file__)


def catalog_to_rec(catalog):
    # get dtype first
    dtype_list = []
    for col_name in catalog.columns:
        col = getattr(catalog, col_name)
        n_obj = len(col)
        if len(col.shape) == 1:
            dtype_list += [(col_name, col.dtype)]
        else:
            dtype_list += [(col_name, col.dtype, col.shape[1])]

    # create empty array
    rec = np.empty(n_obj, dtype=np.dtype(dtype_list))

    # copy columns to array
    for col_name in catalog.columns:
        col = getattr(catalog, col_name)
        if len(col.shape) == 1:
            rec[col_name] = col
        elif col.shape[1] == 1:
            rec[col_name] = col.ravel()
        else:
            rec[col_name] = col

    return rec


class Plugin(BasePlugin):
    def __call__(self):
        par = self.ctx.parameters

        # write catalogs
        if "galaxies" in self.ctx:
            f = self.ctx.current_filter
            filepath_out = par.galaxy_catalog_name_dict[f]

            cat = catalog_to_rec(self.ctx.galaxies)
            # add absolute ellipticies
            try:
                cat = at.add_cols(
                    cat, ["e_abs"], data=np.sqrt(cat["e1"] ** 2 + cat["e2"] ** 2)
                )
            except (ValueError, KeyError) as e:
                LOGGER.warning(f"e_abs could not be calculated: {e}")
            # add noise levels
            try:
                cat = at.add_cols(
                    cat, ["bkg_noise_amp"], data=np.ones(len(cat)) * par.bkg_noise_amp
                )
            except AttributeError as e:
                LOGGER.warning(f"bkg_noise_amp could not be calculated: {e}")

            try:
                if "ra" not in cat.dtype.names and "dec" not in cat.dtype.names:
                    y = np.array(cat["y"], dtype=int)
                    x = np.array(cat["x"], dtype=int)
                    if hasattr(par.bkg_noise_std, "shape"):
                        cat = at.add_cols(
                            cat, ["bkg_noise_std"], data=par.bkg_noise_std[y, x]
                        )
                    else:
                        cat = at.add_cols(
                            cat, ["bkg_noise_std"], data=par.bkg_noise_std
                        )
            except (ValueError, KeyError, AttributeError) as e:
                LOGGER.warning(f"bkg_noise_std could not be calculated: {e}")
            file_utils.write_to_hdf(filepath_out, cat)

        if "stars" in self.ctx:
            filepath_out = par.star_catalog_name_dict[f]
            cat = catalog_to_rec(self.ctx.stars)
            file_utils.write_to_hdf(filepath_out, cat)

    def __str__(self):
        return "write ucat catalog to file"
