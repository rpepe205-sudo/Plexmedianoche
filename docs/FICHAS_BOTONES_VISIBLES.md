# Fichas de películas y series: botones visibles

## Decisión de diseño (21-10-2026)

La interfaz de Plex Media Noche mostrará **icono y texto siempre visibles** en los botones de las fichas, incluso cuando el foco del mando esté en otro control. No depender del hover, del ratón ni de que el botón esté seleccionado para mostrar su nombre.

- Películas: **Reproducir**, **Tráiler**, **Información**, **Favoritos**.
- Series: **Reproducir / Continuar**, **Temporadas y episodios**, **Información**, **Favoritos**.
- Estado **Visto**: solo mostrar la acción si existe un método compatible para marcar contenido visto en la biblioteca Kodi/PKC.
- Tráiler: solo habilitar cuando haya fuente reproducible; no inventar URL ni añadir un acceso roto.
- Favoritos: emplear la acción real soportada por Kodi; comprobar si el elemento ya es favorito y mostrar el estado correcto.
- La navegación por episodios debe abrir temporadas y capítulos reales de la biblioteca sincronizada, no una lista vacía.

## Estética y mando

Fondo azul noche/carbón, detalles dorados, texto legible desde el sofá, contraste alto y foco destacado en dorado. No usar solo color para diferenciar acciones. Permitir izquierda/derecha, aceptar y volver con mando Android TV. No sacrificar legibilidad para mantener más botones en una fila.

## Plan de implementación

1. Inspeccionar en la revisión fijada de Arctic: Zephyr - Reloaded 3.0.3 las ventanas y los includes reales de información de vídeo (p. ej. DialogVideoInfo.xml y sus Includes), sus control IDs, labels, acciones y condiciones.
2. Determinar qué botones son nativos y cuáles requieren personalización. Evitar duplicar botones, modificar IDs de navegación sin pruebas o reemplazar la ventana entera sin necesidad.
3. Añadir parches mínimos y comprobables a `scripts/prepare_skin.py` o recursos versionados bajo `skin/`, sin sustituir `1080i/Home.xml`.
4. Probar XML válido, etiquetas visibles, condiciones de disponibilidad, dependencias, navegación por foco y empaquetado reproducible.
5. Probar en Kodi 21 Omega con una película y una serie reales desde PlexKodiConnect. Confirmar reproducir, continuar, tráiler disponible/no disponible, información, favoritos y episodios. Comprobar también la vuelta con mando.

## Límites de validación

Una comprobación XML o un workflow verde **no demuestra** que los botones funcionen en Kodi ni que PlexKodiConnect permita todas las acciones. Mantener `runtime_tested: false` hasta una prueba real. No subir credenciales Plex, URL privada IPTV ni bases de datos del usuario.

## Referencia visual

La captura conceptual acordada en el chat del usuario se aportará a Work como referencia. No se presupone que la imagen sea una captura del skin en ejecución.
