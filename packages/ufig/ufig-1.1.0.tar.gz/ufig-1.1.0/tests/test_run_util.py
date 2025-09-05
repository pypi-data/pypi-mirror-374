# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Aug 13 2024


import os
import sys
from unittest import mock

import numpy as np
from cosmic_toolbox import arraytools as at

from ufig import run_util


def test_run_util():
    run_util.run_ufig_from_config("ufig.config.test_config")


@mock.patch.dict("sys.modules", {"cosmo_torrent": mock.MagicMock()})
@mock.patch("ufig.plugins.draw_stars_besancon_map.load_besancon_map")
@mock.patch("ufig.plugins.draw_stars_besancon_map.get_interp_nearest")
def test_run_util_adv(mock_interp_nearest, mock_load_besancon):
    # Create mock for cosmo_torrent module
    mock_cosmo = mock.MagicMock()
    mock_cosmo.data_path.return_value = os.path.join(
        os.path.dirname(__file__), "res/besancon_HSC.h5"
    )
    sys.modules["cosmo_torrent"] = mock_cosmo

    # Set up other mocks
    mock_load_besancon.return_value = BESANCON_MAP_INFO
    mock_interp_nearest.return_value = CATALOG

    run_util.run_ufig_from_config("ufig.config.test_config_adv")
    os.remove("ufig_g.fits")
    os.remove("ufig_r.fits")
    os.remove("ufig_i.fits")


BESANCON_MAP_INFO = {
    "healpix_mask": np.ones(768) * -1.6375e30,
    "simulation_area": 2,
    "nside": 8,
    "healpix_list": [None] * 768,
}

CATALOG = at.dict2rec(
    {
        "g": np.array([24, 25, 26]),
        "r": np.array([25, 26, 27]),
        "i": np.array([26, 27, 28]),
        "z": np.array([27, 28, 29]),
        "y": np.array([28, 29, 30]),
    }
)
