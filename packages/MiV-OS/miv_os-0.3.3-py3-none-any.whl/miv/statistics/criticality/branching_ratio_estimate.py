import numpy as np
from scipy.optimize import curve_fit


def brestimate(asdf2, actrange=None, delayrange=None):
    """
    Brestimate - Branching ratio estimate from sub-sampled spike data.

    Parameters
    ----------
    asdf2 : dict
        A dictionary containing spike data in the 'asdf2' format, with keys:
          - 'raster': list of lists, each sub-list are spike times for one channel
          - 'nchannels': int (number of channels)
          - 'nbins': int (total number of time bins)
          - (other metadata keys are ignored here)
    actrange : array-like, optional
        Range of activity values to consider. Default is 0..asdf2['nchannels'].
    delayrange : array-like, optional
        Range of time delays for the slope fit. Default is 1..100.

    Returns
    -------
    br : float
        Estimated branching ratio for the sub-sampled system using the
        Priesemann and Wilting method (exponential fit).
    slopevals : 1D numpy array
        The slope values found by regressing A(t) vs. A(t + delay) across the
        specified delayrange.
    brsimple : float
        The basic branching ratio estimate assuming no sub-sampling (simply
        regressing A(t) vs. A(t + 1)).

    Notes
    -----
    This is a direct Python translation of the MATLAB function:
    [br, slopevals, brsimple] = brestimate(asdf2, varargin).
    """
    # Handle default values for actrange and delayrange
    if actrange is None:
        # MATLAB default: 0:asdf2.nchannels
        actrange = np.arange(asdf2["nchannels"] + 1)
    if delayrange is None:
        # MATLAB default: 1:100
        delayrange = np.arange(1, 101)

    # ------------------------------------------------------------------
    # 1) Build the total activity vector per bin
    #    In MATLAB: Act(asdf2.raster{iChannel}) = Act(...) + 1
    # ------------------------------------------------------------------
    nbins = asdf2["nbins"]
    nchannels = asdf2["nchannels"]

    Act = np.zeros(nbins, dtype=int)  # will store how many spikes occurred in each bin

    # asdf2['raster'][iChannel] is assumed to be 1-based spike times
    for iChannel in range(nchannels):
        for spike_time in asdf2["raster"][iChannel]:
            # Convert to 0-based index in Python
            # If your data is already 0-based, remove the "-1"
            Act[spike_time - 1] += 1

    # ------------------------------------------------------------------
    # 2) Simple branching ratio (no sub-sampling correction).
    #    This is a regression of A(t+1) = slope * A(t) + intercept,
    #    but we only include time points where A(t) is in 'actrange'.
    # ------------------------------------------------------------------
    At = Act[:-1]
    At1 = Act[1:]

    # Keep only times where A(t) is in actrange
    mask = np.isin(At, actrange)
    At_filtered = At[mask]
    At1_filtered = At1[mask]

    # Linear regression: slope = brsimple
    coeffs = np.polyfit(At_filtered, At1_filtered, 1)
    brsimple = coeffs[0]

    # ------------------------------------------------------------------
    # 3) Compute slope for each delay in delayrange
    #    For each k in delayrange, slope_k = polyfit(A(t), A(t+k))
    # ------------------------------------------------------------------
    slopevals = np.zeros(len(delayrange), dtype=float)

    for i, delay in enumerate(delayrange):
        # A(t) vs. A(t+delay)
        A0 = Act[: nbins - delay]
        A_delayed = Act[delay:]

        # Filter by actrange
        mask = np.isin(A0, actrange)
        A0_filtered = A0[mask]
        A_delayed_filtered = A_delayed[mask]

        # Regression
        c = np.polyfit(A0_filtered, A_delayed_filtered, 1)
        slopevals[i] = c[0]

    # ------------------------------------------------------------------
    # 4) Exponential fit of slopevals vs. delayrange
    #    slope(delay) ~ scale * (base^delay)
    #    We interpret 'base' as the branching ratio
    # ------------------------------------------------------------------
    def expfunc(d, base, scale):
        return scale * (base**d)

    # Initial guesses: [1, 1]
    p0 = [1.0, 1.0]

    # Use scipy curve_fit to fit slopevals(delay) = scale * base^delay
    popt, _ = curve_fit(expfunc, delayrange, slopevals, p0=p0)

    # The first parameter is 'base', i.e. the branching ratio
    br = popt[0]

    return br, slopevals, brsimple


# -----------------------------------------------------------------------------
# Example usage:
#   asdf2 = {
#       'raster': [...],       # list of lists of spike times
#       'nchannels': 10,       # number of channels
#       'nbins': 10000         # total number of time bins
#   }
#   br, slopevals, brsimple = brestimate(asdf2)
#
# This will compute the branching ratio (br), the regression slopes for
# delays 1..100 (slopevals), and the simple branching ratio ignoring sub-sampling
# (brsimple).
# -----------------------------------------------------------------------------
