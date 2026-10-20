# Plex Media Noche — skin para Kodi 21.1 Omega

Proyecto de personalización de **Arctic: Zephyr - Reloaded** para Kodi 21.1 Omega. El objetivo inmediato es un ZIP instalable de skin; la prioridad actual no es construir una APK.

## Estado actual

- El workflow `.github/workflows/build-skin-omega.yml` prepara y valida la base original Arctic: Zephyr - Reloaded v3.0.3.
- La ejecución correcta más reciente conocida es [39392947461](https://github.com/rpepe205-sudo/Plexmedianoche/actions/runs/39392947461). Su artefacto es una **base de desarrollo original**, todavía no el skin personalizado terminado.
- La portada original `1080i/Home.xml`, sus controles, dependencias y scripts se conservan; la maqueta del repositorio `skin/1080i/Home.xml` no se inyecta en la base.
- La personalización se desarrollará con el sistema nativo Skin Shortcuts y los ajustes/widgets de Arctic. El paquete no se considerará terminado hasta comprobar la configuración del menú y probarlo en Kodi 21.1 Omega.

## Diseño acordado

- Apariencia cinematográfica nocturna, carbón/azul noche, con detalles dorados y azules.
- Menú principal: **Inicio, Favoritos, Series estrenos, Series, Novedades cine, TV, Ajustes y Apagar**.
- Widgets ligeros para continuar viendo, episodios recientes, series y películas añadidas recientemente.
- Tráilers dentro de las fichas de películas, no como sección independiente.
- TV/IPTV integrada con los canales configurados en Kodi.
- Navegación fiable con mando y compatibilidad con PlexKodiConnect; no automatizar limpiezas que puedan interferir con la biblioteca sincronizada.

## Validación pendiente

Un workflow verde y un ZIP íntegro no demuestran que el skin funcione en el Xiaomi. Hay que instalarlo en Kodi 21.1 Omega y verificar navegación, widgets, carátulas, biblioteca de PlexKodiConnect y TV/IPTV. La base actual conserva el ID upstream `skin.arctic.zephyr.mod`; para una instalación independiente con nombre propio hay que revisar y cambiar de forma segura las referencias y dependencias antes de publicar el paquete final.
