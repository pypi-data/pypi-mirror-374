# Copyright (C) 2019 ETH Zurich, Institute for Particle and Astrophysics

"""
Created on Feb 5, 2019
author: Joerg Herbel
"""

import numba as nb
import numpy as np


def decimal_integer_to_binary(n_bits, arr_decimal, dtype_out):
    """
    Transform a one-dimensional array of decimal integers into its binary
    representation. Returns an array with the shape (len(arr_decimal), n_bits). To
    reconstruct arr_decimal[i], one would perform the operation

    arr_decimal[i] = np.sum(2**np.arange(n_bits) * arr_binary[i])

    This means that this binary representation is reversed with respect to what is
    normally used. For example, normally,

    1100 = 1 * 2**3 + 1 * 2**2 + 0 * 2**1 + 0 * 2**0.

    However, here we have

    1100 = 1 * 2**0 + 1 * 2**1 + 0 * 2**2 + 0 * 2**3.

    ATTENTION: THIS FUNCTION MODIFIES ARR_DECIMAL IN PLACE!
    """
    arr_binary = np.zeros((len(arr_decimal), n_bits), dtype=dtype_out)
    arr_decimal = arr_decimal.astype(dtype_out)
    for i in range(n_bits):
        arr_binary[:, i] = arr_decimal % np.uint(2)
        arr_decimal //= np.uint(2)

    return arr_binary


def get_binary_mask_dtype(n_bits):
    for dtype in [np.uint8, np.uint16, np.uint32, np.uint64]:
        if np.iinfo(dtype).max >= n_bits:
            return dtype

    raise ValueError(
        f"Number of bits {n_bits} exceeding maximum possible value such that np.uint"
        " dtype can be used"
    )


def set_masked_pixels(pixel_mask, maskbits_keep, n_bits):
    """
    Set pixels which are masked according to input bits. This function modifies
    pixel_mask in-place.

    :param pixel_mask: mask
    :param maskbits_keep: mask bits to keep
    :param n_bits: ...
    :return: mask with only bits to keep switched on (same shape as input mask)
    """

    pixel_mask = pixel_mask.copy()

    # special case of no masking
    if len(maskbits_keep) == 0:
        return pixel_mask * 0

    # transform to binary representation
    pixel_mask_bin = decimal_integer_to_binary(
        n_bits, np.ravel(pixel_mask), dtype_out=get_binary_mask_dtype(n_bits)
    )

    # select bits to keep
    pixel_mask_bin = pixel_mask_bin[:, maskbits_keep]

    # transform back to original shape
    pixel_mask_keep = np.sum(pixel_mask_bin, axis=1).reshape(pixel_mask.shape)

    return pixel_mask_keep


@nb.jit(nopython=True)
def select_off_mask(xs, ys, rs, mask):
    # Array holding results
    select_off = np.ones(len(xs), dtype=np.int8)

    # Compute coordinates to be checked
    x_min = np.floor(xs - rs).astype(np.int32)
    y_min = np.floor(ys - rs).astype(np.int32)
    x_max = np.ceil(xs + rs).astype(np.int32)
    y_max = np.ceil(ys + rs).astype(np.int32)

    x_min = np.maximum(x_min, 0)
    y_min = np.maximum(y_min, 0)
    x_max = np.minimum(x_max, mask.shape[1])
    y_max = np.minimum(y_max, mask.shape[0])

    rs_sq = rs**2

    for i in range(len(xs)):
        x = xs[i]
        y = ys[i]
        r_sq = rs_sq[i]

        for xi in range(x_min[i], x_max[i]):
            for yi in range(y_min[i], y_max[i]):
                delta = (xi - x) ** 2 + (yi - y) ** 2
                if delta < r_sq and mask[int(yi), int(xi)] > 0:
                    select_off[i] = 0
                    break
            if select_off[i] == 0:
                break

    return select_off


def pixel_mask_to_catalog_mask(pixel_mask, cat, off_mask_radius):
    x = cat["XWIN_IMAGE"] - 0.5
    y = cat["YWIN_IMAGE"] - 0.5
    r = off_mask_radius * cat["FLUX_RADIUS"]
    r[r < 0] = 5

    return select_off_mask(x, y, r, pixel_mask).astype(bool)


def pixel_mask_to_ucat_catalog_mask(pixel_mask, cat, off_mask_radius, r50_offset=5):
    x = cat["x"]
    y = cat["y"]
    r = off_mask_radius * cat["r50"] + r50_offset
    r[r < 0] = 5

    return select_off_mask(x, y, r, pixel_mask).astype(bool)
