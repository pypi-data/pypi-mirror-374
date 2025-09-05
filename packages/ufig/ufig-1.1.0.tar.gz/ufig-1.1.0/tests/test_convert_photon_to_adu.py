# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Aug 06 2024


import numpy as np
from ivy import context

from ufig.plugins import convert_photons_to_adu


def test_convert_photon_to_adu():
    ctx = context.create_ctx()
    ctx.image = np.ones((1000, 1000), dtype=np.float32)
    ctx.parameters = context.create_ctx()
    ctx.parameters.gain = 2.0

    plugin = convert_photons_to_adu.Plugin(ctx)
    plugin()

    assert np.all(ctx.image == 0.5)


def test_convert_photon_to_adu_with_mask():
    ctx = context.create_ctx()
    ctx.image = np.ones((1000, 1000), dtype=np.float32)
    ctx.image_mask = np.zeros((1000, 1000), dtype=bool)
    ctx.image_mask[500:, 500:] = True
    ctx.parameters = context.create_ctx()
    ctx.parameters.gain = 1.0

    plugin = convert_photons_to_adu.Plugin(ctx)
    plugin()

    assert np.all(ctx.image[:500, :500] == 0)
    assert np.all(ctx.image[500:, 500:] == 1)
