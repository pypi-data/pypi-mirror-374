# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Aug 13 2024


from ivy.loop import Loop

from ufig.config import common
from ufig.workflow_util import FiltersStopCriteria

plugins = [
    "ufig.plugins.multi_band_setup",
    "ivy.plugin.show_stats",
    Loop(
        [
            "ufig.plugins.single_band_setup_intrinsic_only",
        ],
        stop=FiltersStopCriteria(),
    ),
]

for name in [name for name in dir(common) if not name.startswith("__")]:
    globals()[name] = getattr(common, name)
