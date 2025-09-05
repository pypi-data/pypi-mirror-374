# Copyright (C) 2015 ETH Zurich, Institute for Astronomy

"""
Created on Dec 5, 2016

author: tomaszk
"""

import numpy as np


def set_flag_bit_single(value, bit):
    return value | (1 << bit)


def clear_flag_bit_single(value, bit):
    return value & ~(1 << bit)


def check_flag_bit_single(value, bit):
    return bool(value & (1 << bit))


def set_flag_bit(flags, select, field):
    ones = np.ones(np.count_nonzero(select), dtype=flags.dtype)
    flags[select] |= ones << (field * ones)


def check_flag_bit(flags, flagbit):
    isset = (flags & (1 << flagbit)) != 0
    return isset


def rec_float64_to_float32(cat):
    list_new_dtype = []
    all_ok = True

    for i in range(len(cat.dtype)):
        if cat.dtype[i] == np.float64:
            list_new_dtype.append(np.float32)
            all_ok = False
        else:
            list_new_dtype.append(cat.dtype[i])

    if all_ok:
        return cat

    else:
        new_dtype = np.dtype(dict(formats=list_new_dtype, names=cat.dtype.names))
        cat_new = cat.astype(new_dtype)
        return cat_new
