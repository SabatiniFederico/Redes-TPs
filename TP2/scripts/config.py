"""config.py - Configuration for the traceroute scripts"""
import logging
import traceroute

logging.basicConfig(level=logging.INFO)

NUMTRACES = 30
UNIVERSITIES = [
  'uba.ar',            # América, Argentina (misma ciudad)
  'unc.edu.ar',        # América, Argentina (distinta ciudad)
  'usp.br',            # América, Brasil
  'mit.edu',           # América, USA (costa este)
  'berkeley.edu',      # América, USA (costa oeste)
  'epfl.ch',           # Europa, Suiza (europa continental del oeste)
  'itmo.ru',           # Europa, Rusia (europa continental del este)
  'nottingham.ac.uk',  # Europa, Reino Unido (islas europeas)
  'fs.ru.is',          # Europa, Islandia (islas europeas)
  'unisa.ac.za',       # África, Sudáfrica (sur de áfrica)
  'alexu.edu.eg',      # África, Egipto (noreste de áfrica)
  'www.u-tokyo.ac.jp', # Asia, Japón (islas asiáticas)
  'sydney.edu.au',     # Oceanía, Australia
  'hawaii.edu',        # Oceanía, USA, Hawái (islas de la polinesia)
]

PLOTTED_UNIVERSITIES = [
  'itmo.ru',           # Europa, Rusia (europa continental del este)
  'fs.ru.is',          # Europa, Islandia (islas europeas)
  'alexu.edu.eg',      # África, Egipto (noreste de áfrica)
  'unisa.ac.za',       # África, Sudáfrica (sur de áfrica)
]

GEOLITE_DB_PATH = 'GeoLite2-City.mmdb'
START_IP = '190.17.73.129'

#traceroute = traceroute.traceroute
traceroute = traceroute.slow_traceroute
#traceroute = traceroute.scapy_traceroute

# No usamos la página principal de ru.is porque está hosteada en Reino Unido
