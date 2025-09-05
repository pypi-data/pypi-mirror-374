import os

import h5py
import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger

from ufig import mask_utils
from ufig.psf_estimation import correct_brighter_fatter

LOGGER = logger.get_logger(__file__)

ERR_VAL = 999


def transform_forward(vec, scale):
    vec_transformed = (vec - scale[:, 0]) / scale[:, 1]
    return vec_transformed


def transform_inverse(vec_transformed, scale):
    vec = vec_transformed * scale[:, 1] + scale[:, 0]
    return vec


def position_weights_to_nexp(position_weights):
    """
    Transform position weights to number of exposures.
    """
    n_exp = np.sum(position_weights > 0, axis=1).astype(np.uint16)
    return n_exp


def postprocess_catalog(cat):
    """
    Post-process the catalog after PSF prediction.
    This function ensures that the PSF flux ratio is within valid bounds.

    :param cat: Input catalog with PSF parameters.
    :return: None, modifies the catalog in place.
    """
    if "psf_flux_ratio_cnn" in cat.dtype.names:
        cat["psf_flux_ratio_cnn"] = np.clip(
            cat["psf_flux_ratio_cnn"], a_min=0.0, a_max=1.0
        )


def get_position_weights(x, y, pointings_maps):
    """
    Get the position weights for each star based on the number of exposures
    at each pixel location.

    :param x: x-coordinates of stars
    :param y: y-coordinates of stars
    :param pointings_maps: bitmaps indicating exposure coverage
    :return: position weights for each star
    """
    size_y, size_x = pointings_maps.shape

    x_noedge = x.astype(np.int32)
    y_noedge = y.astype(np.int32)
    x_noedge[x_noedge >= size_x] = size_x - 1
    y_noedge[y_noedge >= size_y] = size_y - 1
    x_noedge[x_noedge < 0] = 0
    y_noedge[y_noedge < 0] = 0

    n_pointings = pointings_maps.attrs["n_pointings"]

    n_bit = 64

    position_weights = mask_utils.decimal_integer_to_binary(
        n_bit, pointings_maps["bit1"][y_noedge, x_noedge], dtype_out=np.float64
    )

    for n in range(2, 6):
        n_pointings -= 64
        if n_pointings > 0:
            position_weights = np.concatenate(
                (
                    position_weights,
                    mask_utils.decimal_integer_to_binary(
                        n_bit,
                        pointings_maps[f"bit{str(n)}"][y_noedge, x_noedge],
                        dtype_out=np.float64,
                    ),
                ),
                axis=1,
                dtype=np.float64,
            )
        else:
            break

    norm = np.sum(np.array(position_weights), axis=1, keepdims=True)
    position_weights /= norm
    position_weights[norm[:, 0] == 0] = 0

    return position_weights


def get_star_cube_filename(filepath_cat_out):
    root, ext = os.path.splitext(filepath_cat_out)
    filename_cube = root + "_starcube.h5"
    return filename_cube


def write_star_cube(star_cube, cat, filepath_cat_out):
    filename_cube = get_star_cube_filename(filepath_cat_out)
    with h5py.File(filename_cube, "w") as fh5:
        fh5.create_dataset(
            name="star_cube", data=at.set_storing_dtypes(star_cube), compression="lzf"
        )
        fh5.create_dataset(
            name="cat", data=at.set_storing_dtypes(cat), compression="lzf"
        )
    LOGGER.info(
        f"created star cube file {filename_cube} with {len(cat)} stars, "
        f"size {star_cube.nbytes / 1024**2:.2f} MB"
    )


def apply_brighter_fatter_correction(cat_cnn, psfmodel_corr_brighter_fatter):
    """
    Apply Brighter-Fatter correction to the PSF parameters in the catalog.
    """

    mean_size_before = np.mean(cat_cnn["psf_fwhm_cnn"])
    mean_e1_before = np.mean(cat_cnn["psf_e1_cnn"])
    mean_e2_before = np.mean(cat_cnn["psf_e2_cnn"])

    (
        cat_cnn["psf_fwhm_cnn"],
        cat_cnn["psf_e1_cnn"],
        cat_cnn["psf_e2_cnn"],
    ) = correct_brighter_fatter.brighter_fatter_remove(
        col_mag=cat_cnn["MAG_AUTO"],
        col_fwhm=cat_cnn["psf_fwhm_cnn"],
        col_e1=cat_cnn["psf_e1_cnn"],
        col_e2=cat_cnn["psf_e2_cnn"],
        dict_corr=psfmodel_corr_brighter_fatter,
    )

    mean_size_after = np.mean(cat_cnn["psf_fwhm_cnn"])
    mean_e1_after = np.mean(cat_cnn["psf_e1_cnn"])
    mean_e2_after = np.mean(cat_cnn["psf_e2_cnn"])
    LOGGER.info(
        f"applied brighter-fatter correction, difference in mean "
        f"fwhm={mean_size_after - mean_size_before:2.5f} "
        f"e1={mean_e1_after - mean_e1_before:2.5f} "
        f"e2={mean_e2_after - mean_e2_before:2.5f}"
    )


def adjust_psf_measurements(cat, psf_measurement_adjustment=None):
    """
    Adjust PSF measurements based on provided adjustment parameters.

    :param cat: Input catalog with PSF parameters.
    :param psf_measurement_adjustment: Dictionary with adjustment parameters
                                      for each PSF measurement.
    """

    if psf_measurement_adjustment is None:
        LOGGER.info("NO PSF parameter adjustment")

    else:
        adjust = lambda x, a: x * a[1] + a[0]  # noqa: E731
        for c in psf_measurement_adjustment:
            c_cat = c + "_cnn" if c not in cat.dtype.names else c
            col_adj = adjust(cat[c_cat], psf_measurement_adjustment[c])
            LOGGER.warning(
                f"PSF parameter adjustment {c}: mean frac diff after "
                f"adjustment: {np.mean((col_adj-cat[c_cat]) / cat[c_cat]):2.4f}"
            )
            cat[c_cat] = col_adj


class PSFEstError(ValueError):
    """
    Raised when too few stars for PSF estimation were found.
    """


def write_empty_output(filepath_out, filepath_cat_out=None, save_star_cube=False):
    """
    Creates empty output files when PSF estimation fails.

    This function creates placeholder files to ensure that even when
    PSF estimation fails, the expected output files exist, preventing
    downstream processes from failing due to missing files.

    Parameters
    ----------
    filepath_out : str
        Path to the main PSF model output file
    filepath_cat_out : str, optional
        Path to the catalog output file
    save_star_cube : bool, optional
        Whether a star cube file was expected
    """
    LOGGER.warning("Creating empty output files for failed PSF estimation")

    # Create empty main PSF model file
    write_empty_file(filepath_out)

    # Create empty catalog output if requested
    if filepath_cat_out is not None:
        write_empty_file(filepath_cat_out)

        # Create empty star cube if requested
        if save_star_cube:
            star_cube_path = get_star_cube_filename(filepath_cat_out)
            write_empty_file(star_cube_path)

    LOGGER.info("Created empty output files")


def write_empty_file(path):
    with h5py.File(path, mode="w"):
        pass


def select_validation_stars(n_stars, fraction_validation):
    """
    Select validation stars for PSF model testing.

    :param n_stars: Total number of stars in the catalog.
    :param fraction_validation: Fraction of stars to select for validation.
    :return: Array of indices for validation stars.
    """
    n_validation = int(n_stars * fraction_validation)
    if n_validation == 0:
        return np.array([], dtype=int)

    # Use deterministic selection based on star indices
    # This ensures reproducible validation star selection
    np.random.seed(42)  # Fixed seed for reproducibility
    indices = np.random.choice(n_stars, size=n_validation, replace=False)

    return indices
