# Auditoría externa — Urban Data Challenge 2026

14-11-2026. Objeto: estado de la obra final de Hikage-machi y hito H0 del plan de Claude del 13-11. La inscripción del resumen es una fase distinta de la entrega final. Se conservan los trabajos anteriores; esta auditoría no repite G0 ni sus trabajos GPU.

## Logros comprobados

H0 de datos reales completado en `codex/20261114/`: descarga única del CityGML oficial v4 de Takamatsu, 821.695.076 bytes, SHA-256 `d44976d25c155f78f5090dc8cd1014f816ca03c46e761c9fa8c37d8c39363641`. GTFS conservado de Kotoden, 595.292 bytes, SHA-256 `6c2b1c419d05b9aa3a34439509a3f038a1c516603c405275f31603fdb54b2de6`, reutilizado sin descargarlo otra vez.

Recuento medido: 408 GML de edificios, 268.154 edificios e IDs únicos; 2.160 objetos contienen elementos LOD2; cero partes BuildingPart en los miembros examinados. Se leyeron 3.409.388.878 bytes descomprimidos de edificios, sin extraer todo el ZIP de 17.224.849.087 bytes descomprimidos. No se usaron terreno, texturas, ortofotos ni otros tipos de objetos. CRS observado EPSG:6697: latitud, longitud y altura, con unidades grados/grados/metros.

GTFS medido: 658 paradas, 22 rutas, 1.034 viajes, 25.248 registros de tiempo. Cero referencias rotas, IDs duplicados, coordenadas inválidas o pares viaje/secuencia duplicados en los controles realizados. Escenario horario fijado para el 16-11-2026: 511 viajes y 658 paradas, Asia/Tokyo; no es operación observada.

## Tres comprobaciones nuevas e independientes

1. Segundo algoritmo binario de conteo de etiquetas, independiente del parser XML: 268.154 edificios en los mismos 408 archivos, cero diferencias; cero BuildingPart.
2. Todos los registros geométricos se cotejaron con las envolventes declaradas de sus archivos: cero fuera de ellas con tolerancia numérica 1e-7 en coordenadas nativas; cero IDs repetidos o geometrías sin posiciones. Esto no valida topología ni exactitud física.
3. Segundo lector CSV y segundo cálculo de calendario GTFS: mismos recuentos, zona Asia/Tokyo y 511 viajes del escenario. Las horas no se reducen módulo 24.

`H0_CHECKS.json` registra diez comprobaciones aprobadas y el verificador devuelve código no cero cuando falla. Una revisión independiente, con contexto separado, recalculó hashes, CSV, relaciones/tiempos y muestreó 315 edificios de dos GML con otro parser, sin diferencias materiales en ese alcance. La adaptación de rutas para reproducción pública pasó controles positivos y rechazo de ID duplicado/directorio de trabajo existente, sin repetir la ciencia de G0.

## Derechos y formato

La [convocatoria oficial vigente](https://urbandata-challenge.jp/udc2026_entry) distingue resumen inicial y obra final, permite obras publicables y anuncia el formulario final por separado para finales de noviembre. La entrada inicial del 09-11 consta en el recibo histórico; no se ha reenviado ni se ha presentado una obra final en esta auditoría. Cierre final publicado: 27-12-2026 23:59, interpretado JST como 14:59 UTC.

El README incluido en este CityGML ofrece expresamente escoger CC BY4.0 entre sus licencias; se selecciona esa para la geometría examinada y sus derivados. Kotoden declara CC BY4.0 para su GTFS. Se conservan atribución, README e inventario de fuentes originales. El código propio mantiene MIT. Ningún permiso sobre otros futuros datos se deduce de este hito.

## Defectos y mejoras pendientes

- **B — estado READY insuficiente para una entrega final.** El estado del registro no acredita aplicación utilizable: no hay aún mapa de exposición, comparación Radiance, rutas a pie, dataset final validado o formulario final enviado. H0 corrige la falta de datos reales, no estos requisitos. Volver a PREPARING con evidencia evita confundir una inscripción con una candidatura terminada.
- **C — alcance físico y estadístico pendiente.** H1/H3/H4 y la ablación A/B/C/D siguen sin resultado de ciudad; no se puede declarar superioridad, efecto térmico, ahorro energético ni generalización. La enmienda estadística anterior permanece vigente.
- **C — fuentes con antigüedad y áreas distintas.** La geometría de origen y el horario son de épocas diferentes. Las áreas publicadas en catálogo/mapa/README no son intercambiables; no se obtiene de ellas un porcentaje de cobertura. Topología, actualización de edificios y exactitud de sombras requieren controles posteriores.

## Siguiente paso y observaciones

H0 puede usarse para empezar H1: fijar previamente una muestra de paradas, construir una referencia Radiance y calcular sombras por fecha/hora con unidades explícitas. Calcular espera por patrón/destino y día de servicio sin mezclar viajes incompatibles. Mantener la selección de muestra y el análisis antes de ver resultados. La implementación, el formulario final y la revisión de entrega siguen pendientes; no hay nuevo justificante ni puntuación oficial.

Este veredicto concierne a la obra final completa, no invalida el H0 aprobado ni los controles sintéticos históricos.

VEREDICTO: BLOQUEADO
