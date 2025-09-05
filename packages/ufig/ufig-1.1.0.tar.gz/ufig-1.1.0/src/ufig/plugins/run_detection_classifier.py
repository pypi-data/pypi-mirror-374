# Copyright (C) 2023 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import h5py
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import file_utils, logger
from ivy.plugin.base_plugin import BasePlugin

HDF5_COMPRESS = {"compression": "gzip", "compression_opts": 9, "shuffle": True}

LOGGER = logger.get_logger(__file__)


class Plugin(BasePlugin):
    def __call__(self):
        par = self.ctx.parameters

        # load classifier and config
        clf = par.clf
        conf = par.emu_conf
        clf_params = list(clf.params)

        # load catalogs
        cats = {}
        for f in par.emu_filters:
            cats[f] = h5py.File(par.det_clf_catalog_name_dict[f], "r")

        # create classifier input
        X = {}
        for p in conf["input_band_dep"]:
            for f in par.emu_filters:
                X[p + f"_{f}"] = cats[f]["data"][p]
        for p in conf["input_band_indep"]:
            X[p] = cats[par.filters[0]]["data"][p]

        # Get positions
        x = cats[par.filters[0]]["data"]["x"]
        y = cats[par.filters[0]]["data"]["y"]

        # close catalogs
        for f in par.emu_filters:
            cats[f].close()

        # check if parameters match
        X = at.dict2rec(X)
        # Reorder the fields to match the desired order
        X = X[clf_params]

        # run classifier
        det = clf.predict(X)

        # write detection catalog
        for f in par.emu_filters:
            cat = {}
            for p in conf["input_band_dep"]:
                cat[p] = X[p + f"_{f}"][det]
            for p in conf["input_band_indep"]:
                cat[p] = X[p][det]

            # positions for final catalog
            cat["x"] = x[det]
            cat["y"] = y[det]

            cat = at.dict2rec(cat)
            file_utils.write_to_hdf(
                par.galaxy_catalog_name_dict[f], cat, "data", **HDF5_COMPRESS
            )
        LOGGER.info("Saved detection catalogs")

    def __str__(self):
        return "run detection classifier"
