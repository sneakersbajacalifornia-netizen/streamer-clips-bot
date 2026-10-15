# Streamer Clips Bot

Sistema automático para detectar clips virales de streamers, transformarlos en Shorts con narración y edición original, someterlos a aprobación y publicarlos/programarlos en YouTube.

## Flujo

1. Descubrimiento de clips y tendencias.
2. Puntuación de potencial viral.
3. Filtro de fuentes y derechos.
4. Análisis del clip y generación de contexto original.
5. Narración con voz IA.
6. Edición vertical 9:16, subtítulos y elementos visuales.
7. Control de calidad.
8. Cola de aprobación manual.
9. Publicación o programación en YouTube tras aprobación.

## Streamers iniciales

La lista está en `config/streamers.json` e incluye 22 streamers. El modo `auto_discover` permite incorporar nuevos creadores en tendencia.

## Importante

El sistema no debe asumir que un clip de terceros es reutilizable o monetizable. El filtro de derechos debe priorizar material autorizado/licenciado y contenido transformativo con aporte editorial significativo. La aprobación manual no sustituye la revisión de derechos.

## Estado

Base inicial creada. Las siguientes fases añadirán los módulos de descubrimiento, scoring, generación, renderizado, aprobación y publicación.
