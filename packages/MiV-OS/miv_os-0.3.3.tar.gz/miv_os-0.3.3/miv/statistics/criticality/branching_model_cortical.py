import numpy as np


def cbmodel(
    p, method="seed", nNodes=100, t=10**6, delaydecay=2, spontp=None, nSub=None
):
    """
    Cbmodel - Cortical Branching Model

    Generates a 2D toroidal grid of nodes, each with 4 neighbors. Nodes
    can activate neighbors with probability p. Avalanches are produced
    by one of two methods:
      1) method='seed': discrete avalanches are seeded, separated by
         random 'silent' delays drawn from a power-law distribution.
      2) method='spont': avalanches may overlap in time, with constant
         spontaneous activation probability per node.

    Parameters
    ----------
    p : float
        Transmission probability (0 <= p <= 1) from an active node
        to a non-active neighbor.
    method : str, optional
        Either 'seed' (default) or 'spont'.
    nNodes : int, optional
        Number of nodes in the network (rounded up to form a square).
        Default: 100.
    t : int, optional
        Number of time steps to simulate. Default: 1e6.
    delaydecay : float, optional
        Power-law exponent for inter-avalanche delays in 'seed' mode.
        Default: 2.
    spontp : float, optional
        Spontaneous activation probability per node, per time step.
        Default: 1 / (nNodes^2). Ignored if method='seed' except
        for the case of partial logic in the code.
    nSub : int, optional
        Number of nodes to record (sub-sample). If not specified,
        defaults to nNodes (i.e. record every node).

    Returns
    -------
    asdf2 : dict
        Dictionary with fields:
          - 'raster': list of numpy arrays, one per recorded node,
                      containing the time bins where it was active.
          - 'binsize': int (1)
          - 'nbins': int (t)
          - 'nchannels': int (nNodes)
          - 'expsys': 'CBModel'
          - 'datatype': 'Spikes'
          - 'dataID': 'ModelX'

    Notes
    -----
    This Python function replicates the MATLAB code logic in cbmodel.m.
    The lattice is on a torus so each node has exactly 4 neighbors (up, down,
    left, right), with wrap-around boundaries.
    """
    # ---------------------------------------------------------------------
    # 1) Parse/initialize parameters
    # ---------------------------------------------------------------------
    if spontp is None:
        spontp = 1.0 / (nNodes**2)
    if nSub is None:
        nSub = nNodes

    # Round up nNodes to form a perfect square
    side = int(np.ceil(np.sqrt(nNodes)))
    nNodes = side * side

    # ---------------------------------------------------------------------
    # 2) Construct the adjacency (connectivity) matrix for a toroidal grid
    #    ConMat[i, j] = 1 if node i is a neighbor of node j
    #    Indices are 0-based internally, but we'll keep the same logic as MATLAB.
    # ---------------------------------------------------------------------
    ConMat = np.zeros((nNodes, nNodes), dtype=int)

    def idx(i, j):
        # Convert 2D coords (i, j) to 1D index
        return i * side + j

    for iNode in range(nNodes):
        i = iNode // side
        j = iNode % side

        # up, down, left, right (toroidal)
        up = ((i - 1) % side, j)
        down = ((i + 1) % side, j)
        left = (i, (j - 1) % side)
        right = (i, (j + 1) % side)

        for x, y in [up, down, left, right]:
            ConMat[idx(x, y), iNode] = 1

    # ---------------------------------------------------------------------
    # 3) Prepare the main raster to record activity in sub-sampled nodes
    #    Dimensions: [nSub, t]
    #    We'll collect spike times for each sub-sampled node.
    # ---------------------------------------------------------------------
    raster = np.zeros((nSub, t), dtype=bool)

    # ---------------------------------------------------------------------
    # 4) Helper: Probability conversion vector (for 0..4 active neighbors).
    #    ProbConv[x] = Probability a node becomes active if x neighbors are active.
    #    This implements: 1 - (1 - p)^x
    #    The code in MATLAB incrementally builds it.
    # ---------------------------------------------------------------------
    ProbConv = np.zeros(5, dtype=float)  # for x in [0..4]
    for x in range(1, 5):
        # Probability that a node is activated by at least one of x neighbors
        # each with probability p: 1 - (1 - p)^x
        ProbConv[x] = ProbConv[x - 1] + p - (ProbConv[x - 1] * p)

    # ---------------------------------------------------------------------
    # 5) If nNodes == nSub, we record the entire network directly
    # ---------------------------------------------------------------------
    if nNodes == nSub:
        # If 'seed' method, we do the seed-based avalanche simulation
        if method == "seed":
            # Build discrete-time delays from a truncated power-law distribution
            # dp = cumsum( (1..1000)^(-delaydecay) ), normalized
            distances = np.arange(1, 1001, dtype=float)
            pmf = distances ** (-delaydecay)
            pmf /= pmf.sum()
            dp = np.cumsum(pmf)

            # We iterate over time steps. iT is 1-based in MATLAB, let's do 1-based here too.
            # We'll keep a while loop to mimic the logic exactly.
            iT = 2
            delayFlag = 0  # track whether we just finished an avalanche
            while iT <= t:
                # Check if the network was silent at the previous time step
                if not np.any(
                    raster[:, iT - 2]
                ):  # iT-1 in 1-based => iT-2 in 0-based array
                    # Either seed a new avalanche or skip forward in time
                    if delayFlag == 0:
                        # seed a new avalanche at a random node
                        seed_idx = np.random.randint(nNodes)
                        raster[seed_idx, iT - 1] = True
                        iT += 1
                    else:
                        # skip forward in time by a random delay
                        jump = np.sum(dp < np.random.rand())
                        iT += jump
                        delayFlag = 0
                else:
                    # not silent, so propagate
                    # number of active neighbors for each node
                    active_neighbors = ConMat @ raster[:, iT - 2]
                    # generate new active set
                    # Probability a node is active depends on how many neighbors are active
                    # active_neighbors is in [0..4], so index ProbConv
                    activation_probs = ProbConv[active_neighbors]
                    new_active = np.random.rand(nNodes) < activation_probs
                    raster[:, iT - 1] = new_active
                    delayFlag = 1
                    iT += 1

        elif method == "spont":
            # Overlapping avalanches due to spontaneous activity
            # iT is 1-based
            iT = 2
            while iT <= t:
                active_neighbors = ConMat @ raster[:, iT - 2]
                activation_probs = ProbConv[active_neighbors]
                new_active = np.random.rand(nNodes) < activation_probs
                # incorporate spontaneous activation
                spontaneously_active = np.random.rand(nNodes) < spontp
                new_active = np.logical_or(new_active, spontaneously_active)

                raster[:, iT - 1] = new_active
                iT += 1

        else:
            raise ValueError("method must be 'seed' or 'spont'")

    # ---------------------------------------------------------------------
    # 6) If nNodes > nSub, we only record a random subset of nodes
    # ---------------------------------------------------------------------
    else:
        # Choose which nodes to record
        all_nodes = np.arange(nNodes)
        np.random.shuffle(all_nodes)
        SubList = np.sort(all_nodes[:nSub])

        # Temporary arrays for full network state at each step
        WNPast = np.zeros(nNodes, dtype=bool)
        WNNow = np.zeros(nNodes, dtype=bool)

        if method == "seed":
            # Delay distribution
            distances = np.arange(1, 1001, dtype=float)
            pmf = distances ** (-delaydecay)
            pmf /= pmf.sum()
            dp = np.cumsum(pmf)

            iT = 2
            delayFlag = 0
            while iT <= t:
                if not np.any(WNPast):
                    # If last step was silent
                    if delayFlag == 0:
                        seed_idx = np.random.randint(nNodes)
                        WNNow[seed_idx] = True
                        # Record only sub-sampled nodes
                        raster[:, iT - 1] = WNNow[SubList]
                        # Advance time
                        WNPast[:] = WNNow
                        WNNow[:] = False
                        iT += 1
                    else:
                        jump = np.sum(dp < np.random.rand())
                        iT += jump
                        delayFlag = 0
                else:
                    # Propagate
                    active_neighbors = ConMat @ WNPast
                    activation_probs = ProbConv[active_neighbors]
                    WNNow = np.random.rand(nNodes) < activation_probs

                    # Record only the sub-sampled nodes
                    raster[:, iT - 1] = WNNow[SubList]

                    WNPast[:] = WNNow
                    WNNow[:] = False
                    delayFlag = 1
                    iT += 1

        elif method == "spont":
            iT = 2
            while iT <= t:
                active_neighbors = ConMat @ WNPast
                activation_probs = ProbConv[active_neighbors]
                WNNow = np.random.rand(nNodes) < activation_probs
                # plus spontaneous
                spont_mask = np.random.rand(nNodes) < spontp
                WNNow = np.logical_or(WNNow, spont_mask)

                raster[:, iT - 1] = WNNow[SubList]

                WNPast[:] = WNNow
                WNNow[:] = False
                iT += 1

        else:
            raise ValueError("method must be 'seed' or 'spont'")

    # ---------------------------------------------------------------------
    # 7) Convert to 'asdf2' format
    #    We store a dictionary:
    #      asdf2['raster'] = list of length nSub
    #      each entry is the set of time bins where that sub-node is active
    # ---------------------------------------------------------------------
    asdf2 = {
        "binsize": 1,
        "nbins": t,
        "nchannels": nNodes,
        "expsys": "CBModel",
        "datatype": "Spikes",
        "dataID": "ModelX",
        "raster": [],
    }

    # Fill the raster times for each of the nSub recorded nodes
    # In MATLAB, we do find(raster(iNode,:))
    # We'll keep it 1-based to match typical MATLAB indexing in asdf2.
    for iNode in range(nSub):
        spike_times = np.where(raster[iNode, :])[0] + 1
        asdf2["raster"].append(spike_times)

    return asdf2


# -----------------------------------------------------------------------------
# Example Usage:
#   asdf2 = cbmodel(p=0.25, nNodes=200)
#   This simulates a 200-node (actually 14,400 after rounding up to 120^2)
#   cortical branching model, recording activity from all nodes, using
#   the default 'seed' method for t=1e6 time steps.
#
#   For spontaneous activations instead:
#   asdf2 = cbmodel(p=0.25, method='spont', nNodes=200, t=10_000)
#
#   To record only a 50-node subsample:
#   asdf2 = cbmodel(p=0.25, nNodes=200, nSub=50)
# -----------------------------------------------------------------------------
