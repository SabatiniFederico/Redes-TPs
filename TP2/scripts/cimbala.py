"""Utilities for foing Cimbala's outlier detection"""

import logging

log = logging.getLogger(__name__)

def mean(values):
    """Returns the average for a list of values"""
    return sum(values) / len(values)

def standard_deviation(values):
    """Returns the corrected sample standard deviation for a list of values"""
    sample_mean = mean(values)
    num = len(values)
    s_squared = sum((value - sample_mean)**2 for value in values) / (num - 1)
    return s_squared ** (1/2)

tau_table = {
    3: 1.1511,
    4: 1.4250,
    5: 1.5712,
    6: 1.6563,
    7: 1.7110,
    8: 1.7491,
    9: 1.7770,
    10: 1.7984,
    11: 1.8153,
    12: 1.8290,
    13: 1.8403,
    14: 1.8498,
    15: 1.8579,
    16: 1.8649,
    17: 1.8710,
    18: 1.8764,
    19: 1.8811,
    20: 1.8853,
    21: 1.8891,
    22: 1.8926,
    23: 1.8957,
    24: 1.8985,
    25: 1.9011,
    26: 1.9035,
    27: 1.9057,
    28: 1.9078,
    29: 1.9096,
    30: 1.9114,
    31: 1.9130,
    32: 1.9146,
    33: 1.9160,
    34: 1.9174,
    35: 1.9186,
    36: 1.9198,
    37: 1.9209,
    38: 1.9220,
}

def cimbala(values):
    """Runs Cimbala's algorithm for outlier detection"""
    detected_outlier = True
    outliers = []
    values = list(values)

    if len(values) not in tau_table:
        log.error('The given sample list is either too small or too large')
        return outliers

    while detected_outlier:
        if len(values) not in tau_table:
            log.error('Too much outliers detected!')
            return outliers

        sample_mean = mean(values)
        sample_st = standard_deviation(values)
        tau = tau_table[len(values)]
        (delta_i, i) = max((abs(x - sample_mean), idx)
                        for (idx, x) in enumerate(values))
        detected_outlier = delta_i > tau * sample_st
        if detected_outlier:
            del values[i]
            outliers.append(i)

    return outliers

def partition_hops(uni):
    """
    Partitions the inter-hop information for a given uni into outliers and not
    outliers
    """
    #pylint: disable-msg=import-outside-toplevel
    from analysis import data
    hops = data[uni]['inter-hop']
    outliers_idxs = cimbala(hop['time'] for hop in hops)
    outliers = [hops[idx] for idx in outliers_idxs]
    normal = [hop for (idx, hop) in enumerate(hops) if idx not in outliers_idxs]
    return { 'outliers': outliers, 'normal': normal }

def partitioned_unis():
    """
    Returns the inter-hop information of each uni partitioned with the
    Cimbala's algorithm
    """
    #pylint: disable-msg=import-outside-toplevel
    from analysis import data
    return {
        uni: partition_hops(uni)
        for uni in data
    }
