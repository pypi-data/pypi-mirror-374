Simulating an HSC Deep Field Image
==================================

This tutorial explains how to create a realistic simulation of a Hyper
Suprime-Cam (HSC) deep field image using the galsbi package and UFig. To
run this notebook yourself, you may need to install additional packages
that are not included in the standard installation of galsbi or UFig.

The basic ingredients for the simulation include:

- **Realistic galaxy catalog**: The galaxy catalog contains all galaxies that should be
  rendered in the image. The properties of the galaxies that need to be specified are
  x and y positions, magnitude in the band of interest, half-light radius, Sérsic
  index, and ellipticity parameters (e₁ and e₂). We use the GalSBI model to
  generate this catalog, a comprehensive tutorial about GalSBI can be found in the
  `GalSBI documentation <https://cosmo-docs.phys.ethz.ch/galsbi/>`__.

- **PSF model**: The point spread function (PSF) describes how a point source is imaged
  in the image. We use the PSF estimation pipeline from UFig to estimate the PSF in
  the real image and then apply this PSF to the simulation.

- **Background noise**: A realistic background noise map is essential for a realistic image
  simulation. We estimate the varying background noise from the real image directly.

- **Exposure metadata**: The magnitudes of the galaxies in the catalog have to be
  converted into number of counts in the image. This requires information about the
  magnitude zero point, gain and exposure time. UFig has three supported methods to
  do this conversion:

  1. ``constant``: Assumes constant values for the gain and exposure time across the image.
  2. ``variable``: Requires a map of the exposure time for each pixel and then computes
     the counts based on the mean gain and the exposure time at the object position.
  3. ``gain_map``: Requires a map of the gain for each pixel and then computes the counts
     based on the gain at the object position.

  We will use the ``variable`` method in this tutorial, but also show how to create the
  gain map.

.. code:: python

    import os
    import subprocess

    import h5py
    import healpy as hp
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import simulation_utils  # helper functions, ufig/docs/HSC_DUD/simulation_utils.py
    from astropy import coordinates
    from astropy.coordinates import Angle, SkyCoord
    from astropy.io import fits
    from astropy.stats import SigmaClip
    from astropy.visualization import ImageNormalize, PercentileInterval
    from astropy.wcs import WCS
    from astroquery.vizier import Vizier
    from cosmic_toolbox import arraytools as at
    from cosmic_toolbox import colors, file_utils
    from cosmo_torrent import data_path
    from galsbi import GalSBI
    from photutils.background import Background2D, SExtractorBackground
    from scipy.stats import linregress
    from trianglechain import TriangleChain

    import ufig
    from ufig import coordinate_util
    from ufig.plugins.add_generic_stamp_flags import add_all_stamp_flags
    from ufig.plugins.run_sextractor_forced_photometry import convert_fits_to_hdf
    from ufig.psf_estimation import PSFEstimationPipeline

    colors.set_cycle()

    DATA_DIR = file_utils.get_abs_path("data")
    SEXTRACTOR_DIR = os.path.join(DATA_DIR, "sextractor_output")

    IMAGE_FILE = os.path.join(DATA_DIR, "calexp-HSC-I-9813-702.fits")
    METADATA_CSV = os.path.join(DATA_DIR, "calexp-HSC-I-9813-702_metadata.csv")
    COADD_META_CSV = os.path.join(DATA_DIR, "calexp-HSC-I-9813-702_coadd_metadata.csv")
    SYSMAPS_FILE = os.path.join(DATA_DIR, "sysmaps_demo.h5")
    SYSMAPS_IMPROVED_FILE = os.path.join(DATA_DIR, "sysmaps_demo_improved.h5")
    MASK_FILE = os.path.join(DATA_DIR, "mask_demo.h5")
    OVERLAP_FILE = os.path.join(DATA_DIR, "overlap_demo.h5")
    SEXTRACTOR_CAT = os.path.join(SEXTRACTOR_DIR, "hsc_i_se.cat")
    SEXTRACTOR_SEG = os.path.join(SEXTRACTOR_DIR, "hsc_i_se_seg.fits")
    SEXTRACTOR_BKG = os.path.join(SEXTRACTOR_DIR, "hsc_i_se_bkg.fits")
    BESANCON_HEADER = os.path.join(DATA_DIR, "besancon_sim.header")
    BESANCON_CAT = os.path.join(DATA_DIR, "besancon_sim.fits")
    BESANCON_FILE = os.path.join(DATA_DIR, "besancon_demo.h5")
    GAIA_FILE = os.path.join(DATA_DIR, "gaiadr3_demo.h5")
    PSF_MODEL_FILE = os.path.join(DATA_DIR, "psf_model_demo.h5")
    PSF_MODEL_IMPROVED_FILE = os.path.join(DATA_DIR, "psf_model_improved_demo.h5")
    PSF_CATALOG_FILE = os.path.join(DATA_DIR, "psf_catalog_data.cat")
    PSF_CATALOG_IMPROVED_FILE = os.path.join(DATA_DIR, "psf_catalog_improved_data.cat")
    PSF_CATALOG_SIM_FILE = os.path.join(DATA_DIR, "psf_catalog_sim.cat")
    PSF_CATALOG_SIM_IMPROVED_FILE = os.path.join(DATA_DIR, "psf_catalog_improved_sim.cat")
    CNN_MODEL_PATH = os.path.join(data_path("psf_cnn"), "pretrained")
    GALSBI_CONFIG = "galsbi_HSC_config.py"

    colors.set_cycle()


Preparation of the Real Image: Sky Information and Metadata
-----------------------------------------------------------

Much of the necessary information can be extracted directly from the
real image. The FITS header contains details about the pixel scale and
field of view. We process the metadata to obtain parameters such as
gain, exposure time, and other relevant settings.

**Data Source:** The data was downloaded from the official HSC data
access website:
https://hsc-release.mtk.nao.ac.jp/doc/index.php/data-access\__pdr3/

.. code:: python

    data = fits.open(IMAGE_FILE)
    real_image = data[1].data
    header = data[1].header
    data.close()

    interval = PercentileInterval(90)
    vmin, vmax = interval.get_limits(real_image)
    norm = ImageNormalize(vmin=vmin, vmax=vmax)

Header information
~~~~~~~~~~~~~~~~~~

The FITS header provides the number of pixels and the field of view for
the image. The pixel scale is 0.168 arcsec/pixel, which is constant for
all HSC deep fields.

.. code:: python

    # Create skymapinfo from header
    skymapinfo_ = {}

    # WCS information
    skymapinfo_["pixscale"] = 0.168  # HSC pixel scale in arcsec/pixel
    skymapinfo_["CRPIX1"] = header["CRPIX1"]
    skymapinfo_["CRPIX2"] = header["CRPIX2"]
    skymapinfo_["CRVAL1"] = header["CRVAL1"]
    skymapinfo_["CRVAL2"] = header["CRVAL2"]
    skymapinfo_["NAXIS1"] = header["NAXIS1"]
    skymapinfo_["NAXIS2"] = header["NAXIS2"]

Metadata from Coaddition
~~~~~~~~~~~~~~~~~~~~~~~~

To run SExtractor, we need the magnitude zero point, gain, saturation
level, and mean seeing of the image. This information is not always
present in the header, so we query the metadata and construct these
values ourselves. For the image simulation, we also create maps of exposure
time, number of exposures, and gain for each pixel. We download a .csv
file from the HSC data access website using this command:

.. code:: sql

   SELECT frm.llcra,frm.llcdec,frm.ulcra,frm.ulcdec,frm.urcra,frm.urcdec,frm.lrcra,frm.lrcdec,frm.exptime,frm.gain1,frm.gain2,frm.gain3,frm.gain4,frm.seeing,frm.visit
   FROM pdr3_dud.frame as frm
   JOIN pdr3_dud.mosaicframe as mosfrm USING (frame_num)
   WHERE skymap_id = '98130702' AND (frm.filter01 = 'HSC-I' OR frm.filter01 = 'HSC-I2')

This downloads the information about the individual exposures of the
coadded image.

The HSC camera consists of a mosaic of 116 CCD chips (104 science
detectors), each with four independent amplifiers. The metadata query
returns the coordinates of the chip corners, exposure time, gain,
seeing, and visit number for all mosaic frames used in the coadded
image. If two mosaic frames have the same visit number, they were taken
in the same exposure.

.. code:: python

    (
        llcra,
            llcdecl,
            ulcra,
            ulcdecl,
            urcra,
            urcdecl,
            lrcra,
            lrcdecl,
            exptime,
            gain1,
            gain2,
            gain3,
            gain4,
            seeing,
            visit,

    ) = np.loadtxt(METADATA_CSV, comments="#", delimiter=",", unpack=True, ndmin=2)

.. code:: python

    # Get the world coordinates of the coadded image
    wcs_tile = WCS(header=header)

    # Get the mean gain for each mosaic
    gain = np.mean([gain1, gain2, gain3, gain4], axis=0)

    # Get the pixel coordinates of the corners of the mosaic
    x_ll, y_ll = wcs_tile.all_world2pix(llcra, llcdecl, 1)
    x_ul, y_ul = wcs_tile.all_world2pix(ulcra, ulcdecl, 1)
    x_ur, y_ur = wcs_tile.all_world2pix(urcra, urcdecl, 1)
    x_lr, y_lr = wcs_tile.all_world2pix(lrcra, lrcdecl, 1)

For illustration, we plot the first 10 mosaic frames in comparison to the coadded image.
Some of them are next to each other because they were taken in the same exposure (visit)
but from a different CCD chip.

.. code:: python

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(
        [0, header["NAXIS1"], header["NAXIS1"], 0, 0],
        [0, 0, header["NAXIS1"], header["NAXIS2"], 0],
        color='black',
        lw=2
    )
    for i in range(10):
        xs = [x_ll[i], x_ul[i], x_ur[i], x_lr[i], x_ll[i]]
        ys = [y_ll[i], y_ul[i], y_ur[i], y_lr[i], y_ll[i]]
        ax.plot(xs, ys, ls="--", linewidth=1)
    ax.set_xlim(-3000, 7000)
    ax.set_ylim(-3000, 7000)
    ax.set_title("The first 10 mosaic frames in comparison to the coadded image")


.. image:: output_10_1.png


.. code:: python

    unique_visits, visit_indices = np.unique(visit, return_inverse=True)
    n_visits = len(unique_visits)


With this information, we can create a map of the exposure time, the
number of exposures and the gain for each pixel in the image. To do this,
we just need to loop over the mosaic frames and add the exposure time,
number of exposures, and gain to the corresponding pixels in the map.

*Note about map_pointings:* The map_pointings uses bitmaps with 64-bit
integers to efficiently track visit coverage. Each HSC visit is assigned
a unique visit index from 0 to n_visits-1. To record which pixels are
observed in which visits, binary representation is used: a pixel
observed by visits 0 and 3 will have value 2^0 + 2^3 = 9. To handle
large numbers of visits, multiple 64-bit bitmaps are used:

- Visits 0-63 are stored in the first bitmap (bit1)
- Visits 64-127 are stored in the second bitmap (bit2)
- and so on…

Example: A pixel observed by visits 0, 64, and 70 will have:

- bit1: 2^0 = 1
- bit2: 2^(64-64) + 2^(70-64) = 2^0 + 2^6 = 65

This bitmap approach allows efficient storage and retrieval of visit
overlap information for up to 320 visits (5 × 64 bits) per pixel.

.. code:: python

    n_pix1_coadd = header["NAXIS1"]
    n_pix2_coadd = header["NAXIS2"]
    pixcenters_x, pixcenters_y = np.meshgrid(
                np.arange(n_pix1_coadd, dtype=np.float32) + 0.5,
                np.arange(n_pix2_coadd, dtype=np.float32) + 0.5,
                copy=False,
     )

    map_expt = np.zeros((n_pix2_coadd, n_pix1_coadd), dtype=np.uint16)
    map_nexp = np.zeros((n_pix2_coadd, n_pix1_coadd), dtype=np.uint16)
    map_gain = np.zeros((n_pix2_coadd, n_pix1_coadd), dtype=np.float32)
    map_pointings = np.zeros(
        (n_pix2_coadd, n_pix1_coadd),
        dtype=np.dtype(
        [
                        ("bit1", np.uint64),
                        ("bit2", np.uint64),
                        ("bit3", np.uint64),
                        ("bit4", np.uint64),
                        ("bit5", np.uint64),
                    ]
                ),
            )

    def add_to_maps(
        pixcenters_x,
        pixcenters_y,
        corners_x,
        corners_y,
        exptime,
        gain,
        visit_index,
        map_expt,
        map_gain,
        map_nexp,
        map_pointings,
    ):
        x_min = max(int(np.floor(np.amin(corners_x))), 0)
        x_max = min(int(np.floor(np.amax(corners_x) + 1)), pixcenters_x.shape[1])
        y_min = max(int(np.floor(np.amin(corners_y))), 0)
        y_max = min(int(np.floor(np.amax(corners_y) + 1)), pixcenters_x.shape[0])

        if x_min < x_max and y_min < y_max:
            # Select the region of the map that corresponds to the corners of the mosaic
            select_region_amp = simulation_utils.get_region_selection(
                pixcenters_x[y_min:y_max, x_min:x_max],
                pixcenters_y[y_min:y_max, x_min:x_max],
                corners_x,
                corners_y,
            )
            map_expt[y_min:y_max, x_min:x_max][select_region_amp] += int(exptime)
            map_gain[y_min:y_max, x_min:x_max][select_region_amp] += gain
            map_nexp[y_min:y_max, x_min:x_max][select_region_amp] += 1
            if visit_index < 64:
                map_pointings["bit1"][y_min:y_max, x_min:x_max][
                    select_region_amp
                ] += np.array(2**visit_index, dtype=np.uint64)
            elif visit_index < (64 * 2):
                map_pointings["bit2"][y_min:y_max, x_min:x_max][
                    select_region_amp
                ] += np.array(2 ** (visit_index - 64), dtype=np.uint64)
            elif visit_index < (64 * 3):
                map_pointings["bit3"][y_min:y_max, x_min:x_max][
                    select_region_amp
                ] += np.array(2 ** (visit_index - (64 * 2)), dtype=np.uint64)
            elif visit_index < (64 * 4):
                map_pointings["bit4"][y_min:y_max, x_min:x_max][
                    select_region_amp
                ] += np.array(2 ** (visit_index - (64 * 3)), dtype=np.uint64)
            else:
                map_pointings["bit5"][y_min:y_max, x_min:x_max][
                    select_region_amp
                ] += np.array(2 ** (visit_index - (64 * 4)), dtype=np.uint64)


    for i, x in enumerate(x_ll):
        corners_x = [x_ll[i], x_ul[i], x_ur[i], x_lr[i]]
        corners_y = [y_ll[i], y_ul[i], y_ur[i], y_lr[i]]
        visit_index = visit_indices[i]
        add_to_maps(
                    pixcenters_x,
                    pixcenters_y,
                    corners_x,
                    corners_y,
                    exptime[i],
                    gain[i],
                    visit_index,
                    map_expt,
                    map_gain,
                    map_nexp,
                    map_pointings,
        )

    skymapinfo_["gain_i"] = np.mean(map_gain) / np.mean(map_nexp)
    skymapinfo_["nexp_i"] = np.mean(map_nexp)
    skymapinfo_["exptime_i"] = np.mean(map_expt)

    plt.figure(figsize=(6, 4))
    im0 = plt.imshow(map_expt, origin="lower", cmap="viridis")
    plt.colorbar(im0, label="Exposure time (seconds)")
    plt.title("Exposure time map")


.. image:: output_15_1.png


Additionally, we need some metadata about the coadded image. This
includes the magnitude zero point, the mean seeing (which is needed to
run source extraction), the gain, and the saturation level. For this, we
run the following query:

.. code:: sql

   SELECT llcra, llcdec, ulcra, ulcdec, urcra, urcdec, lrcra, lrcdec, seeing, zeropt, cd1_1, cd1_2, cd2_1, cd2_2, crpix1, crpix2,crval1, crval2, ctype1, ctype2, cunit1, cunit2, naxis1, naxis2, ra2000, dec2000, zeropt_err, ellipticity, ellipticity_pa
   #  FROM pdr3_dud.mosaic
   #  WHERE skymap_id = '98130702' AND band = 'HSC-I'

.. code:: python

    colnames = [
                "llcra",
                "llcdec",
                "ulcra",
                "ulcdec",
                "urcra",
                "urcdec",
                "lrcra",
                "lrcdec",
                "seeing",
                "zeropt",
                "cd1_1",
                "cd1_2",
                "cd2_1",
                "cd2_2",
                "crpix1",
                "crpix2",
                "crval1",
                "crval2",
                "ctype1",
                "ctype2",
                "cunit1",
                "cunit2",
                "naxis1",
                "naxis2",
                "ra2000",
                "dec2000",
                "zeropt_err",
                "ellipticity",
                "ellipticity_pa",
            ]
    meta = pd.read_csv(COADD_META_CSV, comment="#", names=colnames)

    skymapinfo_["seeing_i"] = meta["seeing"].values[0]
    skymapinfo_["magzero_i"] = meta["zeropt"].values[0]
    # simple estimation of the saturation level
    skymapinfo_["satur_i"] = np.nanmax(real_image)
    skymapinfo_["ra2000"] = meta["ra2000"].values[0]
    skymapinfo_["dec2000"] = meta["dec2000"].values[0]

Background maps
---------------

A crucial step for a realistic image simulation is a realistic
background noise map. We estimate the varying background noise from the
real image directly.

.. code:: python

    sigma_clip = SigmaClip(sigma=3)
    bkg_estimator = SExtractorBackground()

    bkg = Background2D(
        real_image,
        128,
        filter_size=(3, 3),
        sigma_clip=sigma_clip,
        bkg_estimator=bkg_estimator,
    )


Now, we can create the combined file with all systematic maps we have
created so far.

.. code:: python

    with h5py.File(SYSMAPS_FILE, mode="w") as fh5:
        fh5.create_dataset(name="map_bsig", data=bkg.background_rms, compression="lzf")
        fh5.create_dataset(name="map_expt", data=map_expt, compression="lzf")
        fh5.create_dataset(name="map_nexp", data=map_nexp, compression="lzf")
        fh5.create_dataset(name="map_gain", data=map_gain, compression="lzf")
        fh5.create_dataset(name="map_pointings", data=map_pointings, compression="lzf")
        fh5.create_dataset(name="map_invv", data=1/fits.getdata(IMAGE_FILE, ext=3), compression="lzf")
        fh5["map_pointings"].attrs["n_pointings"] = n_visits

    skymapinfo_["bkg_mean_i"] = np.background_median
    skymapinfo = at.dict2rec(skymapinfo_)
    np.save("skymapinfo.npy", skymapinfo)
    # skymapinfo is generally an array with all tiles, current_info is the tile we are currently working with
    current_info = skymapinfo[0]


Mask and Overlap files
----------------------

Masks are created using the bright star mask and the survey mask from
the HSC survey. UFig requires the mask in binary flag format, with flag
bits defined for delta weight, stars, and survey mask.

*How flag bits work:* Each pixel in the mask layer is represented by
an integer. The binary representation of this integer encodes which
flags are set for that pixel. For example:

- If bit 0 is set (2^0 = 1), the pixel is flagged by the delta weight mask (not used in our HSC simulations).
- If bit 1 is set (2^1 = 2), the pixel is flagged by the bright star mask.
- If bit 2 is set (2^2 = 4), the pixel is flagged as part of the HSC survey mask.

Multiple flags can be combined: a pixel with value 6 (2 + 4) has both the star and
HSC mask flags set.

The overlap file defines overlapping regions between tiles, which is
necessary to avoid double-counting objects when simulating multiple
tiles. Since we are only simulating a single tile, we can set the
overlap file to be all zeros.

.. code:: python

    mask_layer = fits.getdata(IMAGE_FILE, ext=2)
    mask = np.zeros_like(mask_layer, dtype=int)

    def check_for_flagbit(arr_decimal, flagbit):
        n_bits = 20
        arr_binary = np.zeros(
            (n_bits, np.shape(arr_decimal)[0], np.shape(arr_decimal)[1]), dtype=np.int32
        )
        arr_decimal = arr_decimal.copy().astype(float)
        for i in range(n_bits):
            if i == flagbit:
                mask = np.where((arr_decimal % np.uint(2)) == 1, True, False)
            arr_binary[i, :] = arr_decimal % np.uint(2)
            arr_decimal //= np.uint(2)

        return mask

    FLAGBITS_STAR = 1
    FLAGBITS_HSC_MASK = 2

    mask_star = check_for_flagbit(mask_layer, 9)
    mask_hsc = check_for_flagbit(mask_layer, 8)

    mask += mask_star.astype(int) * 2**FLAGBITS_STAR
    mask += mask_hsc.astype(int) * 2**FLAGBITS_HSC_MASK

    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    axs[0].imshow(real_image, origin="lower", cmap="gray", norm=norm)
    axs[0].set_title("Original Image")
    axs[1].imshow(mask, origin="lower")
    axs[1].set_title("Mask Layer")

    with h5py.File(MASK_FILE, "w") as fh5:
        fh5.create_dataset("mask", data=mask, compression="lzf")

    mask_overlap = np.zeros_like(real_image, dtype=bool)
    with h5py.File(OVERLAP_FILE, "w") as fh5:
        fh5.create_dataset(name="img_mask", data=mask_overlap, compression="lzf")




.. image:: output_24_0.png


Source extraction
-----------------

We use ``SExtractor`` to extract sources and create a segmentation map
from the real image. The mean seeing and gain values obtained from the
metadata are used for this step.

.. code:: python

    config_dir = ufig.__path__[0] + "/res/sextractor"

    # Create output directory if it doesn't exist
    os.makedirs(SEXTRACTOR_DIR, exist_ok=True)

    # Extract image to a clean FITS file (based on your working approach)
    temp_image_path = "temp_image.fits"
    hdu = fits.PrimaryHDU(data=real_image, header=header)
    hdu.writeto(temp_image_path, overwrite=True)

    # Build command using the working pattern from your reference
    sex_command = f"""sex {temp_image_path},{temp_image_path} \
    -c {config_dir}/hsc.config \
    -SEEING_FWHM {current_info["seeing_i"]} \
    -SATUR_KEY NONE \
    -SATUR_LEVEL {current_info["satur_i"]} \
    -MAG_ZEROPOINT {current_info["magzero_i"]} \
    -GAIN_KEY NONE \
    -GAIN {current_info["gain_i"] * current_info["nexp_i"]} \
    -PIXEL_SCALE {current_info["pixscale"]} \
    -STARNNW_NAME {config_dir}/default.nnw \
    -FILTER_NAME {config_dir}/gauss_3.0_5x5.conv \
    -PARAMETERS_NAME {config_dir}/newdefault.param \
    -CATALOG_NAME {SEXTRACTOR_DIR}/hsc_i_se.cat \
    -CHECKIMAGE_TYPE SEGMENTATION,BACKGROUND \
    -CHECKIMAGE_NAME {SEXTRACTOR_DIR}/hsc_i_se_seg.fits,{SEXTRACTOR_DIR}/hsc_i_se_bkg.fits \
    -WEIGHT_TYPE NONE,NONE \
    -WEIGHT_GAIN N,N \
    -CATALOG_TYPE FITS_LDAC \
    -VERBOSE_TYPE QUIET"""

    try:
        result = subprocess.run(
            sex_command, shell=True, capture_output=True, text=True, check=True
        )
        print("SExtractor completed successfully!")
        print(f"Catalog: {SEXTRACTOR_DIR}/hsc_i_se.cat")
        print(f"Segmentation: {SEXTRACTOR_DIR}/hsc_i_se_seg.fits")
        print(f"Background: {SEXTRACTOR_DIR}/hsc_i_se_bkg.fits")

        # Clean up temporary file
        os.remove(temp_image_path)

    except subprocess.CalledProcessError as e:
        print(f"SExtractor failed: {e}")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        print(f"Standard output: {e.stdout}")
    except FileNotFoundError:
        print("SExtractor not found. Install with: brew install sextractor")

    convert_fits_to_hdf(f"{SEXTRACTOR_DIR}/hsc_i_se.cat")


.. code:: python

    # Plot image, segmentation, and background
    segmentation_image = fits.getdata(f"{SEXTRACTOR_DIR}/hsc_i_se_seg.fits")
    background_image = fits.getdata(f"{SEXTRACTOR_DIR}/hsc_i_se_bkg.fits")
    segmentation_mask = segmentation_image != 0

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    axs[0].imshow(real_image, cmap='gray', norm=norm)
    axs[0].set_title('Original Image')
    axs[1].imshow(segmentation_mask, cmap='Blues')
    axs[1].set_title('Segmentation Image')
    axs[2].imshow(background_image, cmap='viridis')
    axs[2].set_title('Background Image')


.. image:: output_27_1.png


.. code:: python

    sexcat_data = at.load_hdf_cols(f"{SEXTRACTOR_DIR}/hsc_i_se.cat")
    tri = TriangleChain(
        fill=True,
        params=["MAG_AUTO", "FLUX_RADIUS", "ELLIPTICITY"],
        ranges={"ELLIPTICITY": (0, 1), "FLUX_RADIUS": (0, 10), "MAG_AUTO": (17, 30) }
        )
    tri.contour_cl(sexcat_data);


.. image:: output_28_2.png


Finally, we assign flags to each source based on the mask and overlap
file. These flags are used for selecting sources for a later analysis,
but also for the PSF estimation.

.. code:: python

    add_all_stamp_flags(
        filename_cat=f"{SEXTRACTOR_DIR}/hsc_i_se.cat",
        filename_overlapblock=f"data/overlap_demo.h5",
        filename_mask=f"data/mask_demo.h5",
        off_mask_radius=1
    )



Stars
-----

Stars are simulated using two approaches:

- The Besançon model of the Milky Way provides a synthetic star catalog.
- The brightest stars in each image are placed at the positions of actual stars from the Gaia catalog.

Besançon model
~~~~~~~~~~~~~~

We use the Besançon model of the Milky Way to generate a synthetic
catalog of stars, providing realistic spatial variations and magnitude
distributions. To do this, we first need to specify the region of the
sky to simulate. The coordinates of the corners of the coadded image
define this area. In this tutorial, the region is relatively small
because we simulate only a single HSC deep field tile. However, the same
approach applies if ``skymapinfo`` contains multiple entries - for
example, when simulating several tiles of the HSC deep field.

.. code:: python

    nside_besancon = 8

    hp_pixels = np.unique(coordinate_util.radec2pix(
        skymapinfo_["ra2000"],
        skymapinfo_["dec2000"],
        nside_besancon
        )
    )
    # add all direct neighbors
    hp_pixels = hp.get_all_neighbours(nside_besancon, hp_pixels).flatten()
    hp_pixels = hp_pixels[hp_pixels >= 0]
    hp_pixels = np.unique(hp_pixels)


    hp_map = np.ones(hp.nside2npix(nside_besancon)) * hp.UNSEEN
    hp_map[hp_pixels] = 1
    besancon_catalog = [None] * len(hp_map)

.. code:: python

    # Transform the healpix pixel centers to RA/Dec
    theta, phi = hp.pix2ang(nside_besancon, hp_pixels)
    ra, dec = coordinate_util.thetaphi2radec(theta, phi)
    coord_icrs = coordinates.SkyCoord(ra, dec, frame="icrs", unit="deg")
    gal_l = coord_icrs.galactic.l.value
    gal_b = coord_icrs.galactic.b.value

With this information, you are ready to submit jobs using the Besançon
web interface: http://model2016.obs-besancon.fr/modele_options.php. For
each Healpix pixel, use the corresponding ``gal_l`` and ``gal_b``
coordinates to run a simulation.

Compared to the default settings, we make several adjustments: we select
the SDSS+JHK filters, choose FITS as the output format, set the maximum
distance to 50 kpc, and use the Healpix pixel’s longitude and latitude
(``gal_l``, ``gal_b``). The solid angle is increased to 5 deg², the r
band is set as the reference band with a limiting magnitude of 30 (all
other magnitude ranges are set from -99 to 99), color ranges are
adjusted to (“r-g”, -10, 99), (“r-i”, -10, 99), (“r-z”, -10, 99),
(“r-u”, -10, 99), and all photometric errors are set to zero.

This simulation process is repeated for each Healpix pixel. To automate
this, you can use the provided script in the public `legacy_abc
repository <https://cosmo-gitlab.phys.ethz.ch/cosmo_public/legacy_abc_public/-/blob/fischbacher24/src/legacy_abc/analysis/systematics/create_besancon_map.py>`__.

After the simulations are complete, the output files need to be
processed.

.. code:: python

    def str_to_float(str):
        s = "".join([c for c in str if c.isdigit() or c == "." or c == "-"])
        f = float(s)
        return f


    def read_catalog(path_header, path_cat, nside, area_store):
        # Header
        with open(path_header, "r") as f:
            lines_header = f.readlines()

        for line in lines_header:
            if "l =" in line and "b =" in line and "Solid angle" in line:
                line = line.strip().split()
                gal_l = str_to_float(line[line.index("(l") + 2])
                gal_b = str_to_float(line[line.index("b") + 2])
                area_besancon = float(line[line.index("angle") + 1])
                break

        coord_gal = coordinates.SkyCoord(gal_l, gal_b, frame="galactic", unit="deg")
        ra = coord_gal.icrs.ra.value
        dec = coord_gal.icrs.dec.value
        ipix = coordinate_util.radec2pix(ra, dec, nside)

        # Catalog
        cat_besancon = fits.getdata(path_cat, ext=1)
        cat_grizY = np.empty(
            len(cat_besancon), dtype=at.get_dtype(["g", "r", "i", "z", "y"])
        )
        cat_grizY["g"] = -(cat_besancon["r-g"] - cat_besancon["r"])
        cat_grizY["r"] = cat_besancon["r"]
        cat_grizY["i"] = -(cat_besancon["r-i"] - cat_besancon["r"])
        cat_grizY["z"] = -(cat_besancon["r-z"] - cat_besancon["r"])
        cat_grizY["y"] = -(cat_besancon["r-z"] - cat_besancon["r"])

        # Subsample
        n_keep = int(len(cat_grizY) * area_store / area_besancon)
        select = np.random.choice(len(cat_grizY), n_keep, replace=n_keep > len(cat_grizY))
        cat_grizY = cat_grizY[select]

        return ipix, cat_grizY

    area_store = 2  # area in deg^2, should be clearly larger than the area of the tile
    i_pix, cat = read_catalog(
        BESANCON_HEADER,
        BESANCON_CAT,
        nside_besancon,
        area_store=area_store
    )


The Besançon catalogs used in our simulation cover 5 square degrees and
are centered at the galactic coordinates of the Healpix pixel centers.
To reduce storage and computational requirements, we only save a
subsample of the stars—specifically, 2/5 (as set by ``area_store``) of
the stars in each catalog. This approach ensures efficiency while
maintaining a realistic star density. To preserve the correct scaling
for later image simulations, we also store the Healpix map’s ``nside``
and the simulated area (``area_store``). These parameters allow us to
properly rescale and subsample stars when generating images, ensuring
that the relative number of stars remains physically accurate.

.. code:: python

    besancon_catalog[i_pix] = cat
    hp_map[i_pix] = len(cat)

    with h5py.File(BESANCON_FILE, "w") as fh5:
        fh5.create_dataset("simulation_area", data=area_store)
        fh5.create_dataset("nside", data=nside_besancon)
        fh5.create_dataset("healpix_mask", data=hp_map)
        for ind, star_cat in enumerate(besancon_catalog):
            if star_cat is not None:
                fh5.create_dataset("healpix_list/{:04d}".format(ind), data=star_cat)

Gaia catalog
~~~~~~~~~~~~

We use the Besançon model to generate the full star sample for our
simulation. To ensure the brightest stars appear at the same position as
in the real data and that we can therefore use the same bright star
mask, we position-match the synthetic catalog with the Gaia catalog. For
this, we only require the positions and G-band magnitudes from Gaia. The
actual matching of Gaia stars to Besançon stars is performed during the
image simulation step, so no further processing is needed at this stage.

.. code:: python

    vquery = Vizier(columns=["Source", "RAJ2000", "DEJ2000", "Gmag"], row_limit=-1)

    field = SkyCoord(
        ra=current_info["ra2000"],
        dec=current_info["dec2000"],
        unit=("deg", "deg"),
        frame="icrs",
    )

    # query for objects within a radius of 1 times image diagonals
    query_radius_pix = np.sqrt(
        current_info["NAXIS1"] ** 2 + current_info["NAXIS2"] ** 2
    )
    query_radius_deg = query_radius_pix * current_info["pixscale"] / 60**2
    gaia_cat = vquery.query_region(
        field,
        radius=Angle(query_radius_deg, "deg"),
        catalog="I/355/gaiadr3",
        cache=False,
    )[0]
    gaia_cat = np.array(gaia_cat)

    # filter catalog
    select = np.ones(len(gaia_cat), dtype=bool)
    for col in gaia_cat.dtype.names:
        select &= np.isfinite(gaia_cat[col])
    gaia_cat = gaia_cat[select]
    print(
            "Removed {} / {} objects".format(len(select) - len(gaia_cat), len(select))
        )


.. parsed-literal::

    Removed 0 / 935 objects


.. code:: python

    cat_out = np.empty(
            len(gaia_cat),
            dtype=[
                ("ra", float),
                ("dec", float),
                ("phot_g_mean_mag", np.float32),
                ("id", int),
            ],
        )
    cat_out["ra"] = gaia_cat["RAJ2000"]
    cat_out["dec"] = gaia_cat["DEJ2000"]
    cat_out["phot_g_mean_mag"] = gaia_cat["Gmag"]
    cat_out["id"] = gaia_cat["Source"]

    at.save_hdf(GAIA_FILE, cat_out, compression="lzf")


PSF estimation
--------------

Estimating the point spread function (PSF) is crucial for realistic
image simulations. We estimate the PSF directly from the real image
using a convolutional neural network (CNN) approach, as developed in
`Herbel+2018 <http://arxiv.org/abs/1801.07615>`__ and
`Kacprzak+2020 <http://arxiv.org/abs/1906.01018>`__.

The pipeline consists of four main steps:

1. **Data Preparation**: Identify stars in the image using the Gaia catalog, extract small cutouts around these stars, and select suitable cutouts based on magnitude and position.
2. **CNN Prediction**: Use a pre-trained CNN model to predict the PSF parameters for each selected star.
3. **PSF Interpolation**: Interpolate the predicted PSF parameters to build a PSF model for the entire image. This uses a Chebyshev polynomial basis (maximum order 4) and incorporates information about the coadd tiling pattern.
4. **PSF Model Storage**: Save the resulting PSF model and the grid of PSF parameter predictions.

.. code:: python

    # Create pipeline instance
    pipeline = PSFEstimationPipeline(
        max_dist_gaia_arcsec=1.5 * 0.168,  # 1.5 pixels
        flag_coadd_boundaries=False,
    )


    # Run the pipeline
    pipeline.create_psf_model(
        filepath_image=IMAGE_FILE,
        filepath_sexcat=SEXTRACTOR_CAT,
        filepath_sysmaps=SYSMAPS_FILE,
        filepath_gaia=GAIA_FILE,
        filepath_cnn=CNN_MODEL_PATH,
        filepath_out_model=PSF_MODEL_FILE,
        filepath_out_cat=PSF_CATALOG_FILE,
    )


Simulating the Image
--------------------

With all ingredients prepared, we use the GalSBI galaxy population model
to create a realistic galaxy catalog and simulate the image. The
simulation uses the systematic maps, mask, overlap file, PSF model, and
star catalogs described above. We use the ``galsbi`` package in the
custom configuration mode to run the simulation. The configuration file
``galsbi_HSC_config.py`` contains all the necessary settings for the
simulation, including the pixel scale, image size, filters, and plugins
to be used.

.. code-block:: python
   :caption: galsbi_HSC_config.py

   # Copyright (C) 2025 ETH Zurich
   # Institute for Particle Physics and Astrophysics
   # Author: Silvan Fischbacher
   # created: Tue Jul 15 2025


   import os

   import numpy as np
   import ufig.config.common
   from cosmo_torrent import data_path
   from ivy.loop import Loop
   from ufig.workflow_util import FiltersStopCriteria
   from cosmic_toolbox import arraytools as at
   import galsbi.ucat.config.common


   # Import all common settings from ucat and ufig as default
   def _update_globals(module, globals_):
       globals_.update(
           {k: v for k, v in module.__dict__.items() if not k.startswith("__")}
       )


   _update_globals(galsbi.ucat.config.common, globals())
   _update_globals(ufig.config.common, globals())

   # Load data from this directory
   path2data = os.path.dirname(os.path.abspath(__file__))
   skymapinfo = np.load(os.path.join(path2data, "skymapinfo.npy"), allow_pickle=True)[0]

   # Size of the image
   sampling_mode = "wcs"
   pixscale = skymapinfo["pixscale"]
   crpix_ra = skymapinfo["CRPIX1"]
   crpix_dec = skymapinfo["CRPIX2"]
   ra0 = skymapinfo["CRVAL1"]
   dec0 = skymapinfo["CRVAL2"]
   size_x = skymapinfo["NAXIS1"]
   size_y = skymapinfo["NAXIS2"]

   # Define the filters
   filters = ["i"]
   filters_full_names = {
       "B": "SuprimeCam_B",
       "i": "HSC_i2",
   }
   reference_band = "i"
   lum_fct_filter_band = "B"  # for sampling the luminosity function
   magzero_dict = {f: skymapinfo[f"magzero_{f}"] for f in filters}

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
               "ufig.plugins.gamma_interpolation_table",
               "ufig.plugins.render_galaxies_flexion",
               "ufig.plugins.render_stars_photon",
               "ufig.plugins.convert_photons_to_adu",
               # because from the image we see single spike in the x direction:
               "ufig.plugins.saturate_pixels_x",
               "galsbi.ucat.plugins.write_catalog",
               "ufig.plugins.write_image",
           ],
           stop=FiltersStopCriteria(),
       ),
       Loop(
           [
               "ufig.plugins.single_band_setup",
               "ufig.plugins.run_sextractor_forced_photometry",
           ],
           stop=FiltersStopCriteria(),
       ),
       "ufig.plugins.match_sextractor_seg_catalog_multiband_read",
       Loop(
           [
               "ufig.plugins.add_generic_stamp_flags",
               "ufig.plugins.estimate_psf",
           ],
           stop=FiltersStopCriteria(),
       ),
       "ufig.plugins.cleanup_catalogs",
       "ivy.plugin.show_stats",
   ]

   # Background noise
   background_type = 'map'
   bkg_noise_multiply_gain = True  # background noise is added before converting to ADU
   sysmaps_type = "sysmaps_hdf_combined"
   filepath_sysmaps_dict = {
       "i": os.path.join(path2data, "data/sysmaps_demo.h5")
   }
   bkg_noise_amp_dict = {
       "i": skymapinfo[f"bkg_mean_i"]
   }
   lanczos_kernel_type = "read_from_file"


   # PSF
   psf_type = "coadd_moffat_cnn_read"
   filepath_psfmodel_input_dict = {
       "i": os.path.join(path2data, "data/psf_model_demo.h5")
   }
   psf_kurtosis = 0.0
   psf_beta = [2.0, 5.0]
   psfmodel_corr_brighter_fatter = {
       "c1r": 0.0,
       "c1e1": 0.0,
       "c1e2": 0.0,
       "mag_ref": 22,
       "apply_to_galaxies": False
   }

   # Exposure time
   exp_time_type = "variable"  # par.n_exp not relevant, map_expt from sysmaps is used
   # Gain
   gain_dict = {
       f: skymapinfo[f"gain_{f}"]*skymapinfo[f"nexp_{f}"] for f in filters
   }

   # Stars
   star_catalogue_type = "besancon_gaia_splice"
   besancon_map_path = os.path.join(path2data, "data/besancon_demo.h5"
                                    )
   filepath_gaia = os.path.join(path2data, "data/gaiadr3_demo.h5"
                                )

   # SExtractor
   sextractor_use_forced_photo = True
   sextractor_params = "newdefault.param"
   sextractor_config = "hsc_deblend_aper.config"
   sextractor_checkimages = ["SEGMENTATION", "BACKGROUND"]
   sextractor_checkimages_suffixes = ["_seg.fits", "_bkg.fits"]
   sextractor_forced_photo_detection_bands = ["i"]
   sextractor_catalog_off_mask_radius = 1
   flag_gain_times_nexp = False  # not necessary because working with effective gain

   # Luminosity function
   lum_fct_z_res = 0.001
   lum_fct_m_max = -4
   lum_fct_z_max = 6

   # position
   position_model = "uniform"

   # Sampling specs
   nside_sampling = 1024
   max_mem_hard_limit_mb = np.inf

   # Magnitude limits
   stars_mag_max = 26
   gals_mag_max = 28
   stars_mag_min = 12
   gals_mag_min = 14

   # Filter throughputs
   filters_file_name = os.path.join(
       data_path("HSC_tables"), "HSC_filters_collection_yfix.h5"
   )

   # Template spectra & integration tables
   n_templates = 5
   templates_file_name = os.path.join(
       data_path("template_BlantonRoweis07"), "template_spectra_BlantonRoweis07.h5"
   )

   # Extinction
   extinction_map_file_name = os.path.join(
       data_path("lambda_sfd_ebv"), "lambda_sfd_ebv.fits"
   )

   # magnitude table
   magnitude_calculation = "table"
   templates_int_tables_file_name = os.path.join(
       data_path("HSC_tables"), "HSC_template_integrals_yfix.h5"
   )

   # Catalog precision
   catalog_precision = np.float32

   # Seed
   seed = 42

   # Matching
   matching_cells = 20
   matching_mag = 'MAG_AUTO'
   matching_x = 'XWIN_IMAGE'
   matching_y = 'YWIN_IMAGE'

   # Rendering
   n_threads_photon_rendering = 2
   mag_pixel_rendering_stars = 5  # increased to 15 for abc

   # Mask and overlaps for flags
   filepath_overlapblock = os.path.join(
       path2data, "data/overlap_demo.h5"
   )
   sextractor_mask_name_dict = {
       "i": os.path.join(path2data, "data/mask_demo.h5"
                         )
   }

   # Parameters that are specific to the Fischbacher+24 model
   # Mainly the different parametrizations of the galaxy population model.
   # DO NOT CHANGE THESE VALUES IF YOU WANT TO USE THE MODEL OF FISCHBACHER+24
   # CHANGING THESE VALUES WILL LEAD TO A DIFFERENT MEANING OF SOME OF THE PARAMETERS
   lum_fct_parametrization = "truncated_logexp"
   ellipticity_sampling_method = "beta_mode_red_blue"
   sersic_sampling_method = "blue_red_betaprime"
   logr50_sampling_method = "sdss_fit"
   template_coeff_sampler = "dirichlet_alpha_mode"
   template_coeff_weight_blue = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
   template_coeff_weight_red = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
   template_coeff_z1_blue = 3
   template_coeff_z1_red = 3

.. code:: python

    model = GalSBI("Fischbacher+24")
    model(config_file=GALSBI_CONFIG, mode="config_file")



First Quality Assessment
------------------------

To assess the quality of the simulation, we compare the simulated image
with the real image side by side. If the visual inspection is
satisfactory, we proceed with quantitative comparisons, such as
background noise statistics and magnitude/size distributions of
galaxies. Note that small differences are expected due to cosmic
variance.

.. code:: python

    images = model.load_images()
    catalogs = model.load_catalogs()


.. code:: python

    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    axs[0].imshow(images["image i"], origin="lower", cmap="gray", norm=norm)
    axs[0].set_title("Simulated Image")
    axs[1].imshow(real_image, origin="lower", cmap="gray", norm=norm)
    axs[1].set_title("Original Image")


.. image:: output_49_1.png


.. code:: python

    background_values_real = real_image[~segmentation_mask]
    background_values_sim = images["image i"][images["segmentation i"] == 0]

    # Plot the background values in a histogram
    fig, ax = plt.subplots(figsize=(4, 2))
    _, bins, patches = ax.hist(
        background_values_real,
        bins=1000,
        histtype="step",
        label="real",
    )
    ax.hist(
        background_values_sim,
        bins=bins,
        histtype="step",
        label="sim",
    )
    ax.set_xlabel("Pixel Value")
    ax.legend()
    ax.set_xlim(-0.05, 0.05)

.. image:: output_50_1.png


.. code:: python

    tri = TriangleChain(
        params=["MAG_AUTO", "FLUX_RADIUS", "ELLIPTICITY"],
        ranges={"ELLIPTICITY": (0, 1), "FLUX_RADIUS": (0, 10), "MAG_AUTO": (17, 30) }
    )
    tri.contour_cl(catalogs["sextractor i"])
    tri.contour_cl(sexcat_data);


.. image:: output_51_1.png

Fine-Tuning
-----------

The agreement between the simulation and the real data is already very good and ready to
be used for most applications. For certain applications, however, the requirements on
PSF or background level might be very strict. In this case, it might be necessary to
fine-tune the PSF estimation and background noise estimation.

Fine-Tuning PSF Estimation
~~~~~~~~~~~~~~~~~~~~~~~~~~

A measured PSF will never be exactly the same as the input PSF used in
the simulation. To account for this, the PSF estimation pipeline can be
fine-tuned. We analyze the differences between the measured PSF
parameters and the input PSF parameters, and apply a linear adjustment
to the measured PSF parameters such that the measured PSF parameters of
the simulation agrees with the measured PSF parameters of the real
image. This especially improves the agreement of the most important PSF
parameters, such as the FWHM.

.. code:: python

    psf_measured_sim = at.load_hdf_cols("data/psf_catalog_sim.cat")
    psf_measured_data = at.load_hdf_cols("data/psf_catalog_data.cat")
    select = psf_measured_sim["psf_fwhm"] != -200
    psf_matched = psf_measured_sim[select]

    psf_params = ["psf_fwhm", "psf_flux_ratio", "psf_e1", "psf_e2", "psf_f1", "psf_f2", "psf_g1", "psf_g2"]
    linear_adjustment = {}
    for par in psf_params:
        result = linregress(psf_matched[par], psf_matched[par+"_ipt"])
        linear_adjustment[par] = (result.intercept, result.slope)

.. code:: python

    pipeline = PSFEstimationPipeline(
        max_dist_gaia_arcsec=1.5 * 0.168,
        flag_coadd_boundaries=False,
        psf_measurement_adjustment=linear_adjustment,
    )


    # Run the pipeline
    pipeline.create_psf_model(
        filepath_image=IMAGE_FILE,
        filepath_sexcat=SEXTRACTOR_CAT,
        filepath_sysmaps=SYSMAPS_FILE,
        filepath_gaia=GAIA_FILE,
        filepath_cnn=CNN_MODEL_PATH,
        filepath_out_model=PSF_MODEL_IMPROVED_FILE,
        filepath_out_cat=PSF_CATALOG_IMPROVED_FILE,
    )


.. code:: python

    model = GalSBI("Fischbacher+24")
    model(
        config_file=GALSBI_CONFIG,
        mode="config_file",
        filepath_psfmodel_input_dict = {
            "i": PSF_MODEL_IMPROVED_FILE
        },
        filepath_psfmodel_output_catalog = PSF_CATALOG_IMPROVED_FILE,
        psf_measurement_adjustment=linear_adjustment,
    )


.. code:: python

    psf_measured_improved_sim = at.load_hdf_cols(PSF_CATALOG_IMPROVED_FILE)
    select = psf_measured_improved_sim["psf_fwhm"] != -200
    psf_matched_improved = psf_measured_improved_sim[select]

    print("Maximum difference between simulated and measured PSF parameters:")
    for par in psf_params:
        print(f"{par}")
        max_diff_before = np.max(np.abs(psf_matched[par] - psf_matched[par+'_ipt']))
        print(f"not adjusted: {max_diff_before:.3f}")
        max_diff_after = np.max(np.abs(psf_matched_improved[par] - psf_matched_improved[par+'_ipt']))
        print(f"adjusted: {max_diff_after:.3f}")
        print("-----------------------------")


.. highlight:: none

.. parsed-literal::
    Maximum difference between simulated and measured PSF parameters:
    psf_fwhm
    not adjusted: 0.141
    adjusted: 0.004
    -----------------------------
    psf_flux_ratio
    not adjusted: 0.009
    adjusted: 0.000
    -----------------------------
    psf_e1
    not adjusted: 0.002
    adjusted: 0.000
    -----------------------------
    psf_e2
    not adjusted: 0.004
    adjusted: 0.004
    -----------------------------
    psf_f1
    not adjusted: 0.012
    adjusted: 0.022
    -----------------------------
    psf_f2
    not adjusted: 0.002
    adjusted: 0.014
    -----------------------------
    psf_g1
    not adjusted: 0.004
    adjusted: 0.004
    -----------------------------
    psf_g2
    not adjusted: 0.003
    adjusted: 0.005
    -----------------------------

.. highlight:: default

Fine-Tuning of Background Noise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our first approach to estimate the background noise estimated the
background image from the full real image. Ideally, we should only
estimate the background in the background regions of the image, where there are no
sources. To achieve this, we can use the segmentation map obtained from the real image.
Using this map as a mask, we can refine our background noise estimation by only
considering the background pixels in the real image. This will lead to a more
accurate estimation of the background noise.

.. code:: python

    sigma_clip = SigmaClip(sigma=3)
    bkg_estimator = SExtractorBackground()

    bkg = Background2D(
        real_image,
        128,
        filter_size=(3, 3),
        sigma_clip=sigma_clip,
        bkg_estimator=bkg_estimator,
        mask=segmentation_mask,
    )

    file_utils.robust_copy(
        SYSMAPS_FILE,
        SYSMAPS_IMPROVED_FILE,
        overwrite=True,
    )

    with h5py.File(SYSMAPS_IMPROVED_FILE, "a") as fh5:
        old_map = fh5["map_bsig"][:]
        del fh5["map_bsig"]
        fh5.create_dataset(name="map_bsig", data=bkg.background_rms, compression="lzf")


.. code:: python

    model = GalSBI("Fischbacher+24")
    model(
        config_file=GALSBI_CONFIG,
        mode="config_file",
        filepath_psfmodel_input_dict = {
            "i": PSF_MODEL_IMPROVED_FILE
        },
        filepath_psfmodel_output_catalog = PSF_CATALOG_IMPROVED_FILE,
        psf_measurement_adjustment=linear_adjustment,
        filepath_sysmaps_dict = {
        "i": file_utils.get_abs_path(SYSMAPS_IMPROVED_FILE)
    }
    )


.. code:: python

    images = model.load_images()
    background_values_real = real_image[segmentation_image == 0]
    background_values_sim = images["image i"][images["segmentation i"] == 0]

    # Plot the background values in a histogram
    fig, ax = plt.subplots(figsize=(4, 2))
    _, bins, patches = ax.hist(
        background_values_real,
        bins=1000,
        histtype="step",
        label="real",
    )
    ax.hist(
        background_values_sim,
        bins=bins,
        histtype="step",
        label="sim",
    )
    ax.set_xlabel("Pixel Value")
    ax.legend()
    ax.set_xlim(-0.05, 0.05)

.. image:: output_60_2.png


The estimated background noise assumes uncorrelated noise, however, in
UFig the background noise is resampled using a Lanczos-3 kernel to
account for correlated noise from the coaddition process. This
resampling leads to small differences in the background noise
statistics. To ensure that the simulated background noise matches the
real image, we can fine-tune the background noise parameters based on
the measured background noise from the real image.

.. code:: python

    background_values_real = real_image[~segmentation_mask]
    background_values_sim = images["image i"][images["segmentation i"] == 0]

    std_correction = np.std(background_values_real) / np.std(background_values_sim)

    with h5py.File(SYSMAPS_IMPROVED_FILE, "a") as fh5:
        old_map = fh5["map_bsig"][:]
        del fh5["map_bsig"]
        fh5.create_dataset(name="map_bsig", data=old_map * std_correction, compression="lzf")

.. code:: python

    model = GalSBI("Fischbacher+24")
    model(
        config_file=GALSBI_CONFIG,
        mode="config_file",
        filepath_psfmodel_input_dict = {
            "i": PSF_MODEL_IMPROVED_FILE
        },
        filepath_psfmodel_output_catalog = PSF_CATALOG_IMPROVED_FILE,
        psf_measurement_adjustment=linear_adjustment,
        filepath_sysmaps_dict = {
        "i": file_utils.get_abs_path(SYSMAPS_IMPROVED_FILE)
    }
    )


.. code:: python

    images = model.load_images()
    background_values_real = real_image[~segmentation_mask]
    background_values_sim = images["image i"][images["segmentation i"] == 0]

    fig, ax = plt.subplots(figsize=(4, 2))
    _, bins, patches = ax.hist(
        background_values_real,
        bins=1000,
        histtype="step",
        label="real",
    )
    ax.hist(
        background_values_sim,
        bins=bins,
        histtype="step",
        label="sim",
    )
    ax.set_xlabel("Pixel Value")
    ax.legend()
    ax.set_xlim(-0.05, 0.05)


.. image:: output_64_2.png


Credits & References
--------------------

The HSC image simulations were mainly developed by Beatrice Moser and
first used in `Moser+2024 <http://arxiv.org/abs/2401.06846>`__. This
tutorial was written by Silvan Fischbacher, for questions or comments,
contact via email at silvanf@phys.ethz.ch
