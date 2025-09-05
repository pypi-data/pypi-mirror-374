# Copyright (C) 2016 ETH Zurich, Institute for Astronomy

"""
Created on Jun 15, 2016
author: Joerg Herbel
"""

from ivy.context import loop_ctx
from ivy.utils.stop_criteria import StopCriteria
from ivy.utils.struct import WorkflowState


class FiltersStopCriteria(StopCriteria):
    """
    Stopping criteria for ivy-loops which makes the loop iterate over all filters in
    ctx.parameters.filters. It also sets the variable ctx.current_filter according
    to the current loop iteration.
    """

    def is_stop(self):
        ctx = self.parent.ctx
        l_ctx = loop_ctx(self.parent)

        if l_ctx.iter >= len(ctx.parameters.filters):
            l_ctx.stop()
        else:
            ctx.current_filter = ctx.parameters.filters[l_ctx.iter]

        return l_ctx.state == WorkflowState.STOP
