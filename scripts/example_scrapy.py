#!/usr/bin/env python3
from scapy.all import *

S1 = {}
count = 0

protocolos = scapy.layers.l2.Ether.payload_guess
def adivinar_protocolo(layer):
    def es_compatible(protocolo):
        for attr_name, attr_val in protocolo[0].items():
            if (getattr(layer, attr_name) != attr_val):
                return False
        return True

    for protocolo in protocolos:
        if (es_compatible(protocolo)):
            return f'{protocolo[1].__name__} ({layer.type})'
    return layer.type

def calcular_informacion(probability):
    return -1 * math.log(probability, 2)

def entropia(fuente):
    entropia = 0
    for cantidad_vista in fuente.values():
        proba_simbolo = cantidad_vista / count
        entropia += proba_simbolo * calcular_informacion(proba_simbolo)
    return entropia

def imprimir_simbolo(simbolo):
    tipo = simbolo[0][0] # broadcast/unicast
    protocolo = simbolo[0][1] # ip/arp/ipv6
    paquetes = simbolo[1] # cantidad de paquetes encontrado
    proba = paquetes/count
    info = calcular_informacion(proba)
    print(f'{tipo}-{protocolo} | {proba:.5f} | {info:.5f}')

def mostrar_fuente(S):
    simbolos = sorted(S.items(), key=lambda x: -x[1])
    print('SIMBOLO | PROBA | INFORMACION')
    for simbolo in S.items():
        imprimir_simbolo(simbolo)
    print(f'Entropia de la fuente: {entropia(S):.5f}')
    print()

def callback(pkt):
    global count
    if pkt.haslayer(Ether):
        dire = "BROADCAST" if pkt[Ether].dst=="ff:ff:ff:ff:ff:ff" else "UNICAST"
        proto = adivinar_protocolo(pkt[Ether]) # El campo type del frame tiene el protocolo
        s_i = (dire, proto) # Aca se define el simbolo de la fuente

        if s_i not in S1:
            S1[s_i] = 0.0

        S1[s_i] += 1.0
        count += 1
        print(f'Llegó el paquete {count}')

    mostrar_fuente(S1)
    if count >= 20000:
        exit()

sniff(prn=callback)
