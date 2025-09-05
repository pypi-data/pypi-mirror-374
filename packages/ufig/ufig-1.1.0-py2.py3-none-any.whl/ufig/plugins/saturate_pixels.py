# Copyright (c) 2013 ETH Zurich, Institute of Astronomy, Lukas Gamper
# <lukas.gamper@usystems.ch>
"""
Created on Oct 7, 2013
@author: Lukas Gamper
"""

import numpy as np
from ivy.plugin.base_plugin import BasePlugin


class Plugin(BasePlugin):
    """
    For pixels that exceed the saturation flux, leak the photons in the column direction
    until all pixels are under the saturation level.

    :param gain: gain of CCD detector (e/ADU)
    :param size_x: size of image in x-direction (pixel)
    :param size_y: size of image in y-direction (pixel)
    :param saturation_level: saturation level in electrons

    """

    def __call__(self):
        # saturate pixels
        saturation = self.ctx.parameters.saturation_level

        ox, oy = np.where(self.ctx.image > saturation)
        odiff = (self.ctx.image[ox, oy] - saturation) / 2.0
        self.ctx.image[ox, oy] = saturation

        ix, iy, idiff = ox.copy(), oy.copy(), odiff.copy()

        while True:
            ix = ix + 1
            mask = (idiff > 0) & (ix < self.ctx.parameters.size_y)
            if not np.any(mask):
                break
            ix, iy, idiff = ix[mask], iy[mask], idiff[mask]
            self.ctx.image[ix, iy] += idiff
            idiff = self.ctx.image[ix, iy] - saturation
            mask = idiff > 0
            self.ctx.image[ix[mask], iy[mask]] = saturation

        while True:
            # index is not writable, so use + instead of +=
            ox = ox - 1
            mask = (odiff > 0) & (ox >= 0)
            if not np.any(mask):
                break
            ox, oy, odiff = ox[mask], oy[mask], odiff[mask]
            self.ctx.image[ox, oy] += odiff
            odiff = self.ctx.image[ox, oy] - saturation
            mask = odiff > 0
            self.ctx.image[ox[mask], oy[mask]] = saturation

        if np.any(self.ctx.image > saturation):  # pragma: no cover
            lost = np.sum(self.ctx.image[self.ctx.image > saturation] - saturation)
            if np.sum(lost) > 0:
                print(
                    f"Lost {np.sum(lost):.0f} photons in saturation"
                    f" on {lost.size} pixels"
                )

    def __str__(self):
        return "saturate pixels"
