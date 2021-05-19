"""Utilities for plotting traceroutes on a map"""
from logging import Logger

from scapy.all import *

import geoip2.database
import geoip2.errors
import config

log_runtime = Logger('world_plot')

def trace_to_lines(self):
    """Display traceroute results on a world map."""

    # Open & read the GeoListIP2 database
    try:
        db = geoip2.database.Reader(config.GEOLITE_DB_PATH)
    except Exception:
        log_runtime.error(
            "Cannot open geoip2 database at %s",
            conf.geoip_city
        )
        return []

    # Regroup results per trace
    ips = {}
    rt = {}
    ports_done = {}
    for s, r in self.res:
        ips[r.src] = None
        if s.haslayer(TCP) or s.haslayer(UDP):
            trace_id = (s.src, s.dst, s.proto, s.dport)
        elif s.haslayer(ICMP):
            trace_id = (s.src, s.dst, s.proto, s.type)
        else:
            trace_id = (s.src, s.dst, s.proto, 0)
        trace = rt.get(trace_id, { 0: config.START_IP, 99: s.dst })
        if not r.haslayer(ICMP) or r.type != 11:
            if trace_id in ports_done:
                continue
            ports_done[trace_id] = None
        trace[s.ttl] = r.src
        rt[trace_id] = trace

    # Get the addresses locations
    trt = {}
    for trace_id in rt:
        trace = rt[trace_id]
        loctrace = []
        for i in range(max(trace)+1):
            ip = trace.get(i, None)
            if ip is None:
                continue
            # Fetch database
            try:
                sresult = db.city(ip)
            except geoip2.errors.AddressNotFoundError:
                print('Lookup failed for', ip)
                continue
            loctrace.append((sresult.location.longitude, sresult.location.latitude))  # noqa: E501
        if loctrace:
            trt[trace_id] = loctrace

    lines = set()

    # Split traceroute measurement
    for trc in trt.values():
        # Gather mesurments data
        data_lines = [(trc[i], trc[i + 1]) for i in range(len(trc) - 1)]
        lines.update(data_lines)

    # Return the drawn lines
    return lines

def lines_to_text(lines):
    """Dump the lines in a format that can be consumed by gnuplot"""
    text = ''
    for (x1, y1), (x2, y2) in lines:
        text += f'{x1:12} {y1:12}\n{x2:12} {y2:12}\n\n'
    return text
