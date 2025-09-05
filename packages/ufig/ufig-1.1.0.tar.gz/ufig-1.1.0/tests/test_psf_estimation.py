# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Mon Jul 28 2025

import os

import h5py
import ivy
import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS
from cosmic_toolbox import arraytools as at
from cosmo_torrent import data_path

from ufig import coordinate_util
from ufig.plugins import (
    add_psf,
    estimate_psf,
    render_stars_photon,
    single_band_setup,
    write_image,
)
from ufig.psf_estimation import PSFEstimationPipeline
from ufig.psf_estimation.star_sample_selection_cnn import (
    beta_cut,
    cut_nearby_bright_star,
    cut_sextractor_flag,
    cut_sysmaps_delta_weight,
    cut_sysmaps_survey_mask,
    kurtosis_cut,
    select_cnn_predictions,
)


class TestPSFEstimation:
    """Test suite for PSF estimation pipeline."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and cleanup test files."""
        self.test_files = [
            "synthetic_image.fits",
            "synthetic_sexcat.cat",
            "synthetic_sysmaps.hdf5",
            "synthetic_gaia.hdf5",
            "psf_model.hdf5",
            "psf_catalog.hdf5",
            "psf_catalog_starcube.h5",
        ]
        yield
        # Cleanup files after each test
        for file in self.test_files:
            if os.path.exists(file):
                os.remove(file)

    def create_synthetic_image(self, size_x=100, size_y=100, seeing=1.0, num_stars=8):
        """
        Create a synthetic image with stars for testing.

        :param size_x: Width of the synthetic image
        :param size_y: Height of the synthetic image
        :param seeing: Simulated seeing in arcseconds
        :param num_stars: Number of stars to simulate
        :return: Ivy context with synthetic image and star positions
        """
        ctx = ivy.context.create_ctx(parameters=ivy.load_configs("ufig.config.common"))

        ctx.parameters.catalog_precision = np.float32
        ctx.parameters.size_x = size_x
        ctx.parameters.size_y = size_y
        ctx.parameters.image_name = "synthetic_image.fits"
        ctx.parameters.seeing = seeing

        ctx.numstars = num_stars
        ctx.stars = ivy.context.create_ctx(
            x=np.array([10, 20, 30, 60, 70, 80, 40, 80][:num_stars]),
            y=np.array([30, 80, 20, 50, 90, 40, 60, 10][:num_stars]),
            magnitude_dict={
                "i": np.array([20, 21, 22, 23, 20, 21, 19, 21][:num_stars])
            },
        )
        ctx.stars.columns = ["id", "x", "y"]

        ctx.image = np.zeros((ctx.parameters.size_x, ctx.parameters.size_y))
        ctx.current_filter = "i"

        # Run plugins to generate image
        single_band_setup.Plugin(ctx)()
        add_psf.Plugin(ctx)()
        render_stars_photon.Plugin(ctx)()
        write_image.Plugin(ctx)()

        return ctx

    def create_test_catalogs(self, ctx):
        """
        Create synthetic catalogs for testing.

        :param ctx: Ivy context with synthetic image and star positions
        """
        # Create SExtractor catalog (from a SEXTRACTOR run on the synthetic image)
        sexcat = {
            "NUMBER": [1, 2, 3, 4, 5, 6, 7, 8],
            "X_IMAGE": [
                80.511024,
                40.503445,
                60.442375,
                10.517624,
                30.487467,
                80.512146,
                20.508577,
                70.48919,
            ],
            "Y_IMAGE": [
                40.520382,
                60.488033,
                50.46702,
                30.493134,
                20.49973,
                10.512237,
                80.48308,
                90.50451,
            ],
            "XWIN_IMAGE": [
                80.51019177,
                40.49721633,
                60.55269756,
                10.49794416,
                30.53501923,
                80.48006705,
                20.49135413,
                70.49460378,
            ],
            "YWIN_IMAGE": [
                40.51825919,
                60.50517469,
                50.51351894,
                30.50165754,
                20.45452863,
                10.51777039,
                80.50026021,
                90.51103971,
            ],
            "ALPHAWIN_J2000": [
                70.45672652,
                70.46080707,
                70.45876182,
                70.46386652,
                70.46182311,
                70.45672947,
                70.46284718,
                70.45774805,
            ],
            "DELTAWIN_J2000": [
                -44.24517318,
                -44.24371306,
                -44.24444301,
                -44.24590492,
                -44.24663897,
                -44.24736488,
                -44.24225227,
                -44.24152095,
            ],
            "MAG_AUTO": [
                19.426374,
                17.424456,
                21.417593,
                18.424326,
                20.41722,
                19.42667,
                19.425726,
                18.423843,
            ],
            "MAGERR_AUTO": [
                0.00155443,
                0.00060554,
                0.00433898,
                0.00096558,
                0.00253206,
                0.00155435,
                0.0015538,
                0.0009652,
            ],
            "FLUX_RADIUS": [
                2.3417478,
                2.325822,
                2.3028274,
                2.3441384,
                2.296018,
                2.3224921,
                2.3198848,
                2.3249793,
            ],
            "XPEAK_IMAGE": [81, 40, 61, 10, 31, 80, 20, 70],
            "YPEAK_IMAGE": [41, 61, 51, 30, 20, 11, 80, 91],
            "X2WIN_IMAGE": [
                1.8685312,
                1.83775652,
                1.77885361,
                1.86673641,
                1.80695597,
                1.80841575,
                1.81432826,
                1.83295269,
            ],
            "Y2WIN_IMAGE": [
                1.81029991,
                1.81358033,
                1.71893156,
                1.83215693,
                1.76005881,
                1.80348027,
                1.80719208,
                1.80156869,
            ],
            "XYWIN_IMAGE": [
                0.00119543,
                0.01166632,
                0.01194275,
                0.00610766,
                -0.01153156,
                0.02906991,
                0.01566321,
                0.00705964,
            ],
            "FLAGS": [0, 16, 2, 0, 0, 0, 1, 0],
            "FLAGS_STAMP": [0, 1, 2, 4, 0, 0, 0, 0],
        }
        sexcat = at.dict2rec(sexcat)
        at.save_hdf_cols("synthetic_sexcat.cat", sexcat)

        # Create system maps
        map_pointings = np.zeros(
            (ctx.parameters.size_y, ctx.parameters.size_x),
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
        map_pointings["bit1"] = 1
        with h5py.File("synthetic_sysmaps.hdf5", "w") as fh5:
            fh5.create_dataset("map_pointings", data=map_pointings, compression="lzf")
            fh5["map_pointings"].attrs["n_pointings"] = 1

        # Create Gaia catalog
        header = fits.getheader("synthetic_image.fits")
        w = WCS(header)
        ra, dec = coordinate_util.xy2radec(w=w, x=ctx.stars.x, y=ctx.stars.y)

        gaia_data = {
            "ra": ra,
            "dec": dec,
            "phot_g_mean_mag": ctx.stars.magnitude_dict["i"],
            "id": np.arange(1, ctx.numstars + 1),
        }
        gaia_data = at.dict2rec(gaia_data)
        at.save_hdf("synthetic_gaia.hdf5", gaia_data)

    def run_psf_estimation_test(
        self, image_kwargs=None, pipeline_kwargs=None, expected_flagged_count=2
    ):
        if image_kwargs is None:
            image_kwargs = {}
        if pipeline_kwargs is None:
            pipeline_kwargs = {}
        # Create synthetic image and catalogs
        ctx = self.create_synthetic_image(**image_kwargs)
        self.create_test_catalogs(ctx)

        # Get CNN model path
        cnn_model_path = os.path.join(data_path("psf_cnn"), "pretrained")

        # Create and run pipeline
        pipeline = PSFEstimationPipeline(
            max_dist_gaia_arcsec=1.5 * 0.168, save_star_cube=True, **pipeline_kwargs
        )
        pipeline.create_psf_model(
            filepath_image="synthetic_image.fits",
            filepath_sexcat="synthetic_sexcat.cat",
            filepath_sysmaps="synthetic_sysmaps.hdf5",
            filepath_gaia="synthetic_gaia.hdf5",
            filepath_cnn=cnn_model_path,
            filepath_out_model="psf_model.hdf5",
            filepath_out_cat="psf_catalog.hdf5",
        )
        return self._basic_checks(ctx, expected_flagged_count)

    def _basic_checks(self, ctx, expected_flagged_count):
        # Load and check results
        cat = at.load_hdf_cols("psf_catalog.hdf5")
        gaia_flagged = cat["psf_fwhm_cnn"] == 999

        # Assert expected number of flagged stars
        assert (
            sum(gaia_flagged) == expected_flagged_count
        ), f"Expected {expected_flagged_count} flagged stars, got {sum(gaia_flagged)}"

        # Check interpolation consistency
        psf_params = [
            "psf_fwhm",
            "psf_flux_ratio",
            "psf_e1",
            "psf_e2",
            "psf_f1",
            "psf_f2",
            "psf_g1",
            "psf_g2",
        ]
        for param in psf_params:
            assert np.allclose(
                cat[f"{param}_cnn"][~gaia_flagged],
                cat[f"{param}_ipt"][~gaia_flagged],
                atol=3e-1,
            ), f"Interpolation inconsistent for parameter {param}"

        # Check FWHM consistency with input seeing
        expected_psf_fwhm = ctx.parameters.seeing / ctx.parameters.pixscale
        assert np.allclose(
            cat["psf_fwhm_ipt"], expected_psf_fwhm, atol=3e-1
        ), "PSF FWHM not consistent with input seeing"

        return cat, ctx

    @pytest.mark.parametrize(
        "image_kwargs,pipeline_kwargs,expected_flagged",
        [
            # Test 1: Default settings - most restrictive flags
            ({}, {}, 4),
            # Test 2: Allow more SExtractor flags
            ({}, {"sextractor_flags": [0, 1, 2, 16]}, 2),
            # Test 3: Add magnitude range restriction
            (
                {},
                {
                    "star_mag_range": (19.5, 22.5),
                    "sextractor_flags": [0, 1, 2, 16],
                },
                6,
            ),
            # Test 4: 40 % validation stars
            (
                {},
                {
                    "fraction_validation_stars": 0.2,
                    "sextractor_flags": [0, 1, 2, 16],
                    "star_mag_range": (10, 30),
                },
                1,
            ),
            # Test 5: different seeing
            ({"seeing": 0.5}, {"precision": np.float32}, 4),
            # Test 6: astrometry errors
            ({}, {"astrometry_errors": True}, 4),
            # Test 7: add brighter-fatter correction
            (
                {},
                {
                    "psfmodel_corr_brighter_fatter": {
                        "c1r": 0.1,
                        "c1e1": 0.1,
                        "c1e2": 0.1,
                        "mag_ref": 22,
                        "apply_to_galaxies": True,
                    }
                },
                4,
            ),
        ],
    )
    def test_psf_estimation_pipeline(
        self, image_kwargs, pipeline_kwargs, expected_flagged
    ):
        """Test PSF estimation pipeline with different configurations."""
        self.run_psf_estimation_test(image_kwargs, pipeline_kwargs, expected_flagged)

    def test_empty_output(self):
        pipeline_kwargs = {"star_mag_range": [5, 6]}
        # no stars, no fitting
        with pytest.raises(ValueError):
            self.run_psf_estimation_test(pipeline_kwargs=pipeline_kwargs)

    def test_plugin(self):
        ctx = self.create_synthetic_image()
        self.create_test_catalogs(ctx)
        ctx.parameters.sextractor_forced_photo_catalog_name = "synthetic_sexcat.cat"
        ctx.parameters.filepath_cnn = os.path.join(data_path("psf_cnn"), "pretrained")
        ctx.parameters.filepath_gaia = "synthetic_gaia.hdf5"
        ctx.parameters.filepath_sysmaps = "synthetic_sysmaps.hdf5"
        ctx.parameters.filepath_psfmodel_output = "psf_model.hdf5"
        ctx.parameters.filepath_psfmodel_output_catalog = "psf_catalog.hdf5"
        plugin = estimate_psf.Plugin(ctx)
        plugin()

    def test_different_n_pointings(self):
        ctx = self.create_synthetic_image()
        self.create_test_catalogs(ctx)

        # Create system maps
        map_pointings = np.zeros(
            (ctx.parameters.size_y, ctx.parameters.size_x),
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
        # We want to test if the pipeline can handle to correctly use the bit maps > 1
        # For this, we need at least 65 individual pointings, let's assume they are all
        # covering the full area
        for i in range(65):
            bit = i // 64 + 1
            map_pointings[f"bit{bit}"] += 2 ** (i % 64)
        with h5py.File("synthetic_sysmaps.hdf5", "w") as fh5:
            fh5.create_dataset("map_pointings", data=map_pointings, compression="lzf")
            fh5["map_pointings"].attrs["n_pointings"] = 65

        # Get CNN model path
        cnn_model_path = os.path.join(data_path("psf_cnn"), "pretrained")

        # Create and run pipeline
        pipeline = PSFEstimationPipeline(
            max_dist_gaia_arcsec=1.5 * 0.168,
        )
        pipeline.create_psf_model(
            filepath_image="synthetic_image.fits",
            filepath_sexcat="synthetic_sexcat.cat",
            filepath_sysmaps="synthetic_sysmaps.hdf5",
            filepath_gaia="synthetic_gaia.hdf5",
            filepath_cnn=cnn_model_path,
            filepath_out_model="psf_model.hdf5",
            filepath_out_cat="psf_catalog.hdf5",
        )
        self._basic_checks(ctx, expected_flagged_count=4)

    def test_adjust_psf_measurement(self):
        """
        Test the adjustment of PSF measurements.
        """
        ctx = self.create_synthetic_image()
        self.create_test_catalogs(ctx)

        # Get CNN model path
        cnn_model_path = os.path.join(data_path("psf_cnn"), "pretrained")

        expected_fwhm = ctx.parameters.seeing / ctx.parameters.pixscale

        # Create and run pipeline
        pipeline = PSFEstimationPipeline(
            max_dist_gaia_arcsec=1.5 * 0.168,
            psf_measurement_adjustment={"psf_fwhm": [expected_fwhm + 1, 1e-2]},
        )
        pipeline.create_psf_model(
            filepath_image="synthetic_image.fits",
            filepath_sexcat="synthetic_sexcat.cat",
            filepath_sysmaps="synthetic_sysmaps.hdf5",
            filepath_gaia="synthetic_gaia.hdf5",
            filepath_cnn=cnn_model_path,
            filepath_out_model="psf_model.hdf5",
            filepath_out_cat="psf_catalog.hdf5",
        )

        cat = at.load_hdf_cols("psf_catalog.hdf5")

        assert np.allclose(
            cat["psf_fwhm_ipt"][~(cat["psf_fwhm_cnn"] == 999)],
            expected_fwhm + 1 + expected_fwhm * 1e-2,
            atol=1e-1,
        ), "PSF FWHM adjustment not applied correctly"


def test_cuts_not_used_by_current_cnn():
    """
    Tests the cuts that are not used by the current CNN.
    """
    beta = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = beta_cut(beta, beta_lim=(1.5, 10))
    assert isinstance(result, np.ndarray), "beta_cut should return a numpy array"
    assert len(result) == len(beta), "Output length should match input length"
    assert np.sum(result) == 4, "Expected 4 stars to pass the beta cut"

    kurtosis = np.array([-1.5, -0.5, 0.5, 1.5, 2.5])
    result = kurtosis_cut(kurtosis, kurtosis_lim=(-1, 1))
    assert isinstance(result, np.ndarray), "kurtosis_cut should return a numpy array"
    assert len(result) == len(kurtosis), "Output length should match input length"
    assert np.sum(result) == 2, "Expected 2 stars to pass the kurtosis cut"


def test_cnn_params():
    psf_cat = {
        "psf_beta_1_cnn": np.array([1.0, 2.0, 3.0, 4.0]),
        "psf_beta_2_cnn": np.array([2.0, 3.0, 4.0, 5.0]),
        "psf_fwhm_cnn": np.array([1.5, 2.0, 3.0, 4.0]),
        "psf_e1_cnn": np.array([0.1, 0.2, 0.3, -0.1]),
        "psf_e2_cnn": np.array([0.1, 0.2, 0.3, -0.1]),
        "psf_f1_cnn": np.array([0.1, 0.2, 0.3, -0.1]),
        "psf_f2_cnn": np.array([0.1, 0.2, 0.3, -0.1]),
        "psf_g1_cnn": np.array([0.1, 0.2, 0.3, -0.1]),
        "psf_g2_cnn": np.array([0.1, 0.2, 0.3, -0.1]),
        "psf_kurtosis_cnn": np.array([0.1, 0.2, 0.3, -2]),
    }
    psf_cat = at.dict2rec(psf_cat)

    flags = select_cnn_predictions(np.zeros(len(psf_cat), dtype=int), psf_cat)
    assert np.all(
        flags == np.array([2**9, 0, 2**11 + 2**12, 2**13]).astype(int)
    ), "Flags should match expected values for CNN parameters"


def test_sextractor_flags():
    """
    Test the SExtractor flags handling in PSF estimation.
    """

    cat = {"FLAGS": np.arange(10)}
    cat = at.dict2rec(cat)

    flags = cut_sextractor_flag(cat, flags=None)
    assert np.all(flags), "All SExtractor flags should be selected"

    flags = cut_sextractor_flag(cat, flags=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9))
    assert np.all(flags), "Selected SExtractor flags should be selected"

    flags = cut_sextractor_flag(cat, flags=np.array([0, 1]))
    assert np.all(flags[:2]), "The first two SExtractor flags should be selected"
    assert np.all(~flags[2:]), "The rest of the SExtractor flags should be rejected"

    flags = cut_sextractor_flag(cat, flags=0)
    assert flags[0], "Only the first SExtractor flag should be selected"
    assert np.all(~flags[1:]), "All other SExtractor flags should be rejected"

    with pytest.raises(ValueError):
        cut_sextractor_flag(cat, flags="only good stars, please")


def test_FLAGS_STAMP():
    """
    Test the FLAGS_STAMP handling in PSF estimation.

    FLAGBIT are defined as follows:
    - FLAGBIT_SYSMAP_DELTA_WEIGHT: 4
    - FLAGBIT_NEARBY_BRIGHT_STAR: 5
    - FLAGBIT_SURVEY_MASK: 6
    """
    cat = {"FLAGS_STAMP": np.array([2**4, 2**5, 2**6, 2**4 + 2**5]).astype(np.uint32)}
    cat = at.dict2rec(cat)

    flags = cut_sysmaps_delta_weight(cat)
    assert np.all(
        flags == np.array([False, True, True, False])
    ), "Expected only the second and third entries to pass the delta weight cut"

    flags = cut_nearby_bright_star(cat)
    assert np.all(
        flags == np.array([True, False, True, False])
    ), "Expected only the first and third entries to pass the nearby bright star cut"

    flags = cut_sysmaps_survey_mask(cat)
    assert np.all(
        flags == np.array([True, True, False, True])
    ), "Expected only the first, second and fourth entries to pass the survey mask cut"

    # no FLAGS_STAMP, so all should pass
    cat = {"FLAGS": np.array([2**4, 2**5, 2**6, 2**4 + 2**5]).astype(np.uint32)}
    cat = at.dict2rec(cat)

    flags = cut_sysmaps_delta_weight(cat)
    assert np.all(flags), "all entries should pass without FLAGS_STAMP"
    flags = cut_nearby_bright_star(cat)
    assert np.all(flags), "all entries should pass without FLAGS_STAMP"
    flags = cut_sysmaps_survey_mask(cat)
    assert np.all(flags), "all entries should pass without FLAGS_STAMP"


def test_wrong_pipeline_input():
    with pytest.raises(ValueError):
        PSFEstimationPipeline(psfmodel_corr_brighter_fatter=True)
    with pytest.raises(ValueError):
        PSFEstimationPipeline(psfmodel_ridge_alpha=True)
