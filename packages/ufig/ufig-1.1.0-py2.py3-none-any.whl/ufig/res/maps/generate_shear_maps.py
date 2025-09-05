# Copyright (c) 2015 ETH Zurich, Institute of Astronomy, Claudio Bruderer
# <claudio.bruderer@phys.ethz.ch>
"""
Created on May 4, 2015
@author: Claudio Bruderer

"""

import argparse

import healpy as hp
import numpy as np

if __name__ == "__main__":
    description = "Fill holes in a map and saves the maps to disk"
    parser = argparse.ArgumentParser(description=description, add_help=True)
    parser.add_argument("inputcl", type=str, help="txt-file containing the shear cls")
    parser.add_argument("l_column", type=int, help="Column with l")
    parser.add_argument(
        "cl_column", type=int, help="Column with corresponding cl-values"
    )
    parser.add_argument("nside", type=int, help="nside of HEALPIX map")
    # parser.add_argument("lmax", type=int, help="Maximum l-value")
    parser.add_argument("outputmap", type=str, help="Name of the output map")
    args = parser.parse_args()

    cl_table = np.loadtxt(args.inputcl, unpack=True)
    ell = cl_table[args.l_column]
    cl = cl_table[args.cl_column]

    # tt = np.ones(args.lmax + 1, dtype=np.float)
    # ee = cl[:args.lmax+1]
    # bb = np.zeros_like(tt)
    # te = np.zeros_like(tt)
    # eb = np.zeros_like(tt)
    # tb = np.zeros_like(tt)
    # cls = [tt, ee, bb, te, eb, tb]
    tt = np.ones_like(cl)
    ee = cl.copy()
    bb = np.zeros_like(tt)
    te = np.zeros_like(tt)
    eb = np.zeros_like(tt)
    tb = np.zeros_like(tt)
    cls = [tt, ee, bb, te, eb, tb]

    maps = hp.synfast(
        cls, args.nside, pol=True, new=True, pixwin=True
    )  # lmax=args.lmax

    hp.write_map(args.outputmap, maps, nest=False, fits_IDL=False, coord="C")
