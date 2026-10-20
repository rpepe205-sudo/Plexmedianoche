# Plex Media Noche — skin para Kodi Omega

Interfaz para Android TV (Xiaomi y Homatics), basada en Arctic: Zephyr - Reloaded 3.0.3. El objetivo visual actual es la foto aportada por el usuario: portada panorámica, tarjetas, cuatro filas de biblioteca, azul noche y foco dorado.

## Estado real

- Skin independiente `skin.plexmedianoche` 0.5.0 con portada nativa personalizada.
- El PC es solo banco de pruebas. Android es el destino final.
- Instalación y apertura comprobadas en Kodi 21.3 para Windows; se está verificando la navegación.
- Biblioteca vacía de forma intencionada durante esta fase. No instalar PlexKodiConnect en el PC ni conectar Plex hasta terminar el skin.
- Pendientes: comprobación visual con catálogo lleno, mandos Xiaomi/Homatics y reproducción en Android.
- No es una APK nueva ni incluye películas, credenciales o IPTV.

[Diseño y compatibilidad](docs/DISENO_FOTO.md) · [Auditoría de archivos y Actions](docs/AUDITORIA.md)

## Paquete reproducible

La base Arctic se fija al commit `27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51`. Descargar ese commit y ejecutar con Python 3.10 o superior:

```text
python scripts/build_skin.py --source RUTA_BASE_ARCTIC --output RUTA_NUEVA --photo
```

El workflow `build-skin-omega.yml` utiliza ese mismo comando y lo valida en pull requests. Comprueba XML, dependencias, fuentes, texturas, controles, navegación, estructura ZIP y SHA256. La portada upstream se guarda como referencia; las fichas, menús de vídeo y reproductor se conservan de Arctic. El comando sin `--photo` permite reproducir la base anterior.

## Instalación prevista en Android

Usar Kodi 21 Omega y resolver las dependencias oficiales de Arctic Reloaded. Instalar el ZIP del skin y seleccionarlo en Ajustes → Interfaz → Skin. La instalación real en Xiaomi y Homatics todavía debe probarse; no se considera verificada por funcionar en Windows.

Después de aprobar el skin se configurarán PlexKodiConnect con la cuenta invitada y PVR IPTV Simple Client con la lista M3U y guía XMLTV del usuario. No ejecutar limpiezas automáticas sobre la biblioteca de PlexKodiConnect.

## Flujos antiguos

La APK queda solo manual y experimental; no se ha reparado ni relanzado. La validación del KIT antiguo queda manual y no publica otro ZIP. La ruta activa entrega un único skin para Kodi, sin recompilar Kodi.
