# Copyright (c) 2016 ETH Zurich, Institute of Astronomy, Cosmology Research Group

"""
Created on Sep 30, 2016
@author: Joerg Herbel
"""

import ivy


def run_ufig_from_config(config, **kwargs):
    """
    Run UFig using an (importable) configuration file. Additional parameters can be
    provided as keyword arguments.

    :param config: Importable configuration file.
    :param kwargs: Additional parameter values.
    :return: Ivy-context created by UFig
    """
    ctx = ivy.execute(config, **kwargs)
    return ctx
