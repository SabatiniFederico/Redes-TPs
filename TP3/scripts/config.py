from socket import getaddrinfo

def resolve_dns(host):
    info = getaddrinfo(host, None)
    assert len(info) > 0
    # Info is a list of 5-uples where the last one is a ip-port tuple
    return info[0][4][0]


# Configuration
verbose = False
hosts = ['uba.ar', 'unc.edu.ar', 'milagro.dc.uba.ar', 'unisa.ac.za', 'alexu.edu.eg', 'itmo.ru', 'fs.ru.is']
ports = list(range(1025))
ips = [resolve_dns(host) for host in hosts]

