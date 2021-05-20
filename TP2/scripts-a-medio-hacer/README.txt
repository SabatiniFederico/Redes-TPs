# Requisitos de análisis según el enunciado

* Calcular el RTT para cada paquete que se haya obtenido respuesta
    - Se puede con traceroute_utils.rtt_for. No lo usamos directamente
* Enviar como mínimo 30 paquetes para un mismo TTL (ráfagas)
    - config.NUMTRACES configura esto
* Analizar las respuestas para distinguir entre varias rutas
    - PENDIENTE: Qué tipo de análisis conviene hacer?
* Calcular el un RTT promedio por TTL (si hay multiples IPs usar la que más
  haya respondido)
    - Hecho con traceroute_utils.filter_most_common_answerer y
      traceroute_utils.average_rtt_for
* Calcular el RTT entre salto restando los valores de RTT de saltos sucesivos.
  Si da negativo calcularlo con el próximo salto que de positivo.
    - Hecho en analysis, por ahora sólo imprimo los resultados
