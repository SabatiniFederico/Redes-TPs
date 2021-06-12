from scapy.layers.inet import IP, UDP, RandShort
from scapy.layers.dns import DNS, DNSQR
from scapy.sendrecv import sr
from config import hosts, verbose

def procesar_respuesta(dns_answer):
    print("Additional Records")
    for record in (dns_answer[DNS].ar or ()):
        print(repr(record))
    print("Name Servers")
    for nameserver in (dns_answer[DNS].ns or ()):
        print(repr(nameserver))
    print("Answer")
    for answer in (dns_answer[DNS].an or ()):
        print(repr(answer))

#ip = IP(dst="199.9.14.201")
ip = IP(dst="1.1.1.1")
udp = UDP(sport=RandShort(), dport=53)
cola = [ip / udp / DNS(rd=1, qd=DNSQR(qname=host, qtype='MX')) for host in hosts]

def main():
    while cola:
        answered, unanswered = sr(cola, verbose=verbose, timeout=10)
        cola.clear()

        for query in unanswered:
            destino = query[IP].dst
            consulta = repr(query[DNS].qd)
            print(f'!!Consulta DNS por {consulta} hacia {destino} no fué respondida')

        for query_answer in answered:
            destino = query_answer[0][IP].dst
            consulta = repr(query_answer[0][DNS].qd)
            print(f'Consulta DNS por {consulta} hacia {destino} fué respondida')
            procesar_respuesta(query_answer[1])

if __name__ == '__main__':
    main()