#!/usr/bin/env python3
"""
Convert the results of a traceroute to a set of lines useful for plotting
"""
import logging
from pickle import load
import geoip2
from traceroute_utils import trace_to_lines, lines_to_text
import ip_to_domain
import config

log = logging.getLogger(__name__)

with open('traceroute.pickle', 'rb') as file:
    queries = load(file)

for university in config.PLOTTED_UNIVERSITIES:
    queries_for_uni = [
        q
        for q in queries
        if ip_to_domain.mapping[q.query.dst] == university
    ]

    lines = trace_to_lines(queries_for_uni)
    text = lines_to_text(lines)

    with open(f'{university}.dat', 'w+') as file:
        file.write(text)

with open('universities.dat', 'w+') as file:
    db = geoip2.database.Reader(config.GEOLITE_DB_PATH)
    for university in config.PLOTTED_UNIVERSITIES:
        any_query_ip = next(
            q.query.dst
            for q in queries
            if ip_to_domain.mapping[q.query.dst] == university
        )
        ip_loc = db.city(any_query_ip).location
        log.info('Location for %s is (%f, %f)', university, ip_loc.longitude,
                 ip_loc.latitude)
        file.write(
            f'{ip_loc.longitude:12} {ip_loc.latitude:12} {university:12}\n'
        )
