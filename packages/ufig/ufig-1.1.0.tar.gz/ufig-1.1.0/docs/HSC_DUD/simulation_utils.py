# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Thu Jul 17 2025,
#
# sources:
# legacy_abc.analysis.systematics.make_sysmaps
# legacy_abc.analysis.systematics.create_besancon_map

import numpy as np
from cosmic_toolbox import logger

LOGGER = logger.get_logger(__name__)


def evaluate_line(slope, intcpt, x):
    return slope * x + intcpt


def compute_slope_and_intcpt(x1, x2, y1, y2):
    if x1 == x2:
        x2 += 1e-5

    slope = (y1 - y2) / (x1 - x2)
    intcpt = y1 - slope * x1

    return slope, intcpt


def get_region_selection(x, y, corners_x, corners_y):
    sorting_x_asc = np.argsort(corners_x)
    sorting_x_des = sorting_x_asc[::-1]
    sorting_y_asc = np.argsort(corners_y)
    sorting_y_des = sorting_y_asc[::-1]

    # Left border
    x1, x2, y1, y2 = (
        corners_x[sorting_x_asc[0]],
        corners_x[sorting_x_asc[1]],
        corners_y[sorting_x_asc[0]],
        corners_y[sorting_x_asc[1]],
    )
    slope, intcpt = compute_slope_and_intcpt(x1, x2, y1, y2)
    if slope > 0:
        select = y < evaluate_line(slope, intcpt, x)
    else:
        select = y > evaluate_line(slope, intcpt, x)

    # Right border
    x1, x2, y1, y2 = (
        corners_x[sorting_x_des[0]],
        corners_x[sorting_x_des[1]],
        corners_y[sorting_x_des[0]],
        corners_y[sorting_x_des[1]],
    )
    slope, intcpt = compute_slope_and_intcpt(x1, x2, y1, y2)
    if slope > 0:
        select &= y > evaluate_line(slope, intcpt, x)
    else:
        select &= y < evaluate_line(slope, intcpt, x)

    # Lower border
    x1, x2, y1, y2 = (
        corners_x[sorting_y_asc[0]],
        corners_x[sorting_y_asc[1]],
        corners_y[sorting_y_asc[0]],
        corners_y[sorting_y_asc[1]],
    )
    slope, intcpt = compute_slope_and_intcpt(x1, x2, y1, y2)
    if slope > 0:
        select &= y > evaluate_line(slope, intcpt, x)
    else:
        select &= y > evaluate_line(slope, intcpt, x)

    # Upper border
    x1, x2, y1, y2 = (
        corners_x[sorting_y_des[0]],
        corners_x[sorting_y_des[1]],
        corners_y[sorting_y_des[0]],
        corners_y[sorting_y_des[1]],
    )
    slope, intcpt = compute_slope_and_intcpt(x1, x2, y1, y2)
    if slope > 0:
        select &= y < evaluate_line(slope, intcpt, x)
    else:
        select &= y < evaluate_line(slope, intcpt, x)

    return select
