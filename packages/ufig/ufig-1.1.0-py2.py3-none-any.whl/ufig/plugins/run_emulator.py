# Copyright (C) 2023 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import h5py
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin

HDF5_COMPRESS = {"compression": "gzip", "compression_opts": 9, "shuffle": True}

LOGGER = logger.get_logger(__file__)


class Plugin(BasePlugin):
    def __call__(self):
        LOGGER.info("Running the full emulator")
        par = self.ctx.parameters

        # load classifier and config
        conf = par.emu_conf
        clf_params = list(par.clf.params)

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
            X[p] = cats[par.emu_filters[0]]["data"][p]

        # Get ucat params that are not part of the emulator
        if "x" in cats[par.emu_filters[0]]["data"].dtype.names:
            x = cats[par.emu_filters[0]]["data"]["x"]
            y = cats[par.emu_filters[0]]["data"]["y"]
            radec = False
        else:
            radec = True
            x = cats[par.emu_filters[0]]["data"]["ra"]
            y = cats[par.emu_filters[0]]["data"]["dec"]
        ids = cats[par.emu_filters[0]]["data"]["id"]

        for f in par.emu_filters:
            cats[f].close()

        X = at.dict2rec(X)
        # Reorder the fields to match the desired order
        X = X[clf_params]

        LOGGER.debug("Running the classifier")
        det = par.clf.predict(X)

        LOGGER.debug("Running the normalizing flow")
        sexcat = par.nflow.sample(X[det])
        select = at.get_finite_mask(sexcat)
        LOGGER.debug("Writing the catalogs")
        # write catalog catalog
        for f in par.emu_filters:
            cat = {}
            for p in conf["input_band_dep"]:
                cat[p] = sexcat[p + f"_{f}"]
            for p in conf["input_band_indep"]:
                cat[p] = sexcat[p]
            for p in conf["output"]:
                cat[p] = sexcat[p + f"_{f}"]

            # positions for final catalog
            if radec:
                cat["ra"] = x[det]
                cat["dec"] = y[det]
            else:
                cat["x"] = x[det]
                cat["y"] = y[det]

                cat["XWIN_IMAGE"] = x[det]
                cat["YWIN_IMAGE"] = y[det]
                cat["X_IMAGE"] = x[det]
                cat["Y_IMAGE"] = y[det]

            cat["id"] = ids[det]

            cat = at.dict2rec(cat)

            # add NO_MATCH_VAL to stars
            # stars = cat["galaxy_type"] == -1
            # cat["z"][stars] = NO_MATCH_VAL

            # write catalog
            filepath = par.sextractor_forced_photo_catalog_name_dict[f]
            at.save_hdf_cols(filepath, cat[select], compression=HDF5_COMPRESS)

        # del par.clf
        # del par.nflow
        del self.ctx.parameters.clf
        del self.ctx.parameters.nflow

    def __str__(self):
        return "run the full emulator"
