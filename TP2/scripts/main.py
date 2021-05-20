#!/usr/bin/env python3
"""Script for generating a traceroute.dat with our traceroute impl"""
from pickle import dump
import config

traces = [
    query
    for _ in range(config.NUMTRACES)
    for query in config.traceroute(config.UNIVERSITIES)
]

with open('traceroute.pickle', 'wb+') as file:
    dump(traces, file)
