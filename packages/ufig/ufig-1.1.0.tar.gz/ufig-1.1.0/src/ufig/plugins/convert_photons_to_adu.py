# Copyright (c) 2013 ETH Zurich, Institute of Astronomy, Lukas Gamper
# <lukas.gamper@usystems.ch>
"""
Created on Aug 19, 2014
@author: Chihway Chang
"""

from ivy.plugin.base_plugin import BasePlugin


class Plugin(BasePlugin):
    """
    Convert integer photon counts into float ADU's by multiplying the quantum efficiency
    and dividing gain.

    :param gain: gain of CCD detector (e/ADU)
    :return: image that is rescaled to some specified zero point
    """

    def __call__(self):
        # rescale zero point
        self.ctx.image /= self.ctx.parameters.gain

        if hasattr(self.ctx, "image_mask"):
            self.ctx.image[~self.ctx.image_mask] = 0

    def __str__(self):
        return "convert photons to ADUs"
