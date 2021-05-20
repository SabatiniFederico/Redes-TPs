"""Script for generating a traceroute.dat file with scapy traceroute impl"""
from scapy.layers.inet import traceroute
import traceroute_utils
import config

traces = [
    query
    for _ in range(config.NUMTRACES)
    for query in traceroute(config.UNIVERSITIES)[0].res
]
lines = traceroute_utils.trace_to_lines(traces)
lines_text = traceroute_utils.lines_to_text(lines)

with open('traceroute.dat', 'w+') as file:
    file.write(lines_text)
