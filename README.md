# Plex Media Noche — skin para Kodi 21.1 Omega

Proyecto de personalización de **Arctic: Zephyr - Reloaded** para Kodi 21.1 Omega. El objetivo inmediato es un ZIP instalable de skin; la prioridad actual no es construir una APK.

## Estado actual

La ruta activa es un skin independiente `skin.plexmedianoche`, con menú inicial personalizado. Aún no es el diseño final probado en los dispositivos.

- Base Arctic: Zephyr - Reloaded 3.0.3 fijada al commit `27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51`.
- El workflow `build-skin-omega.yml` y el ordenador usan `scripts/build_skin.py` para crear y comprobar el mismo paquete.
- Se conservan las dependencias, los créditos y la portada original; se cambia el identificador interno y el menú de Skin Shortcuts.
- La APK antigua queda solo manual. La validación del KIT antiguo ya no publica otro ZIP distinto.
- Véase [la auditoría y las pruebas pendientes](docs/AUDITORIA.md).

Para empaquetar localmente con Python 3.10 o superior, descargar la base del commit fijado y ejecutar:

```text
python scripts/build_skin.py --source RUTA_BASE_ARCTIC --output RUTA_NUEVA_DE_SALIDA
```

La salida debe ser nueva para evitar sobrescribir una compilación anterior. El ZIP y su SHA256 se generan juntos. No incluye credenciales, bibliotecas Plex ni listas IPTV.

## Diseño acordado

- Apariencia cinematográfica nocturna, carbón/azul noche, con detalles dorados y azules.
- Menú principal: **Inicio, Favoritos, Series estrenos, Series, Novedades cine, TV, Ajustes y Apagar**.
- Widgets ligeros para continuar viendo, episodios recientes, series y películas añadidas recientemente.
- Tráilers dentro de las fichas de películas, no como sección independiente.
- TV/IPTV integrada con los canales configurados en Kodi.
- Navegación fiable con mando y compatibilidad con PlexKodiConnect; no automatizar limpiezas que puedan interferir con la biblioteca sincronizada.

## Validación pendiente

Un workflow verde y un ZIP íntegro no demuestran que el skin funcione en el Xiaomi. Hay que instalarlo en Kodi 21.1 Omega y verificar navegación, widgets, carátulas, biblioteca de PlexKodiConnect y TV/IPTV. El paquete usa el ID independiente `skin.plexmedianoche`; la instalación y resolución real de dependencias aún deben verificarse en Kodi.
