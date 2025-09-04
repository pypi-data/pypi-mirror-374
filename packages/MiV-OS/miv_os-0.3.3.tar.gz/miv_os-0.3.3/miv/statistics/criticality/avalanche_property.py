import numpy as np


def avprops(asdf2, ratio=False, fingerprint=False):
    """
    Avprops - Compute avalanche properties from a spike raster in 'asdf2' format.

    Neuronal avalanches are defined as contiguous active bins separated by
    at least one bin of quiescence. By default, returns avalanche size,
    duration, and shape. If 'ratio' is True, also computes a simple
    branching ratio. If 'fingerprint' is True, stores a record of the
    individual events making up each avalanche, grouped by avalanche size.

    Parameters
    ----------
    asdf2 : dict
        A dictionary with keys (typical 'asdf2' format):
          - 'raster': list of 1D arrays (or lists), where each entry i
            contains the time bins (1-based) at which channel i fired.
          - 'nbins', 'nchannels', etc. (not strictly required here except 'raster').
    ratio : bool, optional
        If True, compute the average branching ratio for each avalanche
        and store it in 'branchingRatio'.
    fingerprint : bool, optional
        If True, store a "fingerPrint" of all events in each avalanche,
        grouped by avalanche size.

    Returns
    -------
    Avalanche : dict with keys
        - 'duration': 1D numpy array, avalanche durations (in # of active bins).
        - 'size': 1D numpy array, total number of events in each avalanche.
        - 'shape': list of 1D numpy arrays, each containing the per-bin
          activity (histogram of spike counts across the avalanche time bins).
        - 'branchingRatio': 1D numpy array (if ratio=True), average ratio
          sum( shape[t+1]/shape[t] ) / duration.
        - 'fingerPrint': dict (if fingerprint=True). For each key = avalanche size s,
          the value is a list of 2 x (#events) arrays describing the avalanche
          events (first row = event times, second row = channel IDs).
    """
    # ----------------------------------------------------------------------
    # 1) Collect all event times and their corresponding channels
    # ----------------------------------------------------------------------
    all_times = []
    all_sites = []
    for ch_idx, spike_times in enumerate(asdf2["raster"], start=1):
        # 'spike_times' are the time bins (1-based) at which channel 'ch_idx' fired
        all_times.extend(spike_times)
        all_sites.extend([ch_idx] * len(spike_times))

    if len(all_times) == 0:
        raise ValueError("Empty raster: no spikes detected, no avalanches.")

    # Convert to NumPy arrays
    all_times = np.array(all_times, dtype=int)
    all_sites = np.array(all_sites, dtype=int)

    # ----------------------------------------------------------------------
    # 2) Sort events by time
    # ----------------------------------------------------------------------
    sort_idx = np.argsort(all_times)
    all_times = all_times[sort_idx]
    all_sites = all_sites[sort_idx]

    # We keep a (2 x #events) array for convenience
    sorted_events = np.vstack((all_times, all_sites))

    # ----------------------------------------------------------------------
    # 3) Identify avalanche boundaries
    #    We say that if consecutive events differ by more than 1 bin,
    #    there's a gap => a new avalanche starts.
    # ----------------------------------------------------------------------
    diff_times = np.diff(all_times)
    # In MATLAB: diffTimes(diffTimes == 1) = 0; avBoundaries = find(diffTimes)
    # effectively means 'any gap > 1 is a boundary.'
    diff_times[diff_times == 1] = 0  # so only differences != 0 (i.e., >1) remain
    boundaries = np.where(diff_times != 0)[0]  # 0-based indices in diff_times
    # Append the last event index so we can slice the final avalanche
    boundaries = np.append(boundaries, len(all_times) - 1)
    n_avs = len(boundaries)

    # ----------------------------------------------------------------------
    # 4) Prepare outputs
    # ----------------------------------------------------------------------
    # We'll store results in a dictionary 'Avalanche'
    Avalanche = {}

    # Each avalanche has a 'duration', 'size', and 'shape' entry
    Avalanche["duration"] = np.zeros(n_avs, dtype=int)
    Avalanche["size"] = np.zeros(n_avs, dtype=int)
    Avalanche["shape"] = [None] * n_avs  # list of arrays

    # Optional branching ratio
    if ratio:
        Avalanche["branchingRatio"] = np.zeros(n_avs, dtype=float)

    # Optional fingerprint: a dictionary keyed by avalanche size => list of arrays
    if fingerprint:
        Avalanche["fingerPrint"] = {}

    # ----------------------------------------------------------------------
    # 5) Loop over each avalanche, compute properties
    # ----------------------------------------------------------------------
    av_start = 0
    for iAv in range(n_avs):
        av_end = boundaries[iAv]  # inclusive index for this avalanche
        # Slice of events for this avalanche
        # Note: Python slicing is [start, end+1), so we do av_end+1
        these_events = sorted_events[:, av_start : av_end + 1]

        # 5a) shape: histogram of how many events occur at each time bin
        #     i.e., for each unique time in these_events, how many spikes occurred?
        times_in_avalanche = these_events[0, :]  # the row of times
        unique_times = np.unique(times_in_avalanche)
        # shape array: per unique time, number of events
        shape_arr = np.array([np.sum(times_in_avalanche == ut) for ut in unique_times])

        # Store shape
        Avalanche["shape"][iAv] = shape_arr

        # 5b) duration = number of distinct (active) time bins
        Avalanche["duration"][iAv] = len(unique_times)

        # 5c) size = total number of events
        Avalanche["size"][iAv] = these_events.shape[1]

        # 5d) fingerprint (optional)
        if fingerprint:
            s = Avalanche["size"][iAv]  # avalanche size
            if s not in Avalanche["fingerPrint"]:
                Avalanche["fingerPrint"][s] = []
            # store the 2 x (#events) array for this avalanche
            Avalanche["fingerPrint"][s].append(these_events)

        # 5e) branching ratio (optional)
        if ratio:
            if len(shape_arr) > 1:
                # Sum of shape[t+1]/shape[t], then divide by # of time bins
                ratio_val = np.sum(shape_arr[1:] / shape_arr[:-1])
                ratio_val /= float(Avalanche["duration"][iAv])
                Avalanche["branchingRatio"][iAv] = ratio_val
            else:
                # If the avalanche only has 1 time bin, ratio = 0
                Avalanche["branchingRatio"][iAv] = 0.0

        # Move to next avalanche
        av_start = av_end + 1

    return Avalanche


# --------------------------------------------------------------------------
# Example Usage:
#   # Suppose asdf2 is a dict with a 'raster' key:
#   # asdf2['raster'] = [
#   #    np.array([2, 3, 10]),   # channel 1 spikes
#   #    np.array([3, 11]),      # channel 2 spikes
#   #    ...
#   # ]
#
#   # We can call:
#   Av = avprops(asdf2, ratio=True)
#   print(Av['size'])          # array of avalanche sizes
#   print(Av['duration'])      # array of avalanche durations
#   print(Av['shape'][0])      # shape array of the first avalanche
#   print(Av['branchingRatio'])# array of mean branching ratios
#
#   # For fingerprints:
#   Av = avprops(asdf2, fingerprint=True)
#   # Av['fingerPrint'][s] is a list of 2 x s arrays, one for each avalanche of size s.
# --------------------------------------------------------------------------
