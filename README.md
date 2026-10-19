# Plex Media Noche

Kodi personalizado para Android con interfaz cinematográfica y PlexKodiConnect.

## Qué hay en el repositorio

- `Plex_de_Media_Noche_0.4.0_KIT.zip`: paquete del skin y archivos de configuración del proyecto.
- `.github/workflows/build-android.yml`: compila Kodi para Android ARM64 e incorpora el skin.
- `.github/workflows/validate-skin.yml`: comprueba los XML del skin y genera un ZIP instalable.

## Obtener e instalar la APK de prueba

En GitHub, abre **Actions**, selecciona **Crear APK de Plex Media Noche** y descarga el artefacto **Plex-Media-Noche-APK-arm64** de la ejecución más reciente que haya terminado correctamente. El artefacto es un ZIP; extráelo para obtener `Plex-Media-Noche-arm64.apk`.

La próxima compilación usará el identificador independiente `com.plexmedianoche.kodi`, para instalar Plex Media Noche junto a Kodi sin sustituirlo ni borrar sus datos. La clave de prueba se reutiliza en las compilaciones posteriores para permitir actualizar esta app de prueba. No es una versión de publicación. Los artefactos de APK se conservan durante 7 días.

## Validar el skin

El flujo **Validar skin de Plex Media Noche** se ejecuta cuando cambia el paquete del proyecto o su propio archivo de flujo. También se puede iniciar manualmente desde **Actions**. Si termina correctamente, publica el artefacto **Plex-Media-Noche-skin**.

## Requisitos para la siguiente fase

- Seguir la referencia visual compartida: estética cinematográfica oscura, título destacado, información de novedades y sincronización, y carruseles separados para series y películas.
- Configurar complementos de subtítulos y tráileres para películas y series, accesibles desde el contenido correspondiente y sin accesos globales en el menú principal.
- Sincronizar diariamente las novedades de PlexKodiConnect y hacer una actualización completa de la biblioteca cada martes para mantenerla actualizada y reorganizada, conservando la configuración existente.
