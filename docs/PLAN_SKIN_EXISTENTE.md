# Plex Media Noche — plan de diseño basado en el skin existente

## Decisión técnica

Priorizar una portada y una configuración del skin existente antes de seguir invirtiendo tiempo en la compilación de una APK personalizada. No se elimina ni se descarta el trabajo de APK: queda como objetivo final, pero se pospone hasta validar la interfaz en Kodi.

## Dirección visual elegida

Estilo cinematográfico nocturno, oscuro, elegante y relativamente ligero para Android TV Box:
- Fondo azul noche / carbón, con acentos dorados y azules.
- Un bloque destacado con fanart, título y sinopsis cuando los datos de Kodi estén disponibles.
- Menú horizontal superior: Inicio, Favoritos, Series estrenos, Series, Novedades cine, TV, Ajustes y Apagar.
- Tráilers accesibles desde la ficha de cada película cuando exista una fuente compatible; sin apartado independiente en el menú.
- La base que usa el workflow actual es Arctic: Zephyr - Reloaded, no Arctic Zephyr Resurrection.
- Filas de carteles: Continuar viendo, Series recientes, Cine añadido recientemente y estrenos.
- Navegación completa con mando y foco visible.
- Evitar animaciones pesadas, fondos de vídeo y demasiados widgets simultáneos.

## Estrategia por fases

1. El workflow actual toma como base Arctic: Zephyr - Reloaded. Confirmar con el usuario si el skin que tiene instalado en el TV Box es esa variante o Arctic Zephyr Resurrection.
2. Revisar sus opciones nativas de menú, widgets y vistas. Comprobar «Force Views» solo si la versión instalada lo ofrece; no asumir que las opciones de Reloaded existen en Resurrection.
3. Configurar primero la portada con opciones nativas y probar el acceso a la biblioteca de PlexKodiConnect.
4. Ajustar el diseño solo donde la configuración no alcance. Mantener los cambios aislados y reversibles.
5. Probar navegación, carga de carteles, reproducción, TV/IPTV y rendimiento en el Android TV Box.
6. Cuando la interfaz esté validada, decidir qué archivos incorporar al paquete y a la futura APK.

## Cambios de portada en curso

- `skin/1080i/Home.xml` se ha actualizado para subir la navegación principal a la parte superior y usar los ocho accesos acordados.
- El workflow `.github/workflows/build-skin-omega.yml` se activa al cambiar `Home.xml` y prepara un ZIP basado en Reloaded para Kodi Omega.
- El artefacto debe pasar la validación automatizada y aún necesita una prueba real en Kodi/Android TV Box. No considerar el diseño validado hasta comprobar foco con mando, widgets, carteles, PKC e IPTV.

## Notas técnicas importantes

- PlexKodiConnect administra la biblioteca sincronizada desde el servidor Plex compartido; no se deben añadir tareas automáticas de limpieza que puedan interferir con su base de datos.
- Las rutas y etiquetas de Kodi deben comprobarse en la versión real instalada antes de fijarlas en XML.
- La existencia de una opción experimental de «Force Views» en Arctic Zephyr Reloaded no demuestra que exista en Arctic Zephyr 2 Resurrection.
- La maqueta personalizada actual en `skin/1080i/Home.xml` es una referencia de diseño, no una garantía de que pueda sustituir directamente la portada de cualquier skin: antes hay que comprobar su estructura, dependencias, imágenes y rutas de navegación.
- No declarar la APK terminada ni la interfaz probada hasta instalarla y verificarla en el dispositivo.

## Criterio de éxito

Una portada atractiva, legible desde el sofá, rápida con mando, conectada a la biblioteca real y con Cine / Series / TV como accesos principales. La prioridad es que funcione de forma estable antes que copiar cada detalle de la maqueta original.
