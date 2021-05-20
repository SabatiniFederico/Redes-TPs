"""Script for generating a traceroute.dat with our traceroute impl"""
from traceroute import traceroute
from traceroute_utils import trace_to_lines, lines_to_text
import config

# Do NUMTRACES traces per university
traces = [
    query
    for _ in range(config.NUMTRACES)
    for query in traceroute(config.UNIVERSITIES)
]

lines = trace_to_lines(traces)
text = lines_to_text(lines)

with open('traceroute.dat', 'w+') as file:
    file.write(text)
