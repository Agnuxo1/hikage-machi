# H0: datos reales de Takamatsu

Autor: Francisco Angulo de Lafuente. Preparación y verificación por Codex, 14-11-2026.

Objetivo: materializar el hito H0 de `PLAN_OBRA_FINAL.md` de Claude: CityGML y GTFS de una ciudad, con procedencia, licencia, hashes y recuentos reproducibles. Takamatsu es la candidata de disponibilidad ya prevista; su elección no depende de una métrica de rendimiento. CPU; sin volver a ejecutar G0, sin GPU y sin reenviar la entrada inicial.

## Modelo de trabajo fijado antes de ejecutar

`fuente oficial -> bytes y SHA-256 -> inventario -> recuentos/relaciones/CRS -> cobertura descriptiva -> decisión H0`

| Fuente | Uso de H0 | Control independiente |
|---|---|---|
| GTFS Kotoden, ZIP conservado el 10-11, SHA-256 `6c2b1c419d05b9aa3a34439509a3f038a1c516603c405275f31603fdb54b2de6` | Recuento de paradas/rutas/viajes y tiempos, unicidad y referencias, calendario | Recuento CSV separado, referencias entre tablas y plausibilidad geográfica |
| PLATEAU Takamatsu 2022, CityGML v4 enlazado en el catálogo oficial conservado | Recuento de edificios y partes, LOD, CRS observado y envolventes de cada fichero | Segundo conteo de etiquetas, IDs únicos y comparación entre geometría y envolventes declaradas |
| Política PLATEAU/PDL1.0 y página Kotoden/CC BY4.0 | Atribución y permisos aplicables a cada fuente | Revisar avisos particulares incluidos antes de publicar derivados |

No hay contraste de mejora en H0: son recuentos deterministas de fuentes. H1/H3/H4, la exactitud física, la optimización y los ensayos de la enmienda científica permanecen pendientes. No convertir valores ausentes en ceros. Conservar horas GTFS >=24 sin módulo 24. No mezclar destinos para estimar esperas. La futura espera por horarios se analizará por patrón y día de servicio; no se calcula aquí.

Descarga: un ZIP oficial de CityGML, máximo 2 GiB comprimidos y 12 GiB descomprimidos en lectura; sin cuentas, claves ni ejecución de contenido. Se conservan los bytes originales, no se extraen rutas del ZIP automáticamente. Los inventarios no autorizan por sí solos redistribución ni garantizan exactitud de los datos. No usar texturas, ortofotos ni cartografía de fondo en esta fase.

Aceptación H0: ambas fuentes disponibles con hash y licencia documentados, número de edificios/paradas medido y CRS/cobertura descritos. Un fallo se conserva con su salida y no se presenta como éxito. Los resultados no acreditan todavía obra final, mapa, presentación ni envío. La difusión del derivado se decide tras revisar los avisos particulares del paquete.

Fuentes verificadas el 14-11-2026: [convocatoria](https://urbandata-challenge.jp/udc2026_entry), [Kotoden](https://www.kotoden.co.jp/publichtm/gtfs/index.html), [política PLATEAU](https://www.mlit.go.jp/plateau/site-policy/), [PDL1.0](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0), [catálogo](https://www.geospatial.jp/ckan/dataset/plateau-37201-takamatsu-shi-2022). El acceso web de esta última página devolvió 403; se usa el JSON oficial ya conservado, sin eludir controles.
