# Revisión de skins y mejoras de la beta 5

Revisión de código público, 21 de octubre de 2026. No se instalaron ni midieron los skins de referencia ni se probaron en Kodi estas mejoras.

| Referencia revisada | Evidencia en el código | Aplicación en Media Noche |
| --- | --- | --- |
| Estuary, rama Omega de Kodi | Home ofrece películas a medias y colecciones; la playlist inprogress_movies usa inprogress=true y lastplayed descendente. | Categoría Continuar en Cine y acceso a Colecciones mediante MovieSets. |
| Arctic Horizon 2, revisión 5668ff2bc9ef4bcbef72cb53e1f54e0b98e3bf5d | InProgressEpisodes usa la regla nativa inprogress para episodios. El repositorio figura archivado. | Categoría Continuar episodios en Series, separada de series finalizadas y de episodios recién añadidos. |
| Nimbus, revisión 8b5071b8cd0db3a8e813eb00e9a821d3efad2454 | SkinSettings ofrece configuración de widgets, navegación y visibilidad de sinopsis del OSD. | Dos configuraciones sencillas del inicio y una opción propia, más acotada, para ocultar sinopsis de episodios sin ver. |

Fuentes consultadas:
- [Home de Estuary](https://github.com/xbmc/xbmc/blob/Omega/addons/skin.estuary/xml/Home.xml)
- [Películas a medias de Estuary](https://github.com/xbmc/xbmc/blob/Omega/addons/skin.estuary/playlists/inprogress_movies.xsp)
- [Episodios a medias de Horizon 2](https://github.com/jurialmunkey/skin.arctic.horizon.2/blob/5668ff2bc9ef4bcbef72cb53e1f54e0b98e3bf5d/extras/playlists/InProgressEpisodes.xsp)
- [Ajustes de Nimbus](https://github.com/ivarbrandt/skin.nimbus/blob/8b5071b8cd0db3a8e813eb00e9a821d3efad2454/xml/SkinSettings.xml)
- [Entradas nativas de la biblioteca, incluido MovieSets](https://github.com/xbmc/xbmc/blob/Omega/xbmc/video/windows/GUIWindowVideoNav.cpp)

## Implementado

1. Cine → Continuar y Series → Continuar episodios, con playlists nativas ordenadas por última reproducción. Solo muestran reproducciones a medias; no predicen automáticamente el siguiente capítulo.
2. Diseño → Filas del inicio: catálogo/continuar. La segunda opción convierte las dos primeras filas en episodios y películas a medias; conserva las filas de estrenos y novedades. El catálogo sigue siendo la opción inicial cuando el ajuste no existe.
3. Diseño → Sinopsis de episodios sin ver: visibles/ocultas. Afecta a las cabeceras nuevas y a las fichas abiertas desde sus carátulas. Oculta texto cuando Kodi informa playcount=0; no oculta títulos ni imágenes y no pretende proteger todas las ventanas nativas o complementos externos. No cambia la sinopsis guardada en la base de datos.
4. Cine/Novedades cine → Colecciones en la barra superior. Abre las agrupaciones de películas que ya existan en Kodi; no crea sagas ni modifica metadatos.

Series estrenos conserva exactamente sus dos categorías originales. Las funciones anteriores se implementan con Kodi y la estructura propia, sin incorporar un skin de referencia ni añadir sus helpers o servicios.

## Validación y prueba pendiente

Pasan las comprobaciones de las seis ventanas generadas, fuentes, límites 1080p, foco, destinos, playlists y preservación de Home. Se comprueba el tipo y la regla de las playlists a medias, el intercambio de las filas y las opciones de visibilidad.

Hay nueve pruebas unitarias de datos de fichas y favoritos con API simulada: la nueva prueba verifica que ocultar sinopsis solo afecta a episodios sin ver, que películas/episodios vistos mantienen el texto, que el comportamiento por defecto se conserva y que no se altera el diccionario de datos original.

Antes de dar por funcional la beta: probar en Kodi con una película y un episodio realmente a medias; cambiar el inicio a ambos modos; activar/desactivar la sinopsis y abrir la ficha; comprobar una colección conocida. Las pruebas de código o el ZIP no demuestran esa ejecución.

## Siguientes ideas para valorar juntos

Búsqueda unificada de la biblioteca, más opciones de presentación de reparto y filtros combinados mediante listas inteligentes. Antes de añadir proveedores de valoraciones o recomendaciones externas conviene comprobar qué datos ya sincroniza PKC.

Rutas, sincronización, EPG y catch-up quedan para la sesión con el usuario en el PC. No se ha cambiado la configuración de TV.
