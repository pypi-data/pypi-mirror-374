# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Fri Mar 01 2024

from ivy.plugin.base_plugin import BasePlugin

NAME = "cleanup memory"


class Plugin(BasePlugin):
    """
    Cleanup memory.
    """

    def __call__(self):
        params_to_delete = ["image", "image_mask", "bkg_noise_std"]
        self.delete(params_to_delete)

    def delete(self, params):
        for p in params:
            self.ctx.__dict__.pop(p, None)
            self.ctx.parameters.__dict__.pop(p, None)

    def __str__(self):
        return NAME
