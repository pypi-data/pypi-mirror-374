# Copyright (c) 2013 ETH Zurich, Institute of Astronomy, Lukas Gamper
# <lukas.gamper@usystems.ch>
"""
Created on Oct 7, 2013
@author: Lukas Gamper

"""

import numba as nb
import numpy as np
from ivy.plugin.base_plugin import BasePlugin
from scipy.integrate import dblquad


@nb.jit(nopython=True)
def sum_prod(a, b):
    c = 0.0
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            c += a[i, j] * b[i, j]
    return c


@nb.jit(nopython=True)
def _convolve(a, k, as0, as1, ks0, ks1, cache, border, vals):
    # top
    # border[ks0//2:, ks1//2: -(ks1//2+1)] = a[:ks0,:]
    for i0 in range(ks0):
        for j0 in range(as1):
            border[i0 + ks0 // 2, j0 + ks1 // 2] = a[i0, j0]

    for i1 in range(ks0 // 2, ks0):
        for j in range(ks1 // 2, as1 + ks1 // 2):
            vals[:] = border[
                i1 - ks0 // 2 : i1 + ks0 // 2 + 1, j - ks1 // 2 : j + ks1 // 2 + 1
            ]
            # cache[i1-ks0//2, j-ks1//2] = np.sum(vals * k)
            cache[i1 - ks0 // 2, j - ks1 // 2] = sum_prod(vals, k)

    for i in range(ks0 // 2, as0 - ks0 // 2):
        # left
        for j2 in range(0, ks1 // 2 + 1):
            vals[:] = 0
            vals[:, ks1 // 2 - j2 :] = a[
                i - ks0 // 2 : i + ks0 // 2 + 1, : ks1 // 2 + j2 + 1
            ]
            # cache[-1, j2] = np.sum(vals * k)
            cache[-1, j2] = sum_prod(vals, k)

        # center
        for j3 in range(ks1 // 2 + 1, as1 - ks1 // 2):
            a[i - ks0 // 2, j3 - ks1 // 2 - 1] = cache[0, j3 - ks1 // 2 - 1]
            vals[:] = a[
                i - ks0 // 2 : i + ks0 // 2 + 1, j3 - ks1 // 2 : j3 + ks1 // 2 + 1
            ]
            # cache[-1, j3] = np.sum(vals * k)
            cache[-1, j3] = sum_prod(vals, k)

        # right
        for r, j4 in enumerate(range(as1 - ks1 // 2, as1)):
            a[i - ks0 // 2, j4 - ks1 // 2 - 1] = cache[0, j4 - ks1 // 2 - 1]
            vals[:] = 0
            vals[:, : ks1 - r - 1] = a[i - ks0 // 2 : i + ks0 // 2 + 1, j4 - ks1 // 2 :]
            # cache[-1, j4] = np.sum(vals * k)
            cache[-1, j4] = sum_prod(vals, k)
            r += 1

        # right fill
        for j5 in range(as1, as1 + ks1 // 2 + 1):
            a[i - ks0 // 2, j5 - ks1 // 2 - 1] = cache[0, j5 - ks1 // 2 - 1]
        #
        cache[0 : ks0 // 2, :] = cache[1 : ks0 // 2 + 1, :]

    # bottom
    border[:] = 0
    # border[:ks0-1, ks1//2: -(ks1//2+1)] = a[-(ks0-1):,:]
    for i2 in range(ks0 - 1):
        for j6 in range(as1):
            border[i2, j6 + ks1 // 2] = a[i2 + (as0 - ks0) + 1, j6]

    r = ks0 // 2
    for i3 in range(as0 - ks0 // 2, as0):
        for j7 in range(ks1 // 2, as1 + ks1 // 2):
            a[i3 - ks0 // 2, j7 - ks1 // 2] = cache[0, j7 - ks1 // 2]
            vals[:] = border[
                r - ks0 // 2 : r + ks0 // 2 + 1, j7 - ks1 // 2 : j7 + ks1 // 2 + 1
            ]
            # cache[-1, j7-ks1//2] = np.sum(vals * k)
            cache[-1, j7 - ks1 // 2] = sum_prod(vals, k)
        cache[0 : ks0 // 2, :] = cache[1 : ks0 // 2 + 1, :]
        r += 1

    # bottom fill
    # a[-(ks0//2):, :] = cache[:ks0//2, :]
    for i4 in range(ks0 // 2):
        for j8 in range(as1):
            a[i4 + as0 - ks0 // 2, j8] = cache[i4, j8]


def convolve(a, k):
    # TODO fix segault
    as0, as1 = a.shape
    ks0, ks1 = k.shape
    cache = np.zeros((ks0 // 2 + 1, as1))
    border = np.zeros((ks0 + ks0 // 2, as1 + ks1))
    vals = np.zeros_like(k)

    _convolve(a, k, as0, as1, ks0, ks1, cache, border, vals)

    return a


def get_lanczos_kernel(n):
    lanczos = np.zeros((2 * n + 1, 2 * n + 1), dtype=np.float64)
    for i in range(-n, n + 1, 1):
        for j in range(-n, n + 1, 1):
            lanczos[i + n, j + n] = dblquad(
                lambda x, y: np.sinc(y) * np.sinc(y / n) * np.sinc(x) * np.sinc(x / n),
                i - 0.5,
                i + 0.5,
                lambda x, j=j: j - 0.5,
                lambda x, j=j: j + 0.5,
            )[0]
    lanczos = lanczos / np.sum(lanczos)
    return lanczos


def get_lanczos_kernel_integral(par):
    lanczos = get_lanczos_kernel(par.lanczos_n)
    lanczos = lanczos.astype(par.image_precision)
    return lanczos


def read_resampling_kernel(par):
    from pkg_resources import resource_filename

    import ufig

    filepath_kernel = resource_filename(
        ufig.__name__, "res/resampling/" + par.filename_resampling_kernel
    )
    kernel = np.loadtxt(filepath_kernel)
    kernel = kernel / np.sum(kernel)
    kernel = kernel.astype(par.image_precision)
    return kernel


KERNEL_GENERATOR = {
    "lanczos_integral": get_lanczos_kernel_integral,
    "read_from_file": read_resampling_kernel,
}


class Plugin(BasePlugin):
    """
    Convolve the image with a Lanczos kernel to model the effect of correlated noise.
    The main effect of correlated noise modeled by this kernel is that coming from the
    coadding process.

    :param lanczos_n: the order of lanczos function used to model the resampling

    :return: image after the lanczos convolution

    """

    def __call__(self):
        kernel_gen = KERNEL_GENERATOR[self.ctx.parameters.lanczos_kernel_type]
        kernel_img = kernel_gen(self.ctx.parameters)
        convolve(self.ctx.image, kernel_img)

    def __str__(self):
        return "resample image"
