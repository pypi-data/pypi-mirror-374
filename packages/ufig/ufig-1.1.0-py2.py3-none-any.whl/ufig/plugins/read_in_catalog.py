# Copyright (c) 2015 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>
"""
Created on May 30, 2015
@author: Claudio Bruderer, adapted by Silvan Fischbacher
"""

import numpy as np
from cosmic_toolbox import file_utils
from ivy.plugin.base_plugin import BasePlugin


class Catalog:
    pass


class Plugin(BasePlugin):
    """
    Write star and galaxy catalogs to fits tables. These catalogs are the ufig input
    catalog, ie. the parameters directly associated with the image.

    :param overwrite: whether to overwrite existing image
    :param galaxy_catalog_name: name of output galaxy catalog
    :param star_catalog_name: name of output star catalog

    :return: star and galaxy catalog

    """

    def __call__(self):
        f = self.ctx.current_filter
        par = self.ctx.parameters
        self.ctx.galaxies = Catalog()

        galaxy_catalog = file_utils.read_from_hdf(par.galaxy_catalog_name_dict[f])
        self.ctx.galaxies.columns = list(galaxy_catalog.dtype.names)

        for column in galaxy_catalog.dtype.names:
            if column == "nphot" or column == "id":
                setattr(
                    self.ctx.galaxies,
                    column,
                    np.array(galaxy_catalog[column], dtype=np.int),
                )
            else:
                setattr(
                    self.ctx.galaxies,
                    column,
                    np.array(galaxy_catalog[column], dtype=np.float32),
                )

        self.ctx.stars = Catalog()

        star_catalog = file_utils.read_from_hdf(par.star_catalog_name)
        self.ctx.stars.columns = list(star_catalog.dtype.names)

        for column in star_catalog.dtype.names:
            if column == "nphot" or column == "id":
                setattr(
                    self.ctx.stars, column, np.array(star_catalog[column], dtype=np.int)
                )
            else:
                setattr(
                    self.ctx.stars,
                    column,
                    np.array(star_catalog[column], dtype=np.float32),
                )

        self.ctx.numgalaxies = len(galaxy_catalog)
        self.ctx.numstars = len(star_catalog)

    def __str__(self):
        return "read in fits catalog"
