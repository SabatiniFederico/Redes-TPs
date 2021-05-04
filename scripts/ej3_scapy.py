#!/usr/bin/env python3
from scapy.all import *

# who has
def is_announcement(paquete):
    return paquete.op == 1 and paquete.psrc == paquete.pdst

# is
def is_an_answer(paquete):
    return paquete.op == 2

captura = rdpcap('../wireshark/captura_arp_filtrada.pcapng')
captura_arp = captura.filter(lambda paquete: paquete.haslayer(ARP))
existen = {}

for paquete in captura_arp: 
    simbolo = paquete.hwsrc + '-' + paquete.psrc 
    existen[simbolo] = existen.get(simbolo, 0) + 1
print(existen)