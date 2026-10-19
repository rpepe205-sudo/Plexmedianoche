# Plex Media Noche

Kodi personalizado para Android con interfaz cinematográfica y PlexKodiConnect.

## Qué hay en el repositorio

- `Plex_de_Media_Noche_0.4.0_KIT.zip`: paquete del skin y archivos de configuración del proyecto.
- `.github/workflows/build-android.yml`: compila Kodi para Android ARM64 e incorpora el skin.
- `.github/workflows/validate-skin.yml`: comprueba los XML del skin y genera un ZIP instalable.

## Obtener la APK de prueba

En GitHub, abre **Actions**, selecciona **Crear APK de Plex Media Noche** y pulsa **Run workflow** si no hay una compilación en curso. Cuando termine correctamente, abre esa ejecución y descarga el artefacto **Plex-Media-Noche-APK-arm64**.

La APK de GitHub Actions se firma con una clave de depuración y el artefacto se conserva durante 7 días. Es una compilación de prueba, no una versión de publicación.

## Validar el skin

El flujo **Validar skin de Plex Media Noche** se ejecuta cuando cambia el paquete del proyecto o su propio archivo de flujo. También se puede iniciar manualmente desde **Actions**. Si termina correctamente, publica el artefacto **Plex-Media-Noche-skin**.

## Requisitos para la siguiente fase

- Configurar complementos de subtítulos y tráileres para películas y series, accesibles desde el contenido correspondiente y sin añadir accesos al menú principal.
- Sincronizar diariamente las novedades de PlexKodiConnect y hacer una actualización completa de la biblioteca cada martes para mantenerla actualizada y reorganizada, conservando la configuración existente.
