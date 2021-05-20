#!/usr/bin/env python3
"""
Convert the results of a traceroute to a set of lines useful for plotting
"""
from pickle import load
from traceroute_utils import trace_to_lines, lines_to_text

with open('traceroute.pickle', 'rb') as file:
    traces = load(file)

lines = trace_to_lines(traces)
text = lines_to_text(lines)

with open('traceroute.dat', 'w+') as file:
    file.write(text)
