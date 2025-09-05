# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Aug 06 2024


import numpy as np
import pytest
from ivy import context

from ufig.plugins import cleanup_memory


def test_cleanup_memory():
    ctx = context.create_ctx()
    ctx.image = np.zeros((1000, 1000), dtype=np.float32)
    ctx.parameters = context.create_ctx()
    ctx.parameters.bkg_noise_std = np.zeros((1000, 1000), dtype=np.float32)

    plugin = cleanup_memory.Plugin(ctx)
    plugin()

    with pytest.raises(AttributeError):
        ctx.image  # noqa

    with pytest.raises(AttributeError):
        ctx.parameters.bkg_noise_std  # noqa
