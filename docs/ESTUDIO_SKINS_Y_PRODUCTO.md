# Estudio de skins y oportunidad de producto

Fecha: 20 de octubre de 2026. Proyecto: Plex Media Noche.

## Conclusión

Hay una hipótesis comercial razonable en una experiencia de salón fácil de configurar, mantener y usar en español. Todavía no hay pruebas de demanda de pago, ventas ni ventaja de rendimiento de nuestro proyecto. La versión actual es una personalización temprana de Arctic Zephyr Reloaded; no es un motor propio ni un producto comercial terminado.

El impedimento inmediato para vender este derivado es su licencia: la revisión exacta de Arctic usada por el proyecto declara CC BY-NC-SA 3.0. No debe presupuestarse su venta sin autorización comercial de los titulares pertinentes o sustitución del material por una base con permisos compatibles y recursos propios. Cambiar colores, nombre o muchos XML no elimina la licencia del material reutilizado. Fuente: [LICENSE.txt de la revisión utilizada](https://github.com/beatmasterRS/skin.arctic.zephyr.mod/blob/27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51/LICENSE.txt) y [condiciones CC](https://creativecommons.org/licenses/by-nc-sa/3.0/).

## Alcance de la investigación

Se revisó el catálogo público Omega, fuentes de autores, licencias y complementos de metadatos. No se instalaron ni midieron skins en esta investigación. La ficha web oficial consultada enumera 13 skins: Aeon Nox SiLVO, Aeon Tajo, Amber, Arctic Zephyr Reloaded, Bello 10, Confluence, Copacetic, fTV, Metropolis, Mimic-LR, Quartz, Transparency y Xperience1080. Ese catálogo no representa todos los forks, repositorios externos, versiones históricas ni instalaciones activas. Fuente: [catálogo Omega](https://kodi.tv/addons/omega/category/skins/).

También se incluyeron Estuary y las familias externas Arctic Fuse, Arctic Horizon, Nimbus, FENtastic y Bingie. No se presentan cuotas de mercado, usuarios únicos ni ingresos: estrellas y descargas no permiten inferirlos.

## Comparación útil para nuestro objetivo

La comparación describe orientación y capacidades documentadas, no un ranking de velocidad ni una clasificación exhaustiva de calidad visual.

| Referencia | Qué aporta | Qué exige a nuestro proyecto |
| --- | --- | --- |
| Estuary | Skin incluido en Kodi, interfaz de referencia y menor necesidad de instalar una capa de personalización | Ser más fácil o atractivo sin empeorar navegación; usarlo como control en pruebas |
| Quartz | El autor lo presenta como ligero, con portada configurable | Incluirlo en las mediciones; no proclamar que somos los más ligeros |
| Amber | Orientación a navegación sencilla de la biblioteca | Competir en claridad y facilidad de uso, no solo en colores |
| Arctic Zephyr Reloaded | Base de nuestro proyecto; opciones de vistas, widgets e información ampliada | Reconocer lo heredado; nuestra ventaja sobre la misma base aún es una configuración, no una función exclusiva |
| Aeon Nox SiLVO | Diseño Aeon modernizado y widgets; competidor de personalización | Reducir el tiempo de configuración y comprobar el coste de las opciones activas |
| FENtastic | Widgets configurables, búsqueda e información con valoraciones; diseñado para FEN | Las notas no son una novedad competitiva; su orientación no coincide exactamente con PKC y biblioteca nativa |
| Nimbus | Skin para Omega distribuido por repositorio propio | Referencia adicional para evaluar la presentación y el uso real, sin atribuirle velocidad no medida |
| Arctic Horizon 2 / Fuse 2 | Referencias de la familia Arctic; sus repositorios upstream aparecen archivados | Revisar mantenimiento y dependencia de versiones, no elegir una base solo por una captura |
| Arctic Fuse 3 | Iteración actual de esa familia con rama Omega; licencia NC-SA 4.0 | Referencia de evolución; cambiar a ella no resuelve automáticamente el permiso comercial |
| Bingie | Layout inspirado en Netflix según su autor | Un aspecto de catálogo cinematográfico ya tiene competencia; revisar código, recursos y mantenimiento antes de elegirlo como base |

Fuentes: [Estuary](https://kodi.wiki/view/Add-on:Estuary), [Quartz](https://kodi.tv/addons/omega/skin.quartz/), [Amber](https://kodi.tv/addons/omega/skin.amber/), [SiLVO](https://kodi.tv/addons/omega/skin.aeon.nox.silvo/), [FENtastic](https://github.com/ivarbrandt/skin.fentastic), [Nimbus](https://github.com/ivarbrandt/skin.nimbus), [Horizon 2](https://github.com/jurialmunkey/skin.arctic.horizon.2), [Fuse 2](https://github.com/jurialmunkey/skin.arctic.fuse.2), [Fuse 3](https://github.com/jurialmunkey/skin.arctic.fuse.3), [Bingie](https://github.com/matke-84/skin.bingie).

## Dónde estamos realmente

- Diseño: existe una paleta propia y un menú de ocho accesos. La imagen generada en la conversación es una propuesta conceptual, no una captura del skin funcionando.
- Prestaciones: se heredan las de Arctic y de sus complementos. La integración de PKC y TV está planificada; no se ha probado con la biblioteca ni los canales del usuario.
- Ligereza: el primer arranque reduce el límite de widgets a 12 elementos y desactiva reflejos. Son decisiones para reducir trabajo, no evidencia de una mejora medible de CPU, memoria o latencia. El cambio de paleta no reduce por sí mismo el consumo. El número de filas y las consultas externas también importan.
- Madurez: las comprobaciones y el empaquetado pasan. No existen todavía pruebas de instalación, uso con mando, estabilidad prolongada ni migración de ajustes Windows/Android.
- Diferenciación comercial: todavía baja. Añadir metadatos disponibles en otros skins no basta para justificar el pago. Una instalación sencilla, soporte y estabilidad comprobada podrían aportar valor si las licencias lo permiten.

## Valoraciones, reseñas y tráileres

La base seleccionada ya declara `script.embuary.info` y `plugin.video.themoviedb.helper` como dependencias. Su changelog menciona valoraciones IMDb y mejoras de tráileres; incluye ventanas de integración con Embuary. No hay que acumular varios complementos que hagan la misma consulta. Fuente: [addon.xml de la revisión fijada](https://github.com/beatmasterRS/skin.arctic.zephyr.mod/blob/27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51/addon.xml).

Propuesta de experiencia, todavía pendiente de implementación y pruebas:

1. **Ficha rápida:** nota identificada por fuente, número de votos cuando esté disponible, año, duración, género y sinopsis breve. Distinguir valoración global y valoración personal; mostrar «sin valoración» cuando falte, nunca inventar un cero.
2. **Descubrimiento:** filtro «8 o más» indicando fuente y un mínimo configurable de votos. Separar películas y series, y no equiparar automáticamente nota de serie, temporada y episodio. Limitar los resultados a contenido autorizado y disponible en la biblioteca o marcar de forma clara los títulos que solo sean descubrimiento.
3. **Ficha ampliada a demanda:** reparto, títulos relacionados y reseñas, con autor, fuente, idioma y enlace cuando proceda. Una sinopsis no es una reseña, y una puntuación no implica que podamos obtener el texto de las críticas de ese mismo proveedor.
4. **Tráiler mediante botón:** priorizar idioma español cuando exista y evitar reproducción automática inicialmente. Comprobar el complemento reproductor, disponibilidad del vídeo y limitaciones de la fuente en cada plataforma.
5. **Protección frente a spoilers:** sinopsis breve en portada; descripciones de episodios no vistos y reseñas ocultables. No se puede garantizar que toda reseña o tráiler externo esté libre de spoilers. Si el usuario quería decir «sinopsis», confirmarlo antes de diseñar una función de spoilers específica.

Embuary Info consulta TMDb para personas y vídeos y requiere integración del skin. Su documentación indica clave OMDb propia para datos IMDb/Rotten Tomatoes y advierte que puede recurrir al inglés si faltan datos. Esto debe comprobarse con las versiones efectivamente instaladas. Fuente: [documentación del autor](https://github.com/sualfred/script.embuary.info).

TMDb dispone de un endpoint de reseñas de usuarios de películas; eso acredita la existencia de datos, no que nuestro skin o complemento ya los muestre, ni su cobertura en español. Fuente: [Movie Reviews](https://developer.themoviedb.org/reference/movie-reviews). OMDb documenta consultas por IMDb ID y contenido bajo CC BY-NC 4.0; obtener una clave no resuelve automáticamente el uso comercial. Fuente: [OMDb](https://www.omdbapi.com/).

Arquitectura recomendada: leer primero metadatos sincronizados por PKC; identificar correctamente títulos por IDs; enriquecer al abrir una ficha mediante un proveedor principal; cachear conforme a sus condiciones; poner límites y tiempos de espera; conservar la navegación y reproducción si el proveedor falla. No ejecutar un scraper paralelo que reescriba la biblioteca gestionada por PKC. «Mejores valoradas» requiere un criterio verificable y datos suficientes; no debe depender solo de ordenar resultados parciales de una consulta remota.

## Cómo demostrar rendimiento

Primera selección para pruebas: Estuary, Quartz, Arctic original, Media Noche y una referencia de presentación avanzada compatible con el equipo. Versiones y configuración fijadas. Windows sirve para funcionalidad; el rendimiento objetivo se mide también en un Android de prestaciones modestas y otro más capaz.

Mantener iguales biblioteca, cantidad de elementos, red, imágenes, resolución y complementos activos. Registrar también configuración por defecto, porque permite comparar el tiempo hasta una experiencia útil. Separar cuatro fases: sincronización inicial PKC, arranque en frío, arranque con caché y navegación una vez cargada la portada.

Medir: tiempo hasta poder usar el menú; tiempo hasta cargar carátulas; latencia de navegación y apertura de ficha; memoria y CPU en reposo y al desplazarse; consultas externas; errores; comportamiento sin red. Hacer al menos cinco repeticiones de las operaciones cronometradas y conservar resultados individuales, mediana y rango. Comprobar reproducción, audio, subtítulos y EPG como pruebas funcionales separadas: el skin no controla por sí solo el servidor, el stream ni el decodificador.

No utilizar tamaño del ZIP ni una captura generada como prueba de velocidad o diseño implementado. No asignar notas numéricas globales ni afirmar superioridad antes de contar con mediciones comparables.

## Venta: condiciones y validación de demanda

Hipótesis a contrastar, no mercado demostrado:

- El usuario avanzado dispone de muchas alternativas gratuitas y puede preferir configurar por su cuenta.
- Una familia que quiere una interfaz lista para usar podría valorar instalación y soporte más que un ZIP decorativo.
- Un integrador podría valorar perfiles repetibles, recuperación y documentación, si el mantenimiento por cliente es asumible.

La investigación no ha obtenido ventas verificadas de skins comparables, conversión, volumen de compradores ni precios de mercado representativos. No se deduce demanda de pago de la actividad de un foro, las donaciones o los contadores de descarga. Antes de decidir un precio: entrevistas, demostración funcional, piloto con usuarios ajenos al proyecto y una oferta concreta con permisos resueltos. Registrar tiempo de instalación, incidencias, coste de soporte y aceptación real de pago. No confundir interés verbal con una compra.

Tres caminos posibles:

1. Prototipo personal/no comercial sobre Arctic, para aprender y probar.
2. Acuerdo comercial con titulares que puedan conceder los permisos necesarios, incluyendo recursos y dependencias pertinentes.
3. Producto propio sobre componentes con licencias compatibles con el modelo elegido, con auditoría de imágenes, fuentes, código y atribuciones. «Desde cero» no elimina las condiciones de las APIs usadas.

Vender soporte no es una forma automática de sortear una licencia NC. Las políticas de Kodi distinguen software, marcas y servicios de soporte; hay que revisar el uso concreto. Fuente: [política de marcas de Kodi](https://kodi.wiki/view/Official:Trademark_Policy). Para una marca comercial propia conviene revisar también el nombre provisional «Plex Media Noche», que incorpora una marca ajena. Fuente: [directrices de Plex](https://www.plex.tv/es/about/privacy-legal/plex-trademarks-and-guidelines/).

TMDb distingue proyectos comerciales y de desarrollo y ofrece acuerdos comerciales; no presupuestar que una clave gratuita o incluida por un complemento cubra un producto de pago. Fuente: [FAQ de TMDb](https://developer.themoviedb.org/docs/faq). No se han solicitado permisos ni contactado con autores.

La propuesta vendible debe ser la experiencia y el soporte que legítimamente podamos ofrecer. Una invitación a una biblioteca Plex o una lista IPTV personal no concede derechos para revender su contenido a clientes.

## Orden recomendado

1. Probar el prototipo actual en Windows y un Android, sin rehacer el motor Kodi.
2. Resolver el modelo comercial y las licencias antes de invertir en una reescritura grande para vender.
3. Validar una ficha útil con notas, votos, fuente y tráiler; después reseñas opcionales.
4. Medir y corregir rendimiento; separar un perfil ligero de opciones visuales adicionales si las pruebas lo justifican.
5. Completar onboarding, restauración de ajustes, actualizaciones y diagnóstico sin credenciales.
6. Probar una oferta real con un pequeño grupo antes de decidir si ampliar a otros proyectos.

Recomendación actual: continuar el prototipo personal como banco de pruebas y estudiar una marca y base técnica comercialmente viables en paralelo. No prometer ventas, mejor rendimiento ni exclusividad de funciones con la evidencia disponible.
