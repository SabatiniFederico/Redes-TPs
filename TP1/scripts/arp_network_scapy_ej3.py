#!/usr/bin/env python3
from scapy.all import *

captura = rdpcap('../wireshark/captura_arp_filtrada.pcapng')
captura_arp = captura.filter(lambda paquete: paquete.haslayer(ARP))

src_existentes = {}
dest_existentes = {}
existentes = {}

#for paquete in captura_arp: 
    # simbolo = paquete.hwsrc + ', ' + paquete.psrc 
    # src_existentes[simbolo] = src_existentes.get(simbolo, 0) + 1
# print(src_existentes)

#for paquete in captura_arp: 
    # simbolo = paquete.hwdst + ', ' + paquete.pdst 
    # dest_existentes[simbolo] = dest_existentes.get(simbolo, 0) + 1
# print(dest_existentes)

for paquete in captura_arp: 
    simbolosrc = paquete.psrc 
    simbolodst = paquete.pdst 
    existentes[simbolosrc] = existentes.get(simbolosrc, 0) + 1
    existentes[simbolodst] = existentes.get(simbolodst, 0) + 1
print(existentes)

total = 0
for simbolo in existentes:
    total = existentes[simbolo] + total

def calcular_informacion(probability):
    return -1 * math.log(probability, 2)

def entropia(fuente):
    entropia = 0
    for cantidad_vista in fuente.values():
        proba_simbolo = existentes[simbolo] / total
        entropia += proba_simbolo * calcular_informacion(proba_simbolo)
    return entropia

print('SIMBOLO | PROBA | INFORMACION')
for simbolo in existentes:
    proba_simbolo = existentes[simbolo] / total
    info = calcular_informacion(proba_simbolo)
    print(f'{simbolo} | {proba_simbolo:.5f} | {info:.5f}')

print(f'Entropia de la fuente: {entropia(existentes):.5f}')
    
