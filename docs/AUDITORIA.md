# Auditoría del 20 de octubre de 2026

## Decisión

Continuar con Kodi estable + PlexKodiConnect + skin Plex Media Noche basado en
Arctic Zephyr Reloaded para Omega. IPTV se configura con PVR IPTV Simple Client.
No es necesario recompilar Kodi para personalizar su interfaz.

PlexKodiConnect documenta expresamente el acceso al servidor de un amigo:
https://github.com/croneter/PlexKodiConnect/wiki/Installation
La cuenta debe tener aceptada la invitación y el servidor debe ser accesible.
La reproducción con esta cuenta concreta todavía está pendiente de verificar.
Usar las rutas de reproducción de Plex; no exigir rutas locales del propietario.

Jellyfin necesita un servidor con acceso a los medios. Plexyfin sincroniza
colecciones y carátulas con Jellyfin; su documentación no ofrece un puente de
reproducción de una biblioteca Plex compartida. Por eso no resuelve este caso.
https://github.com/cleverdevil/plexyfin

IPTV Simple admite M3U y guía XMLTV; no proporciona los canales:
https://kodi.wiki/view/Add-on:PVR_IPTV_Simple_Client

## Evidencia de Actions

Se consultaron las 82 ejecuciones existentes y los pasos de los fallos recientes.

| Ejecución | Resultado comprobado |
| --- | --- |
| 39396062807 | Último ZIP del skin correcto; commit 3b1e0457 |
| 39395653702 | Log: AttributeError al llamar findall sobre PosixPath; corregido después en 9ca321e |
| 39390582675 | Última APK: falla Compilar Kodi; Crear APK y Publicar APK omitidos |
| 39385854878 | APK anterior: falla Preparar dependencias de Kodi |
| 39250145366 | APK anterior correcta, incluida creación y publicación del artefacto |

Enlaces: https://github.com/rpepe205-sudo/Plexmedianoche/actions

Los logs completos de los dos últimos fallos de APK no pudieron recuperarse:
el conector respondió Transport closed, también al reintentar el último.
No atribuir el fallo actual a GnuTLS/libzip sin ver el diagnóstico del compilador.
Los pasos de Actions sí fueron recuperados. No se ha lanzado otra APK.

## Problemas corregidos en esta rama

- La APK se anunciaba como manual pero tenía un disparador push: ahora es manual.
- El ZIP actual descargaba master de Arctic, aunque esperaba 3.0.3: ahora fija
  el commit 27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51, comprobado en upstream.
- La validación antigua publicaba un segundo skin desde el KIT y sustituía Home:
  queda manual y solo valida referencias antiguas, sin publicar paquetes.
- El empaquetado real utiliza el mismo script en el ordenador y en Actions,
  comprueba XML, menú, iconos, estructura ZIP, dependencias originales y Home
  original con solo la sustitución del identificador interno del skin.
- Se añade validación del paquete en pull requests y una suma SHA256.

La APK antigua sigue siendo experimental: clona Kodi sin fijar versión, utiliza
otro ID de skin y tiene parches de dependencias y caché que requieren una revisión
independiente antes de volver a compilar. No se presenta como reparada.

## Estado visual y pruebas reales

El menú y el cambio de nombre son una base personalizada, no el diseño terminado.
El menú actual no tiene acceso separado a todas las películas (Cine), y los
elementos llamados estrenos muestran añadidos recientemente, no estrenos por fecha.
Conservar el menú existente hasta contrastar la última imagen aprobada por el usuario.

Kodi del ordenador abre y permite entrar en ajustes; en la pantalla de Películas
se mostró biblioteca vacía y el aspecto Estuary. Esto no confirma la instalación
del skin ni la conexión Plex. No se han cambiado credenciales, perfiles ni bases
de datos. No se ha instalado el nuevo ZIP en Kodi.

Antes de entregar como terminado: verificar versión de Kodi, dependencias del skin,
Skin Shortcuts, inicio de sesión Plex por el usuario, detección del servidor
compartido, reproducción 1080p, reanudación, subtítulos, canales y guía IPTV.
Después probar foco, botón Atrás y rendimiento en Xiaomi y Homatics. La arquitectura
Android instalada debe comprobarse en cada equipo; no se deduce del procesador.
No ejecutar limpiezas automáticas sobre la biblioteca de PlexKodiConnect.
