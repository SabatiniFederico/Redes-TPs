#!/usr/bin/env python3
import sys
import config
from scapy.all import *
from time import *

from geoip2.database import Reader as geoip
from os import environ as env

ips = {}
responses = {}
db = geoip(config.GEOLITE_DB_PATH)

START_IP_LOC = db.city(config.START_IP).location
START_IP_LONG = START_IP_LOC.longitude
START_IP_LAT = START_IP_LOC.latitude

for i in range(2):
    print()
    for ttl in range(1,25):
        probe = IP(dst=sys.argv[1], ttl=ttl) / ICMP()
        t_i = time()
        ans = sr1(probe, verbose=False, timeout=0.8)
        t_f = time()
        rtt = (t_f - t_i)*1000
        if ans is not None:
            ip = ans.src

            if ttl not in responses:
                responses[ttl] = []
                responses[ttl].append((ip, rtt))
            if ttl in responses:
                print(ttl, responses[ttl])
            if ip not in ips:
                try:
                    loc = db.city(ip).location
                    ips[ip] = (loc.longitude, loc.latitude)
                except: pass

print(f'{START_IP_LONG:5} {START_IP_LAT:5}')
for (long, lat) in ips.values():
  print(f'{long:5} {lat:5}')
