"""Simplistic traceroute implementation"""
from scapy.layers.inet import IP, ICMP, sr

def traceroute(dst, timeout=2, verbose=True):
    """Do a traceroute"""
    probe = IP(dst=dst, ttl=(1, 30)) / ICMP()
    answered, _ = sr(probe, verbose=verbose, timeout=timeout)
    if answered is None:
        raise RuntimeError('Nobody replied!')
    return answered
