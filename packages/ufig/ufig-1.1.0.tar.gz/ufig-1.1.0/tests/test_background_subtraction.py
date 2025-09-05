"""
Created on Jan 11, 2016

@author: Tomasz Kacprzak
"""

import numpy as np
from ivy.utils.struct import Struct

from ufig.plugins import background_subtract


def test_background_subtract_plugin():
    ctx = Struct()
    ctx.parameters = Struct(seed=0, bgsubract_n_downsample=10, bgsubract_n_iter=10)

    ctx.image = np.zeros((10, 10), dtype=np.float64) + 1

    plugin = background_subtract.Plugin(ctx)
    assert plugin.__str__() == "subtract background"

    plugin()
    assert np.all(np.isclose(ctx.image, 0))
