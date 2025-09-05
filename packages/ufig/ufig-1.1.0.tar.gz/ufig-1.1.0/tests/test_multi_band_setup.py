# Copyright (C) 2016 ETH Zurich, Institute for Astronomy

"""
Created on Feb 10, 2015
author: Joerg Herbel
"""

from ivy import context

from ufig.plugins import multi_band_setup


def test_multi_band_setup():
    """
    Test setting up file names for rendering images in multiple bands from the tile
    name, the name of the filter bands and file name formats
    """

    # Setup
    filters = ["g", "r", "i", "z", "Y"]
    tile_name = "tile_name"
    image_name_format = "{}_{}.fits"
    image_name_dict = {f: "image" for f in filters}
    galaxy_catalog_name_format = "{}_{}.gal.cat"
    galaxy_catalog_name_dict = {f: "galcat" for f in filters}
    star_catalog_name_format = "{}_{}.star.cat"
    star_catalog_name_dict = {f: "starcat" for f in filters}
    besancon_cat_name_format = "{}_besancon.fits"
    besancon_cat_name = "besancon_cat"
    exp_time_file_name_format = "{}_{}_exp_time.fits"
    exp_time_file_name_dict = {f: "exp_time_map" for f in filters}
    bkg_rms_file_name_format = "{}_{}_bkg_rms.fits"
    bkg_rms_file_name_dict = {f: "bkg_rms_map" for f in filters}
    psf_maps_file_name_format = "psf_maps_{}.fits"
    psf_maps_dict = {f: "psf_maps" for f in filters}
    sextractor_catalog_name_format = "{}_{}.sexcat"
    sextractor_catalog_name_dict = {f: "sexcat" for f in filters}
    weight_image_format = "{}_{}_weights.fits"
    weight_image_dict = {f: "weight_image" for f in filters}

    ctx = context.create_ctx()
    ctx.parameters = context.create_ctx()

    # Test if the plugin runs without error if no parameters at all have been set
    plugin = multi_band_setup.Plugin(ctx)
    plugin()
    assert str(plugin) == "setup multi-band"

    # Test whether the plugin will not change things if only non-empty file names have
    # been passed
    ctx.parameters.image_name_dict = image_name_dict
    ctx.parameters.galaxy_catalog_name_dict = galaxy_catalog_name_dict
    ctx.parameters.star_catalog_name_dict = star_catalog_name_dict
    ctx.parameters.besancon_cat_name = besancon_cat_name
    ctx.parameters.exp_time_file_name_dict = exp_time_file_name_dict
    ctx.parameters.bkg_rms_file_name_dict = bkg_rms_file_name_dict
    ctx.parameters.psf_maps_dict = psf_maps_dict
    ctx.parameters.sextractor_catalog_name_dict = sextractor_catalog_name_dict
    ctx.parameters.weight_image_dict = weight_image_dict
    plugin()
    assert ctx.parameters.image_name_dict == image_name_dict
    assert ctx.parameters.galaxy_catalog_name_dict == galaxy_catalog_name_dict
    assert ctx.parameters.star_catalog_name_dict == star_catalog_name_dict
    assert ctx.parameters.besancon_cat_name == besancon_cat_name
    assert ctx.parameters.exp_time_file_name_dict == exp_time_file_name_dict
    assert ctx.parameters.bkg_rms_file_name_dict == bkg_rms_file_name_dict
    assert ctx.parameters.psf_maps_dict == psf_maps_dict
    assert ctx.parameters.sextractor_catalog_name_dict == sextractor_catalog_name_dict
    assert ctx.parameters.weight_image_dict == weight_image_dict

    # Test whether the plugin will not change things if also filters, tile name and
    # formats are passed
    ctx.parameters.filters = filters
    ctx.parameters.tile_name = tile_name
    ctx.parameters.image_name_format = image_name_format
    ctx.parameters.galaxy_catalog_name_format = galaxy_catalog_name_format
    ctx.parameters.star_catalog_name_format = star_catalog_name_format
    ctx.parameters.besancon_cat_name_format = besancon_cat_name_format
    ctx.parameters.exp_time_file_name_format = exp_time_file_name_format
    ctx.parameters.bkg_rms_file_name_format = bkg_rms_file_name_format
    ctx.parameters.psf_maps_file_name_format = psf_maps_file_name_format
    ctx.parameters.sextractor_catalog_name_format = sextractor_catalog_name_format
    ctx.parameters.weight_image_format = weight_image_format
    plugin()
    assert ctx.parameters.image_name_dict == image_name_dict
    assert ctx.parameters.galaxy_catalog_name_dict == galaxy_catalog_name_dict
    assert ctx.parameters.star_catalog_name_dict == star_catalog_name_dict
    assert ctx.parameters.besancon_cat_name == besancon_cat_name
    assert ctx.parameters.exp_time_file_name_dict == exp_time_file_name_dict
    assert ctx.parameters.bkg_rms_file_name_dict == bkg_rms_file_name_dict
    assert ctx.parameters.psf_maps_dict == psf_maps_dict
    assert ctx.parameters.sextractor_catalog_name_dict == sextractor_catalog_name_dict
    assert ctx.parameters.weight_image_dict == weight_image_dict

    # Test whether the plugin sets file names correctly if they are not set before
    ctx.parameters.image_name_dict = {}
    ctx.parameters.galaxy_catalog_name_dict = {}
    ctx.parameters.star_catalog_name_dict = {}
    ctx.parameters.besancon_cat_name = ""
    ctx.parameters.exp_time_file_name_dict = {}
    ctx.parameters.bkg_rms_file_name_dict = {}
    ctx.parameters.psf_maps_dict = {}
    ctx.parameters.sextractor_catalog_name_dict = {}
    ctx.parameters.weight_image_dict = {}
    plugin()
    assert ctx.parameters.image_name_dict == {
        f: image_name_format.format(tile_name, f) for f in filters
    }
    assert ctx.parameters.galaxy_catalog_name_dict == {
        f: galaxy_catalog_name_format.format(tile_name, f) for f in filters
    }
    assert ctx.parameters.star_catalog_name_dict == {
        f: star_catalog_name_format.format(tile_name, f) for f in filters
    }
    assert ctx.parameters.besancon_cat_name == besancon_cat_name_format.format(
        tile_name
    )
    assert ctx.parameters.exp_time_file_name_dict == {
        f: exp_time_file_name_format.format(tile_name, f) for f in filters
    }
    assert ctx.parameters.bkg_rms_file_name_dict == {
        f: bkg_rms_file_name_format.format(tile_name, f) for f in filters
    }
    assert ctx.parameters.psf_maps_dict == {
        f: psf_maps_file_name_format.format(f) for f in filters
    }
    assert ctx.parameters.sextractor_catalog_name_dict == {
        f: sextractor_catalog_name_format.format(tile_name, f) for f in filters
    }
    assert ctx.parameters.weight_image_dict == {
        f: weight_image_format.format(tile_name, f) for f in filters
    }

    # Test the handling of nested cases
    ctx.parameters.tile_name = "tile_{}_name"
    ctx.parameters.image_name_format = "{}.fits"
    ctx.parameters.image_name_dict = {}
    plugin()
    assert ctx.parameters.image_name_dict == {
        f: ctx.parameters.image_name_format.format(
            ctx.parameters.tile_name, "{}"
        ).format(f)
        for f in filters
    }


if __name__ == "__main__":
    test_multi_band_setup()
