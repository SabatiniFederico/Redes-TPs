#!/usr/bin/env python3
from scapy.layers.inet import IP, TCP, UDP, ICMP, icmpcodes
from scapy.sendrecv import sr, send
from .config import verbose, hosts, ips, ports 

def imprimir_resultados(resultados):
    for resultado in resultados:
        host = resultado['ip']
        try:
            host = hosts[ips.index(host)]
        except ValueError:
            pass
        print(f"{resultado['tipo']}://{host}:{resultado['port']} - {resultado['status']}")


def procesar_respuestas(answers, unanswered):
    resultados = []

    for ignored_packet in unanswered:
        ip = ignored_packet[IP].dst
        tipo = 'desconocido'
        port = 'desconocido'
        status = 'desconocido'

        if ignored_packet.haslayer(TCP):
            tipo = 'tcp'
            port = ignored_packet[TCP].dport
            status = 'filtrado (no answer)'
        elif ignored_packet.haslayer(UDP):
            tipo = 'udp'
            port = ignored_packet[UDP].dport
            status = 'posiblemente abierto (no answer)'
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

    return resultados


def main():
    print('=== DNS Resolution results ===')
    for (idx, host) in enumerate(hosts):
        print(f'{host} => {ips[idx]}')

    answers, unanswered = sr(IP(dst=ips)/TCP(dport=ports, flags='S'), verbose=verbose, timeout=3)
    print("=== TCP Analysis starting ===")
    print("ANSWERS: " + str(len(answers)))
    print("UNANSWERED: " + str(len(unanswered)))
    resultados = procesar_respuestas(answers, unanswered)
    imprimir_resultados(resultados)

    answers, unanswered = sr(IP(dst=ips)/UDP(dport=ports), verbose=verbose, timeout=3)
    print("=== UDP Analysis starting ===")
    print("ANSWERS: " + str(len(answers)))
    print("UNANSWERED: " + str(len(unanswered)))
    resultados = procesar_respuestas(answers, unanswered)
    imprimir_resultados(resultados)


if __name__ == '__main__':
    main()
