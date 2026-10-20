# Plex Media Noche — skin para Kodi 21.1 Omega

Proyecto de personalización de **Arctic: Zephyr - Reloaded** para Kodi 21.1 Omega. El objetivo inmediato es un ZIP instalable de skin; la prioridad actual no es construir una APK.

## Estado actual

- El workflow `.github/workflows/build-skin-omega.yml` usa Arctic: Zephyr - Reloaded v3.0.3 fijado por revisión, aplica el menú y crea un ZIP con ID independiente `skin.plexmedianoche`.
- La ejecución correcta más reciente revisada es [39441881425](https://github.com/rpepe205-sudo/Plexmedianoche/actions/runs/39441881425). Acredita el empaquetado, pero **no prueba instalación, widgets ni navegación en el dispositivo**.
- La portada original `1080i/Home.xml`, sus controles, dependencias y scripts se conservan; la maqueta del repositorio `skin/1080i/Home.xml` no se inyecta en la base.
- La personalización se desarrollará con el sistema nativo Skin Shortcuts y los ajustes/widgets de Arctic. El paquete no se considerará terminado hasta comprobar la configuración del menú y probarlo en Kodi 21.1 Omega.

## Diseño acordado

El paquete aplica una paleta azul noche con acentos dorados y azules. En un perfil nuevo limita los widgets a 12 elementos por fila y desactiva reflejos; mantiene la portada nativa de Arctic y ofrece la paleta original como alternativa. Esto no reproduce automáticamente la maqueta conceptual ni configura widgets con datos reales.

- Apariencia cinematográfica nocturna, carbón/azul noche, con detalles dorados y azules.
- Menú principal: **Inicio, Favoritos, Series estrenos, Series, Cine, Novedades cine, TV, Ajustes y Apagar**.
- Widgets ligeros para continuar viendo, episodios recientes, series y películas añadidas recientemente.
- Tráilers dentro de las fichas de películas, no como sección independiente.
- TV/IPTV integrada con los canales configurados en Kodi.
- Navegación fiable con mando y compatibilidad con PlexKodiConnect; no automatizar limpiezas que puedan interferir con la biblioteca sincronizada.

## Validación pendiente

Un workflow verde y un ZIP íntegro no demuestran que el skin funcione en el Xiaomi. Hay que instalarlo en Kodi 21.1 Omega y verificar navegación, widgets, carátulas, biblioteca de PlexKodiConnect y TV/IPTV. El empaquetado cambia el ID a `skin.plexmedianoche` y sus referencias internas; su funcionamiento real aún necesita esa prueba.

## Android y biblioteca Plex compartida

La vía recomendada es **Kodi oficial + PlexKodiConnect en modo Addon + el skin**. Jellyfin requiere su propio servidor con acceso a los archivos; la invitación Plex no proporciona ese acceso.

La APK heredada queda como vía experimental manual, basada en Kodi 21.1 y su toolchain correspondiente. Usa otra maqueta de skin (`skin.pepe.plexmedianoche`), no el ZIP Arctic, y no integra automáticamente PKC. Los fallos de compilación completos aún necesitan diagnóstico; no hay una APK nueva verificada.

Consulta el [diagnóstico de Android, dependencias, resultados y alternativas](docs/DIAGNOSTICO_ANDROID_Y_ALTERNATIVAS.md).

La [guía de instalación y pruebas en Windows y Android](docs/INSTALAR_Y_PROBAR.md) explica cómo añadir PlexKodiConnect y TV en cada equipo. El artefacto del skin incluye la guía, un informe de dependencias, la revisión upstream y la huella SHA-256 del ZIP.

