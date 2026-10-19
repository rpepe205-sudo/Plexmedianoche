# Plex de Media Noche

Compilación privada de Kodi para Android ARM32, con nombre de aplicación, skin y mantenimiento de biblioteca propios.

## Componentes

- `Plex_de_Media_Noche_0.4.0_KIT.zip`: paquete base de recursos del skin.
- `skin/1080i/Home.xml`: inicio con cabecera destacada y carruseles de series, películas y novedades; usa los datos de la biblioteca local de Kodi.
- `addons/service.plexmedianoche.maintenance`: actualiza la biblioteca de vídeo cada día y, los martes, realiza una limpieza de registros que apunten a archivos que ya no existen.
- `.github/workflows/build-android.yml`: prepara la aplicación **Plex de Media Noche**, identificador independiente `com.plexmedianoche.kodi`, para dispositivos ARM32 (`armeabi-v7a`).
- `.github/workflows/validate-skin.yml`: valida los XML y el servicio, y publica un ZIP instalable del skin.

## Biblioteca y sincronización

Añade las fuentes de vídeo desde Kodi en **Vídeos > Archivos** y configúralas como películas o series. Cuando Kodi las indexe, sus carátulas y novedades llenarán los carruseles. No es necesario compartir acceso ni contraseña de PlexKodiConnect.

El servicio intenta actualizar una biblioteca local de Kodi una vez al día mientras Kodi está abierto. Los martes, después de la actualización, limpia de la base de datos las referencias a archivos desaparecidos; no borra archivos multimedia. **Si detecta PlexKodiConnect instalado, omite tanto la actualización como la limpieza automática**, porque PKC gestiona la biblioteca sincronizada desde Plex y una limpieza de Kodi podría interferir con ella. Si el TV Box está apagado, el trabajo local se ejecutará cuando Kodi vuelva a abrirse.

## Tráileres y subtítulos

Los tráileres dependen de que la ficha del título tenga esa información. Kodi ofrece los subtítulos durante la reproducción; para buscar y descargar subtítulos hace falta instalar y configurar un proveedor desde **Complementos**. Estos accesos se mantienen dentro de las fichas y del reproductor, no en el menú principal.

## Compilación e instalación

En GitHub, abre **Actions**, elige **Crear APK de Plex Media Noche** y descarga el artefacto **Plex-Media-Noche-APK-arm32** de la ejecución más reciente que haya terminado correctamente. Extrae el ZIP y, en el TV Box, instala `Plex-Media-Noche-arm32.apk`.

La APK aparece como **Plex de Media Noche** y puede instalarse junto a Kodi porque usa un identificador independiente. La clave de prueba se reutiliza para permitir actualizaciones de esta APK de desarrollo; no es una firma de publicación. Los artefactos de APK se conservan durante 7 días.
