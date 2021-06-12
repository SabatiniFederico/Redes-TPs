from socket import getaddrinfo

def resolve_dns(host):
    info = getaddrinfo(host, None)
    assert len(info) > 0
    # Info is a list of 5-uples where the last one is a ip-port tuple
    return info[0][4][0]


# Configuration
verbose = False
hosts = ['uba.ar', 'unc.edu.ar', 'milagro.dc.uba.ar', 'unisa.ac.za', 'alexu.edu.eg', 'itmo.ru', 'fs.ru.is', 'iglosiggio.github.io']
ports = list(range(1025))
ips = [resolve_dns(host) for host in hosts]
initial_nameserver = '199.9.14.201'
#initial_nameserver = '1.1.1.1'
