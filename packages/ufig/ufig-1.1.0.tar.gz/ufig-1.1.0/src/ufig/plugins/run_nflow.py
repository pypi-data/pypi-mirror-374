# Copyright (C) 2023 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import contextlib

import h5py
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin

from ufig.plugins.match_sextractor_catalog_multiband_read import NO_MATCH_VAL
from ufig.plugins.write_catalog_for_emu import enrich_star_catalog

HDF5_COMPRESS = {"compression": "gzip", "compression_opts": 9, "shuffle": True}

LOGGER = logger.get_logger(__file__)


class Plugin(BasePlugin):
    def __call__(self):
        par = self.ctx.parameters

        filter = self.ctx.current_filter

        # get classifier and config
        nflow = par.nflow[filter]

        # load catalogs
        with h5py.File(par.galaxy_catalog_name_dict[filter], "r") as fh5:
            cat = fh5["data"][:]

        # remove x and y
        x = cat["x"]
        y = cat["y"]
        cat = at.delete_columns(cat, ["x", "y"])

        sexcat = nflow.sample(cat)

        # add x and y and pretend they are measured by sextractor
        sexcat = at.add_cols(sexcat, ["XWIN_IMAGE", "YWIN_IMAGE", "X_IMAGE", "Y_IMAGE"])
        sexcat["XWIN_IMAGE"] = x
        sexcat["YWIN_IMAGE"] = y
        sexcat["X_IMAGE"] = x
        sexcat["Y_IMAGE"] = y

        # add NO_MATCH_VAL to stars
        _, enriched_params1 = enrich_star_catalog(cat=None, par=par)
        _, enriched_params2 = enrich_star_catalog(cat=None, par=par)
        stars = sexcat["galaxy_type"] == -1
        enriched_params = enriched_params1 + enriched_params2
        # TODO: for now don't do it
        enriched_params = []
        for p in enriched_params:
            with contextlib.suppress(KeyError):
                sexcat[p][stars] = NO_MATCH_VAL
        sexcat["z"][stars] = NO_MATCH_VAL

        # write catalog
        filepath = par.sextractor_forced_photo_catalog_name_dict[
            self.ctx.current_filter
        ]
        at.save_hdf_cols(filepath, sexcat, compression=HDF5_COMPRESS)

    def __str__(self):
        return "run the normalizing flow"
