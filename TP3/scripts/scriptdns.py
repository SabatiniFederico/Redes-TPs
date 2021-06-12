from itertools import groupby
from scapy.layers.inet import IP, UDP, RandShort
from scapy.layers.dns import DNS, DNSQR, dnstypes
from scapy.sendrecv import sr
from config import (
    hosts,
    initial_nameserver,
    known_ips,
    resolve_dns,
    verbose,
    write_graphs
)

dnstype_for = { value: key for key, value in dnstypes.items() }

def ns_bytes_to_str(ns):
    return ns[:-1].decode('ascii')

def procesar_respuesta(query, answer, packet_queue, query_graph):
    host = query[DNS].qd.qname.decode('ascii')
    dns_server = query[IP].dst
    dns_answer = answer[DNS]
    ns_answers = list(dns_answer.ns.iterpayloads()) if dns_answer.ns else []
    soa = [record for record in ns_answers
           if record.type == dnstype_for['SOA']]
    nameservers = [ns_bytes_to_str(record.rdata)
                   for record in ns_answers
                   if record.type == dnstype_for['NS']]

    if len(soa) > 1:
        print(f"!![{host}] Más de un SOA, cortando acá")
        query_graph.add((host, dns_server, host, 'Error: Múltiples SOA'))
        return

    if soa:
        nameservers.append(ns_bytes_to_str(soa[0].mname))
    if nameservers:
        print(f"[{host}] Encontramos los nameservers: {nameservers}")

    if dns_answer.an is None and not nameservers:
        print(f"!![{host}] Ni MX ni nameservers, cortando acá")
        query_graph.add((host, dns_server, 'Error: Ni MX ni nameservers'))
    elif dns_answer.an is None:
        if soa:
            print('!!Registro SOA en la respuesta, cortando acá')
            query_graph.add((host, dns_server, 'SOA (no tiene MX)'))
            return

        print(f"##[{host}] Reintentando con {nameservers}")
        for nameserver in nameservers:
            try:
                ip = resolve_dns(nameserver)
                packet_queue.add((ip, host))
                query_graph.add((host, dns_server, ip))
            except Exception as err:
                print(f'!![{host}] Error resolviendo {nameserver} ({err})')
                query_graph.add((host, dns_server, nameserver))
                query_graph.add((host, nameserver, f'Error: {err}'))
    else:
        mx_answers = list(dns_answer.an.iterpayloads()) if dns_answer.an else []
        for mx_answer in mx_answers:
            mx_host = mx_answer.exchange.decode('ascii')
            print(f'[{host}] MX Found: {mx_host}')
            query_graph.add((host, dns_server, f'MX {mx_host}'))

def mandar_consulta_a(server, host):
    ip = IP(dst=server)
    udp = UDP(sport=RandShort(), dport=53)
    return ip / udp / DNS(rd=1, qd=DNSQR(qname=host, qtype='MX'))

def print_graphviz(query_graph, file):
    def write_node_name_for(maybe_ip):
        host = known_ips.get(maybe_ip)
        if host is None:
            file.write(f'"{maybe_ip}"')
        else:
            file.write(f'"{host}\\n({maybe_ip})"')

    file.write('digraph {\n')
    for (_, from_node, to_node) in query_graph:
        write_node_name_for(from_node)
        file.write(' -> ')
        write_node_name_for(to_node)
        file.write('\n')
    file.write('}\n')

def main():
    cola = set((initial_nameserver, host) for host in hosts)
    query_graph = set()
    iteracion = 0
    while cola:
        print(f"=== Mandando los paquetes de la iteración {iteracion} ===")
        paquetes = [mandar_consulta_a(server, host) for server, host in cola]
        cola.clear()
        answered, unanswered = sr(paquetes, verbose=verbose, timeout=10)

        for query in unanswered:
            destino = query[IP].dst
            host = query[DNS].qd.qname.decode('ascii')
            print(f'!![{host}] Consulta DNS hacia {destino} no fué respondida')
            query_graph.add((host, destino, 'Error: Sin respuesta'))

        for query, answer in answered:
            destino = query[IP].dst
            host = query[DNS].qd.qname.decode('ascii')
            print(f'[{host}] Consulta DNS hacia {destino} fué respondida')
            procesar_respuesta(query, answer, cola, query_graph)

        iteracion += 1

    if write_graphs:
        sorted_graph = sorted(query_graph, key=lambda edge: edge[0])
        for host, edges in groupby(sorted_graph, lambda edge: edge[0]):
            list_edges = list(edges)
            with open(f'{host}.dns_trace.dot', 'w+') as file:
                print_graphviz(list_edges, file)

if __name__ == '__main__':
    main()
