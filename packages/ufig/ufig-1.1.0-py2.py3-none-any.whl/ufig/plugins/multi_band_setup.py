# Copyright (C) 2016 ETH Zurich, Institute for Astronomy

"""
Created on May 3, 2016
author: Joerg Herbel
"""

import warnings

from ivy.plugin.base_plugin import BasePlugin

NAME = "setup multi-band"


class Plugin(BasePlugin):
    """
    Prepare for the rendering of multiple images. This plugin essentially allows to
    change the names of files used in the rendering of images in different bands by
    providing a format for the corresponding file names. This format specifies the way
    file names are obtained from the name of the tile in the sky and/or the filter band
    names. It contains '{}' where the tile name and/or the filter band name have to be
    inserted to obtain the correct file name(s).

    :param filters: List of names of filter bands used to render images, optional.
    :param tile_name: Name of the tile in the sky corresponding to the images rendered
            in this run, optional.
    :param image_name_dict: Dictionary of image names for each filter band used to
            render an image, optional.
    :param image_name_format: Format of images names, used to obtain the image names
            from the name of the tile and the name(s) of the filter band(s), optional.
    :param galaxy_catalog_name_dict: Dictionary of galaxy catalog names for each filter
            band used to render an image, optional.
    :param galaxy_catalog_name_format: Format of galaxy catalog names, used to obtain
            the catalog names from the name of the tile and the name(s) of the filter
            band(s), optional.
    :param star_catalog_name_dict: Dictionary of star catalog names for each filter band
            used to render an image.
    :param star_catalog_name_format: Format of star catalog names, used to obtain the
            catalog names from the name of the tile and the name(s) of the filter
            band(s), optional.
    :param besancon_cat_name: Name of a catalog of stars drawn from the Besancon model
            of the galaxy, optional.
    :param besancon_cat_name_format: Format of the name of a catalog of stars drawn from
            the Besancon model, used to obtain the catalog name from the name of the
            tile, optional.
    :param exp_time_file_name_dict: Dictionary of file names of maps of exposure times
            for each filter band used to render an image, optional.
    :param exp_time_file_name_format: Format of file names of maps of exposure times,
            used to obtain the file names from the name of the tile and the name(s) of
            the filter band(s), optional.
    :param bkg_rms_file_name_dict: Dictionary of file names of maps of the standard
            deviation of the background for each filter band used to render an image,
            optional.
    :param bkg_rms_file_name_format: Format of file names of maps of the standard
            deviation of the background, used to obtain the file names from the name of
            the tile and the name(s) of the filter band(s), optional.
    :param psf_maps_dict: Dictionary of file names of PSF maps for each filter band used
            to render an image, optional.
    :param psf_maps_file_name_format: Format of file names of PSF maps, used to obtain
            the file names from the name of the tile and the name(s) of the filter
            band(s), optional.
    :param sextractor_catalog_name_dict: Dictionary of SExtractor catalog names for each
            filter band used to render an image, optional.
    :param sextractor_catalog_name_format: Format of SExtractor catalog names, used to
            obtain the catalog names from the name of the tile and the name(s) of the
            filter band(s), optional.
    :param weight_image_dict: Dictionary of weight image names used by SExtractor for
            each filter band used to render an image, optional.
    :param weight_image_format: Format of weight image names used by SExtractor, used to
            obtain the names from the name of the tile and the name(s) of the filter
            band(s), optional.

    :return: ctx.parameters with multi-band dictionaries modified accordingly.
    """

    def __call__(self):
        par = self.ctx.parameters

        # Ensure that reference band is rendered first
        try:
            # add emu_filters to match the order of the filters
            par.emu_filters = par.filters.copy()
            par.filters.remove(par.reference_band)
            par.filters.insert(0, par.reference_band)
        except AttributeError:
            pass
        except ValueError:
            warnings.warn(
                "Reference band is not in the list of filter bands for which"
                " images are rendered.",
                stacklevel=1,
            )

        # Ensure that the detection band is rendered first (in case of forced
        # photometry)
        if hasattr(par, "sextractor_forced_photo_detection_bands"):
            # check that all bands used for detection will be rendered
            for band in par.sextractor_forced_photo_detection_bands:
                if band not in par.filters:
                    raise ValueError(
                        f"Filter band {band} in sextractor_forced_photo_detection_bands"
                        " but not in filters"
                    )

            # in case of a single detection band, ensure that this band will be rendered
            # first
            if len(par.sextractor_forced_photo_detection_bands) == 1:
                par.filters.remove(par.sextractor_forced_photo_detection_bands[0])
                par.filters.insert(0, par.sextractor_forced_photo_detection_bands[0])

                if hasattr(par, "reference_band") and (
                    par.reference_band != par.sextractor_forced_photo_detection_bands[0]
                ):
                    warnings.warn(
                        "Reference band is different from SExtractor forced-photometry"
                        "detection band, this can lead to crashes.",
                        stacklevel=1,
                    )

        try:
            if not par.image_name_dict:
                par.image_name_dict = {
                    f: par.image_name_format.format(par.tile_name, "{}").format(f)
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass

        try:
            if not par.galaxy_catalog_name_dict:
                par.galaxy_catalog_name_dict = {
                    f: par.galaxy_catalog_name_format.format(
                        par.tile_name, "{}"
                    ).format(f)
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass
        try:
            if not par.star_catalog_name_dict:
                par.star_catalog_name_dict = {
                    f: par.star_catalog_name_format.format(par.tile_name, "{}").format(
                        f
                    )
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass

        try:
            if not par.besancon_cat_name:
                par.besancon_cat_name = par.besancon_cat_name_format.format(
                    par.tile_name
                )
        except AttributeError:
            pass

        try:
            if not par.exp_time_file_name_dict:
                par.exp_time_file_name_dict = {
                    f: par.exp_time_file_name_format.format(par.tile_name, "{}").format(
                        f
                    )
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass
        try:
            if not par.bkg_rms_file_name_dict:
                par.bkg_rms_file_name_dict = {
                    f: par.bkg_rms_file_name_format.format(par.tile_name, "{}").format(
                        f
                    )
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass

        try:
            if not par.psf_maps_dict:
                par.psf_maps_dict = {
                    f: par.psf_maps_file_name_format.format(f) for f in par.filters
                }
        except AttributeError:
            pass

        try:
            if not par.sextractor_catalog_name_dict:
                par.sextractor_catalog_name_dict = {
                    f: par.sextractor_catalog_name_format.format(
                        par.tile_name, "{}"
                    ).format(f)
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass

        try:
            if not par.sextractor_forced_photo_catalog_name_dict:
                par.sextractor_forced_photo_catalog_name_dict = {
                    f: par.sextractor_forced_photo_catalog_name_format.format(
                        par.tile_name, "{}"
                    ).format(f)
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass
        try:
            if not par.weight_image_dict:
                par.weight_image_dict = {
                    f: par.weight_image_format.format(par.tile_name, "{}").format(f)
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass

        try:
            if not par.filepath_psfmodel_input_dict:
                par.filepath_psfmodel_input_dict = {
                    f: par.filepath_psfmodel_input_format.format(f) for f in par.filters
                }
        except AttributeError:
            pass

        try:
            if not par.filepath_psfmodel_output_dict:
                par.filepath_psfmodel_output_dict = {
                    f: par.filepath_psfmodel_output_format.format(
                        par.sextractor_catalog_name_dict[f]
                    )
                    for f in par.filters
                }
        except (KeyError, AttributeError):
            pass

        try:
            if not par.filepath_sysmaps_dict:
                par.filepath_sysmaps_dict = {
                    f: par.filepath_sysmaps_format.format(f) for f in par.filters
                }  # this somehow crashes
        except AttributeError:
            pass

        try:
            if not par.det_clf_catalog_name_dict:
                par.det_clf_catalog_name_dict = {
                    f: par.det_clf_catalog_name_format.format(
                        par.tile_name, "{}"
                    ).format(f)
                    for f in par.filters
                }
        except (AttributeError, IndexError):
            pass

        try:
            if not par.bkg_amp_variation_sigma_dict:
                par.bkg_amp_variation_sigma_dict = {
                    f: par.bkg_amp_variation_sigma for f in par.filters
                }
        except AttributeError:
            pass

        try:
            if not par.bkg_noise_variation_sigma_dict:
                par.bkg_noise_variation_sigma_dict = {
                    f: par.bkg_noise_variation_sigma for f in par.filters
                }
        except AttributeError:
            pass

        try:
            if not par.psf_fwhm_variation_sigma_dict:
                par.psf_fwhm_variation_sigma_dict = {
                    f: par.psf_fwhm_variation_sigma for f in par.filters
                }
        except AttributeError:
            pass

    def __str__(self):
        return NAME
