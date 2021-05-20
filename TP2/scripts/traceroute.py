"""
Simplistic traceroute implementation
"""
import logging
from scapy.layers.inet import IP, ICMP, sr, traceroute as __traceroute

log = logging.getLogger(__name__)


def traceroute(dst, timeout=2, verbose=False):
    """Do a traceroute"""
    log.info('Starting traceroute against: %s', dst)

    probe = IP(dst=dst, ttl=(1, 30)) / ICMP()
    answered, _ = sr(probe, verbose=verbose, timeout=timeout)
    if not answered:
        logging.error('Nobody replied!')
        return []
    return answered

def slow_traceroute(dst, timeout=2, verbose=False):
    """Do a traceroute... packet by packet"""
    if isinstance(dst, str):
        dst = [dst]

    answered = []

    for host in dst:
        log.info('Starting traceroute against: %s', host)
        for ttl in range(1, 31):
            log.info('Sending request for ttl=%d', ttl)
            probe = IP(dst=host, ttl=ttl) / ICMP()
            ans, _ = sr(probe, verbose=verbose, timeout=timeout)
            if len(ans) > 0:
                log.info('Received response from %s', ans[0].answer.src)
                answered.append(ans[0])

    if not answered:
        logging.error('Nobody replied!')
    return answered

def scapy_traceroute(dst, timeout=2, verbose=False):
    """Do a traceroute using scapy's own implementation"""
    log.info('Starting traceroute against: %s', dst)

    return __traceroute(dst, timeout=timeout, verbose=verbose)[0].res
