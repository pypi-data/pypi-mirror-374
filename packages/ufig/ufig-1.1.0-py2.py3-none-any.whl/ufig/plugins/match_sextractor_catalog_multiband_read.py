# Copyright (c) 2015 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>

"""
Created on Apr 12, 2015
@author: Claudio Bruderer

"""

from functools import reduce

import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger
from ivy.plugin.base_plugin import BasePlugin
from sklearn.neighbors import BallTree

from ufig.plugins.match_sextractor_seg_catalog_multiband_read import NO_MATCH_VAL

LOGGER = logger.get_logger(__file__)

HDF5_COMPRESS = {"compression": "gzip", "compression_opts": 9, "shuffle": True}


def match(x_in, y_in, mag_in, x_out, y_out, mag_out, par):
    """
    Match UFig input positions and magnitudes to SExtractor output positions and
    magnitudes.

    :param x_in: Input x-coordinates (in SExtractor convention)
    :param y_in: Input y-coordinates (in SExtractor convention)
    :param mag_in: Input magnitudes
    :param x_out: Output x-coordinates
    :param y_out: Output y-coordinates
    :param mag_out: Output magnitudes
    :param par.max_radius: Maximum distance between an input and a detected objects to
                           classify as a match.
    :param par.mag_diff: Maximum magnitude difference between an input and a detected
                         object to classify as a match.

    :return: Indices linking detected to input objects.
    """

    # use ball tree to find input objects close enough to detected objects
    tree = BallTree(np.stack((x_in, y_in), axis=-1), leaf_size=1000, metric="euclidean")
    inds_dist_match = tree.query_radius(
        np.stack((x_out, y_out), axis=-1),
        par.max_radius,
        return_distance=True,
        sort_results=True,
    )[0]

    indices_link = np.full_like(x_out, NO_MATCH_VAL, dtype=int)

    # compare input and output magnitudes, set closest object with sufficiently small
    # magnitude difference as match
    for c, ind_dist_match in enumerate(inds_dist_match):
        delta_mag = np.fabs(mag_out[c] - mag_in[ind_dist_match])
        select_mag = delta_mag < par.mag_diff

        if np.any(select_mag):
            indices_link[c] = ind_dist_match[select_mag][0]

    return indices_link


class Plugin(BasePlugin):
    """
    Matches a Source Extractor catalog to the input catalogs and adds all the input
    columns to the Source Extractor catalog.
    """

    def get_sexcat_paths(self, f):
        """
        Get paths of SExtractor catalogs to be matched from list of plugins.

        :param plugin_list: List of plugins
        :return: List of paths of SExtractor catalogs to be matched
        """

        paths = self.ctx.parameters.sextractor_forced_photo_catalog_name_dict[f]
        return paths

    def get_ucat_paths(self, f, sg):
        if sg == "galaxy":
            paths = self.ctx.parameters.galaxy_catalog_name_dict[f]
        elif sg == "star":
            paths = self.ctx.parameters.star_catalog_name_dict[f]

        return paths

    def __call__(self):
        par = self.ctx.parameters

        indices_link = {}
        sexcat_dict = {}
        gal_dict = {}
        star_dict = {}
        x_out_dict = {}
        y_out_dict = {}
        mag_out_dict = {}
        x_in = np.array([], float)
        y_in = np.array([], float)
        mag_in_dict = {}
        path_ucat = {}
        path_sexcat = {}
        indices_link_b = {}

        for f in par.filters:
            if "galaxies" in self.ctx:
                path_ucat[f] = self.get_ucat_paths(f=f, sg="galaxy")
                gal_dict[f] = at.load_hdf(path_ucat[f])
                # match
                x_in = gal_dict[f]["x"]
                y_in = gal_dict[f]["y"]
                mag_in_dict[f] = gal_dict[f]["mag"]
            if "stars" in self.ctx:
                path_ucat[f] = self.get_ucat_paths(f=f, sg="star")
                star_dict[f] = at.load_hdf(path_ucat[f])
                x_in = np.append(x_in, star_dict[f]["x"])
                y_in = np.append(y_in, star_dict[f]["y"])
                mag_in_dict[f] = np.append(mag_in_dict[f], star_dict[f]["mag"])
            # 0.5-shift due to different pixel conventions in UFig and Sextractor
            x_in += 0.5
            y_in += 0.5
            path_sexcat[f] = self.get_sexcat_paths(f=f)
            # load catalog
            sexcat_dict[f] = at.load_hdf_cols(path_sexcat[f])
            x_out_dict[f] = sexcat_dict[f][par.matching_x]
            y_out_dict[f] = sexcat_dict[f][par.matching_y]
            mag_out_dict[f] = sexcat_dict[f][par.matching_mag]

            indices_link_b[f] = match(
                x_in,
                y_in,
                mag_in_dict[f],
                x_out_dict[f],
                y_out_dict[f],
                mag_out_dict[f],
                par,
            )

        indices_link = reduce(
            lambda x, y: np.where(x == y, x, NO_MATCH_VAL), indices_link_b.values()
        )

        # check that there is no multiple counting
        inds, counts = np.unique(
            indices_link[indices_link != NO_MATCH_VAL], return_counts=True
        )
        multi = sum(np.where(counts != 1, True, False))
        LOGGER.info(f"There are {multi} matches to the same index")
        LOGGER.info(
            f"This means {sum(counts[counts != 1])} galaxies instead of {multi}"
        )

        # split matches into stars and galaxies
        galaxy_mask = (indices_link < self.ctx.numgalaxies) & (
            indices_link != NO_MATCH_VAL
        )
        star_mask = (indices_link >= self.ctx.numgalaxies) & (
            indices_link != NO_MATCH_VAL
        )
        galaxy_indices = indices_link[galaxy_mask]
        star_indices = indices_link[star_mask] - self.ctx.numgalaxies

        def append_(obj, col):
            new_columns.append(f"{col}:{obj[col].dtype.str}")
            new_column_shapes.append(obj[col].shape[1:])
            new_columns_names.append(col)

        for f in par.filters:
            # add columns
            new_columns = []
            new_column_shapes = []
            new_columns_names = []

            for col in gal_dict[f].dtype.names:
                if col not in sexcat_dict[f].dtype.names:
                    append_(gal_dict[f], col)

            for col in star_dict[f].dtype.names:
                if (
                    col not in sexcat_dict[f].dtype.names
                    and col not in gal_dict[f].dtype.names
                ):
                    append_(star_dict[f], col)

            if "star_gal" not in sexcat_dict[f].dtype.names:
                new_columns.append(f"star_gal:{np.array([NO_MATCH_VAL]).dtype.str}")
                new_column_shapes.append(())
                new_columns_names.append("star_gal")

            sexcat_dict[f] = at.add_cols(
                sexcat_dict[f], new_columns, shapes=new_column_shapes, data=NO_MATCH_VAL
            )

            # add matched values
            if "star_gal" in new_columns_names:
                sexcat_dict[f]["star_gal"][galaxy_mask] = 0
                sexcat_dict[f]["star_gal"][star_mask] = 1
                new_columns_names.remove("star_gal")

            for new_col in new_columns_names:
                if new_col in gal_dict[f].dtype.names:
                    sexcat_dict[f][new_col][galaxy_mask] = gal_dict[f][new_col][
                        galaxy_indices
                    ]

                if new_col in star_dict[f].dtype.names:
                    sexcat_dict[f][new_col][star_mask] = star_dict[f][new_col][
                        star_indices
                    ]

            # write extended catalog to disk
            at.save_hdf_cols(path_sexcat[f], sexcat_dict[f], compression=HDF5_COMPRESS)

    def __str__(self):
        return "match catalog to input"
