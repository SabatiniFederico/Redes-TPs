from scapy.layers.inet import IP, UDP, RandShort
from scapy.layers.dns import DNS, DNSQR, dnstypes
from scapy.sendrecv import sr
from config import hosts, initial_nameserver, verbose

dnstype_for = { value: key for key, value in dnstypes.items() }

def procesar_respuesta(query, answer, packet_queue):
    consulta = repr(query[DNS].qd)
    host = query[DNS].qd.qname.decode('ascii')
    dns_answer = answer[DNS]
    soa = [record for record in (dns_answer.ns or ()) if record.type == dnstype_for['SOA']]

    if len(soa) > 1:
        print(f"!![{host}] Hay más de un SOA, esto viola el estándar, no proseguimos con el análisis")
        return

    nameservers = [record.rdata[:-1].decode('ascii') for record in (dns_answer.ns or ()) if record.type == dnstype_for['NS']]
    nameservers.extend(record.mname[:-1].decode('ascii') for record in soa)
    print(f"[{host}] Encontramos los nameservers: {nameservers}")

    if dns_answer.an is None and not nameservers:
        print(f"!![{host}] No hubo respuesta MX ni nameservers, fallo en {consulta}")
    elif dns_answer.an is None:
        if soa:
            nuevo_host = soa[0].rrname[:-1].decode('ascii')
            if host == nuevo_host:
                print('!!Hay un registro SOA equivalente a la consulta realizada, no se encontró registro MX')
                return

            print(f'##[{host}] Hay un registro de SOA, cambiando la consulta de {host} a {nuevo_host}')
            host = nuevo_host
        packet_queue.extend(mandar_consulta_a(server, host) for server in nameservers)
        print(f"##[{host}] Reintentando con los nameservers en la respuesta: {nameservers}")
    else:
        for answer in (dns_answer.an or ()):
            print(f'[{host}] {repr(answer)}')

def mandar_consulta_a(server, host):
    ip = IP(dst=server)
    udp = UDP(sport=RandShort(), dport=53)
    return ip / udp / DNS(rd=1, qd=DNSQR(qname=host, qtype='MX'))

def main():
    cola = [mandar_consulta_a(initial_nameserver, host) for host in hosts]
    iteracion = 0
    while cola:
        print(f"=== Mandando los paquetes de la iteración {iteracion} ===")
        answered, unanswered = sr(cola, verbose=verbose, timeout=10)
        cola.clear()

        for query in unanswered:
            destino = query[IP].dst
            consulta = repr(query[DNS].qd)
            host = query[DNS].qd.qname.decode('ascii')
            print(f'!![{host}] Consulta DNS hacia {destino} no fué respondida')

        for query, answer in answered:
            destino = query[IP].dst
            consulta = repr(query[DNS].qd)
            host = query[DNS].qd.qname.decode('ascii')
            print(f'[{host}] Consulta DNS hacia {destino} fué respondida')
            procesar_respuesta(query, answer, cola)
        
        iteracion += 1

if __name__ == '__main__':
    main()