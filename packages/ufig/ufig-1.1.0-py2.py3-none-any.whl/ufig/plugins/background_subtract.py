# Copyright (c) 2016 ETH Zurich, Institute of Astronomy, Tomasz Kacprzak
# <tomasz.kacprzak@phys.ethz.ch>
"""
Created on Jan 5, 2016
@author: Tomasz Kacprzak

"""

import numpy as np
from ivy.plugin.base_plugin import BasePlugin

__all__ = ["sigma_clip"]


class Plugin(BasePlugin):
    """
    Subtracting background from an image, following recipe in SWarp
    https://www.astromatic.net/pubsvn/software/swarp/trunk/doc/swarp.pdf

    :param bgsubract_n_iter: number if iterations for sigma clipping, higher
                             bgsubract_n_iter means more precision and less speed
    :param bgsubract_n_downsample: use every n_downsample pixel, higher n_downsample
                                   means faster and less accurate background estimation

    :return: Image with background subtracted
    """

    def __call__(self):
        if hasattr(self.ctx, "image_mask"):
            img_flat = self.ctx.image[self.ctx.image_mask].ravel()
        else:
            img_flat = self.ctx.image.ravel()
        data = img_flat[:: self.ctx.parameters.bgsubract_n_downsample]
        data_clipped = sigma_clip(
            data, sig=3, iters=self.ctx.parameters.bgsubract_n_iter, maout="inplace"
        )
        background_level = 2.5 * np.ma.median(data_clipped) - 1.5 * np.ma.mean(
            data_clipped
        )
        self.ctx.image -= background_level

        if hasattr(self.ctx, "image_mask"):
            self.ctx.image[~self.ctx.image_mask] = 0

    def __str__(self):
        return "subtract background"


# modified sigma clip function
def sigma_clip(data, sig=3, iters=1, cenfunc=np.median, varfunc=np.var, maout=False):
    """
    Perform sigma-clipping on the provided data.

    This performs the sigma clipping algorithm - i.e. the data will be iterated
    over, each time rejecting points that are more than a specified number of
    standard deviations discrepant.

    .. note::
        `scipy.stats.sigmaclip` provides a subset of the functionality in this
        function.

    :param data: array-like The data to be sigma-clipped (any shape).
    :param sig: float The number of standard deviations (*not* variances) to use as the
                clipping limit.
    :param iters: int or NoneThe number of iterations to perform clipping for, or None
                  to clip until convergence is achieved (i.e. continue until the last
                  iteration clips nothing).
    :param cenfunc: callable The technique to compute the center for the clipping. Must
                    be a callable that takes in a 1D data array and outputs the central
                    value. Defaults to the median.
    :param varfunc: callable The technique to compute the variance about the center.
                    Must be a callable that takes in a 1D data array and outputs the
                    width estimator that will be interpreted as a variance. Defaults to
                    the variance.
    :param maout: bool or 'copy' If True, a masked array will be returned. If the
                  special string 'inplace', the masked array will contain the same array
                  as `data`, otherwise the array data will be copied.

    :return: filtereddata : `numpy.ndarray` or `numpy.masked.MaskedArray`
        If `maout` is True, this is a masked array with a shape matching the
        input that is masked where the algorithm has rejected those values.
        Otherwise, a 1D array of values including only those that are not
        clipped.
    :return: mask : boolean array
        Only present if `maout` is False. A boolean array with a shape matching
        the input `data` that is False for rejected values and True for all
        others.

    Examples

    This will generate random variates from a Gaussian distribution and return
    only the points that are within 2 *sample* standard deviation from the
    median::

        >>> from astropy.stats import sigma_clip
        >>> from numpy.random import randn
        >>> randvar = randn(10000)
        >>> data,mask = sigma_clip(randvar, 2, 1)

    This will clipping on a similar distribution, but for 3 sigma relative to
    the sample *mean*, will clip until converged, and produces a
    `numpy.masked.MaskedArray`::

        >>> from astropy.stats import sigma_clip
        >>> from numpy.random import randn
        >>> from numpy import mean
        >>> randvar = randn(10000)
        >>> maskedarr = sigma_clip(randvar, 3, None, mean, maout=True)

    """

    data = np.array(data, copy=False)
    oldshape = data.shape
    data = data.ravel()
    data_centered = np.zeros_like(data)

    mask = np.ones(data.size, bool)

    for _ in range(iters):
        std_nsig = np.sqrt(varfunc(data[mask]) * sig**2)
        mean = cenfunc(data[mask])
        data_centered[:] = data[:]
        data_centered -= mean
        mask = data_centered <= std_nsig

    if maout:
        return np.ma.MaskedArray(data, ~mask, copy=maout != "inplace")
    else:
        return data[mask], mask.reshape(oldshape)
