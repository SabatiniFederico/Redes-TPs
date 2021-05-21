#!/usr/bin/env python3
"""
Convert the results of a traceroute to a set of lines useful for plotting
"""
from pickle import load
from traceroute_utils import trace_to_lines, lines_to_text
import ip_to_domain
import config

with open('traceroute.pickle', 'rb') as file:
    queries = load(file)

# Usar sólo las rutas a analizar
queries = [
    q
    for q in queries
    if ip_to_domain.mapping[q.query.dst] in config.PLOTTED_UNIVERSITIES
]

lines = trace_to_lines(queries)
text = lines_to_text(lines)

with open('traceroute.dat', 'w+') as file:
    file.write(text)
