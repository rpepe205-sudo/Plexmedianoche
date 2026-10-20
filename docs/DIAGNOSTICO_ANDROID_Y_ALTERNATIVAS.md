# Diagnóstico Android y alternativas — 20 de octubre de 2026

## Recomendación para una biblioteca Plex compartida

Usar Kodi oficial 21 Omega + PlexKodiConnect (PKC) + el ZIP del skin. Evita mantener un fork completo de Kodi y permite desarrollar la interfaz sin reconstruir una APK. La invitación debe estar aceptada en la misma cuenta Plex que se usa para iniciar sesión en PKC. Elegir el servidor remoto y las bibliotecas autorizadas; usar **Addon (Default)**, sin rutas nativas SMB/NFS. No se necesita administrar el servidor para utilizar la biblioteca compartida, pero su disponibilidad, permisos y capacidad de transcodificación dependen del propietario.

| Alternativa | Encaje en este caso | Condiciones |
| --- | --- | --- |
| Kodi oficial + PKC + skin | Recomendación | PKC sincroniza con la base de datos nativa de Kodi y admite Omega. Comprobar acceso con la cuenta invitada y reproducción en el dispositivo. |
| Kodi sin complemento Plex | Insuficiente por sí solo | Una invitación de Plex no proporciona acceso SMB/NFS a los archivos. Necesita un complemento que autentique contra Plex. |
| Cliente oficial Plex | Referencia para comprobar acceso y reproducción | Permite separar un problema de permisos/servidor de un problema de PKC o del skin; no ofrece el skin personalizado de Kodi. |
| APK propia basada en Kodi | Posible, mayor coste de mantenimiento | Compilación nativa, dependencias, firma e integración de complementos. Compilarla no concede nuevos permisos Plex. La APK heredada no instala PKC automáticamente. |
| Jellyfin | No sustituye directamente la invitación actual | Jellyfin sirve bibliotecas de archivos accesibles para su propio servidor. La invitación Plex no equivale a acceso a esos archivos ni a una cuenta Jellyfin. Haría falta colaboración del propietario para ofrecer Jellyfin. |

La compatibilidad de PKC no garantiza acceso a una biblioteca concreta. No se ha iniciado sesión en la cuenta Plex del usuario ni se ha reproducido contenido real. No introducir tokens Plex en el repositorio, ZIP o logs. PKC gestiona la biblioteca: conservar la protección existente contra UpdateLibrary/CleanLibrary cuando está instalado.

Fuentes primarias consultadas:

- [Funciones y compatibilidad de PKC](https://github.com/croneter/PlexKodiConnect).
- [Configuración inicial de PKC: autenticación, servidores remotos y modo Addon](https://github.com/croneter/PlexKodiConnect/wiki/Configure-PKC-on-the-First-Run).
- [Invitaciones y acceso compartido Plex](https://support.plex.tv/articles/201105738-creating-and-managing-server-shares/).
- [Bibliotecas Jellyfin y rutas de archivos](https://jellyfin.org/docs/general/server/libraries/).

## Resultados observados en GitHub Actions

- [39390582675](https://github.com/rpepe205-sudo/Plexmedianoche/actions/runs/39390582675): fallo en **Compilar Kodi**, código de salida 2; dependencias y generación CMake terminaron correctamente. No llegó al empaquetado de APK. Las anotaciones indican que no encontró libzip.a ni libmicrohttpd.a en la ruta fija comprobada.
- [39385854878](https://github.com/rpepe205-sudo/Plexmedianoche/actions/runs/39385854878): fallo en **Preparar dependencias de Kodi**. Las etapas posteriores se omitieron.
- [39369721218](https://github.com/rpepe205-sudo/Plexmedianoche/actions/runs/39369721218): fallo en **Compilar Kodi**.
- [39250145366](https://github.com/rpepe205-sudo/Plexmedianoche/actions/runs/39250145366): ejecución Android anterior correcta, incluida creación y publicación de APK. Ese éxito corresponde a otro commit; no valida main actual ni su funcionamiento en el dispositivo.
- [39396062807](https://github.com/rpepe205-sudo/Plexmedianoche/actions/runs/39396062807): empaquetado del skin Omega correcto. No es una compilación Android ni una prueba de navegación en Kodi.

La descarga de los logs completos mediante el conector falla con `Transport closed`; GitHub exige iniciar sesión para verlos en la página pública. La red del ejecutor tampoco consigue conectar con el proxy configurado. Por tanto, **no se ha identificado el mensaje exacto del compilador/enlazador**. Los ajustes TLS anteriores se conservan como hipótesis heredada, sin atribuirles un diagnóstico nuevo. No afirmar que el fallo C++ esté resuelto hasta completar otra compilación.

## Errores de configuración corregidos

1. El workflow clonaba la rama móvil master de Kodi. En la revisión consultada, `version.txt` declara **23.0 ALPHA1**, incompatible con el objetivo documentado 21.1 Omega. Se fija Kodi 21.1 a `183eb85f108c3d8b44a578de80f575f27afe9b9a`.
2. SDK/NDK y herramientas correspondían al Kodi actual. Se alinean con la [guía de Android de Kodi 21.1](https://github.com/xbmc/xbmc/blob/21.1-Omega/docs/README.Android.md): API de plataforma 34, build-tools 33.0.1, NDK r21e 21.4.7075529, Java 17 y ruta NDK explícita.
3. Se eliminan los parches de nombres de objetivos CMake: APP_NAME se mantiene como Kodi; solo cambia APP_PACKAGE a com.plexmedianoche.kodi.
4. La ruta fija `arm-linux-androideabi-24-debug` podía omitir las bibliotecas reales. Se descubre el prefijo instalado ARM32 y se exige comprobar ambos archivos estáticos y sus referencias crypto antes de compilar Kodi.
5. La caché de bibliotecas compiladas no estaba vinculada a la revisión Kodi ni al toolchain y no conservaba todo el estado Make. Se retira esa caché y se conservan solo las descargas. La primera compilación será más lenta, pero no reutilizará binarios de otra versión.
6. Se elimina el disparador push de la APK; queda manual. Los cambios se comprueban con un workflow corto de YAML, bash, Python y XML.
7. Se conservan logs de bootstrap, configure, dependencias, CMake, compilación y empaquetado mediante tee y pipefail, y se publican como artefacto incluso tras fallo. La APK se comprueba además con apksigner, aapt y prueba de integridad ZIP.
8. La base Arctic v3.0.3 se fija por SHA. Se diferencia el artefacto de maqueta experimental del ZIP basado en Arctic; la APK heredada sigue usando la maqueta y **no equivale al skin Arctic personalizado**.

## Validación y pasos pendientes

Validado localmente: cuatro workflows parsean; todos sus bloques bash y Python incrustado tienen sintaxis válida; XML y Python del proyecto parsean. Los parches TLS y de empaquetado se aplican a los archivos de Kodi 21.1. La comprobación de archivos estáticos se ejercitó con archivos reales creados mediante cc/ar: acepta el prefijo API 21 y archivos válidos, rechaza prefijo ausente y símbolos crypto pendientes.

Pendiente: compilación completa de dependencias y APK con el nuevo origen, descarga e instalación de la APK, firma persistente y prueba de Plex/PKC en el Android TV Box. La firma actual es de depuración y su continuidad depende de una caché, no de una clave de lanzamiento persistente. No se han lanzado compilaciones largas durante esta revisión.

Para seguir por la vía recomendada, probar primero Kodi oficial + PKC con la invitación real y después instalar el ZIP del skin. Para continuar la APK, ejecutar manualmente el workflow en la rama corregida y revisar el artefacto de diagnóstico si falla; no reutilizar ni relanzar el workflow antiguo sin cambios.
