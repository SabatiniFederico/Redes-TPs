"""Script for generating a traceroute.dat file with scapy traceroute impl"""
from scapy.all import traceroute
import traceroute_utils
import config

trace = traceroute(config.UNIVERSITIES)
lines = traceroute_utils.trace_to_lines(trace[0])
lines_text = traceroute_utils.lines_to_text(lines)

with open('traceroute.dat', 'w+') as file:
  file.write(lines_text)
