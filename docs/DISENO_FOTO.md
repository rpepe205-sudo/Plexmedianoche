# Portada Plex Media Noche 0.5.0

Referencia: foto aportada por el usuario el 20 de octubre de 2026, diseñada desde
el móvil. Es el objetivo visual actual y sustituye al menú anterior como dirección
del proyecto. Destino: Xiaomi y Homatics con Android TV. El PC solo sirve para
probar el skin; no instalar PlexKodiConnect en el PC.

## Implementación

`scripts/photo_layout.py` genera una portada nativa de Kodi a 1920×1080: fanart
panorámico, metadatos reales, banda de ocho tarjetas, cuatro filas con filtros,
barra inferior, azul noche y foco dorado. Los menús de vídeo, fichas, ajustes,
reproductor, TV y diálogos se conservan de Arctic Reloaded. El paquete incluye
la portada upstream como referencia en resources/upstream-Home.xml.

El menú superior contiene Favoritos, Estrenos de series, Series, Cine, Estrenos
de cine, TV, Tráilers y Subtítulos. La barra inferior añade Ajustes y Apagar.
Tráilers usa el tráiler disponible de la película destacada. Subtítulos se habilita
durante la reproducción de vídeo. No se muestran fechas de actualización ficticias.
Estrenos se alimenta de añadidos recientes de la biblioteca, no de una cartelera.
Los filtros laterales solo ofrecen categorías que tienen una ruta real en Kodi.

Las filas consumen videodb:// y no incluyen contenido del servidor ni credenciales.
La primera vez, con biblioteca vacía, se presenta un mensaje de espera. No hace
falta conectar Plex para comprobar instalación, fuentes, foco y botones del skin.
La foto de referencia contiene carátulas y fanart: el resultado visual con catálogo
lleno todavía necesita una prueba posterior con una biblioteca de prueba o real.

## Android

El manifiesto mantiene plataforma all y la API de Kodi Omega. No se incluyen
ejecutables Windows, rutas de discos, servicios de mantenimiento ni código ARM
compilado. Se usan controles de Kodi y navegación con flechas/OK/Atrás.
Esto permite compartir el ZIP entre plataformas, pero no sustituye las pruebas
en Android TV: falta verificar foco con los mandos Xiaomi/Homatics, carga de
carátulas, reproducción 1080p, audio y subtítulos en esos equipos.

## Reproducir el paquete

Descargar la base Arctic del commit fijado por build-skin-omega.yml y ejecutar:

```text
python scripts/build_skin.py --source RUTA_BASE_ARCTIC --output RUTA_NUEVA --photo
```

La comprobación incluye identidades, dependencias, XML, fuentes, texturas,
identificadores únicos y destinos de navegación. El workflow usa el mismo comando.
El ZIP es una versión de prueba del skin y no una APK ni una biblioteca incluida.
