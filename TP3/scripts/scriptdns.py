from scapy.layers.inet import IP, UDP, RandShort
from scapy.layers.dns import DNS, DNSQR, dnstypes
from scapy.sendrecv import sr
from config import hosts, initial_nameserver, resolve_dns, known_ips, verbose

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
        query_graph.append(((dns_server, host), ('Error: Múltiples SOA', host)))
        return

    if soa:
        nameservers.append(ns_bytes_to_str(soa[0].mname))
    if nameservers:
        print(f"[{host}] Encontramos los nameservers: {nameservers}")

    if dns_answer.an is None and not nameservers:
        print(f"!![{host}] Ni MX ni nameservers, cortando acá")
        query_graph.append(((dns_server, host), ('Error: Ni MX ni nameservers', host)))
    elif dns_answer.an is None:
        if soa:
            print('!!Registro SOA en la respuesta, cortando acá')
            query_graph.append(((dns_server, host), ('SOA (no tiene MX)', host)))
            return

        print(f"##[{host}] Reintentando con {nameservers}")
        for nameserver in nameservers:
            try:
                ip = resolve_dns(nameserver)
                packet_queue.add((ip, host))
                query_graph.append(((dns_server, host), (ip, host)))
            except Exception as err:
                print(f'!![{host}] Error resolviendo {nameserver} ({err})')
                query_graph.append(((dns_server, host), (nameserver, host)))
                query_graph.append(((nameserver, host), (f'{err}', host)))
    else:
        mx_answers = list(dns_answer.an.iterpayloads()) if dns_answer.an else []
        for mx_answer in mx_answers:
            mx_host = mx_answer.exchange.decode('ascii')
            print(f'[{host}] MX Found: {mx_host}')
            query_graph.append(((dns_server, host), (f'MX {mx_host}', host)))

def mandar_consulta_a(server, host):
    ip = IP(dst=server)
    udp = UDP(sport=RandShort(), dport=53)
    return ip / udp / DNS(rd=1, qd=DNSQR(qname=host, qtype='MX'))

def print_graphviz(query_graph, file):
    file.write('digraph {\n')
    for (origin, query) in query_graph:
        if origin == ():
            file.write('START')
        else:
            origin_host = known_ips.get(origin[0], origin[0])
            file.write(f'"{origin_host}\\n{origin[1]}"')
        query_host = known_ips.get(query[0], query[0])
        file.write(f' -> "{query_host}\\n{query[1]}"\n')
    file.write('}\n')

def main():
    cola = set((initial_nameserver, host) for host in hosts)
    query_graph = [((), dest) for dest in cola]
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

        for query, answer in answered:
            destino = query[IP].dst
            host = query[DNS].qd.qname.decode('ascii')
            print(f'[{host}] Consulta DNS hacia {destino} fué respondida')
            procesar_respuesta(query, answer, cola, query_graph)

        iteracion += 1

    with open('dns_calls.dot', 'w+') as file:
        print_graphviz(query_graph, file)

if __name__ == '__main__':
    main()
