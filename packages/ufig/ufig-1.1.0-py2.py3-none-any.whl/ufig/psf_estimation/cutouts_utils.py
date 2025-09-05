# Copyright (c) 2017 ETH Zurich, Cosmology Research Group
"""
Created on Feb 23, 2021
@author: Tomasz Kacprzak
"""

import numba as nb
import numpy as np


@nb.jit(nopython=True)
def find_max_flux_pos(x, y, delta_x, delta_y, image):
    """
    Find the position of the maximum flux in a 2D image around a given position (x, y).

    :param x: x-coordinate of the center position
    :param y: y-coordinate of the center position
    :param delta_x: array of x offsets to check
    :param delta_y: array of y offsets to check
    :param image: 2D numpy array representing the image
    :return: (xi_max, yi_max) - coordinates of the pixel with maximum flux
    """

    max_flux = -np.inf
    xi_max = 0
    yi_max = 0

    for dx in delta_x:
        for dy in delta_y:
            xi = x + dx
            yi = y + dy

            if (
                0 <= xi < image.shape[1]
                and 0 <= yi < image.shape[0]
                and image[yi, xi] > max_flux
            ):
                max_flux = image[yi, xi]
                xi_max = xi
                yi_max = yi

    return xi_max, yi_max


def get_cutouts(x_peak, y_peak, image, pointings_maps, stamp_shape):
    """
    Get cube of coutouts around a list of coordinates.

    :param x_peak: list of x positions
    :param y_peak: list of y positions
    :param image: 2D image
    :param pointings_maps: an array with binary pointings indicators
    :param stamp_shape: (nx, ny) shape of stamp, fixed for all objects
    """

    stamp_half_x = stamp_shape[1] // 2
    stamp_half_y = stamp_shape[0] // 2

    delta_x_check = np.arange(-1, 2, dtype=np.int32)
    delta_y_check = np.arange(-1, 2, dtype=np.int32)

    cube = np.zeros((len(x_peak),) + stamp_shape, dtype=np.float32)

    select_image_boundary = np.zeros(len(x_peak), dtype=bool)
    select_coadd_boundary = np.zeros(len(x_peak), dtype=bool)
    select_max_flux_centered = np.zeros(len(x_peak), dtype=bool)

    for i_obj in range(len(x_peak)):
        # 1) select pixel with maximum intensity
        xi_max, yi_max = find_max_flux_pos(
            x_peak[i_obj], y_peak[i_obj], delta_x_check, delta_y_check, image
        )

        # 2) compute indices for cutting out
        x_start = xi_max - stamp_half_x
        y_start = yi_max - stamp_half_y
        x_stop = xi_max + stamp_half_x + 1
        y_stop = yi_max + stamp_half_y + 1

        # 3) check if star is completely on image
        select_image_boundary[i_obj] = (
            (x_start >= 0)
            & (y_start >= 0)
            & (x_stop < image.shape[1])
            & (y_stop < image.shape[0])
        )

        # 4) check if star hits any chip boundaries
        pointings = pointings_maps[y_start:y_stop, x_start:x_stop]
        select_coadd_boundary[i_obj] = len(np.unique(pointings)) == 1

        # 5) check if cutout is centered on maximum flux (if full stamp is in image)
        if select_image_boundary[i_obj]:
            cutout = image[y_start:y_stop, x_start:x_stop]
            select_max_flux_centered[i_obj] = cutout[
                stamp_half_y, stamp_half_x
            ] == np.amax(cutout)
        else:
            select_max_flux_centered[i_obj] = False
        if select_max_flux_centered[i_obj]:
            cube[i_obj, :, :] = cutout

    return cube, select_image_boundary, select_coadd_boundary, select_max_flux_centered
