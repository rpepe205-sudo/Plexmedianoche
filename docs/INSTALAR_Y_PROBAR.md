# Plex Media Noche: instalación y pruebas

Este paquete es una versión para pruebas. El empaquetado verifica XML, iconos, dependencias declaradas y la integridad del ZIP. Todavía no acredita instalación ni reproducción en Windows o Android.

## Contenido del paquete

- `PlexMediaNoche-skin-Omega.zip`: complemento `skin.plexmedianoche`, independiente de Arctic original.
- `validacion-skin.json`: dependencias declaradas, versión y comprobaciones realizadas. `runtime_tested: false` indica que no se ha probado en Kodi.
- `SHA256SUMS.txt`: huella del ZIP para comprobar descargas.
- `arctic-source-sha.txt`: revisión exacta de la base upstream.

No descomprimir el ZIP del skin para instalarlo. Si se descarga el artefacto ZIP de GitHub Actions, extraer primero ese envoltorio para encontrar `PlexMediaNoche-skin-Omega.zip`.

## Primero, Windows 11

1. Utilizar Kodi oficial de la serie 21 Omega. Comprobar la versión en Información del sistema. Para las primeras pruebas, usar un perfil separado sin una biblioteca local que sea necesario conservar: PlexKodiConnect administra directamente la base de datos de Kodi.
2. En Complementos, instalar desde archivo ZIP y seleccionar el ZIP del skin. Si Kodi lo solicita, permitir orígenes desconocidos para instalar este paquete. Resolver las dependencias que muestre Kodi; consultar la lista exacta en `validacion-skin.json` si falla alguna. El paquete no incluye copias de esas dependencias.
3. Seleccionar Plex Media Noche en Ajustes > Interfaz > Skin. Conservar Estuary como alternativa para volver a una interfaz conocida.
4. El tema inicial añade azul noche, dorado y azul claro; limita los widgets a 12 elementos por fila y desactiva reflejos en un perfil nuevo. Las opciones existentes de un perfil ya configurado no se reinician. Las paletas `Media Noche` y `Arctic Original` quedan disponibles en los colores del skin.

## PlexKodiConnect (PKC)

1. Añadir la fuente HTTPS `https://croneter.github.io/pkc-source/` en el administrador de archivos de Kodi.
2. Instalar desde ZIP `repository.plexkodiconnect.Kodi-Omega.STABLE.zip` de esa fuente.
3. Instalar desde repositorio > PlexKodiConnect Addons > Complementos de vídeo > PlexKodiConnect. Dejar que Kodi resuelva sus dependencias; no copiar complementos binarios de otro sistema.
4. Iniciar sesión con la cuenta Plex que tiene aceptada la invitación. Autorizar mediante el flujo que muestra PKC; no guardar códigos ni tokens en GitHub o en un paquete de distribución.
5. Elegir el servidor remoto autorizado y el modo **Addon (Default)**. No añadir rutas de Windows, SMB ni NFS para esta biblioteca compartida.
6. Esperar la sincronización. PKC no viene preinstalado en este ZIP de skin y el inicio de sesión requiere intervención del usuario en su equipo.

Referencias: [instalación de PKC](https://github.com/croneter/PlexKodiConnect/wiki/Installation) y [configuración inicial](https://github.com/croneter/PlexKodiConnect/wiki/Configure-PKC-on-the-First-Run).

## Televisión

Instalar **PVR IPTV Simple Client** desde el repositorio oficial de Kodi correspondiente a ese sistema. Configurar la lista M3U remota de forma privada en el equipo, habilitar el cliente y comprobar canales y reproducción. La URL facilitada contiene credenciales y no se incluye en este paquete. Configurar una EPG XMLTV solo cuando se disponga de su dirección; no inventar una URL. El skin muestra TV mediante los canales PVR de Kodi y no actúa como cliente IPTV por sí mismo.

## Pruebas antes de pasar a Android

- Abrir los nueve accesos: Inicio, Favoritos, Series estrenos, Series, Cine, Novedades cine, TV, Ajustes y Apagar. Inicio vuelve a la portada; no es una sección de contenido independiente.
- Comprobar textos, contraste, foco, flechas, atrás y acceso a Ajustes. Comprobar que no aparecen errores al generar el menú con Skin Shortcuts.
- Probar una película y un episodio autorizados, pausa, reanudación, audio y subtítulos. Revisar que continuar viendo y el estado visto se sincronizan con Plex.
- Configurar los widgets mediante las opciones nativas de Arctic. La maqueta conceptual no equivale a widgets ya conectados ni a una captura de Kodi real.
- Probar varios canales, cambio de canal, audio y guía de programación cuando exista EPG.
- Si falla algo, recoger el registro Kodi después de reproducir el problema. Revisar y ocultar tokens Plex, credenciales y URL de IPTV antes de compartirlo.

## Copias y Android

Con Kodi cerrado se puede conservar una copia privada completa como recuperación del PC. No publicarla: puede incluir cuentas y credenciales.

Para trasladar la personalización, guardar el skin y revisar los ajustes de `addon_data/skin.plexmedianoche` y los datos de Skin Shortcuts del perfil. Exportar solo lo necesario para el skin; revisar que no haya rutas absolutas ni información privada. Una copia completa de Windows no es un instalador portable para Android.

En cada Android: instalar Kodi y los complementos de esa plataforma, instalar el mismo ZIP de skin, aplicar los ajustes compatibles, iniciar sesión en PKC y sincronizar. Configurar TV de forma privada. Probar reproducción y navegación con mando en un primer dispositivo antes de repetir en los demás. La biblioteca local de PKC se genera por dispositivo; no restaurar su base de datos de Windows como si fuera universal.
