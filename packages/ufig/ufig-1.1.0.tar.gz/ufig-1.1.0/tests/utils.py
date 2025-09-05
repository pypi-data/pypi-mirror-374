# Copyright (C) 2013 ETH Zurich, Institute for Astronomy

"""
Created on Apr 4, 2014

author: jakeret
"""

import hope

hope.rangecheck = True

try:
    import os

    os.environ["HUDSON_URL"]
    JENKINS = True
except KeyError:
    JENKINS = False
