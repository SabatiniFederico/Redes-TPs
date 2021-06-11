from scapy.all import *
from .config import ips, hosts, verbose

answer = sr( ip / udp / dns , verbose=0, timeout=10)

print(answer[DNS])


if answer.haslayer(DNS) and answer[DNS].qd.qtype == 1:
    print("Additional Records")
    for i in range(answer[DNS].arcount):
        print(answer[DNS].ar[i].rrname, answer[DNS].ar[i].rdata)
    print("Name Servers")
    for i in range(answer[DNS].nscount):
        print(answer[DNS].ns[i].rrname, answer[DNS].ns[i].rdata)
    print("Answer")
    for i in range(answer[DNS].ancount):
        print(answer[DNS].an[i].rrname, answer[DNS].an[i].rdata)

