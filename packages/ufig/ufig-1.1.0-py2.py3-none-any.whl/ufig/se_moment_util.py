import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger

LOGGER = logger.get_logger(__file__)


def moments_to_distortion(x2, y2, xy):
    """
    Convert SExtractor second moments to ellipticity parameters.

    :param x2: Second moments in x-direction (X2WIN_IMAGE from SExtractor)
    :param y2: Second moments in y-direction (Y2WIN_IMAGE from SExtractor
    :param xy: Cross moments (XYWIN_IMAGE from SExtractor)
    :return: e1, e2, r50: Ellipticity components and effective radius
    """
    x2 = np.asarray(x2)
    y2 = np.asarray(y2)
    xy = np.asarray(xy)

    e1 = (x2 - y2) / (x2 + y2)
    e2 = (2.0 * xy) / (x2 + y2)
    r50 = np.sqrt((x2 + y2) / (2.0 * np.log(2)))
    return e1, e2, r50


def get_se_cols(cat):
    # add columns
    list_new_cols = ["se_mom_e1:f4", "se_mom_e2:f4", "se_mom_fwhm:f4", "se_mom_win:f4"]

    cat = at.ensure_cols(rec=cat, names=list_new_cols)

    # Shape from momemts
    (
        cat["se_mom_e1"],
        cat["se_mom_e2"],
        cat["se_mom_fwhm"],
    ) = moments_to_distortion(
        x2=cat["X2WIN_IMAGE"], y2=cat["Y2WIN_IMAGE"], xy=cat["XYWIN_IMAGE"]
    )
    cat["se_mom_win"] = cat["FLUX_RADIUS"] * 2 / np.sqrt(8 * np.log(2))
    return cat
