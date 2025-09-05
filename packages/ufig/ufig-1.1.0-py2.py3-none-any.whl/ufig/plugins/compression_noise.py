# Copyright (c) 2013 ETH Zurich, Institute of Astronomy, Lukas Gamper
# <lukas.gamper@usystems.ch>
"""
Created on 04/2016
@author: Tomasz Kacprzak

"""

import numpy as np
from ivy.plugin.base_plugin import BasePlugin


# Todo: Update documentation
class Plugin(BasePlugin):
    def __call__(self):
        # Reseed random library
        np.random.seed(
            self.ctx.parameters.seed + self.ctx.parameters.compression_noise_seed_offset
        )

        chunk = (
            self.ctx.parameters.chunksize,
            self.ctx.parameters.chunksize,
        )  # quadratic chunks for now
        img_shape = self.ctx.image.shape

        for i in range(img_shape[0] // chunk[0]):
            idx0 = slice(i * chunk[0], (i + 1) * chunk[0])
            for j in range(img_shape[1] // chunk[1]):
                idx1 = slice(j * chunk[1], (j + 1) * chunk[1])
                self.ctx.image[idx0, idx1] += np.random.uniform(
                    low=-self.ctx.parameters.compression_noise_level,
                    high=self.ctx.parameters.compression_noise_level,
                    size=chunk,
                )

    def __str__(self):
        return "add compression noise"
