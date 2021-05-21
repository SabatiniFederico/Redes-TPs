#!/usr/bin/env python3
"""
Analyze the results of a traceroute with the methods requested
"""
import logging
from pickle import load
from traceroute_utils import (
    split_in_traces, average_rtt_for, filter_most_common_answerer
)
import ip_to_domain
import config

log = logging.getLogger(__name__)

with open('traceroute.pickle', 'rb') as file:
    queries = load(file)
    # Filtrar los que fueron respuestas exitosas
    queries = [query for query in queries if query.answer.type != 0]

traces = split_in_traces(queries)

for destination, queries_per_ttl in traces.items():
    log.info('=== Processing trace %s -> %s (%s) ===', config.START_IP,
             destination, ip_to_domain.mapping[destination])
    average_rtt_per_ttl = []
    for ttl, queries in sorted(queries_per_ttl.items()):
        log.info('[ttl=%d] %d queries got answered', ttl, len(queries))
        log.info('[ttl=%d] average rtt for all answers %f', ttl,
                 average_rtt_for(queries))

        queries_for_average = filter_most_common_answerer(queries)
        average_rtt = average_rtt_for(queries_for_average)
        most_common_answerer = queries_for_average[0].answer.src
        average_rtt_per_ttl.append((ttl, average_rtt))

        log.info('[ttl=%d] most common answerer %s', ttl, most_common_answerer)
        log.info('[ttl=%d] %d answers from the most common answerer', ttl,
                 len(queries_for_average))
        log.info('[ttl=%d] average rtt for the most common answerer %f', ttl,
                 average_rtt)

    log.info('=== Inter hop RTT ===')
    for i, (ttl, average) in enumerate(average_rtt_per_ttl[:-1]):
        next_idx = i + 1
        while True:
            next_ttl, next_average = average_rtt_per_ttl[next_idx]
            inter_hop_rtt = next_average - average
            if inter_hop_rtt >= 0:
                break

            log.warning('ttl=%d was longer than ttl=%d !', ttl, next_ttl)
            next_idx += 1
            if next_idx >= len(average_rtt_per_ttl):
                break
        if inter_hop_rtt < 0:
            log.error('No ttl resulted in a positive inter-hop RTT for ttl=%d',
                      ttl)
            continue
        log.info('%d -> %d took %f ms', ttl, next_ttl, inter_hop_rtt)
