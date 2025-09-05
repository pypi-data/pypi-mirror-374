# Copyright (C) 2018 ETH Zurich, Institute for Particle Physics and Astrophysics

"""
Created on Mar 6, 2018
author: Joerg Herbel
"""

import numpy as np

# ==================================================================
# G E N E R A L
# ==================================================================

# Filters

# Filter bands (multi-band only):
filters = ["g", "r", "i", "z", "Y"]

# Reference filter band for cutting eg. apparent star magnitudes:
reference_band = "r"

# Output

# Tile name (multi-band only):
tile_name = "ufig"

# Format of image names (multi-band only):
image_name_format = "{}_{}.fits"

# Format of galaxy catalog names (multi-band only)
galaxy_catalog_name_format = "{}_{}.gal.cat"

# Format of star catalog names (multi-band only)
star_catalog_name_format = "{}_{}.star.cat"

# Format of detection clf catalog names (multi-band only)
det_clf_catalog_name_format = "{}_{}.det_clf.cat"

# Dictionary of image names (multi-band only):
image_name_dict = {}

# Dictionary of galaxy catalog names (multi-band only):
galaxy_catalog_name_dict = {}

# Dictionary of star catalog names (multi-band only):
star_catalog_name_dict = {}

# Dictionary of detection clf catalog names (multi-band:
det_clf_catalog_name_dict = {}
# only)

# output image name:
image_name = "ufig.fits"

# output catalog of galaxies used:
galaxy_catalog_name = "ufig.gal.cat"

# output catalog of stars used:
star_catalog_name = "ufig.star.cat"


# True if file should be overwritten:
overwrite = True

# Maps path

# Remote dir containing shear and PSF maps:
maps_remote_dir = "ufig_res/maps/"

# Directory for writing SExtractor weight maps to fits:
tempdir_weight_fits = ""

# Filepath containing overlap information:
filepath_overlapblock = None


# Seed and RNGs

# General seed set when initializing UFig:
seed = 102301239

# Seed offset set before converting mags to number of phot for gals
gal_nphot_seed_offset = 500

# Seed offset set before sampling the number of stars:
star_num_seed_offset = 600

# Seed offset set before sampling star positions:
star_dist_seed_offset = 700

# Seed offset set before converting mags to number of phot for stars
star_nphot_seed_offset = 800

# Seed offset set before rendering the gals (different phot noise)
gal_render_seed_offset = 900

# Seed offset set before rendering the stars (different phot noise)
star_render_seed_offset = 1000

# Seed offset set before drawing the background values in each pixel
background_seed_offset = 1100
coeffs_seed_offset = 1300  # Seed offset set before drawing template coefficients

# Seed offset set before adding compression noise to image
compression_noise_seed_offset = 123234

# galsbi seeds that are needed in ufig
seed_ngal = 500
gal_dist_seed_offset = 200
gal_sersic_seed_offset = 300
gal_ellipticities_seed_offset = 400

# Value in ADU out to which stellar profiles are rendered (should be
render_stars_accuracy = 0.3
# sub-dominant to noise rms)


# Number of threads used when rendering photon-based:
n_threads_photon_rendering = 1

# Stars below this magnitude will be rendered:
mag_pixel_rendering_stars = 17
# using pixel fft, ignoring higher order PSF moments

# ==================================================================
# C A M E R A
# ==================================================================

# pixel scale (arcsec/pixel):
pixscale = 0.263

# Dictionary of saturation levels (multi-band only):
saturation_level_dict = {}

# Dictionary of gain_dict (multi-band only):
gain_dict = {}

# saturation (ADU):
saturation_level = 35256.77280358

# gain (e/ADU):
gain = 4.321430284118572

# ==================================================================
# I M A G E   P R O P E R T I E S
# ==================================================================

# number of pixels on image x-axis:
size_x = 10000

# number of pixels on image y-axis:
size_y = 10000

# center of field:
ra0 = 70.459787

# center of field:
dec0 = -44.244444

# Dictionary of magnitude zeropoints (multi-band only):
magzero_dict = {}

# magnitude zeropoint:
magzero = 30.0

# Dictionary of exposure times (multi-band only):
exposure_time_dict = {}

# exposure time (s) of a single exposure:
exposure_time = 90.0

# precision of the image:
image_precision = np.float64

# ==================================================================
# I N P U T   C A T A L O G S
# ==================================================================

nside_sampling = 512
apparent_magnitude_offset = 0.0

# Stars
# ----------------------------------
# magnitude distribution (empricial)
# ----------------------------------:


# coefficient for CDF of stars:
stars_mag_0 = 17

# coefficients for CDF of stars:
stars_mag_cdf_a = 0.000214734

# magnitude distribution (a0,:
stars_mag_cdf_b = -0.00978518

# a1, a2, a3 for (A.7) in Berge:
stars_mag_cdf_c = 0.189962

# et al. 2012):
stars_mag_cdf_d = 2.80165

# maximum star magnitude cutoff:
stars_mag_max = 27.0

# minimum star magnitude cutoff:
stars_mag_min = 14.0

# increase or decrease the number of stars:
# (they will be resampled from the Besancon model)
stars_counts_scale = 1

# catalog precision
catalog_precision = np.float64

# ---------------------------------
# magnitude distribution (Besancon)
# ---------------------------------

# type of Besancon to use, options available::
# besancon_map - use spatially varying Besancon model
# besancon_gaia_splice - splice GAIA and Besancon
star_catalogue_type = "besancon_map"

# Format of besancon catalog file name (multi-band only)
besancon_cat_name_format = "{}_besancon.fits"

# Catalog containing sample of stars:
besancon_cat_name = "ufig_besancon.fits"

# --------------------------------
# GAIA stars
# --------------------------------
filepath_gaia = "DES0441-4414_gaia.h5"
gaia_mag_g_limit = 19

# Maximum distanace in pixels to match detected objects with GAIA input
max_dist_pix_match_gaia = 1

# ---------------------------------------------------
# spatially varying magnitude distribution (Besancon)
# ---------------------------------------------------

# Path to pickle file containing list of available Besancon catalogs:
besancon_map_path = "cats/besancon_map_y1a1_nside8.pkl"

# Galaxies
# ------------------------------------
# magnitude distribution (single-band)
# ------------------------------------

# coefficient for CDF of galaxies:
gals_mag_0 = 23

# coefficients for CDF of galaxies:
gals_mag_cdf_a = 0

# magnitude distribution (a0,a1, a2, a3 for (A.7) in Berge et al. 2012):
gals_mag_cdf_b = -0.0076
gals_mag_cdf_c = 0.356
gals_mag_cdf_d = 4.52

# maximum galaxy magnitude cutoff:
gals_mag_max = 27

# minimum galaxy magnitude cutoff:
gals_mag_min = 16

# -----------------------------------
# size-mag distribution (single-band)
# -----------------------------------

# rms r50 size distribution (arcsec):
size_sigma = 0.35638773798050416

# corr angle for r50 size-mag theta in (A.11) Berge et al. 2012
size_theta = 0.10000007376338751

# mean magnitude; mag_p in (A.11):
size_mag_mean = 25.309

# mean log(r50); log(r50,p) in (A.11):
size_log_mean = -0.796


# --------------------------
# Limit on number of photons
# --------------------------


# Upper limit on the sum of the number of photons for all galaxies. This parameter has
# the function to limit runtime for ABC runs. A reasonable value depends, among others,
# on the size of the image and the apparent magnitude limits:
n_phot_sum_gal_max = np.inf


# ==================================================================
# S H E A R
# ==================================================================

# Type of the shear field (constant or variable):
shear_type = "constant"

# ---------------
# constant shear
# ---------------

# 1-Component of constant shear added to ellipticity:
g1_constant = 0.0

# 2-Component of constant shear added to ellipticity:
g2_constant = 0.0

# --------------
# variable shear
# --------------

# Shear maps; must be stored in res/maps/ or in remote_dir
shear_maps = "shear_maps.fits"

# Prefactor to account for a potential flipping of the shear g1-map:
g1_prefactor = -1

# ==================================================================
# P S F
# ==================================================================

# Type of the PSF field to add, options
#   constant_moffat:
#   maps_moffat:
#   coadd_moffat_cnn
#   coadd_moffat_cnn_read:
psf_type = "constant_moffat"


# beta parameter of the Moffat PSF:
# Relative flux in the first component of the PSF (set to one if PSF
# consists of a single component)
psf_beta = [3.5]
psf_flux_ratio = 1.0
psf_flux_ratio_variable = False

# ------------
# constant psf
# ------------

# FWHM of total PSF (arcsec):
seeing = 0.9

# mean PSF e1:
psf_e1 = 0.015

# mean PSF e2:
psf_e2 = 0.01

# ------------
# variable psf
# ------------

# Format of file names of PSF maps (multi-band only)
psf_maps_file_name_format = "psf_{}.fits"

# Dictionary of file names of PSF maps (multi-band only):
psf_maps_dict = {}

# Healpy maps with PSF fields (0: r50, 1: e1, 2: e2):
psf_maps = "sva1_2048_psf.fits"
filepath_psfmodel_input = "DES0441-4414_r_psfmodel.h5"
filepath_psfmodel_input_format = "DES0441-4414_{}_psfmodel.h5"
filepath_psfmodel_input_dict = {}


# Fudge factor calibrating input psf_r50:
psf_r50_factor = 1.0

# Additive shift calibrating input psf_r50:
psf_r50_shift = 0.0

# Fudge factor calibrating input psf_e1:
psf_e1_factor = 1.0

# Additive shift calibrating input psf_e1:
psf_e1_shift = 0.0

# Prefactor to account for a potential flipping of the PSF e1-map:
psf_e1_prefactor = -1

# Fudge factor calibrating input psf_e2:
psf_e2_factor = 1.0

# factors to modify the PSF cnn parameters:
psf_cnn_factors = {
    "psf_fwhm_cnn": [0.0, 1.0],
    "psf_e1_cnn": [0.0, 1.0],
    "psf_e2_cnn": [0.0, 1.0],
    "psf_f1_cnn": [0.0, 1.0],
    "psf_f2_cnn": [0.0, 1.0],
    "psf_g1_cnn": [0.0, 1.0],
    "psf_g2_cnn": [0.0, 1.0],
    "psf_kurtosis_cnn": [0.0, 1.0],
    "psf_flux_ratio_cnn": [0, 1.0],
}


# exponential suppression factor for the PSF flexions:
psf_flexion_suppression = -5.0


# ==============
# PSF estimation
# ==============

# Output PSF model:
filepath_psfmodel_output = "ufig_psfmodel.h5"

# Format of SExtractor output catalog filenames (multi-band only)
filepath_psfmodel_output_format = "{}.psfmodel.h5"

# Dictionary of file names of output catalogs:
filepath_psfmodel_output_dict = {}
# (multi-band only)

# Catalog of PSF model parameters
filepath_psfmodel_output_catalog = "ufig_psfmodel.cat"

# Whether to store the filepath_psfmodel_output file (False will remove it)
psfmodel_output_store = False

# Polynomial order for fitting PSF:
psfmodel_poly_order = 5

# Regression regularisation parameter dictionary:
psfmodel_ridge_alpha = dict(
    psf_flux_ratio_cnn=2.10634454232412,
    psf_fwhm_cnn=0.12252798573828638,
    psf_e1_cnn=0.5080218046913018,
    psf_e2_cnn=0.5080218046913018,
    psf_f1_cnn=2.10634454232412,
    psf_f2_cnn=2.10634454232412,
    psf_g1_cnn=1.311133937421563,
    psf_g2_cnn=1.311133937421563,
    se_mom_fwhm=0.12,
    se_mom_win=0.12,
    se_mom_e1=0.51,
    se_mom_e2=0.51,
    astrometry_diff_x=0.5,
    astrometry_diff_y=0.5,
)

# Type of polynomial to fit, options: [standard, chebyshev]:
psfmodel_polynomial_type = "standard"

# magnitude of stars used in PSF fitting:
psfmodel_star_mag_range = [17, 22]

# clip star outliers in PSF measurement:
psfmodel_n_sigma_clip = 3

# fraction of stars to exclude from PSF fitting, use later for validation
psfmodel_fraction_validation_stars = 0

# parameters for correcting brighter fatter
psfmodel_corr_brighter_fatter = {
    "c1r": 0.0,
    "c1e1": 0.0,
    "c1e2": 0.0,
    "mag_ref": 22,
    "apply_to_galaxies": False,
}

# columns use to find star outliers
psfmodel_outlier_removal_columns = [
    "psf_fwhm",
    "psf_e1",
    "psf_e2",
]

# maximum number of refits for outlier removal
psfmodel_n_max_refit = 10

# astrometry errors flag
psfmodel_astrometry_errors = False

# star stamp shape
psfmodel_star_stamp_shape = (19, 19)

# sextractor flags for star selection
psfmodel_sextractor_flags = [0, 16]

# flag coadd boundaries
psfmodel_flag_coadd_boundaries = True

# moments limits
psfmodel_moments_lim = (-99, 99)

# beta limits
psfmodel_beta_lim = (1.5, 10)

# fwhm limits
psfmodel_fwhm_lim = (1, 10)

# ellipticity limits
psfmodel_ellipticity_lim = (-0.3, 0.3)

# flexion limits
psfmodel_flexion_lim = (-0.3, 0.3)

# kurtosis limits
psfmodel_kurtosis_lim = (-1, 1)

# raise underdetermined error flag
psfmodel_raise_underdetermined_error = False

# PSF measurement adjustment (None or dict)
psf_measurement_adjustment = None

# minimum number of exposures
psfmodel_min_n_exposures = 0

# save star cube flag
psfmodel_save_star_cube = False

# maximum distance for GAIA matching in arcsec
psfmodel_max_dist_gaia_arcsec = 0.1

# CNN variance type
psfmodel_cnn_variance_type = "constant"

# ==================================================================
# Shear estimation
# ================

# which method to use for shape estimation [moments_source_extractor, hsm]:
shear_estimation_method = "moments_source_extractor"
shear_estimation_stamp_shape = 29
shear_estimation_moments_window = "FLUX_RADIUS"
shear_estimation_hsm_round_moments = True
shear_estimation_hsm_params = {"max_mom2_iter": 1000}

# ===============
# remove overlap with multiple tiles
# ===============
filename_overlapblock = "DES0441-4414_overlapblock.h5"

# ==================================================================
# R A D I A L   G A L A X Y   P R O F I L E S   T A B L E
# ==================================================================

# Whether table with values of the inverse is computed on-the-fly
compute_gamma_table_onthefly = False

# size of the interpolation for the:
sersicprecision = 9

# interpolation of the intrinsic galaxy function:
gammaprecision = 13

# boundary between different interpolation regimes of the radial cdf
gammaprecisionhigh = 4
# Wheter to copy the gamma table to the current working directory to avoid too many jobs
# accessing the same file
copy_gamma_table_to_cwd = False

# ==================================================================
# B A C K G R O U N D   A N D   E X P O S U R E   T I M E
# ==================================================================

# Format of sysmaps:
#   'sysmaps_hdf'
#   'sysmaps_hdf_combined'
sysmaps_type = "sysmaps_hdf"


# Background

# Type of the background model:
background_type = "gaussian"

# --------------
# constant noise
# --------------

# rms Gaussian noise (ADU) in coadd:
background_sigma = 5.8819049462619528

# -----------------------------------------------
# single-file systematic maps with exposure info
# #-----------------------------------------------
filepath_sysmaps = "tile_sys/DES0441-4414_r_sysmaps.h5"

# Format of file names of background images (multi-band only)
filepath_sysmaps_format = "tile_sys/DES0441-4414_{}_sysmaps.h5"

# Dictionary of file names of background images (multi-band only)
filepath_sysmaps_dict = {}


# --------------
# variable noise
# --------------

# Format of file names of background images (multi-band only):
bkg_rms_file_name_format = "ufig_{}_bgrms.fits"
# Dictionary of file names of background images (multi-band only):
bkg_rms_file_name_dict = {}

# Map containing the RMS of the background across the image:
bkg_rms_file_name = "background_rms.fits"
# Scaling the background_rms-map
bkg_noise_scale = 1.00
# Amplitude of the bkg_rms-map and mean of const gaussian bkg:
bkg_noise_amp = 0.0

# Use if background_noise is called before convert_photons_to_adu:
bkg_noise_multiply_gain = False

# ------------------
# compression noise
# -----------------
# Uniform noise in range [-compression_noise_level, compression_noise_level]
compression_noise_level = 0.6
# to emulate compression noise

# -----------
# chunked map
# -----------
chunksize = 2500  # Size of the quadratic chunks background map is split up in

# Exposure Time
exp_time_type = "constant"  # Whether the exposure time varies across the image

# ----------------------
# constant exposure time
# ----------------------
n_exp_dict = {}  # Dictionary of exposure time (multi-band only)
n_exp = 7  # effective number of exposures in coadd

# ----------------------
# variable exposure time
# ----------------------

# Format of file names of exposure time images (multi-band only)
exp_time_file_name_format = "ufig_{}_texp.fits"

# Dictionary of file names of exposure time images (multi-band only)
exp_time_file_name_dict = {}

# Image of the exposure time in every pixel
exp_time_file_name = ""

# Background subtraction

# number of iterations for sigma clipping
bgsubract_n_iter = 10

# spacing of pixels in img bkg estimation is done for (downsampling)
bgsubract_n_downsample = 50

# size in pixels for local sky subtraction
back_size = 128

# Resampling

# lanczos_integral or read_from_file
lanczos_kernel_type = "lanczos_integral"

# -------
# lanczos
# -------

# kernel to simulate correlated noise (only for lanczos_integral)
lanczos_n = 2

# ------------------------
# empirical lanczos kernel
# ------------------------
# Filepath containing empirical resampling kernel

filename_resampling_kernel = "lanczos_resampling_kernel_n3.txt"

# ==================================================================
# S O U R C E   E X T R A C T O R
# ==================================================================

# SExtractor executable
sextractor_binary = "sex"

# SExtractor configuration file
sextractor_config = "default.sex"

# SExtractor S/G separation neural network
sextractor_nnw = "default.nnw"

# SExtractor filter
sextractor_filter = "gauss_3.0_5x5.conv"

# SExtractor parameter file
sextractor_params = "default.param"
# Format of SExtractor output catalog filenames (multi-band only)
sextractor_catalog_name_format = "{}_{}.sexcat"

# Dictionary of file names of output catalogs (multi-band only)
sextractor_catalog_name_dict = {}

# SExtractor output catalog
sextractor_catalog_name = "ufig.sexcat"

# SExtractor check-images; ["SEGMENTATION","BACKGROUND","APERTURES"]
sextractor_checkimages = []

# SExtractor check-images suffixes; ["_seg.fits","_bkg.fits","_ap.fits"]
sextractor_checkimages_suffixes = []
sextractor_use_temp = False
sextractor_use_forced_photo = False
# radius for the adding of the flags
sextractor_catalog_off_mask_radius = 1

# -----------------------------
# variable source extractor run
# -----------------------------

# SExtractor weighting scheme (usually NONE or MAP_WEIGHT)
weight_type = "NONE"

# SExtractor boolean whether weight maps are gain maps (Y) or not (N)
weight_gain = "N"
# Format of file names of weight images (multi-band only)
weight_image_format = "{}_{}_invvar.fits"

# Dictionary of file names of weight images (multi-band only)
weight_image_dict = {}
# Name of weight image stored in maps_remote_dir
weight_image = "DES0441-4414_r_invvar.fits"
flag_gain_times_nexp = True

# ---------------------------------------
# Forced-photometry run (multi-band only)
# ---------------------------------------
# Dictionary of file names of output catalogs for forced-photometry mode (multi-band
# only)
sextractor_forced_photo_catalog_name_dict = {}

# Format of SExtractor output catalog filenames for forced-photomery mode (multi-band
# only)
sextractor_forced_photo_catalog_name_format = "{}_{}_forced_photo.sexcat"

# Filter band used as detection image for forced-photometry mode (multi-band only)
sextractor_forced_photo_detection_bands = ["r"]
# Dictionary of file names of mask files for forced-photometry mode (multi-band only)
sextractor_mask_name_dict = {}


# ==================================================================
# M A T C H I N G
# ==================================================================

# Number of cells in which obj are matched each axis is divided
matching_cells = 20

# Percentage of overlap of matching cells
cells_overlap = 0.05

# Max radius in x- and y-direction for obj to be matched (pixels)
max_radius = 2.5

# Max mag difference for obj between input and output
mag_diff = 4

# Extension the SExtractor catalog resides in
sextractor_ext = 2

# Column containing x-coordinates used to match obj
matching_x = "XWIN_IMAGE"

# Column containing y-coordinates used to match obj
matching_y = "YWIN_IMAGE"

# Column containing magnitude used to match obj
matching_mag = "MAG_AUTO"

# ==================================================================
# E M U L A T O R
# ==================================================================

# how to estimate the flux when running the emulator, options available:
# - none: no flux estimation
# - full_image: estimate flux from a simplified rendering of the full image
# - points: equivalent to full_image but only evaluated at the positions of the objects
#   (and therefore sometimes faster)
# - integrated: average galaxy density weighted by magnitudes and size
# - binned_integrated: average galaxy density weighted by magnitudes and size in bins
# - ngal: number of galaxies for different magnitude cuts
flux_estimation_type = "none"

# magnitude value that is used for scaling
mag_for_scaling = [22, 23, 24]

# r50 value that is used for scaling
r50_for_scaling = 0.5

# number of bins used for flux estimation
n_bins_for_flux_estimation = 1

# if to use the minimal emulator that does not require local information (e.g. bkg or
# psf)
emu_mini = False


# ==================================================================
# V A R I A B L E   S Y S T E M A T I C S
# ==================================================================

# These parameters are used to add some noise on estimated systematics such
# as background and PSF. This is useful to test the robustness of the pipeline
# to small errors in the systematics.

# Background
# ----------------
# standard deviation of the scatter added to the background amplitude
bkg_amp_variation_sigma = 0.0
bkg_amp_variation_sigma_dict = {}
# standard deviation of the scatter added to the background noise
bkg_noise_variation_sigma = 0.0
bkg_noise_variation_sigma_dict = {}

# PSF
# ----------------
# standard deviation of the scatter added to the PSF fwhm
psf_fwhm_variation_sigma = 0.0
psf_fwhm_variation_sigma_dict = {}
