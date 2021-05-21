"""
Mapping from the destination IPs on traceroute.pickle to the original domains

IP recollection created using `dig`.
"""

def collect_all_domains():
    """
    Returns a dict with (<ip>, <domain>) entries for each domain in the config
    """
    #pylint: disable-msg=import-outside-toplevel
    from config import UNIVERSITIES
    from subprocess import check_output
    dig_results = check_output(['dig', *UNIVERSITIES], text=True)
    # Split lines
    dig_results = dig_results.split('\n')
    # Remove empty lines
    dig_results = filter(lambda x: x != '', dig_results)
    # Remove comments
    dig_results = filter(lambda x: x[0] != ';', dig_results)
    # Split each line
    dig_results = map(str.split, dig_results)
    # Transform into a generator of (<ip>, <domain>) pairs
    # (strips the last char of the domain because it's a dot)
    dig_results = map(lambda line: (line[-1], line[0][:-1]), dig_results)
    return dict(dig_results)

# Collected on 2021-05-20
mapping = {
    '157.92.5.15': 'uba.ar',
    '200.16.16.170': 'unc.edu.ar',
    '200.16.16.171': 'unc.edu.ar',
    '200.16.16.174': 'unc.edu.ar',
    '200.144.248.41': 'usp.br',
    '23.51.172.199': 'mit.edu',
    '35.163.72.93': 'berkeley.edu',
    '128.178.222.108': 'epfl.ch',
    '77.234.204.10': 'itmo.ru',
    '185.18.139.133': 'nottingham.ac.uk',
    '130.208.243.161': 'fs.ru.is',
    '163.200.81.55': 'unisa.ac.za',
    '193.227.16.128': 'alexu.edu.eg',
    '210.152.243.234': 'www.u-tokyo.ac.jp',
    '129.78.5.8': 'sydney.edu.au',
    '128.171.149.56': 'hawaii.edu',
    # Added by hand. mit.edu is hosted on Akamai and changes the domain IP
    # constantly. This was done by a process of elimination. So we are assuming
    # that these IPs where from MIT when we did the experiments.
    '23.6.131.69': 'mit.edu',
    '23.44.86.137': 'mit.edu',
    '23.73.244.9': 'mit.edu',
    '23.197.152.105': 'mit.edu',
    '104.98.82.71': 'mit.edu',
    '104.105.46.71': 'mit.edu',
    '104.119.1.239': 'mit.edu',
    '104.122.79.128': 'mit.edu',
}
