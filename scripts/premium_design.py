"""Diseño «Premium minimalista» aprobado el 22 nov 2026.

Rehace las pantallas propias del skin (Inicio, Series estrenos, Series, Cine,
Novedades cine y Diseño) y añade Ficha de película (1196) y Serie (1197).
Todas comparten la barra de menú inferior de cristal (id 9100).
Se ejecuta después de cinematic_design.build_design y sobrescribe sus ventanas.
"""
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from cinematic_design import LIBRARIES, PLAYLISTS, hidden_episode_plot

GOLD = 'FFE5BC70'
DARK = 'FF08121F'
WHITE = 'FFFFFFFF'
MUTED = 'E6DDE6EF'
FAINT = 'A6DDE6EF'
MEDIA = 'special://skin/extras/medianoche/'
ICONS = 'special://skin/extras/icons/'
INFO_SCRIPT = 'special://skin/extras/medianoche_info.py'
FICHA_SCRIPT = 'special://skin/extras/medianoche_ficha.py'
TRAILER_SCRIPT = 'special://skin/extras/medianoche_trailer.py'
FAV_SCRIPT = 'special://skin/extras/medianoche_misfavoritos.py'
DOWNLOAD_SCRIPT = 'special://skin/extras/medianoche_descargar.py'
EXPLORE_SCRIPT = 'special://skin/extras/medianoche_explore.py'
P = 'Window(home).Property'

FONTS = [  # nombre, archivo, tamaño
    ('MN_Hero', 'MN-BebasNeue.ttf', 120),
    ('MN_HeroM', 'MN-BebasNeue.ttf', 100),
    ('MN_Num', 'MN-BebasNeue.ttf', 30),
    ('MN_Brand', 'MN-Cinzel-SemiBold.ttf', 24),
    ('MN_Rating', 'MN-Outfit-SemiBold.ttf', 40),
    ('MN_Head', 'MN-Outfit-SemiBold.ttf', 26),
    ('MN_Button', 'MN-Outfit-SemiBold.ttf', 22),
    ('MN_Ep', 'MN-Outfit-Medium.ttf', 25),
    ('MN_Tab', 'MN-Inter-Medium.ttf', 23),
    ('MN_Body', 'MN-Inter-Medium.ttf', 23),
    ('MN_Meta', 'MN-Inter-Medium.ttf', 22),
    ('MN_Small', 'MN-Inter-Medium.ttf', 20),
    ('MN_Kicker', 'MN-Inter-Medium.ttf', 19),
    ('MN_Tiny', 'MN-Inter-Medium.ttf', 17),
    ('MN_Dock', 'MN-Inter-Medium.ttf', 19),
    ('MN_Card', 'MN-Outfit-SemiBold.ttf', 21),
]

DOCK = [  # etiqueta, icono, acción, ventana de la sección
    ('Inicio', 'home.png', 'ReplaceWindow(1191)', '1191'),
    ('Mi lista', 'favourites.png', 'ReplaceWindow(1190)', '1190'),
    ('Series', 'tv.png', 'ReplaceWindow(1192)', '1192'),
    ('Cine', 'film.png', 'ReplaceWindow(1193)', '1193'),
    ('Estrenos', 'recent.png', 'ReplaceWindow(1194)', '1194'),
    ('TV', 'livetv.png', 'ActivateWindow(TVChannels)', ''),
    ('Ajustes', 'settings.png', 'ReplaceWindow(1195)', '1195'),
    ('Apagar', 'power.png', 'ActivateWindow(shutdownmenu)', ''),
]

LIB_DOWN = [('50', 'Integer.IsGreater(Container(50).NumItems,0)'),
            ('9100', '!Integer.IsGreater(Container(50).NumItems,0)')]

_C = 'Integer.IsGreater(Container(520).NumItems,0)'
_R = 'Integer.IsGreater(Container(521).NumItems,0)'
CONT_DOWN = [('520', _C), ('521', f'!{_C} + {_R}'), ('9100', f'!{_C} + !{_R}')]

FAVS = 'special://profile/addon_data/skin.plexmedianoche/'
LISTAS = 'plugin://plugin.video.medianoche/'
GRIDS = {  # ventana: (título, tipo, [(pestaña, contenido)])
    1190: ('Mi lista', 'movie', [
        ('Todo', 'plugin://plugin.video.medianoche/?lista=milista'),
        ('Películas', FAVS + 'favoritos-movie.xsp'),
        ('Series', FAVS + 'favoritos-tvshow.xsp'),
    ]),
    1192: ('Series', 'tvshow', [
        ('Novedades', PLAYLISTS + 'series.xsp'),
        ('Temporadas nuevas', PLAYLISTS + 'series-temporadas-nuevas.xsp'),
        ('Continuar', PLAYLISTS + 'episodios-continuar.xsp'),
        ('Géneros', 'videodb://tvshows/genres/'),
        ('Mi lista', FAVS + 'favoritos-tvshow.xsp'),
    ]),
    1193: ('Cine', 'movie', [
        ('Novedades', PLAYLISTS + 'cine-reciente.xsp'),
        ('Recomendadas', PLAYLISTS + 'cine-recomendadas.xsp'),
        ('Continuar', PLAYLISTS + 'cine-continuar.xsp'),
        ('Géneros', 'videodb://movies/genres/'),
        ('Mi lista', FAVS + 'favoritos-movie.xsp'),
    ]),
    1194: ('Estrenos', 'movie', [
        ('Estrenos', PLAYLISTS + 'cine-estrenos.xsp'),
        ('Últimas añadidas', PLAYLISTS + 'cine-reciente.xsp'),
        ('Sin ver', PLAYLISTS + 'cine-sin-ver.xsp'),
    ]),
}

HOME_ROWS = [  # id, fila, contenido, forma  (solo novedades: carga rápida)
    (520, 'Continuar viendo', LISTAS + '?lista=continuar', 'wide'),
    (504, 'Novedades series', PLAYLISTS + 'series.xsp', 'poster'),
    (503, 'Temporadas nuevas', PLAYLISTS + 'series-temporadas-nuevas.xsp', 'poster'),
    (501, 'Novedades cine', PLAYLISTS + 'cine-reciente.xsp', 'poster'),
    (502, 'Estrenos', PLAYLISTS + 'cine-estrenos.xsp', 'poster'),
]

# Cada sección: filas de arriba abajo que se deslizan a izquierda y derecha.
SECTION_ROWS = {
    1192: ('Series', [
        (620, 'Continuar viendo', PLAYLISTS + 'episodios-continuar.xsp', 'wide'),
        (621, 'Novedades', PLAYLISTS + 'series.xsp', 'poster'),
        (622, 'Temporadas nuevas', PLAYLISTS + 'series-temporadas-nuevas.xsp', 'poster'),
        (623, 'Mi lista', FAVS + 'favoritos-tvshow.xsp', 'poster'),
    ]),
    1193: ('Cine', [
        (630, 'Continuar viendo', PLAYLISTS + 'cine-continuar.xsp', 'wide'),
        (631, 'Novedades', PLAYLISTS + 'cine-reciente.xsp', 'poster'),
        (632, 'Recomendadas', PLAYLISTS + 'cine-recomendadas.xsp', 'poster'),
        (633, 'Estrenos', PLAYLISTS + 'cine-estrenos.xsp', 'poster'),
        (634, 'Mi lista', FAVS + 'favoritos-movie.xsp', 'poster'),
    ]),
    1194: ('Estrenos', [
        (640, 'Estrenos', PLAYLISTS + 'cine-estrenos.xsp', 'poster'),
        (641, 'Últimas añadidas', PLAYLISTS + 'cine-reciente.xsp', 'poster'),
        (642, 'Sin ver', PLAYLISTS + 'cine-sin-ver.xsp', 'poster'),
    ]),
    1190: ('Mi lista', [
        (650, 'Todo', LISTAS + '?lista=milista', 'poster'),
        (651, 'Películas', FAVS + 'favoritos-movie.xsp', 'poster'),
        (652, 'Series', FAVS + 'favoritos-tvshow.xsp', 'poster'),
    ]),
}
ALL_ROWS = HOME_ROWS + [r for _, rows in SECTION_ROWS.values() for r in rows]


# ---------------------------------------------------------------- utilidades
def add(parent, tag, text=None, **attrs):
    node = ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items() if v is not None})
    if text is not None:
        node.text = str(text)
    return node


def ctrl(parent, kind, x, y, w, h, identity=None):
    node = add(parent, 'control', type=kind, **({'id': identity} if identity else {}))
    for tag, value in (('left', x), ('top', y), ('width', w), ('height', h)):
        add(node, tag, value)
    return node


def img(parent, x, y, w, h, texture, color=None, border=None, diffuse=None,
        aspect=None, background=False, fade=None, visible=None):
    node = ctrl(parent, 'image', x, y, w, h)
    attrs = {}
    if color:
        attrs['colordiffuse'] = color
    if border:
        attrs['border'] = border
    if diffuse:
        attrs['diffuse'] = diffuse
    if background:
        attrs['background'] = 'true'
    add(node, 'texture', texture, **attrs)
    if aspect:
        add(node, 'aspectratio', aspect)
    if fade:
        add(node, 'fadetime', fade)
    if visible:
        add(node, 'visible', visible)
    return node


def lbl(parent, x, y, w, h, text, font='MN_Body', color=WHITE, align=None,
        aligny='center', visible=None, wrap=False, scroll=False):
    node = ctrl(parent, 'label', x, y, w, h)
    add(node, 'font', font)
    add(node, 'textcolor', color)
    if align:
        add(node, 'align', align)
    add(node, 'aligny', aligny)
    add(node, 'label', text)
    if wrap:
        add(node, 'wrapmultiline', 'true')
    if scroll:
        add(node, 'scroll', 'true')
    if visible:
        add(node, 'visible', visible)
    return node


def textbox(parent, x, y, w, h, text, font='MN_Body', color='E6DDE6EF', visible=None):
    node = ctrl(parent, 'textbox', x, y, w, h)
    add(node, 'font', font)
    add(node, 'textcolor', color)
    add(node, 'label', text)
    if visible:
        add(node, 'visible', visible)
    return node


def nav(node, **moves):
    for tag, value in moves.items():
        for item in (value if isinstance(value, list) else [value]):
            if isinstance(item, tuple):
                add(node, 'on' + tag, item[0], condition=item[1])
            else:
                add(node, 'on' + tag, item)


def zoom(node, end=106, centre=None):
    attrs = {'effect': 'zoom', 'start': '100', 'end': str(end), 'time': '160',
             'tween': 'cubic', 'easing': 'out'}
    if centre:
        attrs['center'] = centre
    add(node, 'animation', 'Focus', **attrs)
    add(node, 'animation', 'Unfocus', **{**attrs, 'start': str(end), 'end': '100'})


# ------------------------------------------------------------- recursos
def make_textures(target):
    from PIL import Image, ImageDraw, ImageFilter
    target.mkdir(parents=True, exist_ok=True)
    s = 4  # sobremuestreo para bordes suaves

    def save(image, name, size):
        image.resize(size, Image.LANCZOS).save(target / name)

    def rounded(w, h, r, outline=0):
        im = Image.new('RGBA', (w * s, h * s), (255, 255, 255, 0))
        d = ImageDraw.Draw(im)
        if outline:
            d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, outline=(255, 255, 255, 255),
                                width=outline * s)
        else:
            d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=(255, 255, 255, 255))
        return im

    save(rounded(128, 128, 32), 'pill.png', (128, 128))
    save(rounded(64, 64, 14), 'round14.png', (64, 64))
    check = Image.new('RGBA', (64 * s, 64 * s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(check)
    draw.ellipse((0, 0, 64 * s - 1, 64 * s - 1), fill=(229, 188, 112, 255))
    draw.line([(18 * s, 33 * s), (28 * s, 43 * s), (46 * s, 23 * s)], fill=(8, 18, 31, 255), width=6 * s)
    save(check, 'check.png', (64, 64))
    save(rounded(64, 64, 10, outline=2), 'outline10.png', (64, 64))
    save(rounded(340, 510, 24), 'mask_poster.png', (340, 510))
    save(rounded(512, 288, 22), 'mask_wide.png', (512, 288))
    circle = Image.new('RGBA', (128 * s, 128 * s), (255, 255, 255, 0))
    ImageDraw.Draw(circle).ellipse((0, 0, 128 * s - 1, 128 * s - 1), fill=(255, 255, 255, 255))
    save(circle, 'circle.png', (128, 128))
    ring = Image.new('RGBA', (128 * s, 128 * s), (255, 255, 255, 0))
    ImageDraw.Draw(ring).ellipse((2 * s, 2 * s, 126 * s, 126 * s), outline=(255, 255, 255, 255), width=3 * s)
    save(ring, 'ring.png', (128, 128))
    glow = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
    ImageDraw.Draw(glow).rounded_rectangle((40, 40, 160, 160), 20, fill=(255, 255, 255, 200))
    glow.filter(ImageFilter.GaussianBlur(16)).save(target / 'glow.png')
    night = (4, 7, 12)
    left = Image.new('RGBA', (256, 4))
    for x in range(256):
        a = int(250 * max(0.0, 1 - (x / 255) ** 1.6))
        for y in range(4):
            left.putpixel((x, y), night + (a,))
    left.save(target / 'grad_left.png')
    bottom = Image.new('RGBA', (4, 256))
    for y in range(256):
        a = int(255 * min(1.0, (y / 255) ** 1.3 * 1.15))
        for x in range(4):
            bottom.putpixel((x, y), night + (a,))
    bottom.save(target / 'grad_bottom.png')
    top = bottom.transpose(Image.FLIP_TOP_BOTTOM)
    top.save(target / 'grad_top.png')


def install_fonts(base, project):
    fonts_dir = project / 'skin/fonts'
    for path in sorted(fonts_dir.glob('*')):
        shutil.copyfile(path, base / 'fonts' / path.name)
    font_xml = base / '1080i/Font.xml'
    tree = ET.parse(font_xml)
    # ZIP ligero: fuera el juego de letras chino-coreano (51 MB) que no se usa;
    # en algunos Android TV un ZIP tan pesado cierra Kodi al instalarlo.
    for fontset in list(tree.getroot().findall('fontset')):
        if fontset.get('id', '').startswith('CJK'):
            tree.getroot().remove(fontset)
    used = {n.text for n in tree.getroot().iter('filename')}
    for path in (base / 'fonts').glob('InterCJK*'):
        if path.name not in used:
            path.unlink()
    for fontset in tree.getroot().findall('fontset'):
        for name, filename, size in FONTS:
            font = add(fontset, 'font')
            add(font, 'name', name)
            add(font, 'filename', filename)
            add(font, 'size', size)
    ET.indent(tree.getroot(), space='    ')
    tree.write(font_xml, encoding='UTF-8', xml_declaration=True)


# -------------------------------------------------------- piezas comunes
def background(controls, art):
    img(controls, 0, 0, 1920, 1080, 'common/white.png', 'FF04070C')
    img(controls, 0, 0, 1920, 1080, art, aspect='scale', background=True, fade='400')
    img(controls, 0, 0, 1500, 1080, MEDIA + 'grad_left.png')
    img(controls, 0, 440, 1920, 640, MEDIA + 'grad_bottom.png')
    img(controls, 0, 0, 1920, 160, MEDIA + 'grad_top.png', 'B3FFFFFF')


def header(controls):
    lbl(controls, 80, 36, 600, 40, 'MEDIA NOCHE', 'MN_Brand', 'E6FFFFFF')
    lbl(controls, 1240, 36, 600, 40,
        '$INFO[System.Time]  ·  $INFO[System.Date(ddd d mmm)]', 'MN_Meta', MUTED, 'right')


def dock(controls, page, up):
    """Barra inferior de cristal: icono + nombre; la sección elegida, en dorado."""
    img(controls, 80, 994, 1760, 74, MEDIA + 'pill.png', '24FFFFFF', border='32')
    img(controls, 112, 994, 1696, 1, 'common/white.png', '4DFFFFFF')
    listing = ctrl(controls, 'list', 85, 994, 1750, 74, 9100)
    add(listing, 'orientation', 'horizontal')
    add(listing, 'scrolltime', '0')
    add(listing, 'onup', up)
    if page != '1191':
        add(listing, 'onback', 'ReplaceWindow(1191)')
    for tag in ('itemlayout', 'focusedlayout'):
        layout = add(listing, tag, width='218', height='74')
        focused = tag == 'focusedlayout'
        if focused:
            on = 'Control.HasFocus(9100)'
            img(layout, 2, 0, 214, 74, MEDIA + 'glow.png', '73E5BC70', border='60', visible=on)
            img(layout, 6, 8, 206, 58, MEDIA + 'pill.png', GOLD, border='32', visible=on)
            icon = img(layout, 18, 22, 30, 30, '$INFO[ListItem.Icon]', DARK, aspect='keep', visible=on)
            lbl(layout, 56, 8, 150, 58, '$INFO[ListItem.Label]', 'MN_Dock', DARK, visible=on, scroll=True)
            off = '!Control.HasFocus(9100)'
            img(layout, 18, 22, 30, 30, '$INFO[ListItem.Icon]', MUTED, aspect='keep', visible=off)
            lbl(layout, 56, 8, 150, 58, '$INFO[ListItem.Label]', 'MN_Dock', MUTED, visible=off)
        else:
            img(layout, 18, 22, 30, 30, '$INFO[ListItem.Icon]', MUTED, aspect='keep')
            lbl(layout, 56, 8, 150, 58, '$INFO[ListItem.Label]', 'MN_Dock', MUTED)
        # Sección actual: punto dorado bajo el icono.
        img(layout, 26, 58, 10, 10, MEDIA + 'circle.png', GOLD,
            visible='String.IsEqual(ListItem.Property(current),1)'
                    + (' + !Control.HasFocus(9100)' if focused else ''))
    content = add(listing, 'content')
    for label, icon, action, window in DOCK:
        item = add(content, 'item')
        add(item, 'label', label)
        add(item, 'icon', ICONS + icon)
        add(item, 'onclick', action)
        add(item, 'property', '1' if window == page else '0', name='current')
    return listing


def pill_button(controls, identity, x, y, w, text, icon, actions):
    node = ctrl(controls, 'button', x, y, w, 64, identity)
    add(node, 'texturefocus', MEDIA + 'pill.png', colordiffuse=GOLD, border='32')
    add(node, 'texturenofocus', MEDIA + 'pill.png', colordiffuse='E6E5BC70', border='32')
    add(node, 'font', 'MN_Button')
    add(node, 'textcolor', DARK)
    add(node, 'focusedcolor', DARK)
    add(node, 'textoffsetx', '40')
    add(node, 'align', 'center')
    add(node, 'aligny', 'center')
    add(node, 'label', text)
    for action in actions:
        if isinstance(action, tuple):
            add(node, 'onclick', action[0], condition=action[1])
        else:
            add(node, 'onclick', action)
    glow = img(controls, x - 18, y - 18, w + 36, 100, MEDIA + 'glow.png', '8CE5BC70', border='60',
               visible=f'Control.HasFocus({identity})')
    controls.remove(glow)
    controls.insert(list(controls).index(node), glow)
    img(controls, x + 22, y + 20, 24, 24, ICONS + 'play2.png', DARK, aspect='keep')
    return node


def text_button(controls, identity, x, y, text, icon, actions, width=None):
    """Botón con icono y texto: se lee bien desde el sofá."""
    width = width or (92 + len(text) * 12)
    node = ctrl(controls, 'button', x, y, width, 60, identity)
    add(node, 'texturefocus', MEDIA + 'pill.png', colordiffuse=GOLD, border='30')
    add(node, 'texturenofocus', MEDIA + 'pill.png', colordiffuse='33FFFFFF', border='30')
    add(node, 'font', 'MN_Button')
    add(node, 'textcolor', WHITE)
    add(node, 'focusedcolor', DARK)
    add(node, 'textoffsetx', '54')
    add(node, 'aligny', 'center')
    add(node, 'label', text)
    for action in actions:
        if isinstance(action, tuple):
            add(node, 'onclick', action[0], condition=action[1])
        else:
            add(node, 'onclick', action)
    img(controls, x + 20, y + 17, 26, 26, ICONS + icon, DARK, aspect='keep',
        visible=f'Control.HasFocus({identity})')
    img(controls, x + 20, y + 17, 26, 26, ICONS + icon, WHITE, aspect='keep',
        visible=f'!Control.HasFocus({identity})')
    return node


def round_button(controls, identity, x, y, icon, actions, visible=None):
    node = ctrl(controls, 'button', x, y, 64, 64, identity)
    add(node, 'texturefocus', MEDIA + 'circle.png', colordiffuse=GOLD)
    add(node, 'texturenofocus', MEDIA + 'ring.png', colordiffuse='73FFFFFF')
    add(node, 'label', '')
    for action in actions:
        if isinstance(action, tuple):
            add(node, 'onclick', action[0], condition=action[1])
        else:
            add(node, 'onclick', action)
    if visible:
        add(node, 'visible', visible)
    on = img(controls, x + 18, y + 18, 28, 28, ICONS + icon, DARK, aspect='keep',
             visible=f'Control.HasFocus({identity})')
    off = img(controls, x + 18, y + 18, 28, 28, ICONS + icon, WHITE, aspect='keep',
              visible=f'!Control.HasFocus({identity})')
    if visible:
        for image in (on, off):
            image.find('visible').text = f'[{image.find("visible").text}] + [{visible}]'
    return node


def tab(controls, identity, x, y, w, text, selected, actions=(), focus=()):
    """Pestaña de texto: el botón es invisible y el texto lo pintan etiquetas."""
    node = ctrl(controls, 'button', x, y, w, 50, identity)
    add(node, 'texturefocus', '')
    add(node, 'texturenofocus', '')
    add(node, 'font', 'MN_Tab')
    add(node, 'textcolor', '00FFFFFF')
    add(node, 'focusedcolor', '00FFFFFF')
    add(node, 'label', text)
    for action in actions:
        add(node, 'onclick', action)
    for action in focus:
        add(node, 'onfocus', action)
    active = f'[{selected} | Control.HasFocus({identity})]'
    lbl(controls, x, y, w, 50, text, 'MN_Tab', WHITE, visible=active)
    lbl(controls, x, y, w, 50, text, 'MN_Tab', FAINT, visible=f'!{active}')
    img(controls, x, y + 50, w - 20, 3, 'common/white.png', GOLD, visible=selected)
    img(controls, x, y + 50, w - 20, 3, 'common/white.png', '80FFFFFF',
        visible=f'Control.HasFocus({identity}) + !{selected}')
    return node


def poster_list(controls, identity, x, y, w, content, visible=None, small=False):
    """Fila de carátulas: la enfocada crece, con marco dorado y halo."""
    pw, ph = (140, 210) if small else (170, 255)
    step = pw + 30
    listing = ctrl(controls, 'list', x, y, w, ph + 70, identity)
    add(listing, 'orientation', 'horizontal')
    add(listing, 'scrolltime', '220', tween='cubic', easing='out')
    add(listing, 'preloaditems', '2')
    for tag in ('itemlayout', 'focusedlayout'):
        layout = add(listing, tag, width=str(step), height=str(ph + 70))
        top = 35
        centre = f'{15 + pw // 2},{top + ph // 2}'
        if tag == 'focusedlayout':
            on = f'Control.HasFocus({identity})'
            halo = img(layout, -15, top - 30, pw + 60, ph + 60, MEDIA + 'glow.png', '80E5BC70',
                       border='60', visible=on)
            zoom(halo, 108, centre)
            frame = img(layout, 9, top - 6, pw + 12, ph + 12, MEDIA + 'round14.png', GOLD,
                        border='14', visible=on)
            zoom(frame, 108, centre)
        art = img(layout, 15, top, pw, ph, '$VAR[MediaNoche.Poster]',
                  None if tag == 'focusedlayout' else '99FFFFFF',
                  diffuse=MEDIA + 'mask_poster.png', aspect='scale', background=True)
        art.find('texture').set('fallback', 'DefaultVideo.png')
        if tag == 'focusedlayout':
            zoom(art, 108, centre)
        watched = img(layout, pw - 18, top + 8, 28, 28, MEDIA + 'check.png',
                      visible='ListItem.IsWatched | String.IsEqual(ListItem.Overlay,OverlayWatched.png)')
        if tag == 'focusedlayout':
            zoom(watched, 108, centre)
        bar = ctrl(layout, 'progress', 27, top + ph - 16, pw - 24, 5)
        add(bar, 'texturebg', 'common/white.png', colordiffuse='59FFFFFF')
        add(bar, 'midtexture', 'common/white.png', colordiffuse=GOLD)
        add(bar, 'info', 'ListItem.PercentPlayed')
        add(bar, 'visible', 'ListItem.IsResumable')
    add(listing, 'content', content, target='videos', limit='20')
    if visible:
        add(listing, 'visible', visible)
    return listing


def item_click(listing, prefix='ListItem'):
    """Película → ficha; serie → pantalla de serie; episodio → reproducir."""
    for node in list(listing.findall('onclick')):
        listing.remove(node)
    add(listing, 'onclick', f'RunScript({FICHA_SCRIPT},movie,$INFO[{prefix}.DBID])',
        condition=f'String.IsEqual({prefix}.DBType,movie)')
    add(listing, 'onclick', f'RunScript({FICHA_SCRIPT},tvshow,$INFO[{prefix}.DBID])',
        condition=f'String.IsEqual({prefix}.DBType,tvshow)')
    add(listing, 'onclick', f'RunScript({FICHA_SCRIPT},play,$INFO[{prefix}.DBType],$INFO[{prefix}.DBID])',
        condition=f'String.IsEqual({prefix}.DBType,episode)')


def hero_texts(controls, prefix, y=170, kicker=None, plot=True, plot_hidden=None):
    """Título grande, datos y sinopsis del elemento enfocado."""
    if kicker:
        lbl(controls, 80, y, 1000, 30, kicker, 'MN_Kicker', GOLD)
    title = (f'$INFO[{prefix}.TVShowTitle]', f'String.IsEqual({prefix}.DBType,episode)')
    lbl(controls, 80, y + 30, 1150, 140, title[0], 'MN_Hero', WHITE, visible=title[1])
    lbl(controls, 80, y + 30, 1150, 140, f'$INFO[{prefix}.Label]', 'MN_Hero', WHITE,
        visible=f'!{title[1]}')
    meta = (f'$INFO[{prefix}.Year]$INFO[{prefix}.Genre,  ·  ]'
            f'$INFO[{prefix}.Duration(mins),  ·  , min]'
            f'$INFO[{prefix}.Rating,  ·  ★ ]')
    episode_meta = (f'T$INFO[{prefix}.Season]  ·  E$INFO[{prefix}.Episode]  ·  $INFO[{prefix}.Label]')
    lbl(controls, 80, y + 175, 1100, 34, meta, 'MN_Meta', MUTED, visible=f'!{title[1]}')
    lbl(controls, 80, y + 175, 1100, 34, episode_meta, 'MN_Meta', MUTED, visible=title[1])
    if plot:
        box = textbox(controls, 80, y + 220, 900, 66, f'$INFO[{prefix}.Plot]', 'MN_Body')
        if plot_hidden:
            add(box, 'visible', f'![{plot_hidden}]')
            lbl(controls, 80, y + 220, 900, 34, 'Sinopsis oculta para evitar spoilers.',
                'MN_Body', FAINT, visible=plot_hidden)


# ------------------------------------------------------------------ Inicio
def hero_badges(parent, prefix, x, y):
    """Etiquetas 4K/1080p, HDR y canales de audio del elemento enfocado."""
    group = ctrl(parent, 'grouplist', x, y, 900, 36)
    add(group, 'orientation', 'horizontal')
    add(group, 'itemgap', '8')
    entries = [
        ('4K', f'String.IsEqual({prefix}.VideoResolution,4K)'),
        (f'$INFO[{prefix}.VideoResolution]p', f'!String.IsEmpty({prefix}.VideoResolution) + !String.IsEqual({prefix}.VideoResolution,4K)'),
        ('DOLBY VISION', f'String.IsEqual({prefix}.HdrType,dolbyvision)'),
        ('HDR', f'!String.IsEmpty({prefix}.HdrType) + !String.IsEqual({prefix}.HdrType,dolbyvision)'),
        ('7.1', f'String.IsEqual({prefix}.AudioChannels,8)'),
        ('5.1', f'String.IsEqual({prefix}.AudioChannels,6)'),
        ('ESTÉREO', f'String.IsEqual({prefix}.AudioChannels,2)'),
        (f'$INFO[{prefix}.MPAA]', f'!String.IsEmpty({prefix}.MPAA)'),
    ]
    for text, visible in entries:
        node = add(group, 'control', type='button')
        add(node, 'width', 'auto')
        add(node, 'height', '34')
        add(node, 'texturenofocus', MEDIA + 'outline10.png', colordiffuse='B3FFFFFF', border='12')
        add(node, 'texturefocus', MEDIA + 'outline10.png', colordiffuse='B3FFFFFF', border='12')
        add(node, 'font', 'MN_Tiny')
        add(node, 'textcolor', WHITE)
        add(node, 'disabledcolor', WHITE)
        add(node, 'textoffsetx', '12')
        add(node, 'aligny', 'center')
        add(node, 'label', text)
        add(node, 'enable', 'false')
        add(node, 'visible', visible)


def wide_list(controls, identity, x, y, w, content, visible=None):
    """Fila «Seguir viendo»: imágenes horizontales con serie, episodio y progreso."""
    cw, ch = 224, 126
    listing = ctrl(controls, 'list', x, y, w, ch + 16, identity)
    add(listing, 'orientation', 'horizontal')
    add(listing, 'scrolltime', '220', tween='cubic', easing='out')
    add(listing, 'preloaditems', '2')
    for tag in ('itemlayout', 'focusedlayout'):
        layout = add(listing, tag, width=str(cw + 24), height=str(ch + 16))
        focused = tag == 'focusedlayout'
        if focused:
            img(layout, 6, 2, cw + 12, ch + 12, MEDIA + 'round14.png', GOLD, border='14',
                visible=f'Control.HasFocus({identity})')
        art = img(layout, 12, 8, cw, ch, '$INFO[ListItem.Art(thumb)]', None if focused else 'CCFFFFFF',
                  diffuse=MEDIA + 'mask_wide.png', aspect='scale', background=True)
        art.find('texture').set('fallback', 'DefaultTVShows.png')
        img(layout, 12, 8 + ch - 70, cw, 70, MEDIA + 'grad_bottom.png', diffuse=MEDIA + 'mask_wide.png')
        lbl(layout, 24, 8 + ch - 54, cw - 24, 26,
            '$INFO[ListItem.TVShowTitle]', 'MN_Card', WHITE,
            visible='!String.IsEmpty(ListItem.TVShowTitle)')
        lbl(layout, 24, 8 + ch - 54, cw - 24, 26, '$INFO[ListItem.Label]', 'MN_Card', WHITE,
            visible='String.IsEmpty(ListItem.TVShowTitle)')
        lbl(layout, 24, 8 + ch - 30, cw - 24, 22,
            'T$INFO[ListItem.Season] · E$INFO[ListItem.Episode]', 'MN_Tiny', MUTED,
            visible='!String.IsEmpty(ListItem.TVShowTitle)')
        bar = ctrl(layout, 'progress', 12, 8 + ch - 6, cw, 6)
        add(bar, 'texturebg', 'common/white.png', colordiffuse='40FFFFFF')
        add(bar, 'midtexture', 'common/white.png', colordiffuse=GOLD)
        add(bar, 'info', 'ListItem.PercentPlayed')
        add(bar, 'visible', 'ListItem.IsResumable')
    add(listing, 'content', content, target='videos', limit='20')
    if visible:
        add(listing, 'visible', visible)
    return listing


def build_home(window_id='1191', rows_cfg=None, section=None):
    """Inicio: destacado arriba y filas de arriba abajo; cada fila avanza a izquierda y derecha."""
    rows_cfg = rows_cfg or HOME_ROWS
    root = ET.Element('window', type='window', id=str(window_id))
    # Empieza en el menú de abajo: siempre se puede usar aunque las filas sigan cargando.
    add(root, 'defaultcontrol', '9100', always='true')
    add(root, 'onload', f'SetProperty(MediaNoche.Page,{window_id})')
    add(root, 'onload', 'SetFocus($INFO[Window.Property(MediaNoche.Row)])',
        condition='!String.IsEmpty(Window.Property(MediaNoche.Row))')
    controls = add(root, 'controls')
    background(controls, '$VAR[MediaNoche.HeroArt]')
    header(controls)
    row = 'Window.Property(MediaNoche.Row)'
    for identity, name, _, _ in rows_cfg:
        prefix = f'Container({identity}).ListItem'
        group = add(controls, 'control', type='group')
        add(group, 'visible', f'String.IsEqual({row},{identity}) + Integer.IsGreater(Container({identity}).NumItems,0)')
        lbl(group, 80, 96, 1000, 30, name.upper(), 'MN_Kicker', GOLD)
        episode = f'String.IsEqual({prefix}.DBType,episode)'
        no_logo = f'String.IsEmpty({prefix}.Art(clearlogo)) + String.IsEmpty({prefix}.Art(tvshow.clearlogo))'
        img(group, 80, 128, 640, 118, f'$VAR[MediaNoche.Logo{identity}]', aspect='keep', fade='300',
            visible=f'!String.IsEmpty({prefix}.Art(clearlogo)) | !String.IsEmpty({prefix}.Art(tvshow.clearlogo))')
        lbl(group, 80, 124, 1200, 124, f'$INFO[{prefix}.TVShowTitle]', 'MN_HeroM', WHITE,
            visible=f'{no_logo} + {episode}')
        lbl(group, 80, 124, 1200, 124, f'$INFO[{prefix}.Label]', 'MN_HeroM', WHITE,
            visible=f'{no_logo} + !{episode}')
        meta = (f'$INFO[{prefix}.Year]$INFO[{prefix}.Genre,  ·  ]'
                f'$INFO[{prefix}.Duration(mins),  ·  , min]$INFO[{prefix}.Rating,  ·  ★ ]')
        lbl(group, 80, 256, 1200, 32, meta, 'MN_Meta', MUTED, visible=f'!{episode}')
        lbl(group, 80, 256, 1200, 32,
            f'T$INFO[{prefix}.Season]  ·  E$INFO[{prefix}.Episode]  ·  $INFO[{prefix}.Label]',
            'MN_Meta', MUTED, visible=episode)
        hero_badges(group, prefix, 80, 296)
        box = textbox(group, 80, 340, 1000, 58, f'$INFO[{prefix}.Plot]', 'MN_Small')
        add(box, 'visible', f'![{hidden_episode_plot(identity)}]')
    welcome = add(controls, 'control', type='group')
    add(welcome, 'visible', 'String.IsEmpty(Window.Property(MediaNoche.Row))')
    lbl(welcome, 80, 124, 1200, 124, (section or 'Buenas historias, siempre').upper(), 'MN_HeroM', WHITE)
    lbl(welcome, 80, 256, 1300, 32, 'Sube con el mando para recorrer las filas.', 'MN_Meta', MUTED)
    # Filas en una columna que se desplaza sola al bajar.
    rows = ctrl(controls, 'grouplist', 0, 420, 1920, 556, 400)
    add(rows, 'orientation', 'vertical')
    add(rows, 'itemgap', '6')
    add(rows, 'scrolltime', '260', tween='cubic', easing='out')
    add(rows, 'ondown', '9100')
    for identity, name, source, kind in rows_cfg:
        wide = kind == 'wide'
        height = 186 if wide else 316
        block = add(rows, 'control', type='group')
        add(block, 'width', '1920')
        add(block, 'height', str(height))
        lbl(block, 80, 0, 900, 34, name, 'MN_Head', WHITE)
        count = lbl(block, 1240, 0, 600, 34, f'$INFO[Container({identity}).NumItems,, títulos]', 'MN_Small', FAINT, 'right')
        add(count, 'visible', f'Integer.IsGreater(Container({identity}).NumItems,0)')
        if wide:
            listing = wide_list(block, identity, 68, 38, 1784, source)
        else:
            listing = poster_list(block, identity, 70, 30, 1780, source, small=True)
        add(listing, 'onfocus', f'SetProperty(MediaNoche.Row,{identity})')
        ids = [r[0] for r in rows_cfg]
        here = ids.index(identity)
        for tag, others, fallback in (('ondown', ids[here + 1:], '9100'), ('onup', ids[:here][::-1], None)):
            skipped = []
            for other in others:
                cond = ' + '.join([f'Integer.IsGreater(Container({other}).NumItems,0)'] +
                                  [f'!Integer.IsGreater(Container({o}).NumItems,0)' for o in skipped])
                add(listing, tag, str(other), condition=cond)
                skipped.append(other)
            if fallback:
                add(listing, tag, fallback, condition=' + '.join(
                    f'!Integer.IsGreater(Container({o}).NumItems,0)' for o in skipped) or None)
        if wide:
            for node in list(listing.findall('onclick')):
                listing.remove(node)
            add(listing, 'onclick', f'RunScript({FICHA_SCRIPT},play,$INFO[ListItem.DBType],$INFO[ListItem.DBID])')
        else:
            item_click(listing)
        message = {'milista': 'Pulsa «Mi lista» en una ficha para guardarla aquí.',
                   'continuar': 'Aquí aparecerá lo que dejes a medias.'}.get(
            'milista' if 'milista' in source else 'continuar' if 'continuar' in source else '',
            'Todavía no hay títulos en esta fila.')
        empty = lbl(block, 90, 60, 1400, 50, message, 'MN_Small', FAINT)
        add(empty, 'visible', f'!Container({identity}).IsUpdating + Integer.IsEqual(Container({identity}).NumItems,0)')
        if source.startswith('plugin://'):
            hint = lbl(block, 90, 100, 1400, 40, 'Necesita el complemento «Media Noche · Listas».', 'MN_Tiny', FAINT)
            add(hint, 'visible', '!System.HasAddon(plugin.video.medianoche)')
    listing = dock(controls, str(window_id), 400)
    for node in list(listing.findall('onup')):
        listing.remove(node)
    add(listing, 'onup', 'SetFocus($INFO[Window.Property(MediaNoche.Row)])',
        condition='!String.IsEmpty(Window.Property(MediaNoche.Row))')
    add(listing, 'onup', '400', condition='String.IsEmpty(Window.Property(MediaNoche.Row))')
    return root


# --------------------------------------------------------------- bibliotecas
def build_library(window_id, title, media, tabs):
    """Cuadrícula de 5 columnas; a la izquierda, sinopsis, datos y tráiler del enfocado."""
    path = 'Window.Property(MediaNoche.Path)'
    root = ET.Element('window', type='window', id=str(window_id))
    add(root, 'defaultcontrol', '101', always='true')
    add(root, 'onload', f'SetProperty(MediaNoche.Page,{window_id})')
    add(root, 'onload', f'SetProperty(MediaNoche.Path,{tabs[0][1]})',
        condition='String.IsEmpty(Window.Property(MediaNoche.Path))')
    add(root, 'onload', 'SetProperty(MediaNoche.Cat,101)',
        condition='String.IsEmpty(Window.Property(MediaNoche.Cat))')
    add(root, 'onload', 'SetFocus($INFO[Window.Property(MediaNoche.Cat)])')
    add(root, 'onload', 'AlarmClock(mn_rejilla,SetFocus(50),00:01,silent)')
    controls = add(root, 'controls')
    background(controls, '$VAR[MediaNoche.LibraryArt]')
    img(controls, 0, 0, 1920, 1080, 'common/white.png', '73000000')
    header(controls)
    prefix = 'Container(50).ListItem'
    # Panel izquierdo.
    lbl(controls, 80, 100, 560, 30, title.upper(), 'MN_Kicker', GOLD)
    info = add(controls, 'control', type='group')
    add(info, 'visible', 'Integer.IsGreater(Container(50).NumItems,0)')
    logo = img(info, 80, 140, 560, 130, f'$INFO[{prefix}.Art(clearlogo)]', aspect='keep', fade='250',
               visible=f'!String.IsEmpty({prefix}.Art(clearlogo))')
    logo.find('aspectratio').set('align', 'left')
    episode = f'String.IsEqual({prefix}.DBType,episode)'
    no_logo = f'String.IsEmpty({prefix}.Art(clearlogo))'
    lbl(info, 80, 136, 560, 140, f'$INFO[{prefix}.TVShowTitle]', 'MN_HeroM', WHITE,
        aligny='top', wrap=True, visible=f'{no_logo} + {episode}')
    lbl(info, 80, 136, 560, 140, f'$INFO[{prefix}.Label]', 'MN_HeroM', WHITE,
        aligny='top', wrap=True, visible=f'{no_logo} + !{episode}')
    lbl(info, 80, 284, 560, 32,
        f'$INFO[{prefix}.Year]$INFO[{prefix}.Duration(mins),  ·  , min]$INFO[{prefix}.Rating,  ·  ★ ]',
        'MN_Meta', MUTED, visible=f'!{episode}')
    lbl(info, 80, 284, 560, 32,
        f'T$INFO[{prefix}.Season]  ·  E$INFO[{prefix}.Episode]  ·  $INFO[{prefix}.Label]',
        'MN_Meta', MUTED, visible=episode)
    lbl(info, 80, 318, 560, 30, f'$INFO[{prefix}.Genre]', 'MN_Small', FAINT)
    hero_badges(info, prefix, 80, 356)
    box = textbox(info, 80, 404, 560, 230, f'$INFO[{prefix}.Plot]', 'MN_Small')
    add(box, 'visible', f'![{hidden_episode_plot(50)}]')
    add(box, 'autoscroll', '6000,4000,2', time='3000', delay='6000', repeat='8000')
    lbl(info, 80, 404, 560, 32, 'Sinopsis oculta para evitar spoilers.', 'MN_Small', FAINT,
        visible=hidden_episode_plot(50))
    folder = f'String.IsEqual({prefix}.DBType,genre)'
    play = [(f'RunScript({FICHA_SCRIPT},play,$INFO[{prefix}.DBType],$INFO[{prefix}.DBID])',
             f'!String.IsEqual({prefix}.DBType,tvshow) + !{folder}'),
            (f'RunScript({FICHA_SCRIPT},tvshow,$INFO[{prefix}.DBID])', f'String.IsEqual({prefix}.DBType,tvshow)'),
            (f'SetProperty(MediaNoche.Path,$INFO[{prefix}.FolderPath])', folder)]
    img(controls, 80, 656, 560, 1, 'common/white.png', '66E5BC70')
    b = pill_button(controls, 801, 80, 680, 230, 'Reproducir', 'play2.png', play)
    nav(b, right=802, up=101, down=804)
    b = text_button(controls, 802, 326, 680, 'Tráiler', 'film.png',
                    [f'RunScript({TRAILER_SCRIPT},$ESCINFO[{prefix}.Trailer])'])
    nav(b, left=801, right=50, up=101, down=805)
    b = text_button(controls, 804, 80, 756, 'Mi lista', 'favourites.png',
                    [f'RunScript({FAV_SCRIPT},$INFO[{prefix}.DBType],$INFO[{prefix}.DBID],toggle)'], 188)
    nav(b, right=805, up=801, down=9100)
    b = text_button(controls, 805, 284, 756, 'Descargar', 'download.png',
                    [f'RunScript({DOWNLOAD_SCRIPT},$INFO[{prefix}.DBType],$INFO[{prefix}.DBID])'], 200)
    nav(b, left=804, right=803, up=802, down=9100)
    b = text_button(controls, 803, 500, 756, 'Ficha', 'info.png',
                    [(f'RunScript({FICHA_SCRIPT},$INFO[{prefix}.DBType],$INFO[{prefix}.DBID])',
                      f'!String.IsEqual({prefix}.DBType,episode)'),
                     (f'RunScript({INFO_SCRIPT},episode,$INFO[{prefix}.DBID])', episode)], 140)
    nav(b, left=805, right=50, up=802, down=9100)
    # Pestañas encima de la cuadrícula.
    x = 690
    for index, (name, content) in enumerate(tabs):
        width = 40 + len(name) * 12
        identity = 101 + index
        selected = f'String.IsEqual(Window.Property(MediaNoche.Cat),{identity})'
        node = tab(controls, identity, x, 96, width, name, selected,
                   focus=[f'SetProperty(MediaNoche.Path,{content})',
                          f'SetProperty(MediaNoche.Cat,{identity})'])
        nav(node, left=identity - 1 if index else 801,
            right=identity + 1 if index + 1 < len(tabs) else identity, down=LIB_DOWN)
        x += width + 22
    count = lbl(controls, 1340, 100, 500, 40, '$INFO[Container(50).NumItems,, títulos]',
                'MN_Small', FAINT, 'right')
    add(count, 'visible', 'Integer.IsGreater(Container(50).NumItems,0)')
    # Cuadrícula.
    pw, ph, cw, chh = 186, 279, 234, 320
    grid = ctrl(controls, 'panel', 690, 156, 1170, 830, 50)
    add(grid, 'orientation', 'vertical')
    add(grid, 'scrolltime', '220', tween='cubic', easing='out')
    add(grid, 'preloaditems', '2')
    nav(grid, up='SetFocus($INFO[Window.Property(MediaNoche.Cat)])', left=802, down=9100)
    for tag in ('itemlayout', 'focusedlayout'):
        layout = add(grid, tag, width=str(cw), height=str(chh))
        focused = tag == 'focusedlayout'
        cx, cy = (cw - pw) // 2, 22
        centre = f'{cx + pw // 2},{cy + ph // 2}'
        if focused:
            on = 'Control.HasFocus(50)'
            halo = img(layout, cx - 30, cy - 30, pw + 60, ph + 60, MEDIA + 'glow.png', '80E5BC70',
                       border='60', visible=on)
            zoom(halo, 106, centre)
            frame = img(layout, cx - 6, cy - 6, pw + 12, ph + 12, MEDIA + 'round14.png', GOLD,
                        border='14', visible=on)
            zoom(frame, 106, centre)
        art = img(layout, cx, cy, pw, ph, '$VAR[MediaNoche.Poster]',
                  None if focused else 'B3FFFFFF', diffuse=MEDIA + 'mask_poster.png',
                  aspect='scale', background=True)
        art.find('texture').set('fallback', 'DefaultVideo.png')
        if focused:
            zoom(art, 106, centre)
        # Géneros y carpetas: tarjeta con el nombre.
        lbl(layout, cx + 10, cy + 10, pw - 20, ph - 20, '$INFO[ListItem.Label]', 'MN_Head', WHITE,
            align='center', wrap=True, visible='String.IsEqual(ListItem.DBType,genre)')
        check = img(layout, cx + pw - 36, cy + 8, 28, 28, MEDIA + 'check.png',
                    visible='ListItem.IsWatched | String.IsEqual(ListItem.Overlay,OverlayWatched.png)')
        if focused:
            zoom(check, 106, centre)
        bar = ctrl(layout, 'progress', cx + 12, cy + ph - 16, pw - 24, 5)
        add(bar, 'texturebg', 'common/white.png', colordiffuse='59FFFFFF')
        add(bar, 'midtexture', 'common/white.png', colordiffuse=GOLD)
        add(bar, 'info', 'ListItem.PercentPlayed')
        add(bar, 'visible', 'ListItem.IsResumable')
    add(grid, 'content', f'$INFO[{path}]', target='videos', limit='400')
    item_click(grid)
    add(grid, 'onclick', f'SetProperty(MediaNoche.Path,$INFO[{prefix}.FolderPath])',
        condition=f'String.IsEqual({prefix}.DBType,genre)')
    genres = 'videodb://movies/genres/' if media == 'movie' else 'videodb://tvshows/genres/'
    add(grid, 'onback', f'SetProperty(MediaNoche.Path,{genres})',
        condition=f'String.StartsWith({path},{genres}) + !String.IsEqual({path},{genres})')
    lbl(controls, 700, 400, 1100, 60, 'Cargando tu biblioteca…', 'MN_Body', FAINT,
        visible='Container(50).IsUpdating')
    empty = lbl(controls, 700, 400, 1100, 60, 'Todavía no hay títulos aquí.', 'MN_Body', FAINT,
                visible='!Container(50).IsUpdating + Integer.IsEqual(Container(50).NumItems,0)')
    lbl(controls, 700, 450, 1100, 60,
        'En la ficha de una película o serie, pulsa «Mi lista» para añadirla.', 'MN_Small', FAINT,
        visible='!Container(50).IsUpdating + Integer.IsEqual(Container(50).NumItems,0)'
                ' + [String.Contains(Window.Property(MediaNoche.Path),favoritos-) | String.Contains(Window.Property(MediaNoche.Path),milista)]')
    dock(controls, str(window_id), 50)
    return root


# ------------------------------------------------------------- preferencias
def build_preferences():
    root = ET.Element('window', type='window', id='1195')
    add(root, 'defaultcontrol', '101', always='true')
    add(root, 'onload', 'SetProperty(MediaNoche.Page,1195)')
    controls = add(root, 'controls')
    background(controls, '')
    header(controls)
    lbl(controls, 80, 150, 1000, 30, 'AJUSTES', 'MN_Kicker', GOLD)
    lbl(controls, 80, 180, 1400, 140, 'TU FORMA DE VER LA NOCHE', 'MN_HeroM', WHITE)
    lbl(controls, 80, 320, 1400, 34, 'Elige tu inicio y entra en los ajustes de Kodi o del skin.', 'MN_Meta', MUTED)
    entries = [
        ('Ajustes de Kodi', ['ActivateWindow(Settings)']),
        ('Ajustes del skin', ['ActivateWindow(SkinSettings)']),
        ('Inicio premium', ['Skin.Reset(medianoche.nativehome)', 'ReplaceWindow(1191)']),
        ('Inicio clásico', ['Skin.SetBool(medianoche.nativehome)', 'ReplaceWindow(Home)']),
        ('$VAR[MediaNoche.EpisodePlotMode]', ['Skin.ToggleSetting(medianoche.hideepisodeplots)']),
        ('Carpeta de descargas', ['Skin.SetPath(medianoche.descargas)']),
    ]
    for index, (text, actions) in enumerate(entries):
        identity = 101 + index
        node = ctrl(controls, 'button', 80 + (index % 2) * 620, 400 + (index // 2) * 100, 580, 76, identity)
        add(node, 'texturefocus', MEDIA + 'pill.png', colordiffuse=GOLD, border='32')
        add(node, 'texturenofocus', MEDIA + 'pill.png', colordiffuse='1CFFFFFF', border='32')
        add(node, 'font', 'MN_Button')
        add(node, 'textcolor', WHITE)
        add(node, 'focusedcolor', DARK)
        add(node, 'textoffsetx', '34')
        add(node, 'aligny', 'center')
        add(node, 'label', text)
        for action in actions:
            add(node, 'onclick', action)
        nav(node, left=identity - 1 if index else identity, right=identity + 1 if index + 1 < len(entries) else identity,
            up=identity - 2 if index > 1 else identity, down=identity + 2 if index + 2 < len(entries) else 9100)
    dock(controls, '1195', 101)
    return root


# ------------------------------------------------------------------- fichas
def person_row(controls, prefix, x, y, count, visible):
    for index in range(1, count + 1):
        key = f'{P}({prefix}.Cast{index}'
        group = add(controls, 'control', type='group')
        add(group, 'visible', f'{visible} + !String.IsEmpty({key}.Name))')
        cx = x + (index - 1) * 140
        img(group, cx + 15, y, 100, 100, 'common/white.png', '2EFFFFFF',
            diffuse=MEDIA + 'circle.png')
        photo = img(group, cx + 15, y, 100, 100, f'$INFO[{key}.Thumb)]', diffuse=MEDIA + 'circle.png',
                    aspect='scale', background=True)
        photo.find('texture').set('fallback', 'DefaultActor.png')
        img(group, cx + 15, y, 100, 100, MEDIA + 'ring.png', '4DFFFFFF')
        lbl(group, cx, y + 108, 130, 26, f'$INFO[{key}.Name)]', 'MN_Small', WHITE, 'center')
        lbl(group, cx, y + 134, 130, 24, f'$INFO[{key}.Role)]', 'MN_Tiny', FAINT, 'center')


def badges(controls, prefix, x, y, w, align='left'):
    group = ctrl(controls, 'grouplist', x, y, w, 40)
    add(group, 'orientation', 'horizontal')
    add(group, 'itemgap', '8')
    add(group, 'align', align)
    for index in range(1, 4):
        key = f'{P}({prefix}.Badge{index})'
        node = add(group, 'control', type='button')
        add(node, 'width', 'auto')
        add(node, 'height', '36')
        add(node, 'texturenofocus', MEDIA + 'outline10.png', colordiffuse='99FFFFFF', border='12')
        add(node, 'texturefocus', MEDIA + 'outline10.png', colordiffuse='99FFFFFF', border='12')
        add(node, 'font', 'MN_Tiny')
        add(node, 'textcolor', WHITE)
        add(node, 'disabledcolor', WHITE)
        add(node, 'textoffsetx', '12')
        add(node, 'aligny', 'center')
        add(node, 'label', f'$INFO[{key}]')
        add(node, 'enable', 'false')
        add(node, 'visible', f'!String.IsEmpty({key})')


def rating_meta(controls, prefix, x, y):
    lbl(controls, x, y, 76, 50, f'$INFO[{P}({prefix}.Rating)]', 'MN_Rating', GOLD, 'right',
        visible=f'!String.IsEmpty({P}({prefix}.Rating))')
    lbl(controls, x + 80, y + 6, 50, 44, '/10', 'MN_Small', FAINT,
        visible=f'!String.IsEmpty({P}({prefix}.Rating))')
    lbl(controls, x + 140, y, 1100, 50, f'$INFO[{P}({prefix}.Meta)]$INFO[{P}({prefix}.EndTime),  ·  ]', 'MN_Meta', MUTED)


def build_ficha():
    """Ficha de película: cartel, datos, botones y pestañas Reparto/Parecidas/Detalles."""
    f = 'MN.F'
    root = ET.Element('window', type='window', id='1196')
    add(root, 'defaultcontrol', '1201', always='true')
    add(root, 'onload', 'SetProperty(MN.Tab,1301)')
    add(root, 'onload', f'RunScript({FAV_SCRIPT},movie,$INFO[{P}({f}.DBID)],refresh)')
    controls = add(root, 'controls')
    background(controls, f'$INFO[{P}({f}.Fanart)]')
    img(controls, 0, 0, 1920, 1080, MEDIA + 'grad_left.png')
    poster = img(controls, 100, 80, 400, 600, f'$INFO[{P}({f}.Poster)]',
                 diffuse=MEDIA + 'mask_poster.png', aspect='scale', background=True)
    poster.find('texture').set('fallback', 'DefaultVideo.png')
    badges(controls, f, 100, 704, 400, 'center')
    x = 570
    lbl(controls, x, 70, 1250, 30, f'$INFO[{P}({f}.Kicker)]', 'MN_Kicker', GOLD)
    lbl(controls, x, 100, 1250, 140, f'$INFO[{P}({f}.Title)]', 'MN_Hero', WHITE)
    rating_meta(controls, f, x, 245)
    textbox(controls, x, 310, 1150, 132, f'$INFO[{P}({f}.Plot)]')
    lbl(controls, x, 452, 1250, 34, f'$INFO[{P}({f}.Credits)]', 'MN_Small', MUTED)
    b = pill_button(controls, 1201, x, 510, 260, f'$INFO[{P}({f}.PlayLabel)]', 'play2.png',
                    [f'RunScript({FICHA_SCRIPT},play,movie,$INFO[{P}({f}.DBID)])'])
    nav(b, right=1202, down=1301)
    b = text_button(controls, 1202, x + 280, 512, 'Tráiler', 'film.png',
                    [f'RunScript({TRAILER_SCRIPT},$INFO[{P}({f}.TrailerEsc)])'])
    nav(b, left=1201, right=1203, down=1301)
    b = text_button(controls, 1203, x + 472, 512, '$VAR[MediaNoche.FavLabel]', 'favourites.png',
                    [f'RunScript({FAV_SCRIPT},movie,$INFO[{P}({f}.DBID)],toggle)'], 228)
    nav(b, left=1202, right=1205, down=1301)
    b = text_button(controls, 1205, x + 716, 512, 'Descargar', 'download.png',
                    [f'RunScript({DOWNLOAD_SCRIPT},movie,$INFO[{P}({f}.DBID)])'], 200)
    nav(b, left=1203, right=1204, down=1301)
    b = text_button(controls, 1204, x + 932, 512, 'Más info', 'info.png',
                    [f'RunScript({INFO_SCRIPT},movie,$INFO[{P}({f}.DBID)])'], 188)
    nav(b, left=1205, down=1301)
    tabs = (('Reparto', 1301), ('Parecidas', 1302), ('Detalles', 1303))
    tx = x
    for index, (name, identity) in enumerate(tabs):
        selected = f'String.IsEqual(Window.Property(MN.Tab),{identity})'
        node = tab(controls, identity, tx, 610, 160, name, selected,
                   focus=[f'SetProperty(MN.Tab,{identity})'])
        nav(node, left=tabs[index - 1][1], right=tabs[(index + 1) % 3][1], up=1201,
            down=[('1400', 'String.IsEqual(Window.Property(MN.Tab),1302)')])
        tx += 180
    person_row(controls, f, x, 690, 8, 'String.IsEqual(Window.Property(MN.Tab),1301)')
    similar = poster_list(controls, 1400, x - 15, 660, 1270,
                          f'$INFO[{P}({f}.SimilarPath)]', small=True,
                          visible='String.IsEqual(Window.Property(MN.Tab),1302)')
    nav(similar, up=1302)
    item_click(similar)
    textbox(controls, x, 690, 1150, 300, f'$INFO[{P}({f}.Details)]', 'MN_Meta', MUTED,
            visible='String.IsEqual(Window.Property(MN.Tab),1303)')
    return root


def build_serie():
    """Serie: datos a la izquierda; temporadas y episodios a la derecha."""
    s = 'MN.S'
    root = ET.Element('window', type='window', id='1197')
    add(root, 'defaultcontrol', '1201', always='true')
    add(root, 'onload', f'RunScript({FAV_SCRIPT},tvshow,$INFO[{P}({s}.DBID)],refresh)')
    add(root, 'onload', f'SetFocus(300,$INFO[{P}({s}.SeasonPos)],absolute)')
    add(root, 'onload', 'SetFocus(1201)')
    controls = add(root, 'controls')
    background(controls, f'$INFO[{P}({s}.Fanart)]')
    img(controls, 0, 0, 1920, 1080, MEDIA + 'grad_left.png')
    img(controls, 760, 0, 1160, 1080, 'common/white.png', '8C050A12')
    x = 90
    lbl(controls, x, 70, 640, 30, f'$INFO[{P}({s}.Kicker)]', 'MN_Kicker', GOLD)
    lbl(controls, x, 100, 640, 124, f'$INFO[{P}({s}.Title)]', 'MN_HeroM', WHITE, scroll=True)
    rating_meta(controls, s, x, 230)
    badges(controls, s, x, 292, 640)
    textbox(controls, x, 344, 640, 132, f'$INFO[{P}({s}.Plot)]', 'MN_Body')
    lbl(controls, x, 494, 400, 30, f'$INFO[{P}({s}.NextInfo)]', 'MN_Small', MUTED)
    lbl(controls, x + 340, 494, 300, 30, f'$INFO[{P}({s}.Watched)]', 'MN_Small', MUTED, 'right')
    img(controls, x, 532, 640, 4, 'common/white.png', '26FFFFFF')
    for pct in range(5, 101, 5):
        img(controls, x, 532, int(640 * pct / 100), 4, 'common/white.png', GOLD,
            visible=f'String.IsEqual({P}({s}.Bucket),{pct})')
    b = pill_button(controls, 1201, x, 566, 300, f'$INFO[{P}({s}.PlayLabel)]', 'play2.png',
                    [f'RunScript({FICHA_SCRIPT},play,episode,$INFO[{P}({s}.NextDBID)])'])
    nav(b, right=1202, up=300, down=1203)
    b = text_button(controls, 1202, x + 316, 566, 'Tráiler', 'film.png',
                    [f'RunScript({TRAILER_SCRIPT},$INFO[{P}({s}.TrailerEsc)])'])
    nav(b, left=1201, right=300, down=1205)
    b = text_button(controls, 1203, x, 642, '$VAR[MediaNoche.FavLabel]', 'favourites.png',
                    [f'RunScript({FAV_SCRIPT},tvshow,$INFO[{P}({s}.DBID)],toggle)'], 228)
    nav(b, right=1205, up=1201)
    b = text_button(controls, 1205, x + 244, 642, 'Descargar', 'download.png',
                    [f'RunScript({DOWNLOAD_SCRIPT},tvshow,$INFO[{P}({s}.DBID)])'], 200)
    nav(b, left=1203, right=1204, up=1202)
    b = text_button(controls, 1204, x + 460, 642, 'Más info', 'info.png',
                    [f'RunScript({INFO_SCRIPT},tvshow,$INFO[{P}({s}.DBID)])'], 180)
    nav(b, left=1205, right=300, up=1202)
    person_row(controls, s, x - 15, 760, 4, 'true')
    # Temporadas (pestañas) y episodios.
    seasons = ctrl(controls, 'list', 830, 70, 1000, 60, 300)
    add(seasons, 'orientation', 'horizontal')
    add(seasons, 'scrolltime', '200')
    nav(seasons, left=1202, down=310, up=310)
    for tag in ('itemlayout', 'focusedlayout'):
        layout = add(seasons, tag, width='250', height='60')
        current = tag == 'focusedlayout'
        lbl(layout, 0, 0, 230, 50,
            '$INFO[ListItem.Label]$INFO[ListItem.Property(WatchedEpisodes),  ·  ,]'
            '$INFO[ListItem.Property(TotalEpisodes),/,]',
            'MN_Tab', WHITE if current else FAINT, scroll=current)
        if current:
            img(layout, 0, 52, 210, 3, 'common/white.png', GOLD)
    add(seasons, 'content', f'videodb://tvshows/titles/$INFO[{P}({s}.DBID)]/', target='videos')
    episodes = ctrl(controls, 'list', 830, 150, 1010, 920, 310)
    add(episodes, 'orientation', 'vertical')
    add(episodes, 'scrolltime', '220', tween='cubic', easing='out')
    nav(episodes, left=1201, up=300)
    add(episodes, 'onclick', f'RunScript({FICHA_SCRIPT},play,episode,$INFO[ListItem.DBID])')
    for tag in ('itemlayout', 'focusedlayout'):
        big = tag == 'focusedlayout'
        layout = add(episodes, tag, width='1010', height='250' if big else '122')
        if big:
            img(layout, 0, 4, 1000, 240, MEDIA + 'round14.png', '12FFFFFF', border='14')
            img(layout, 0, 4, 1000, 240, MEDIA + 'outline10.png', GOLD, border='12',
                visible='Control.HasFocus(310)')
        tw, th = (256, 144) if big else (176, 99)
        thumb = img(layout, 18, 20 if big else 12, tw, th, '$INFO[ListItem.Art(thumb)]',
                    diffuse=MEDIA + 'mask_wide.png', aspect='scale', background=True)
        thumb.find('texture').set('fallback', 'DefaultTVShows.png')
        img(layout, 18 + tw - 36, (20 if big else 12) + 8, 28, 28, MEDIA + 'check.png',
            visible='ListItem.IsWatched | String.IsEqual(ListItem.Overlay,OverlayWatched.png)')
        if big:
            bar = ctrl(layout, 'progress', 18, 20 + th - 6, tw, 6)
            add(bar, 'texturebg', 'common/white.png', colordiffuse='40FFFFFF')
            add(bar, 'midtexture', 'common/white.png', colordiffuse=GOLD)
            add(bar, 'info', 'ListItem.PercentPlayed')
            add(bar, 'visible', 'ListItem.IsResumable')
        tx = 18 + tw + 26
        lbl(layout, tx, 16 if big else 18, 70, 40, '$INFO[ListItem.Episode]', 'MN_Num',
            GOLD if big else FAINT)
        lbl(layout, tx + 60, 16 if big else 18, 1000 - tx - 80, 40, '$INFO[ListItem.Title]',
            'MN_Head' if big else 'MN_Ep', WHITE, scroll=big)
        lbl(layout, tx, 56 if big else 58, 1000 - tx - 20, 30,
            '$INFO[ListItem.Duration(mins),, min]$INFO[ListItem.Premiered,  ·  ]', 'MN_Small', FAINT)
        if big:
            spoiler = ('Skin.HasSetting(medianoche.hideepisodeplots) + '
                       '!ListItem.IsWatched + !ListItem.IsResumable')
            textbox(layout, tx, 96, 1000 - tx - 30, 132, '$INFO[ListItem.Plot]', 'MN_Small',
                    'E6DDE6EF', visible=f'![{spoiler}]')
            lbl(layout, tx, 96, 600, 30, 'Sinopsis oculta para evitar spoilers.', 'MN_Small',
                FAINT, visible=spoiler)
    add(episodes, 'content',
        f'videodb://tvshows/titles/$INFO[{P}({s}.DBID)]/$INFO[Container(300).ListItem.Season]/',
        target='videos')
    return root


# ------------------------------------------------------------- variables
def variables(root):
    """Fondo del destacado de Inicio y fondos de las bibliotecas."""
    fav = add(root, 'variable', name='MediaNoche.FavLabel')
    add(fav, 'value', 'En mi lista', condition='String.IsEqual(Window(home).Property(MediaNoche.FavouriteState),added)')
    add(fav, 'value', 'Mi lista')
    hero = add(root, 'variable', name='MediaNoche.HeroArt')
    for identity, *_ in ALL_ROWS:
        on = f'String.IsEqual(Window.Property(MediaNoche.Row),{identity})'
        for field in ('Art(fanart)', 'Art(tvshow.fanart)'):
            add(hero, 'value', f'$INFO[Container({identity}).ListItem.{field}]',
                condition=f'{on} + !String.IsEmpty(Container({identity}).ListItem.{field})')
    add(hero, 'value', '')
    for identity, *_ in ALL_ROWS:
        logo = add(root, 'variable', name=f'MediaNoche.Logo{identity}')
        for field in ('Art(clearlogo)', 'Art(tvshow.clearlogo)'):
            add(logo, 'value', f'$INFO[Container({identity}).ListItem.{field}]',
                condition=f'!String.IsEmpty(Container({identity}).ListItem.{field})')
        add(logo, 'value', '')


# ------------------------------------------------------------------ montaje
def save(path, root):
    # Estas listas ya traen su propio resaltado: que fluidez_resaltado no las toque.
    for listing in root.iter('control'):
        if listing.get('type') == 'list':
            for tag, mark in (('focusedlayout', 'resaltado'), ('itemlayout', 'atenuado')):
                layout = listing.find(tag)
                if layout is not None:
                    layout.set('medianoche', mark)
    ET.indent(root, space='    ')
    ET.ElementTree(root).write(path, encoding='UTF-8', xml_declaration=True)


def fix_focus_colours(base):
    """Barra de selección dorada con texto oscuro en todas las ventanas de Kodi.

    Un preajuste de color de Arctic podía dejar la barra en blanco con el texto
    blanco (no se leía la opción seleccionada, p. ej. al elegir bibliotecas en PKC).
    """
    defs_path = base / '1080i/Includes_Defs.xml'
    defs = ET.parse(defs_path)
    variable = defs.getroot().find("variable[@name='ColorHighlight']")
    for value in list(variable):
        variable.remove(value)
    add(variable, 'value', 'FFE5BC70')  # hex: también vale dentro de [COLOR]
    defs.write(defs_path, encoding='UTF-8', xml_declaration=True)
    for palette in ('defaults.xml', 'Media Noche.xml'):
        path = base / 'colors' / palette
        tree = ET.parse(path)
        for color in tree.getroot().findall('color'):
            if color.get('name') == 'Selected':
                color.text = 'FF0B1320'
        tree.write(path, encoding='UTF-8', xml_declaration=True)


def apply(base, project):
    directory = base / '1080i'
    make_textures(base / 'extras/medianoche')
    install_fonts(base, project)
    for window_id, (title, media, tabs) in GRIDS.items():
        filename = ('Custom_SeriesEstrenos_1190.xml' if window_id == 1190
                    else f'Custom_MediaNoche_{window_id}.xml')
        title_rows, rows = SECTION_ROWS[window_id]
        save(directory / filename, build_home(str(window_id), rows, title_rows))
    save(directory / 'Custom_MediaNoche_1191.xml', build_home())
    save(directory / 'Custom_MediaNoche_1195.xml', build_preferences())
    save(directory / 'Custom_MediaNoche_1196.xml', build_ficha())
    save(directory / 'Custom_MediaNoche_1197.xml', build_serie())
    includes_path = directory / 'Includes_MediaNoche.xml'
    includes = ET.parse(includes_path).getroot()
    variables(includes)
    save(includes_path, includes)
    fix_focus_colours(base)
    for name in ('medianoche_ficha.py', 'medianoche_explore.py', 'medianoche_misfavoritos.py',
                 'medianoche_descargar.py'):
        shutil.copyfile(project / 'skin/extras' / name, base / 'extras' / name)
    return {'premium_windows': [1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197],
            'fonts': [name for name, _, _ in FONTS], 'dock_items': len(DOCK)}
