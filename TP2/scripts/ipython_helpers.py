# coding: utf-8
"""Small scripts for working with the data collected"""

from analysis import data
unis = list(data.keys())

import socket
def reverse_dns(ip):
    """Hostname for a given IP"""
    try:
        return f'{socket.gethostbyaddr(ip)[0]} [{ip}]'
    except:
        return f'[{ip}]'

import geoip2
import config
db = geoip2.database.Reader(config.GEOLITE_DB_PATH)
def ip_location(ip):
    """Location for a given IP"""
    try:
        loc = db.city(ip)
        return f'{reverse_dns(ip)}, {loc.city.name}, {loc.country.name}'
    except:
        return f'{reverse_dns(ip)}, None, None'

def ttls(uni_data):
    """Returns a generator through the ttls of a given uni_data"""
    return ((ttl, ttl_data)
            for (ttl, ttl_data) in uni_data.items()
            if isinstance(ttl, int))

def ttl_ip_rtts(uni):
    """Returns a dict of TTL -> (set(<ips>), rtt (all), rtt) for a given uni"""
    return {
        ttl:
         (set(p.answer.src for p in ttl_data['queries']),
          ttl_data.get('average-rtt-all'),
          ttl_data.get('average-rtt'))
        for (ttl, ttl_data) in ttls(data[uni])
        if ttl_data.get('average-rtt') is not None
    }

def ttl_location_rtt(uni):
    """Returns a dict of TTL -> (set(<locations>), rtt) for a given uni"""
    return {
        ttl:
         (set(ip_location(p.answer.src) for p in ttl_data['queries']),
          ttl_data.get('average-rtt'))
        for (ttl, ttl_data) in ttls(data[uni])
        if ttl_data.get('average-rtt') is not None
    }

def ttl_location_queries(uni):
    """Returns a dict of TTL -> (set(<locations>), [rtts]) for a given uni"""
    return {
        ttl:
         (set(ip_location(p.answer.src) for p in ttl_data['queries']),
          [(p.answer.time - p.query.time) * 1000
           for p in ttl_data.get('most-common-answerer-answers', [])])
        for (ttl, ttl_data) in ttls(data[uni])
    }

def inter_hops():
    """Returns a dict of Uni -> [{from: TTL, to: TT:L, time: inter-hop-rtt}]"""
    return {
        uni: uni_data['inter-hop']
        for (uni, uni_data) in data.items()
    }

def uni_ratios():
    """Returns the ratios of hops-with-answer/total for each uni"""
    import pickle
    import traceroute_utils
    queries = pickle.load(open('traceroute.pickle', 'rb'))
    return {
        uni: traceroute_utils.known_hops_ratio(uni_queries)
        for (uni, uni_queries) in traceroute_utils.split_in_traces(queries).items()
    }

def uni_lengths():
    """Returns the length of the routes for each uni"""
    return {
        uni: sum(
            1
            for (ttl, data) in ttls(uni_data)
            if any(q.answer.type == 11 for q in data['queries']))
        for (uni, uni_data) in data.items()
    }
