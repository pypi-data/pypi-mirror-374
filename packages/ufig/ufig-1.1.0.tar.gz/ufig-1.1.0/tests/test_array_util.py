# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Aug 13 2024


import numpy as np

from ufig.array_util import (
    check_flag_bit,
    check_flag_bit_single,
    clear_flag_bit_single,
    rec_float64_to_float32,
    set_flag_bit,
    set_flag_bit_single,
)


def test_set_flag_bit_single():
    assert set_flag_bit_single(0, 0) == 1
    assert set_flag_bit_single(0, 1) == 2
    assert set_flag_bit_single(1, 1) == 3


def test_clear_flag_bit_single():
    assert clear_flag_bit_single(3, 0) == 2
    assert clear_flag_bit_single(3, 1) == 1
    assert clear_flag_bit_single(7, 1) == 5


def test_check_flag_bit_single():
    assert check_flag_bit_single(1, 0) is True
    assert check_flag_bit_single(1, 1) is False
    assert check_flag_bit_single(3, 1) is True


def test_set_flag_bit():
    flags = np.array([0, 0, 0, 0], dtype=np.int32)
    select = np.array([True, False, True, False])
    set_flag_bit(flags, select, 1)
    np.testing.assert_array_equal(flags, [2, 0, 2, 0])


def test_check_flag_bit():
    flags = np.array([1, 2, 3, 4], dtype=np.int32)
    result = check_flag_bit(flags, 1)
    np.testing.assert_array_equal(result, [False, True, True, False])


def test_rec_float64_to_float32():
    dt = np.dtype([("a", np.float64), ("b", np.int32), ("c", np.float64)])
    cat = np.array([(1.0, 2, 3.0)], dtype=dt)

    cat_new = rec_float64_to_float32(cat)

    assert cat_new.dtype["a"] == np.float32
    assert cat_new.dtype["b"] == np.int32
    assert cat_new.dtype["c"] == np.float32

    np.testing.assert_array_almost_equal(cat["a"], cat_new["a"])
    np.testing.assert_array_equal(cat["b"], cat_new["b"])
    np.testing.assert_array_almost_equal(cat["c"], cat_new["c"])
