# Diseño cinematográfico — Plex Media Noche 3.0.4~beta2

## Qué incorpora el paquete

| Pantalla | Diseño y contenido |
| --- | --- |
| Inicio | Cabecera con fanart y sinopsis del título seleccionado, marca, reloj y fecha reales; cuatro filas: Series, Cine, Series estrenos y Novedades cine. |
| Series estrenos | Dos categorías a la izquierda: Series completas (finalizadas, últimas incorporaciones primero) y Episodios recientes. |
| Series | Todas las series, Finalizadas y Episodios recientes. |
| Cine | Todas las películas, Añadidas recientemente y Sin ver. |
| Novedades cine | Últimas incorporaciones y Pendientes de ver. |
| Fichas | Ventana nativa con fondo nocturno, fanart tenue, 20 botones con icono y texto persistente y foco dorado. |
| Diseño | Elección entre inicio cinematográfico e inicio clásico; acceso a ajustes del skin. |
| TV, Favoritos, ajustes y apagado | Accesos a las ventanas nativas de Kodi; la paleta nocturna ya se aplica al skin base. |

Las carátulas conservan la proporción 2:3 y la categoría elegida queda marcada al explorar la fila. Los títulos, fanart, género, año, sinopsis, temporadas y episodios proceden de Kodi. No se incluyen carátulas de muestra, meteorología inventada ni supuestas fechas de sincronización.

El inicio consulta hasta 13 elementos por fila (52 en total); las bibliotecas interiores conservan el catálogo completo. No se reproducen tráilers automáticamente. Se precarga un elemento por fila para contener el coste en Android TV.

## Pulido de la beta 2

Los menús conservan texto visible y añaden iconos nativos con colores de foco de alto contraste. Las carátulas muestran Visto o Continuar únicamente cuando Kodi proporciona ese estado; son indicadores de lectura, sin una nueva acción para marcar contenido visto.

La carátula se obtiene por prioridad: poster del elemento, poster de la serie y miniatura. El fanart puede heredarse de la serie y el clearlogo solo aparece si existe. Se mantienen proporciones, datos reales y las acciones ya implementadas.

## Navegación y fichas

- Las categorías de la izquierda abren su lista en la navegación nativa al aceptar. Derecha pasa a las carátulas y Atrás regresa a la categoría elegida.
- Las carátulas de series abren las temporadas reales de la biblioteca. Las de películas y episodios consultan los detalles locales por ID y abren el diálogo nativo de Kodi con ruta, ID, carátulas y posición de reproducción.
- El helper de fichas utiliza InfoTagVideo y Dialog.info disponibles en Kodi Omega; los campos solicitados se contrastaron con el esquema JSON-RPC de Omega. La reproducción concreta de las rutas PKC requiere prueba real.
- Los botones nativos de Reproducir, Continuar y temporadas se conservan. El tráiler solo se ofrece con ListItem.Trailer.
- Favoritos consulta y alterna el estado de Kodi, con lectura posterior para confirmar. No modifica listas del servidor Plex.
- Inicio clásico conserva Home.xml original. La entrada cinematográfica se realiza mediante los includes de control inicial del Home, condicionada por la preferencia medianoche.nativehome. El cambio se revierte desde Diseño → Inicio clásico.

## Verificación realizada

- Sintaxis Python, XML y playlists.
- Seis ventanas generadas con IDs sin colisiones con las ventanas del upstream fijado.
- Fuentes contrastadas con Font.xml; controles dentro de 1920×1080; destinos de foco y playlists existentes.
- Home.xml conservado; controles originales de la ficha intactos al añadir el fondo.
- Cuatro pruebas de datos de fichas (rutas plugin, ID/resume/art, consulta de episodios, errores).
- Cuatro pruebas de Favoritos (ciclo realista añadir/quitar con API simulada, nombres personalizados, ventanas de series y fallos).
- Regresiones de los 19 IDs nativos de botones y visibilidad persistente de etiquetas.
- GitHub Actions prepara el ZIP, valida todos los XML y comprueba la integridad del archivo. Consultar el resultado del run para el commit entregado.

## Pendiente en el equipo del usuario

No se ha ejecutado Kodi ni revisado visualmente este diseño en un render real de Kodi. runtime_tested sigue false y el PR permanece como borrador.

Al llegar al PC, instalar el ZIP y probar primero el inicio, Diseño → Inicio clásico/cinematográfico, las categorías y la vuelta con mando. Después probar una película, una serie y un episodio con PKC, reanudación, favoritos, tráiler, subtítulos e IPTV; repetir en Xiaomi/Homatics para revisar legibilidad y rendimiento.

Las rutas y la sincronización se dejan para esa sesión. El posible fallo previo de las series no está diagnosticado. Una fila vacía no demuestra que el skin esté roto: hay que comprobar la biblioteca y el registro de PKC. El filtro de finalizadas depende de que Kodi tenga status=Ended; no se deduce a partir de capítulos vistos ni garantiza que todos estén disponibles.

## Instalación

Descargar el artefacto Plex-Media-Noche-skin-Kodi-21-Omega de la compilación entregada. Extraerlo y, en Kodi, instalar el archivo interior PlexMediaNoche-skin-Omega.zip. El ZIP del código del repositorio y el contenedor exterior del artefacto no son el addon.

La versión del fork es 3.0.4~beta2, con ID skin.plexmedianoche; la base continúa fijada en Arctic Zephyr Reloaded 3.0.3, SHA 27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51. Se mantienen dependencias y atribución originales. No se construye APK.
