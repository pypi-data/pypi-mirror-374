# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Fri Sep 06 2024


from cosmic_toolbox import arraytools as at
from cosmic_toolbox import file_utils, logger
from ivy.plugin.base_plugin import BasePlugin

LOGGER = logger.get_logger(__file__)


class Plugin(BasePlugin):
    """
    Cleanup the catalogs:
    - delete det_clf catalogs
    - load the sextractor catalogs and restructure them such that they can be loaded
    with at.load_hdf like the ucat catalog
    """

    def __call__(self):
        par = self.ctx.parameters

        for f in par.det_clf_catalog_name_dict:
            file_utils.robust_remove(par.det_clf_catalog_name_dict[f])

        try:
            for f in par.sextractor_forced_photo_catalog_name_dict:
                cat = at.load_hdf_cols(par.sextractor_forced_photo_catalog_name_dict[f])
                file_utils.robust_remove(
                    par.sextractor_forced_photo_catalog_name_dict[f]
                )
                at.save_hdf(par.sextractor_forced_photo_catalog_name_dict[f], cat)
        except FileNotFoundError:
            pass

    def __str__(self):
        return "cleanup catalogs"
