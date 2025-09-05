import os

import galsbi.ucat.config.common
from cosmo_torrent import data_path
from ivy.loop import Loop

import ufig.config.common
from ufig.workflow_util import FiltersStopCriteria

# Import all common settings from ucat and ufig
for name in [
    name for name in dir(galsbi.ucat.config.common) if not name.startswith("__")
]:
    globals()[name] = getattr(galsbi.ucat.config.common, name)
for name in [name for name in dir(ufig.config.common) if not name.startswith("__")]:
    globals()[name] = getattr(ufig.config.common, name)


pixscale = 0.168
size_x = 1000
size_y = 1000
ra0 = 0
dec0 = 0

# Define the filters
filters = ["g", "r", "i"]
filters_full_names = {
    "B": "SuprimeCam_B",
    "g": "HSC_g",
    "r": "HSC_r2",
    "i": "HSC_i2",
}

# Define the plugins that should be used
plugins = [
    "ufig.plugins.multi_band_setup",
    "galsbi.ucat.plugins.sample_galaxies",
    "ufig.plugins.draw_stars_besancon_map",
    Loop(
        [
            "ufig.plugins.single_band_setup",
            "ufig.plugins.background_noise",
            "ufig.plugins.resample",
            "ufig.plugins.add_psf",
            "ufig.plugins.render_galaxies_flexion",
            "ufig.plugins.render_stars_photon",
            "ufig.plugins.convert_photons_to_adu",
            "ufig.plugins.saturate_pixels",
            "ufig.plugins.write_image",
        ],
        stop=FiltersStopCriteria(),
    ),
    "ivy.plugin.show_stats",
]

star_catalogue_type = "besancon_map"
besancon_map_path = os.path.join(data_path("besancon_HSC"), "besancon_HSC.h5")

filters_file_name = os.path.join(
    data_path("HSC_tables"), "HSC_filters_collection_yfix.h5"
)
n_templates = 5
templates_file_name = os.path.join(
    data_path("template_BlantonRoweis07"), "template_spectra_BlantonRoweis07.h5"
)
extinction_map_file_name = os.path.join(
    data_path("lambda_sfd_ebv"), "lambda_sfd_ebv.fits"
)
magnitude_calculation = "table"
templates_int_tables_file_name = os.path.join(
    data_path("HSC_tables"), "HSC_template_integrals_yfix.h5"
)
