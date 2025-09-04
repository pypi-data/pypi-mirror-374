import numpy as np


def bethelattice(pTrans, nTrials, StopLayer, StopLayerFinal):
    """
    Bethelattice - generates Bethe Lattice data (branching process)

    Generates data from a Bethe Lattice. Each active site in layer i
    can activate up to two new sites in layer i+1 (each with probability pTrans).
    Activity propagates at one time step per layer. The function records:
      1) The full spike rasters (only for avalanches with duration < StopLayer)
      2) The sizes of all avalanches (fullsizes)
      3) The durations of all avalanches (fulldurs)
      4) The shapes of all avalanches (fullshapes)

    Parameters
    ----------
    pTrans : float
        Probability (0 to 1) that activity propagates from an active site
        to each of its two descendants.
    nTrials : int
        Number of independent avalanches (trials) to generate.
    StopLayer : int
        Maximum duration for which individual spiking sites (neuron IDs)
        are tracked in detail. Keep this small (e.g., < 15) to avoid large growth.
    StopLayerFinal : int
        Maximum duration any avalanche can last. Avalanches exceeding StopLayer
        in duration are no longer individually tracked, but their size and shape
        are recorded.

    Returns
    -------
    asdf2 : dict
        Dictionary with keys:
            'raster': list of lists, where each sub-list contains the
                      time bins at which a particular neuron fired.
            'binsize': int (1)
            'nbins': int (total number of time bins in the entire simulation)
            'nchannels': int (total number of possible neurons)
            'expsys': str ('BetheLattice')
            'datatype': str ('Spikes')
            'dataID': str ('ModelX')
    fullsizes : 1D numpy array
        Size of each avalanche (total number of spikes).
    fulldurs : 1D numpy array
        Duration (in layers/time bins) of each avalanche.
    fullshapes : list of 1D numpy arrays
        Shape of each avalanche; element i is an array of length fulldurs[i],
        where each entry is the number of active sites at that time step.
    """
    # Initialize arrays/lists to hold outputs
    AllSpkRecord = [None] * nTrials  # Will hold detailed spike data for each trial
    Durs = np.zeros(nTrials, dtype=int)  # Duration of each trial (if < StopLayer)
    fullshapes = [None] * nTrials  # Shapes for all trials (including > StopLayer)
    fullsizes = np.zeros(nTrials, dtype=int)
    fulldurs = np.zeros(nTrials, dtype=int)

    # Track the maximum layer and neuron index used (for building 'asdf2')
    MaxLayer = 1
    MaxNeuron = 1

    for iTrial in range(nTrials):
        # Print the trial number (as in MATLAB's "iTrial" line).
        # Remove or comment out if not needed.
        print(f"Trial {iTrial + 1}/{nTrials}")

        # ---------------------------
        # First phase: Record details up to StopLayer
        # ---------------------------

        iLayer = 1
        # ActiveListOld stores the set of active sites at the current layer.
        # In MATLAB, it's initialized to [1]. We do the same here.
        ActiveListOld = [1]
        # SpkRecord will store [layer, siteInLayer]
        SpkRecord = [[1, 1]]  # Corresponds to a 2D array in MATLAB: [1,1]

        # Loop until we run out of active sites or reach StopLayer
        while (len(ActiveListOld) > 0) and (iLayer < StopLayer):
            iLayer += 1
            # Generate Bernoulli( pTrans ) for each possible new descendant
            # Each active site can branch into 2 new sites.
            Hits = np.random.rand(2 * len(ActiveListOld)) < pTrans
            HitList = np.where(Hits)[0]  # Indices where Hits is True

            # Convert linear indices in [0, 2*len(ActiveListOld)) to
            # siteInLayer indices by integer division. Also determine
            # whether it's the first or second descendant of that site.
            ActiveListNew = []
            for h in HitList:
                ancestor_index = h // 2  # which ancestor
                # In MATLAB, we had:
                #   EOList = mod(HitList,2)
                #   EOList(EOList == 0) = 2
                # We replicate that logic:
                if (h % 2) == 0:
                    descendant_offset = 1
                else:
                    descendant_offset = 2

                Anc = ActiveListOld[ancestor_index]
                # Next layer's site ID:
                new_site = 2 * (Anc - 1) + descendant_offset
                ActiveListNew.append(new_site)

            # Record spiking: each entry is [layer, new_site]
            for s in ActiveListNew:
                SpkRecord.append([iLayer, s])

            ActiveListOld = ActiveListNew

        # If avalanche stopped before reaching StopLayer, record the spikes
        if len(ActiveListOld) == 0:
            AllSpkRecord[iTrial] = SpkRecord

            # Update max layer/neuron seen so far
            recorded_layers = [row[0] for row in SpkRecord]
            recorded_neurons = [row[1] for row in SpkRecord]

            this_max_layer = max(recorded_layers)
            this_max_layer_neurons = [
                row[1] for row in SpkRecord if row[0] == this_max_layer
            ]
            this_max_neuron = (
                max(this_max_layer_neurons) if len(this_max_layer_neurons) > 0 else 1
            )

            if this_max_layer > MaxLayer:
                MaxLayer = this_max_layer
                MaxNeuron = this_max_neuron
            elif this_max_layer == MaxLayer:
                MaxNeuron = max(MaxNeuron, this_max_neuron)

            # Record this trial's duration
            Durs[iTrial] = max(recorded_layers)
        else:
            # We haven't recorded anything in AllSpkRecord[iTrial]
            # if avalanche continues beyond StopLayer. That's consistent with MATLAB,
            # which only records SpkRecord for shorter avalanches.
            AllSpkRecord[iTrial] = SpkRecord if len(SpkRecord) > 0 else []

        # ---------------------------
        # Second phase: continue (if needed), but don't record each neuron
        # ---------------------------

        # We'll compute the "size" (# of total spikes) and "shape" (# of active sites per layer)
        # so far based on SpkRecord.
        TempSize = len(SpkRecord)  # number of spikes so far
        layers_in_spk = [row[0] for row in SpkRecord]
        unique_layers = np.unique(layers_in_spk)
        # Count how many spikes happened at each layer (the "shape")
        TempShape = np.array(
            [np.sum(layers_in_spk == L) for L in unique_layers], dtype=int
        )

        # Now continue until avalanche dies or we reach StopLayerFinal
        while (len(ActiveListOld) > 0) and (iLayer < StopLayerFinal):
            iLayer += 1
            Hits = np.random.rand(2 * len(ActiveListOld)) < pTrans
            num_hits = np.count_nonzero(Hits)
            TempSize += num_hits

            if num_hits > 0:
                # Extend the shape
                TempShape = np.append(TempShape, num_hits)

            # ActiveListNew is 1..num_hits if num_hits>0, else empty
            if num_hits > 0:
                ActiveListOld = list(range(1, num_hits + 1))
            else:
                ActiveListOld = []

        # Record final avalanche info
        fullsizes[iTrial] = TempSize
        fulldurs[iTrial] = iLayer - 1  # Because iLayer started at 1
        fullshapes[iTrial] = TempShape

    # -----------------------------------------------------------
    # Convert to the asdf2 structure
    # -----------------------------------------------------------

    # Determine the largest layer used
    # MaxLayer is the largest layer encountered in any short avalanche
    # We also have to handle the global numbering of neurons. In MATLAB:
    #   LayerCor(i) = LayerCor(i-1) + 2^(i-1)  (with LayerCor(1) = 0)
    LayerCor = np.zeros(MaxLayer + 1, dtype=int)  # +1 so we can index by layer directly
    for iLayer in range(2, MaxLayer + 1):
        LayerCor[iLayer] = LayerCor[iLayer - 1] + 2 ** (iLayer - 2)

    # Total possible neurons
    # nNeurons = LayerCor(MaxLayer) + 2^(MaxLayer-1)
    nNeurons = LayerCor[MaxLayer] + 2 ** (MaxLayer - 1)

    # Compute the start time for each avalanche
    StartTimes = np.ones(nTrials, dtype=int)
    for i in range(1, nTrials):
        if Durs[i - 1] > 0:
            StartTimes[i] = StartTimes[i - 1] + Durs[i - 1] + 1
        else:
            StartTimes[i] = StartTimes[i - 1]

    # Build the raster: a list of lists, each for one neuron
    raster = [[] for _ in range(nNeurons)]
    # Fill raster times
    for iTrial in range(nTrials):
        spk_record = AllSpkRecord[iTrial]
        if not spk_record:
            continue
        for layer_id, site_id in spk_record:
            # Convert (layer_id, site_id) to global neuron index
            # global_idx = LayerCor[layer_id] + site_id
            # But remember layer_id can range up to MaxLayer, so we index directly.
            global_idx = LayerCor[layer_id] + site_id - 1  # -1 for 0-based in Python
            # The spike occurs at time StartTimes[iTrial] + layer_id
            spike_time = StartTimes[iTrial] + layer_id
            raster[global_idx].append(spike_time)

    # Build asdf2 (a dictionary in Python)
    asdf2 = {
        "raster": raster,
        "binsize": 1,
        # The total number of bins is from time=1 up to the last avalanche's end
        "nbins": int(StartTimes[-1] + Durs[-1] + 1),
        "nchannels": nNeurons,
        "expsys": "BetheLattice",
        "datatype": "Spikes",
        "dataID": "ModelX",
    }

    return asdf2, fullsizes, fulldurs, fullshapes


# ----------------------------------------------------------------------
# Example usage:
# asdf2, fullsizes, fulldurs, fullshapes = bethelattice(
#     pTrans=0.5,
#     nTrials=100,
#     StopLayer=8,
#     StopLayerFinal=10**6
# )
#
# This simulates 100 avalanches. Avalanches shorter than 8 layers
# are fully tracked (spike times & site IDs). Those going longer
# than 8 layers only have size, duration, and shape recorded. Any
# avalanche continuing past 10^6 layers is forcibly stopped.
# ----------------------------------------------------------------------
