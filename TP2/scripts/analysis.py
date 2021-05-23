#!/usr/bin/env python3
"""
Analyze the results of a traceroute with the methods requested
"""
import logging
from pickle import load
from traceroute_utils import (
    split_in_traces, average_rtt_for, filter_most_common_answerer,
    has_icmp_type, known_hops_ratio
)
import config

log = logging.getLogger(__name__)

def count(iterable):
    """
    Poor man's len()
    """
    return sum(1 for _ in iterable)

with open('traceroute.pickle', 'rb') as file:
    queries = load(file)

traces = split_in_traces(queries)

data = {}

for destination, queries_per_ttl in traces.items():
    log.info('=== Processing trace %s -> %s ===', config.START_IP, destination)
    destination_data = {}
    data[destination] = destination_data

    known_hops_ratio(queries_per_ttl)
    average_rtt_per_ttl = []

    for ttl, queries in queries_per_ttl.items():
        ttl_data = { 'ttl': ttl, 'queries': queries }
        destination_data[ttl] = ttl_data

        echo_replies = count(filter(has_icmp_type(0), queries))
        time_exceeded_replies = count(filter(has_icmp_type(11), queries))
        log.info('[ttl=%d] Total = %d, Echo-Reply = %d, Time-Exceeded = %d',
                 ttl, len(queries), echo_replies, time_exceeded_replies)
        ttl_data['replies'] = len(queries)
        ttl_data['echo-replies'] = echo_replies
        ttl_data['time-exceeded-replies'] = time_exceeded_replies

        # Sanity check
        assert len(queries) == echo_replies + time_exceeded_replies

        # Ignoramos los Echo-Reply cómo dice el enunciado
        queries = [q for q in queries if q.answer.type != 0]
        # Si no hay nada para procesar seguimos adelante
        if not queries:
            continue

        average_rtt_all = average_rtt_for(queries)
        log.info('[ttl=%d] average rtt for all answers %f', ttl,
                 average_rtt_all)
        ttl_data['average-rtt-all'] = average_rtt_all

        queries_for_average = filter_most_common_answerer(queries)
        average_rtt = average_rtt_for(queries_for_average)
        most_common_answerer = queries_for_average[0].answer.src
        average_rtt_per_ttl.append((ttl, average_rtt))

        log.info('[ttl=%d] most common answerer %s', ttl, most_common_answerer)
        log.info('[ttl=%d] %d answers from the most common answerer', ttl,
                 len(queries_for_average))
        log.info('[ttl=%d] average rtt for the most common answerer %f', ttl,
                 average_rtt)
        ttl_data['average-rtt'] = average_rtt
        ttl_data['most-common-answerer'] = most_common_answerer
        ttl_data['most-common-answerer-answers'] = queries_for_average

    log.info('=== Inter hop RTT ===')
    inter_hop_data = []
    destination_data['inter-hop'] = inter_hop_data
    for i, (ttl, average) in enumerate(average_rtt_per_ttl[:-1]):
        next_idx = i + 1
        while True:
            next_ttl, next_average = average_rtt_per_ttl[next_idx]
            inter_hop_rtt = next_average - average
            if inter_hop_rtt >= 0:
                break

            log.warning('ttl=%d was longer than ttl=%d !', ttl, next_ttl)
            # Sanity check
            assert ttl < next_ttl

            next_idx += 1
            if next_idx >= len(average_rtt_per_ttl):
                break
        if inter_hop_rtt < 0:
            log.error('No ttl resulted in a positive inter-hop RTT for ttl=%d',
                      ttl)
            continue
        log.info('%d -> %d took %f ms', ttl, next_ttl, inter_hop_rtt)
        inter_hop_data.append({
            'from': ttl,
            'to': next_ttl,
            'time': inter_hop_rtt
        })
