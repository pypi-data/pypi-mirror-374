# Copyright (c) 2017 ETH Zurich, Cosmology Research Group
"""
Created on 05 May, 2018
@author: Tomasz Kacprzak
"""


def brighter_fatter_remove(col_mag, col_fwhm, col_e1, col_e2, dict_corr):
    fac = (col_mag - dict_corr["mag_ref"]) / dict_corr["mag_ref"]
    col_fwhm_rem = col_fwhm + fac * dict_corr["c1r"]
    col_e1_rem = col_e1 + fac * dict_corr["c1e1"]
    col_e2_rem = col_e2 + fac * dict_corr["c1e2"]
    return col_fwhm_rem, col_e1_rem, col_e2_rem


def brighter_fatter_add(col_mag, col_fwhm, col_e1, col_e2, dict_corr):
    fac = (col_mag - dict_corr["mag_ref"]) / dict_corr["mag_ref"]
    col_fwhm_add = col_fwhm - fac * dict_corr["c1r"]
    col_e1_add = col_e1 - fac * dict_corr["c1e1"]
    col_e2_add = col_e2 - fac * dict_corr["c1e2"]
    return col_fwhm_add, col_e1_add, col_e2_add
