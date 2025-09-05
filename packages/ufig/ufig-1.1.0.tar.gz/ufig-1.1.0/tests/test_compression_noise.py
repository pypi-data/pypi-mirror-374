# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Aug 13 2024


import numpy as np
from ivy import context

from ufig.plugins import compression_noise


def test_compression_noise():
    ctx = context.create_ctx()
    ctx.image = np.zeros((1000, 1000), dtype=np.float32)
    ctx.parameters = context.create_ctx(
        chunksize=100,
        seed=42,
        compression_noise_seed_offset=1996,
        compression_noise_level=10,
    )

    plugin = compression_noise.Plugin(ctx)
    plugin()

    # check that image has now noise
    assert np.all(ctx.image != 0)
    assert abs(np.mean(ctx.image)) < 1e-2
    assert 9 < np.max(ctx.image) < 10
    assert -10 < np.min(ctx.image) < -9
