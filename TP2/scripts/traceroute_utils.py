"""
Utilities for plotting traceroutes on a map and doing analysis of a traceroute
"""
import logging

from scapy.layers.inet import TCP, UDP, ICMP

import geoip2.database
import geoip2.errors

import ip_to_domain
import config

log = logging.getLogger(__name__)

def split_in_traces(answered_queries):
    """
    Given an List of QueryAnswer objects returns the traces found

    The result is a dictionary with the following structure:

    {
        <destination-domain-0>: {
            <ttl-0>: [<query-answer-0>, <query-answer-1>, ...],
            <ttl-1>: [...],
            ...
        },
        <destination-domain-1>: { ... },
        ...
    }

    If there was no QueryAnswer object for a given ttl then the result will not
    have the corresponding entry.

    Code based on scapy.layers.inet.TracerouteResult.world_trace
    """
    # Regroup results per trace
    traces = {}
    for query_answer in answered_queries:
        sent, _ = query_answer
        trace_id = ip_to_domain.mapping.get(sent.dst, sent.dst)
        trace = traces.get(trace_id, {})
        trace_ttl = trace.get(sent.ttl, [])
        trace_ttl.append(query_answer)
        trace[sent.ttl] = trace_ttl
        traces[trace_id] = trace

    # Order by ttl
    for trace_id, trace in traces.items():
        traces[trace_id] = dict(sorted(trace.items()))
    return traces

def rtt_for(query_answer):
    """
    Given a QueryAnswer object returns the RTT (in millisenconds)
    """
    return (query_answer.answer.time - query_answer.query.time) * 1000

def average_rtt_for(answered_queries):
    """
    Given a list of QueryAnswer objects returns average RTT (in millisenconds)
    """
    return sum(map(rtt_for, answered_queries)) / len(answered_queries)

def filter_most_common_answerer(answered_queries):
    """
    Given a list of QueryAnswer objects returns a list with only the
    QueryAnswer objects with responses from the most common source in the
    answers
    """
    grouped_by_answerer = {}
    for query_answer in answered_queries:
        answerer = query_answer.answer.src
        list_for_answerer = grouped_by_answerer.get(answerer, [])
        list_for_answerer.append(query_answer)
        grouped_by_answerer[answerer] = list_for_answerer

    def add_length(list_for_answerer):
        return (len(list_for_answerer), list_for_answerer)

    biggest_length = max(map(add_length, grouped_by_answerer.values()))

    return biggest_length[1]

def known_hops_ratio(queries_grouped_by_ttl):
    """
    Given a list of queries grouped by ttl returns the ratio of TTLs with some
    time-exceeded answer.

    The last "valid" ttl is the previous to the first ttl with only echo-reply
    answers (and non-zero answers) or the last ttl with Time-exceeded answers.
    """

    ttls_with_only_echo_reply = filter(
        lambda kv: all(map(has_icmp_type(0), kv[1])),
        queries_grouped_by_ttl.items()
    )
    ttls_with_time_exceeded = filter(
        lambda kv: any(map(has_icmp_type(11), kv[1])),
        queries_grouped_by_ttl.items()
    )
    # We will use it more than one time so just run the generator
    ttls_with_time_exceeded = list(ttls_with_time_exceeded)
    last_valid_ttl = next(ttls_with_only_echo_reply, None)
    if last_valid_ttl is not None:
        last_valid_ttl = last_valid_ttl[0] - 1
    else:
        last_valid_ttl = max(ttls_with_time_exceeded)[0]

    log.info('Last valid TTL: %d', last_valid_ttl)
    log.info('TTLs with some time exceeded answers: %d',
             len(ttls_with_time_exceeded))
    log.info('Ratio answered/total: %f',
             len(ttls_with_time_exceeded) / last_valid_ttl)

    return len(ttls_with_time_exceeded) / last_valid_ttl

def has_icmp_type(icmp_type):
    """
    Given an ICMP type returns a predicate testing for that type in a
    QueryAnswer object
    """
    def pred(query_ans):
        return query_ans.answer.type == icmp_type
    return pred

def trace_to_lines(answered_queries):
    """Display traceroute results on a world map."""

    # Open & read the GeoListIP2 database
    db = geoip2.database.Reader(config.GEOLITE_DB_PATH)

    # Regroup results per trace
    ips = {}
    rt = {}
    for s, r in answered_queries:
        ips[r.src] = None
        if s.haslayer(TCP) or s.haslayer(UDP):
            trace_id = (s.src, s.dst)
        elif s.haslayer(ICMP):
            trace_id = (s.src, s.dst)
        else:
            trace_id = (s.src, s.dst)
        trace = rt.get(trace_id, {
            0: set([config.START_IP]),
            99: set([s.dst])
        })
        trace_ttl = trace.get(s.ttl, set())
        trace_ttl.add(r.src)
        trace[s.ttl] = trace_ttl
        rt[trace_id] = trace

    # Get the addresses locations
    trt = {}
    for trace_id in rt:
        trace = rt[trace_id]
        loctrace = []
        for i in range(max(trace)+1):
            ips_at_ttl = trace.get(i, None)
            if ips_at_ttl is None:
                continue
            locations_at_ttl = set()
            for ip in ips_at_ttl:
                # Fetch database
                try:
                    ip_loc = db.city(ip).location
                except geoip2.errors.AddressNotFoundError:
                    log.warning('Lookup failed for %s', ip)
                    continue
                locations_at_ttl.add((ip_loc.longitude, ip_loc.latitude, ip))
            if locations_at_ttl:
                loctrace.append(locations_at_ttl)
        if loctrace:
            trt[trace_id] = loctrace

    lines = set()

    # Split traceroute measurement
    for trace, trc in trt.items():
        # Gather mesurments data
        log.info('Processing lines for trace: %s -> %s', trace[0], trace[1])
        for i in range(len(trc) - 1):
            for (from_long, from_lat, from_ip)  in trc[i]:
                from_point = (from_long, from_lat)
                from_city = db.city(from_ip)
                from_loc = f'{from_city.city.name}, {from_city.country.name}'
                for (to_long, to_lat, to_ip) in trc[i+1]:
                    to_point = (to_long, to_lat)
                    to_city = db.city(to_ip)
                    to_loc = f'{to_city.city.name}, {to_city.country.name}'
                    if from_point != to_point:
                        log.info('[%d] %s (%s) -> %s (%s)', i, from_loc,
                                 from_ip, to_loc, to_ip)
                        lines.add((from_point, to_point))

    # Return the drawn lines
    return lines

def lines_to_text(lines):
    """Dump the lines in a format that can be consumed by gnuplot"""
    text = ''
    for (x, y), (xx, yy) in lines:
        text += f'{x:12} {y:12}\n{xx:12} {yy:12}\n\n'
    return text
