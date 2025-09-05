"""
Created on Mar 11, 2014

@author: Chihway Chang, Lukas Gamper
adapted by Silvan Fischbacher, 2024
"""

import numpy as np
from ivy.utils.struct import Struct
from scipy import ndimage

from ufig.plugins import resample


def test_convolution():
    matrix = np.random.random(size=(100, 100))
    kernel = resample.get_lanczos_kernel(2)
    conv_matrix = ndimage.convolve(matrix.copy(), kernel, mode="constant", cval=0.0)

    resample.convolve(matrix, kernel)

    assert np.allclose(conv_matrix, matrix, atol=0, rtol=1e-13)


def test_resampling():
    n = 3
    lanczos = resample.get_lanczos_kernel(n)

    ctx = Struct()
    ctx.parameters = Struct(
        lanczos_n=n, lanczos_kernel_type="lanczos_integral", image_precision=np.float32
    )

    ctx.image = np.zeros((21, 21), dtype=np.float64)
    ctx.image[10, 10] = 1.0
    plugin = resample.Plugin(ctx)
    plugin()

    assert np.allclose(np.sum(ctx.image), 1, atol=0.001)
    assert np.allclose(
        lanczos, ctx.image[10 - n : 10 + n + 1, 10 - n : 10 + n + 1], atol=0.005
    )

    n = 4
    lanczos = resample.get_lanczos_kernel(n)

    ctx = Struct()
    ctx.parameters = Struct(
        lanczos_n=n, lanczos_kernel_type="lanczos_integral", image_precision=np.float32
    )

    ctx.image = np.zeros((21, 21), dtype=np.float64)
    ctx.image[0, 0] = 1.0
    plugin = resample.Plugin(ctx)
    plugin()

    factor = np.sum(lanczos[n:, n:])
    assert np.allclose(np.sum(ctx.image), factor, atol=0.02)
    assert np.allclose(lanczos[n:, n:], ctx.image[: n + 1, : n + 1], atol=0.02)

    n = 3
    lanczos = resample.get_lanczos_kernel(n)

    ctx = Struct()
    ctx.parameters = Struct(
        lanczos_n=n, lanczos_kernel_type="lanczos_integral", image_precision=np.float32
    )

    ctx.image = np.zeros((21, 21), dtype=np.float64)
    ctx.image[0, n - 1] = 1.0
    plugin = resample.Plugin(ctx)
    plugin()

    factor = np.sum(lanczos[n:, 1:])
    assert np.allclose(np.sum(ctx.image), factor, atol=0.02)
    assert np.allclose(lanczos[n:, 1:], ctx.image[: n + 1, : 2 * n], atol=0.02)

    ctx.image = np.zeros((21, 21), dtype=np.float64)
    ctx.image[1, 10] = 1.0
    plugin = resample.Plugin(ctx)
    plugin()

    factor = np.sum(lanczos[n - 1 :, :])
    assert np.allclose(np.sum(ctx.image), 1, atol=0.02)
    assert np.allclose(
        lanczos[n - 1 :, :] / factor,
        ctx.image[: n + 1 + 1, 10 - n : 10 + n + 1],
        atol=0.02,
    )


def test_resample_read():
    ctx = Struct(image=np.zeros((21, 21), dtype=np.float32))
    ctx.image[1, 10] = 1.0
    ctx.parameters = Struct(
        lanczos_kernel_type="read_from_file",
        filename_resampling_kernel="lanczos_resampling_kernel_n3.txt",
        image_precision=np.float32,
    )
    plugin = resample.Plugin(ctx)
    plugin()
