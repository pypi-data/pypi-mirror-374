"""
Created on Nov, 2014

@author: Claudio Bruderer
adapted by: Silvan Fischbacher
"""

import os

import numpy as np
from ivy import context
from pkg_resources import resource_filename
from scipy.special import gammaincinv

import ufig
from ufig.plugins.gamma_interpolation_table import Plugin


def test_interpolation_table():
    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        compute_gamma_table_onthefly=True,
        sersicprecision=9,
        gammaprecision=13,
        gammaprecisionhigh=4,
        copy_gamma_table_to_cwd=False,
    )

    par = ctx.parameters
    plugin = Plugin(ctx)
    plugin()
    intrinsicTable = ctx.intrinsicTable

    x = np.linspace(0.0, 1.0, 2**par.gammaprecision + 1)[:-1]

    index = 15
    n = 10.0 * (float(index) / 2**par.sersicprecision)
    k = gammaincinv(2.0 * n, 0.5)
    y1 = gammaincinv(2.0 * n, x) ** n / k**n
    y2 = (
        gammaincinv(2.0 * n, 1.0 + (x - 1) * 1.0 / 2**par.gammaprecisionhigh) ** n
        / k**n
    )
    assert np.allclose(y1, intrinsicTable[index, : 2**par.gammaprecision], rtol=0.00001)
    assert np.allclose(
        y2, intrinsicTable[index, 2**par.gammaprecision : -1], rtol=0.00001
    )
    assert np.max(intrinsicTable[index]) == intrinsicTable[index, -1]

    index = 452
    n = 10.0 * (float(index) / 2**par.sersicprecision)
    k = gammaincinv(2.0 * n, 0.5)
    y1 = gammaincinv(2.0 * n, x) ** n / k**n
    y2 = (
        gammaincinv(2.0 * n, 1.0 + (x - 1) * 1.0 / 2**par.gammaprecisionhigh) ** n
        / k**n
    )
    assert np.allclose(y1, intrinsicTable[index, : 2**par.gammaprecision], rtol=0.00001)
    assert np.allclose(
        y2, intrinsicTable[index, 2**par.gammaprecision : -1], rtol=0.00001
    )
    assert np.max(intrinsicTable[index]) == intrinsicTable[index, -1]

    del ctx.intrinsicTable

    ctx.parameters.compute_gamma_table_onthefly = False
    plugin = Plugin(ctx)
    plugin()
    intrinsicTable_saved = ctx.intrinsicTable
    assert np.allclose(intrinsicTable_saved, intrinsicTable, rtol=0.00001)


def test_copy_gamma_to_cwd(tmpdir):
    os.chdir(tmpdir)

    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        compute_gamma_table_onthefly=False,
        sersicprecision=9,
        gammaprecision=13,
        gammaprecisionhigh=4,
        copy_gamma_table_to_cwd=False,
    )
    par = ctx.parameters

    filename = (
        f"intrinsic_table_{par.sersicprecision}_{par.gammaprecision}_"
        f"{par.gammaprecisionhigh}"
    )
    if np.__version__ >= "2":
        filename += "_np2"
    filepath = os.path.join(os.getcwd(), f"{filename}.fits")
    assert not os.path.exists(filepath)

    try:
        ctx.parameters.copy_gamma_table_to_cwd = True
        plugin = Plugin(ctx)
        plugin()
        assert os.path.exists(filepath)

        plugin = Plugin(ctx)
        plugin()
        assert os.path.exists(filepath)

    finally:
        os.remove(filepath)


def test_save_new_interpolation_table():
    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        compute_gamma_table_onthefly=True,
        sersicprecision=8,
        gammaprecision=11,
        gammaprecisionhigh=3,
        copy_gamma_table_to_cwd=False,
    )
    par = ctx.parameters

    filename = (
        f"intrinsic_table_{par.sersicprecision}_{par.gammaprecision}_"
        f"{par.gammaprecisionhigh}"
    )
    if np.__version__ >= "2":
        filename += "_np2"
    resource_directory = resource_filename(ufig.__name__, "res/intrinsictables/")
    filepath = os.path.join(resource_directory, f"{filename}.fits")
    try:
        plugin = Plugin(ctx)
        plugin()
        plugin.save_new_interpolation_table()

        assert os.path.exists(filepath)
    finally:
        os.remove(filepath)
