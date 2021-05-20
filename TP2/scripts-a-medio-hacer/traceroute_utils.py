"""
Utilities for plotting traceroutes on a map and doing analysis of a traceroute

El código debe permitir:
* Calcular el RTT para cada paquete que se haya obtenido respuesta
* Se recomienda enviar como mínimo 30 paquetes para un mismo TTL (ráfagas)
* Analizar las respuestas para distinguir entre varias rutas
* Calcular el un RTT promedio por TTL
    - en caso de tener respuestas de múltiples IPs usar la que haya respondido
      más veces
* Calcular el RTT entre salto restando los valores de RTT de saltos sucesivos.
  - si da negativo calcularlo con el próximo salto que de positivo.
"""
import logging

from scapy.layers.inet import TCP, UDP, ICMP

import geoip2.database
import geoip2.errors
import config

log = logging.getLogger(__name__)

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
                locations_at_ttl.add((ip_loc.longitude, ip_loc.latitude))
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
            for from_ in trc[i]:
                for to_ in trc[i+1]:
                    if from_ != to_:
                        log.info('[%d] %s -> %s', i, from_, to_)
                        lines.add((from_, to_))

    # Return the drawn lines
    return lines

def lines_to_text(lines):
    """Dump the lines in a format that can be consumed by gnuplot"""
    text = ''
    for (x, y), (xx, yy) in lines:
        text += f'{x:12} {y:12}\n{xx:12} {yy:12}\n\n'
    return text
