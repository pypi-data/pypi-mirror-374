# Copyright (C) 2014 ETH Zurich, Institute for Astronomy

"""
Created on Jul 9, 2014

author: jakeret
"""

import numpy as np
import pytest

from ufig.plugins.add_lensing import add_shear

pytestmark = pytest.mark.xfail


class BaseGalaxyCatalog:
    """
    Simple galaxy catalog configuration
    """

    int_mag = np.array([18.0])
    mag = int_mag
    x = np.array([25.5])
    y = np.array([25.5])
    int_e1 = np.array([0.0])
    int_e2 = np.array([0.0])
    psf_e1 = np.array([0.0])
    psf_e2 = np.array([0.0])
    nphot = np.array([5000])
    sersic_n = np.array([2])
    int_r50 = np.array([5])
    r50 = int_r50
    gamma1 = np.array([0], dtype=np.float32)
    gamma2 = np.array([0], dtype=np.float32)
    e1, e2 = add_shear(int_e1, int_e2, gamma1, gamma2)


class PointSourceGalaxyCatalog(BaseGalaxyCatalog):
    """
    Simple point source galaxy catalog configuration
    """

    int_r50 = np.array([0])
    r50 = int_r50


class EllipticalGalaxyCatalog(BaseGalaxyCatalog):
    """
    Simple elliptical galaxy catalog configuration
    """

    int_e1 = np.array([0.4])
    int_e2 = np.array([0.3])
    gamma1 = np.array([0])
    gamma2 = np.array([0])
    e1, e2 = add_shear(int_e1, int_e2, gamma1, gamma2)


class EllipticalGalaxyAndPSFCatalog(BaseGalaxyCatalog):
    """
    Simple elliptical galaxy catalog configuration with an elliptical PSF
    """

    int_e1 = np.array([0.4])
    int_e2 = np.array([0.3])
    gamma1 = np.array([0])
    gamma2 = np.array([0])
    e1, e2 = add_shear(int_e1, int_e2, gamma1, gamma2)
    psf_e1 = np.array([0.1])
    psf_e2 = np.array([0.15])


class SphericalGalaxyEllipticalPSFCatalog(BaseGalaxyCatalog):
    """
    Simple elliptical galaxy catalog configuration with an elliptical PSF
    """

    psf_e1 = np.array([0.1])
    psf_e2 = np.array([0.15])
