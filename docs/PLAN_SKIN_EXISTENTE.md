# Plex Media Noche — plan de diseño basado en el skin existente

## Decisión técnica

Priorizar una portada y una configuración del skin existente antes de seguir invirtiendo tiempo en la compilación de una APK personalizada. No se elimina ni se descarta el trabajo de APK: queda como objetivo final, pero se pospone hasta validar la interfaz en Kodi.

## Dirección visual elegida

Estilo cinematográfico nocturno, oscuro, elegante y relativamente ligero para Android TV Box:
- Fondo azul noche / carbón, con acentos dorados y azules.
- Un bloque destacado con fanart, título y sinopsis cuando los datos de Kodi estén disponibles.
- Menú directo: Favoritos, Estrenos de series, Series, Cine, Estrenos de cine, TV y Tráilers.
- Filas de carteles: Continuar viendo, Series recientes, Cine añadido recientemente y estrenos.
- Navegación completa con mando y foco visible.
- Evitar animaciones pesadas, fondos de vídeo y demasiados widgets simultáneos.

## Estrategia por fases

1. Confirmar el nombre exacto y versión del skin instalado (Arctic Zephyr Resurrection o Arctic Zephyr Reloaded).
2. Revisar sus opciones nativas de menú, widgets y vistas. Comprobar «Force Views» solo si la versión instalada lo ofrece; no asumir que las opciones de Reloaded existen en Resurrection.
3. Configurar primero la portada con opciones nativas y probar el acceso a la biblioteca de PlexKodiConnect.
4. Ajustar el diseño solo donde la configuración no alcance. Mantener los cambios aislados y reversibles.
5. Probar navegación, carga de carteles, reproducción, TV/IPTV y rendimiento en el Android TV Box.
6. Cuando la interfaz esté validada, decidir qué archivos incorporar al paquete y a la futura APK.

## Notas técnicas importantes

- PlexKodiConnect administra la biblioteca sincronizada desde el servidor Plex compartido; no se deben añadir tareas automáticas de limpieza que puedan interferir con su base de datos.
- Las rutas y etiquetas de Kodi deben comprobarse en la versión real instalada antes de fijarlas en XML.
- La existencia de una opción experimental de «Force Views» en Arctic Zephyr Reloaded no demuestra que exista en Arctic Zephyr 2 Resurrection.
- La maqueta personalizada actual en `skin/1080i/Home.xml` es una referencia de diseño, no una garantía de que pueda sustituir directamente la portada de cualquier skin: antes hay que comprobar su estructura, dependencias, imágenes y rutas de navegación.
- No declarar la APK terminada ni la interfaz probada hasta instalarla y verificarla en el dispositivo.

## Criterio de éxito

Una portada atractiva, legible desde el sofá, rápida con mando, conectada a la biblioteca real y con Cine / Series / TV como accesos principales. La prioridad es que funcione de forma estable antes que copiar cada detalle de la maqueta original.
