
## Matthew A. Dorsey
## @mad-mpikg
## Max Planck Institute for Colloids and Interfacial Sciences
## 2025.08.19
## contains methods for smoothing, fitting and / or filtering noisy, non-linear data, including calculating derivates, finding maxima, minima, etc.

## PACKAGES
# native / conda packages
import sys, os, math
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm
from scipy import interpolate # spline for curve fitting
from scipy import signal as sig # used for monotonic curve smoothing


## PARAMETERS
# none


## METHODS
# converts linear scale to log scale
def lin2log(x, base = 10):
    # docstring
    """
    lin2log(x, base = 10)

    converts any real, non-negative value to a logarithmic scale.

    Parameters
    ----------
    x : float, int
        any real non-negative number to convert to log scale
    base : float, int
        any real non-negative number to use as log base

    Returns
    -------
    float
        math.log(x) / math.log(base), where math.log is already a base
        10 logarithmic operation
    """

    # perform operation
    # TODO :: vectorize operation
    return math.log(x) / math.log(base)

# converts log scale to linear scale
def log2lin (x, base = 10):
    # docstring
    """
    lin2log(x, base = 10)

    converts any real, non-negative number from a logarithmic scale to a linear scale

    Parameters
    ----------
    x : float, int
        any real non-negative and nonzero number
    base : float, int
        any real non-negative and nonzero number that represents the
        base of the log scale the number already exists on

    Returns
    -------
    float
        math.pow(base, x), or base ** x
    """

    # perform operation
    # TODO :: vectorize operation
    return math.pow(base, x)

# uses Savitzky-Golay filter to fit noisy, non-linear data
def poly_smooth (x = None, y = None, order = 2, window = None, n_fit = None):
    """
    sgfilter(x = None, y = None, log = False, order = 2, window = None)

    apply to Savitzky-Golay to noisy or nonlinear data

    Parameters
    ----------
    x : list, array
        1D array or list which represents the x-values of filtered
        data, should be equally spaced
    y : list, array
        1D array or list which represents the y-values of filtered
        data, should be same length as x
    order : int
        polynomial order to apply to filtered data, cannot be less
        than 2
    window : int
        integer no greater than len(x), number of data points to feed
        to sg filter. When window < len(x), multiple sg filters are
        applied and duplicates are averaged
    n_fit : int
        number of data points to generate. if unspecified, n_int =
        len(x)

    Returns
    -------
    x0_filter : list
        linearly spaced set of x-values with length n_int
    y0_filter : list
        filtered set of y_vales with length n_int
    """

    if window is None:
        window = len(x)

    if n_fit is None:
        n_fit = len(x)

    # convert data to logscale if requested
    x0 = [] # zero order x-data
    y0 = [] # zero order y-data
    for i in range(len(x)):
        x0.append(x[i])
        y0.append(y[i])

    # initialize the arrays for sg filter averaging
    sg_x_cum = []
    sg_x_count = []
    sg_y_cum = []
    sg_y_count = []
    for i in range(n_fit):
        sg_x_cum.append((i / (n_fit - 1)) * (max(x0) - min(x0)) + min(x0))
        sg_x_count.append(0)
        sg_y_cum.append(0.)
        sg_y_count.append(0)

    for i in range(len(x0) - (window - 1)):
        # apply sg filter to subset of data which corresponds to window length # generate data set within window
        x0_fit = [] # zero order x-data corresponding to window
        y0_fit = [] # zero order y-data corresponding to window

        # parse subset of filtered data from set
        for j in range(window):
            x0_fit.append(x0[i + j])
            y0_fit.append(y0[i + j])

        # apply the sg filter
        # y0_filter = sig.savgol_filter(y0_fit, window, order)
        # print(sig.savgol_coeffs(y0_fit, window, order))
        p = np.polyfit(x0_fit, y0_fit, order)
        p = np.poly1d(p)

        # cumulate the filter for averaging
        for j in range(n_fit):
            # only accumulate if x0_fit is within the range
            if sg_x_cum[j] <= max(x0_fit) and sg_x_cum[j] >= min(x0_fit):
                sg_y_cum[j] += p(sg_x_cum[j])
                sg_y_count[j] += 1

    # average values post filtering
    for i in range(len(sg_x_cum)):
        # sg_x_cum[i] = sg_x_cum[i] / sg_x_count[i]
        sg_y_cum[i] = sg_y_cum[i] / sg_y_count[i]

    # if conversted to log scale, return to linear scale
    x0_filter = []
    y0_filter = []
    for i in range(len(sg_x_cum)):
        x0_filter.append(sg_x_cum[i])
        y0_filter.append(sg_y_cum[i])

    # return y data
    return x0_filter, y0_filter


