# Fichas y biblioteca — Kodi 21 Omega

## Cambios implementados

- 20 controles de las fichas con icono y texto persistente, fuente Tiny de la base (26 px), botones de 390×88 y foco dorado. Los 19 IDs nativos y sus rutas de navegación se conservan; Favoritos usa el ID nuevo 9876.
- Reproducir/Continuar refleja ListItem.IsResumable. Temporadas y episodios conserva SendClick(8). El acceso de siguiente episodio se mantiene condicionado a una ruta real de la biblioteca.
- Información muestra el panel local; no necesita una consulta a Embuary para esa acción.
- Los dos modos de tráiler y su vista previa exigen ListItem.Trailer. No se usa una búsqueda IMDB/Bingie como sustituto de una fuente conocida.
- Favoritos consulta Favourites.GetFavourites y utiliza Favourites.AddFavourite, cuya implementación en Kodi Omega alterna añadir/quitar. Vuelve a consultar para confirmar el cambio. Conserva los nombres personalizados al quitar. Las películas apuntan al archivo/plugin registrado por Kodi; las series abren temporadas en videodb. No cambia favoritos del servidor Plex.
- Cine: catálogo completo por título de ordenación. Novedades cine: catálogo por fecha de incorporación descendente. No se aplica un límite de días.
- El menú principal conserva Series estrenos. Abre la ventana 1190, con Series completas y Episodios recientes como categorías a la izquierda y carátulas a la derecha. Aceptar sobre una categoría abre su playlist en la navegación nativa; las carátulas permiten abrir temporadas o reproducir episodios.
- Series completas: tipo tvshows, status is Ended, dateadded descendente. Episodios recientes conserva la playlist de episodios.

## Semántica de Series completas

Decisión del usuario: series añadidas recientemente que ya estén finalizadas, no comprobar que todos los episodios estén disponibles. Se muestran las finalizadas empezando por las últimas incorporadas, sin ventana temporal arbitraria.
Kodi Omega admite FieldTvShowStatus en playlists de tipo tvshows. El filtro necesita que PKC haya escrito Ended en el campo status de Kodi; falta comprobarlo con esta biblioteca. Si falta ese dato, el apartado puede quedar vacío. La entrada Series conserva todo el catálogo. No se infiere finalización por cantidad de episodios o por estado visto.

## Verificación

Pruebas estáticas sobre Includes.xml, Includes_DialogVideoInfo.xml y DialogVideoInfo.xml de la revisión 27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51:
IDs conservados, etiquetas sin dependencia del foco, acciones nativas no afectadas, otros includes sin modificaciones y tráilers sin búsqueda de fuentes inventadas.

Cuatro pruebas de Favoritos con API simulada: ciclo añadir/consultar/quitar conservando rutas plugin y nombres personalizados, acceso a temporadas, respuesta OK sin cambio real, y rechazo de elementos no compatibles.

El workflow ejecuta estas comprobaciones, prepara el addon, valida XML, conserva Home.xml y empaqueta con SHA256. Un ZIP generado no equivale a una prueba en Kodi. runtime_tested permanece false.

## Instalar y probar

1. Abrir el run del workflow enlazado en el PR y descargar el artefacto Plex-Media-Noche-skin-Kodi-21-Omega. Extraer ese contenedor para obtener PlexMediaNoche-skin-Omega.zip; el artefacto exterior no es el addon.
2. En Kodi 21: Ajustes → Add-ons → Instalar desde un archivo ZIP → seleccionar PlexMediaNoche-skin-Omega.zip. Instalar las dependencias indicadas por Kodi y elegir Plex Media Noche como skin.
3. Película: comprobar texto sin foco, reproducir y continuar, Información local, tráiler con y sin fuente, y favoritos al abrir de nuevo la ficha. Confirmar el favorito también en el menú de Kodi.
4. Serie: abrir temporadas/episodios, reproducir el siguiente episodio cuando esté disponible, añadir/quitar favorito y abrirlo desde Favoritos.
5. Comparar Series completas con una serie finalizada conocida y otra en emisión; comprobar el estado sincronizado por PKC. Episodios recientes debe mostrar episodios, no series.
6. Con mando: izquierda/derecha por toda la barra, subir/bajar, aceptar y volver; revisar recorte de etiquetas y desplazamiento horizontal en Windows y Xiaomi/Homatics.
7. Comprobar IPTV con PVR IPTV Simple Client, subtítulos y reproducción con PKC en modo Addon.

No se ha accedido al PC ni ejecutado Kodi en esta sesión. No se implementa Marcar visto sin ensayo real de compatibilidad con PKC. No se incluyen credenciales, bases de datos ni URLs privadas.
