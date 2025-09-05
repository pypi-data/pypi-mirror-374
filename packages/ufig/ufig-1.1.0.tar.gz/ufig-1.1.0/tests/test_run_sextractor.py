# Copyright (C) 2014 ETH Zurich, Institute for Astronomy

"""
Created on Jun 11, 2014

author: jakeret
adapted by Silvan Fischbacher, 2024
"""

import os
from unittest.mock import patch

import h5py
import numpy as np
import pytest
from astropy.io import fits
from cosmic_toolbox import arraytools as at
from ivy import context, workflow_manager
from pkg_resources import resource_filename

import ufig
from ufig.plugins import run_sextractor, run_sextractor_forced_photometry


class TestRunSextratorPlugin:
    plugin = None

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ctx = context.create_ctx()
        self.ctx.parameters = workflow_manager.load_configs("ufig.config.common")
        self.plugin = run_sextractor.Plugin(self.ctx)

    def test_run_use_temp(
        self,
    ):
        with patch("ufig.io_util.get_abs_path") as abs_path_mock:
            abs_path_mock.return_value = "dummy_path"

            with patch("subprocess.check_call") as command_mock:
                command_mock.return_value = (0, None, None)
                catalog_name = self.ctx.parameters.sextractor_catalog_name

                self.ctx.parameters.sextractor_use_temp = True
                self.plugin()
                assert catalog_name != self.ctx.parameters.sextractor_catalog_name


def test_cmd_gen():
    conf_dir = resource_filename(ufig.__name__, "res/sextractor/")
    maps_dir = "ufig_res/maps/"

    ctx = context.create_ctx()

    # The values don't matter as nothing is executed, most of them just need to be
    # different than what is set
    ctx.parameters = context.create_ctx(
        sextractor_binary="asdf",
        image_name="brrr.fits",
        sextractor_config="brrr.sex",
        seeing=0.8362,
        pixscale=0.31,
        saturation_level=23210.0231,
        magzero=29.5687,
        gain=3.896,
        sextractor_nnw="brrr.nnw",
        sextractor_filter="fourier_3.5_6x6.conv",
        sextractor_params="brrr.param",
        sextractor_catalog_name="poiu.sexcat",
        sextractor_checkimages=[],
        sextractor_checkimages_suffixes=[],
        maps_remote_dir="ufig_res/maps/",
        weight_image="tile_sys/DES0441-4414_r_invvar.fits",
        filepath_weight_fits="tile_sys/DES0441-4414_r_invvar.fits",
        weight_type="NONE",
        weight_gain="Y",
        n_exp=2,
    )

    par = ctx.parameters

    cmd_ref = (
        "asdf brrr.fits -c "
        + conf_dir
        + "brrr.sex -SEEING_FWHM 0.8362 -SATUR_KEY NONE -SATUR_LEVEL "
        "23210.0231 -MAG_ZEROPOINT 29.5687 -GAIN_KEY NONE -GAIN"
        " 7.792 -PIXEL_SCALE 0.31 -STARNNW_NAME "
        + conf_dir
        + "brrr.nnw -FILTER_NAME "
        + conf_dir
        + "fourier_3.5_6x6.conv -PARAMETERS_NAME "
        + conf_dir
        + "brrr.param -CATALOG_NAME poiu.sexcat -CHECKIMAGE_TYPE NONE"
        " -CHECKIMAGE_NAME NONE -CATALOG_TYPE "
        "FITS_LDAC -VERBOSE_TYPE QUIET"
    )

    cmd = run_sextractor.get_sextractor_cmd(ctx)[0]
    cmd = " ".join(cmd)
    assert cmd == cmd_ref

    par.sextractor_checkimages = ["APERTURES", "BACKGROUND"]
    par.sextractor_checkimages_suffixes = ["_apert.fits", "_background.fits"]
    par.weight_type = "MAP_WEIGHT"

    cmd_ref = (
        "asdf brrr.fits -c "
        + conf_dir
        + "brrr.sex -SEEING_FWHM 0.8362 -SATUR_KEY NONE -SATUR_LEVEL "
        "23210.0231 -MAG_ZEROPOINT 29.5687 -GAIN_KEY NONE -GAIN 7.792"
        " -PIXEL_SCALE 0.31 -STARNNW_NAME "
        + conf_dir
        + "brrr.nnw -FILTER_NAME "
        + conf_dir
        + "fourier_3.5_6x6.conv -PARAMETERS_NAME "
        + conf_dir
        + "brrr.param -CATALOG_NAME poiu.sexcat -CHECKIMAGE_TYPE APERTURES,BACKGROUND"
        " -CHECKIMAGE_NAME "
        "poiu_apert.fits,poiu_background.fits -CATALOG_TYPE FITS_LDAC"
        " -VERBOSE_TYPE QUIET -WEIGHT_IMAGE "
        + maps_dir
        + "tile_sys/DES0441-4414_r_invvar.fits -WEIGHT_TYPE MAP_WEIGHT -WEIGHT_GAIN Y"
    )

    with patch("ufig.io_util.get_abs_path") as abs_path_mock:
        abs_path_mock.return_value = "ufig_res/maps/" + par.weight_image
        cmd = run_sextractor.get_sextractor_cmd(ctx)[0]

    cmd = " ".join(cmd)
    assert cmd == cmd_ref


def test_cmd_gen_forced_photo():
    binary_name = "sex"
    image_name = ("image_ref.fits", "image.fits")
    config_name = "hsc_deblend_aper.config"
    kwargs = {
        "seeing_fwhm": 0.5390596195068957,
        "satur_key": "NONE",
        "satur_level": 233.78025817871094,
        "mag_zeropoint": 27.0,
        "gain_key": "NONE",
        "gain": 53.576499938964844,
        "pixel_scale": 0.168,
        "starnnw_name": "default.nnw",
        "filter_name": "gauss_3.0_5x5.conv",
        "parameters_name": "newdefault.param",
        "catalog_name": "cat.cat",
        "checkimage_type": "SEGMENTATION,BACKGROUND",
        "checkimage_name": "seg.fits,bkg.fits",
        "weight_type": "NONE,NONE",
        "weight_gain": "N,N",
        "catalog_type": "FITS_LDAC",
        "verbose_type": "QUIET",
    }
    ufig_path = ufig.__path__[0]
    cmd_ref = [
        "sex",
        "image_ref.fits,image.fits",
        "-c",
        os.path.join(ufig_path, "res/sextractor/hsc_deblend_aper.config"),
        "-SEEING_FWHM",
        "0.5390596195068957",
        "-SATUR_KEY",
        "NONE",
        "-SATUR_LEVEL",
        "233.78025817871094",
        "-MAG_ZEROPOINT",
        "27.0",
        "-GAIN_KEY",
        "NONE",
        "-GAIN",
        "53.576499938964844",
        "-PIXEL_SCALE",
        "0.168",
        "-STARNNW_NAME",
        os.path.join(ufig_path, "res/sextractor/default.nnw"),
        "-FILTER_NAME",
        os.path.join(ufig_path, "res/sextractor/gauss_3.0_5x5.conv"),
        "-PARAMETERS_NAME",
        os.path.join(ufig_path, "res/sextractor/newdefault.param"),
        "-CATALOG_NAME",
        "cat.cat",
        "-CHECKIMAGE_TYPE",
        "SEGMENTATION,BACKGROUND",
        "-CHECKIMAGE_NAME",
        "seg.fits,bkg.fits",
        "-WEIGHT_TYPE",
        "NONE,NONE",
        "-WEIGHT_GAIN",
        "N,N",
        "-CATALOG_TYPE",
        "FITS_LDAC",
        "-VERBOSE_TYPE",
        "QUIET",
    ]

    cmd = run_sextractor_forced_photometry.build_sextractor_cmd(
        binary_name, image_name, config_name, **kwargs
    )
    assert cmd == cmd_ref


def create_fits_image():
    dtype = np.dtype(
        [
            ("NUMBER", ">i4"),
            ("FLAGS", ">i2"),
            ("X_IMAGE", ">f4"),
            ("Y_IMAGE", ">f4"),
            ("XWIN_IMAGE", ">f8"),
            ("YWIN_IMAGE", ">f8"),
            ("ALPHAWIN_J2000", ">f8"),
            ("DELTAWIN_J2000", ">f8"),
            ("FLUX_AUTO", ">f4"),
            ("FLUXERR_AUTO", ">f4"),
            ("MAG_AUTO", ">f4"),
            ("MAGERR_AUTO", ">f4"),
            ("FLUX_APER", ">f4", (2,)),
            ("FLUXERR_APER", ">f4", (2,)),
            ("MAG_APER", ">f4", (2,)),
            ("MAGERR_APER", ">f4", (2,)),
            ("FLUX_RADIUS", ">f4"),
            ("FWHM_IMAGE", ">f4"),
            ("XMIN_IMAGE", ">i4"),
            ("YMIN_IMAGE", ">i4"),
            ("XMAX_IMAGE", ">i4"),
            ("YMAX_IMAGE", ">i4"),
            ("XPEAK_IMAGE", ">i4"),
            ("YPEAK_IMAGE", ">i4"),
            ("MU_MAX", ">f4"),
            ("A_IMAGE", ">f4"),
            ("B_IMAGE", ">f4"),
            ("THETA_IMAGE", ">f4"),
            ("ELLIPTICITY", ">f4"),
            ("CLASS_STAR", ">f4"),
            ("X2WIN_IMAGE", ">f8"),
            ("Y2WIN_IMAGE", ">f8"),
            ("XYWIN_IMAGE", ">f8"),
            ("BACKGROUND", ">f4"),
            ("THRESHOLD", ">f4"),
        ]
    )

    data = np.array(
        [
            (
                1,
                3,
                3274.1848,
                430.72128,
                3274.12878836,
                430.75856363,
                34.15981685,
                -5.65783091,
                3445.0496,
                5.9862194,
                18.157011,
                0.00188707,
                [676.6187, 1123.738],
                [2.4095569, 3.1152046],
                [19.92414, 19.373337],
                [0.00386743, 0.00301059],
                13.740291,
                14.83932,
                3191,
                270,
                3426,
                551,
                3274,
                431,
                20.593039,
                16.911448,
                11.332142,
                -36.64408,
                0.32991296,
                0.02863255,
                56.38672115,
                51.01921889,
                -9.0255028,
                0.00614746,
                0.04557959,
            ),
            (
                2,
                2,
                2815.7488,
                320.31265,
                2815.72904852,
                320.44891172,
                34.1813126,
                -5.66298,
                316.18942,
                2.127418,
                20.750132,
                0.00730694,
                [115.91615, 171.22998],
                [1.0398678, 1.2953492],
                [21.83964, 21.41605],
                [0.00974236, 0.00821555],
                8.204077,
                14.803906,
                2773,
                227,
                2855,
                361,
                2816,
                321,
                22.18677,
                11.530312,
                4.137183,
                89.3095,
                0.6411907,
                0.02859935,
                10.9068151,
                27.71573561,
                0.15439901,
                0.00775979,
                0.04557959,
            ),
            (
                3,
                2,
                2523.4783,
                277.6646,
                2523.45180122,
                277.2591217,
                34.1950186,
                -5.66499603,
                420.1557,
                2.6274228,
                20.441475,
                0.00679125,
                [100.74325, 165.79266],
                [0.9764746, 1.2775552],
                [21.99196, 21.451086],
                [0.01052628, 0.00836843],
                11.208703,
                16.058117,
                2496,
                205,
                2583,
                324,
                2524,
                278,
                22.525309,
                9.80451,
                8.31776,
                64.02164,
                0.15163939,
                0.0281303,
                35.80985469,
                40.97300437,
                2.23528326,
                0.00730327,
                0.04557959,
            ),
        ],
        dtype=dtype,
    )
    return data


def test_convert_fits_to_hdf():
    data = create_fits_image()

    hdu = fits.BinTableHDU(data)

    hdu.writeto("output.cat", overwrite=True)

    run_sextractor_forced_photometry.convert_fits_to_hdf("output.cat", fits_ext=None)

    data_hdf = at.load_hdf_cols("output.cat")
    assert np.all(np.sort(data_hdf.dtype.names) == np.sort(data.dtype.names))
    for name in data.dtype.names:
        assert np.allclose(data_hdf[name], data[name], rtol=1e-6, atol=1e-6)

    os.remove("output.cat")


def create_dummy_files(filters):
    for f in filters:
        # dummy image (fits file)
        hdu = fits.PrimaryHDU(np.random.rand(100, 100))
        hdu.writeto(f + ".fits", overwrite=True)

        # dummy sysmaps (hdf file)
        data_sets = [
            "map_bsig",
            "map_expt",
            "map_gain",
            "map_invv",
            "map_nexp",
            "map_pointings",
        ]
        with h5py.File(f + "_sysmaps.h5", "w") as fh5:
            for ds in data_sets:
                fh5.create_dataset(ds, data=np.random.rand(100, 100))

        # dummy catalog (because sextractor is not run)
        data = create_fits_image()
        primary_hdu = fits.PrimaryHDU()
        first_hdu = fits.ImageHDU()
        second_hdu = fits.BinTableHDU(data)
        hdul = fits.HDUList([primary_hdu, first_hdu, second_hdu])
        hdul.writeto(f + ".cat", overwrite=True)

        # dummy segmentation map (because sextractor is not run)
        seg_map = np.random.randint(0, 10, (100, 100))
        hdu = fits.PrimaryHDU(seg_map)
        hdu.writeto(f + "_seg.fits", overwrite=True)

        # dummy background map (because sextractor is not run)
        bkg_map = np.random.rand(100, 100)
        hdu = fits.PrimaryHDU(bkg_map)
        hdu.writeto(f + "_bkg.fits", overwrite=True)


def test_run_sextractor_forced_photo():
    create_dummy_files(["i", "r"])
    ctx = context.create_ctx()
    ctx.current_filter = "r"
    ctx.parameters = context.create_ctx(
        sextractor_forced_photo_catalog_name_dict={"i": "i.cat", "r": "r.cat"},
        sextractor_use_temp=False,
        sextractor_forced_photo_detection_bands=["i"],
        image_name_dict={"i": "i.fits", "r": "r.fits"},
        tempdir_weight_fits="",
        weight_type="NONE",
        sysmaps_type="sysmaps_hdf_combined",
        filepath_sysmaps_dict={"i": "i_sysmaps.h5", "r": "r_sysmaps.h5"},
        maps_remote_dir=os.getcwd(),
        filters=["i", "r"],
        sextractor_checkimages=["SEGMENTATION", "BACKGROUND"],
        sextractor_checkimages_suffixes=["_seg.fits", "_bkg.fits"],
        flag_gain_times_nexp=False,
        sextractor_binary="sex",
        image_name="r.fits",
        sextractor_config="hsc_deblend_aper.config",
        pixscale=0.168,
        saturation_level=233.78025817871094,
        magzero=27.0,
        gain=53.576499938964844,
        sextractor_nnw="default.nnw",
        sextractor_filter="gauss_3.0_5x5.conv",
        sextractor_params="newdefault.param",
        weight_gain="N",
    )
    with patch("subprocess.check_call") as command_mock:
        command_mock.return_value = (0, None, None)
        plugin = run_sextractor_forced_photometry.Plugin(ctx)
        plugin()

    for f in ["i", "r"]:
        os.remove(f + ".cat")
        os.remove(f + ".fits")
        os.remove(f + "_sysmaps.h5")
    os.remove("i_seg.fits")
    os.remove("i_bkg.fits")
    os.remove("r_seg.h5")
    os.remove("r_bkg.h5")


def test_run_sextractor_forced_photo2():
    create_dummy_files(["i", "r"])
    ctx = context.create_ctx()
    ctx.current_filter = "r"
    ctx.parameters = context.create_ctx(
        sextractor_forced_photo_catalog_name_dict={"i": "i.cat", "r": "r.cat"},
        sextractor_use_temp=False,
        sextractor_forced_photo_detection_bands=["i", "r"],
        image_name_dict={"i": "i.fits", "r": "r.fits"},
        tempdir_weight_fits="",
        weight_type="NONE",
        sysmaps_type="sysmaps_hdf_combined",
        filepath_sysmaps_dict={"i": "i_sysmaps.h5", "r": "r_sysmaps.h5"},
        maps_remote_dir=os.getcwd(),
        filters=["i", "r"],
        sextractor_checkimages=[],
        sextractor_checkimages_suffixes=[],
        flag_gain_times_nexp=False,
        sextractor_binary="sex",
        image_name="r.fits",
        sextractor_config="hsc_deblend_aper.config",
        pixscale=0.168,
        saturation_level=233.78025817871094,
        magzero=27.0,
        gain=53.576499938964844,
        sextractor_nnw="default.nnw",
        sextractor_filter="gauss_3.0_5x5.conv",
        sextractor_params="newdefault.param",
        weight_gain="N",
    )
    with patch("subprocess.check_call") as command_mock:
        command_mock.return_value = (0, None, None)
        plugin = run_sextractor_forced_photometry.Plugin(ctx)
        plugin()

    for f in ["i", "r"]:
        os.remove(f + ".cat")
        os.remove(f + ".fits")
        os.remove(f + "_sysmaps.h5")
    os.remove("i_seg.fits")
    os.remove("i_bkg.fits")
    os.remove("r_seg.fits")
    os.remove("r_bkg.fits")
