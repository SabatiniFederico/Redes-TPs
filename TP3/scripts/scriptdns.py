#!/usr/bin/env python3
from socket import getaddrinfo
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmpcodes
from scapy.sendrecv import sr, send

def resolve_dns(host):
    print('Resolviendo', host)
    info = getaddrinfo(host, None)
    assert len(info) > 0
    # Info is a list of 5-uples where the last one is a ip-port tuple
    return info[0][4][0]

def analysis(packet):
    answers, unanswered = sr(packet, verbose=verbose, timeout=3)

    for ignored_packet in unanswered:
        ip = ignored_packet[IP].dst
        tipo = 'desconocido'
        port = 'desconocido'
        status = 'filtrado (no answer)'

        if ignored_packet.haslayer(TCP):
            tipo = 'tcp'
            port = ignored_packet[TCP].dport
        elif ignored_packet.haslayer(UDP):
            tipo = 'udp'
            port = ignored_packet[UDP].dport
        else:
            print('Query no reconocido', repr(ignored_packet))

        if (port, status) == ('desconocido', 'desconocido'):
            continue

        resultados.append({
            'ip': ip,
            'tipo': tipo,
            'port': port,
            'status': status
        })

    for query_answer in answers:
        query, answer = query_answer
        ip = query[IP].dst
        tipo = 'desconocido'
        port = 'desconocido'
        status = 'desconocido'

        if query.haslayer(TCP):
            tipo = 'tcp'
            port = query[TCP].dport
        elif query.haslayer(UDP):
            tipo = 'udp'
            port = query[UDP].dport
        else:
            print('Query no reconocido', repr(query))
            continue

        if answer.haslayer(TCP):
            tcp_answer = answer[TCP]
            if tcp_answer.flags == 0x12:
                status = 'abierto'
                send(IP(dst=ip)/TCP(dport=port, flags='AR'), verbose=verbose)
            elif tcp_answer.flags == 0x14:
                status = 'cerrado'
        elif answer.haslayer(ICMP):
            icmp_answer = answer[ICMP]
            if icmp_answer.type == 3:
                # Destination unreachable, asumimos filtrado
                status = f"filtrado ({icmpcodes[3].get(icmp_answer.code, 'unkwnown code')})"
            else:
                print('Unknown icmp code/type combination')
        else:
            print('Respuesta no reconocida', repr(answer))

        if (port, status) == ('desconocido', 'desconocido'):
            continue

        resultados.append({
            'ip': ip,
            'tipo': tipo,
            'port': port,
            'status': status
        })

    for (idx, host) in enumerate(hosts):
        print(f'{host} => {ips[idx]}')

    for resultado in resultados:
        host = resultado['ip']
        try:
            host = hosts[ips.index(host)]
        except ValueError:
            pass
        print(f"{resultado['tipo']}://{host}:{resultado['port']} - {resultado['status']}")

#ports = [19, 20, 21, 22, 23, 53, 80]
ports = [i for i in range(1025)]
verbose = False
hosts = ['uba.ar', 'unc.edu.ar', 'milagro.dc.uba.ar', 'unisa.ac.za', 'alexu.edu.eg', 'itmo.ru', 'fs.ru.is']
resultados = []
ips = [resolve_dns(host) for host in hosts]

analysis(IP(dst=ips)/TCP(dport=ports, flags='S'))
analysis(IP(dst=ips)/UDP(dport=ports))
