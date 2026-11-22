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
MUTED = 'B3DDE6EF'
FAINT = '80DDE6EF'
MEDIA = 'special://skin/extras/medianoche/'
ICONS = 'special://skin/extras/icons/'
INFO_SCRIPT = 'special://skin/extras/medianoche_info.py'
FICHA_SCRIPT = 'special://skin/extras/medianoche_ficha.py'
TRAILER_SCRIPT = 'special://skin/extras/medianoche_trailer.py'
FAV_SCRIPT = 'special://skin/extras/medianoche_favourites.py'
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
    ('MN_Ep', 'MN-Outfit-Medium.ttf', 23),
    ('MN_Tab', 'MN-Inter-Medium.ttf', 20),
    ('MN_Body', 'MN-Inter-Regular.ttf', 22),
    ('MN_Meta', 'MN-Inter-Regular.ttf', 20),
    ('MN_Small', 'MN-Inter-Regular.ttf', 18),
    ('MN_Kicker', 'MN-Inter-Medium.ttf', 17),
    ('MN_Tiny', 'MN-Inter-Regular.ttf', 15),
    ('MN_Dock', 'MN-Inter-Medium.ttf', 16),
]

DOCK = [  # etiqueta, icono, acción, ventana de la sección
    ('Inicio', 'home.png', 'ReplaceWindow(1191)', '1191'),
    ('Favoritos', 'favourites.png', 'ActivateWindow(Favourites)', ''),
    ('Series estrenos', 'recentlyadded.png', 'ReplaceWindow(1190)', '1190'),
    ('Series', 'tv.png', 'ReplaceWindow(1192)', '1192'),
    ('Cine', 'film.png', 'ReplaceWindow(1193)', '1193'),
    ('Novedades cine', 'recent.png', 'ReplaceWindow(1194)', '1194'),
    ('TV', 'livetv.png', 'ActivateWindow(TVChannels)', ''),
    ('Ajustes', 'settings.png', 'ReplaceWindow(1195)', '1195'),
    ('Apagar', 'power.png', 'ActivateWindow(shutdownmenu)', ''),
]

LIB_DOWN = [('50', 'Integer.IsGreater(Container(50).NumItems,0)'),
            ('9100', '!Integer.IsGreater(Container(50).NumItems,0)')]

HOME_ROWS = [  # id, pestaña, lista
    (501, 'Novedades cine', 'cine-reciente.xsp'),
    (502, 'Series estrenos', 'series-completas.xsp'),
    (503, 'Continuar series', 'episodios-continuar.xsp'),
    (504, 'Continuar cine', 'cine-continuar.xsp'),
    (505, 'Cine', 'cine.xsp'),
    (506, 'Series', 'series.xsp'),
]


# ---------------------------------------------------------------- utilidades
def add(parent, tag, text=None, **attrs):
    node = ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})
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
    night = (5, 10, 18)
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
    img(controls, 0, 0, 1920, 1080, 'common/white.png', 'FF050A12')
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
    img(controls, 80, 972, 1760, 84, MEDIA + 'pill.png', '1CFFFFFF', border='32')
    img(controls, 112, 972, 1696, 1, 'common/white.png', '40FFFFFF')
    listing = ctrl(controls, 'list', 85, 972, 1750, 84, 9100)
    add(listing, 'orientation', 'horizontal')
    add(listing, 'scrolltime', '0')
    add(listing, 'onup', up)
    if page != '1191':
        add(listing, 'onback', 'ReplaceWindow(1191)')
    for tag in ('itemlayout', 'focusedlayout'):
        layout = add(listing, tag, width='194', height='84')
        focused = tag == 'focusedlayout'
        if focused:
            on = 'Control.HasFocus(9100)'
            img(layout, 2, 4, 190, 76, MEDIA + 'glow.png', '73E5BC70', border='60', visible=on)
            img(layout, 6, 10, 182, 64, MEDIA + 'pill.png', GOLD, border='32', visible=on)
            icon = img(layout, 16, 27, 30, 30, '$INFO[ListItem.Icon]', DARK, aspect='keep', visible=on)
            lbl(layout, 52, 10, 138, 64, '$INFO[ListItem.Label]', 'MN_Dock', DARK, visible=on, scroll=True)
            off = '!Control.HasFocus(9100)'
            img(layout, 16, 27, 30, 30, '$INFO[ListItem.Icon]', MUTED, aspect='keep', visible=off)
            lbl(layout, 52, 10, 138, 64, '$INFO[ListItem.Label]', 'MN_Dock', MUTED, visible=off)
        else:
            img(layout, 16, 27, 30, 30, '$INFO[ListItem.Icon]', MUTED, aspect='keep')
            lbl(layout, 52, 10, 138, 64, '$INFO[ListItem.Label]', 'MN_Dock', MUTED)
        # Sección actual: punto dorado bajo el icono.
        img(layout, 26, 66, 10, 10, MEDIA + 'circle.png', GOLD,
            visible='String.IsEqual(ListItem.Property(page),Window.Property(MediaNoche.Page))'
                    + (' + !Control.HasFocus(9100)' if focused else ''))
    content = add(listing, 'content')
    for label, icon, action, window in DOCK:
        item = add(content, 'item')
        add(item, 'label', label)
        add(item, 'icon', ICONS + icon)
        add(item, 'onclick', action)
        add(item, 'property', window, name='page')
    return listing


def pill_button(controls, identity, x, y, w, text, icon, actions):
    node = ctrl(controls, 'button', x, y, w, 64, identity)
    add(node, 'texturefocus', MEDIA + 'pill.png', colordiffuse=GOLD, border='32')
    add(node, 'texturenofocus', MEDIA + 'pill.png', colordiffuse='E6E5BC70', border='32')
    add(node, 'font', 'MN_Button')
    add(node, 'textcolor', DARK)
    add(node, 'focusedcolor', DARK)
    add(node, 'textoffsetx', '62')
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
    img(controls, x + 26, y + 20, 24, 24, ICONS + 'play2.png', DARK, aspect='keep')
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
    add(listing, 'content', content, target='videos', limit='25')
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
def build_home():
    root = ET.Element('window', type='window', id='1191')
    add(root, 'defaultcontrol', '701', always='true')
    add(root, 'onload', 'SetProperty(MediaNoche.Page,1191)')
    add(root, 'onload', 'SetProperty(MediaNoche.Row,501)',
        condition='String.IsEmpty(Window.Property(MediaNoche.Row))')
    add(root, 'onload', 'SetProperty(MediaNoche.RowTab,701)',
        condition='String.IsEmpty(Window.Property(MediaNoche.RowTab))')
    add(root, 'onload', 'SetFocus($INFO[Window.Property(MediaNoche.RowTab)])')
    controls = add(root, 'controls')
    background(controls, '$VAR[MediaNoche.HeroArt]')
    header(controls)
    row = 'Window.Property(MediaNoche.Row)'
    # Textos del elemento enfocado de la fila activa.
    for identity, name, _ in HOME_ROWS:
        group = add(controls, 'control', type='group')
        add(group, 'visible', f'String.IsEqual({row},{identity})')
        hero_texts(group, f'Container({identity}).ListItem', 150, name.upper(), plot=True,
                   plot_hidden=hidden_episode_plot(identity))
        empty = add(group, 'control', type='group')
        add(empty, 'visible', f'!Container({identity}).IsUpdating + Integer.IsEqual(Container({identity}).NumItems,0)')
        lbl(empty, 80, 180, 1150, 140, 'BUENAS HISTORIAS, SIEMPRE', 'MN_Hero', WHITE)
        lbl(empty, 80, 325, 1150, 34, 'Cuando PlexKodiConnect sincronice tu biblioteca, tus títulos aparecerán aquí.',
            'MN_Meta', MUTED)
    # Botones del destacado.
    play = []
    more = []
    trailer = []
    for identity, _, _ in HOME_ROWS:
        on = f'String.IsEqual({row},{identity})'
        prefix = f'Container({identity}).ListItem'
        play.append((f'RunScript({FICHA_SCRIPT},play,$INFO[{prefix}.DBType],$INFO[{prefix}.DBID])',
                     f'{on} + !String.IsEqual({prefix}.DBType,tvshow)'))
        play.append((f'RunScript({FICHA_SCRIPT},tvshow,$INFO[{prefix}.DBID])',
                     f'{on} + String.IsEqual({prefix}.DBType,tvshow)'))
        more.append((f'RunScript({FICHA_SCRIPT},$INFO[{prefix}.DBType],$INFO[{prefix}.DBID])',
                     f'{on} + !String.IsEqual({prefix}.DBType,episode)'))
        more.append((f'RunScript({INFO_SCRIPT},episode,$INFO[{prefix}.DBID])',
                     f'{on} + String.IsEqual({prefix}.DBType,episode)'))
        trailer.append((f'RunScript({TRAILER_SCRIPT},$ESCINFO[{prefix}.Trailer])', on))
    b = pill_button(controls, 801, 80, 470, 250, 'Reproducir', 'play2.png', play)
    nav(b, right=802, down='SetFocus($INFO[Window.Property(MediaNoche.RowTab)])')
    b = round_button(controls, 802, 350, 470, 'film.png', trailer)
    nav(b, left=801, right=803, down='SetFocus($INFO[Window.Property(MediaNoche.RowTab)])')
    b = round_button(controls, 803, 434, 470, 'info.png', more)
    nav(b, left=802, down='SetFocus($INFO[Window.Property(MediaNoche.RowTab)])')
    # Pestañas de filas.
    x = 80
    for index, (identity, name, _) in enumerate(HOME_ROWS):
        width = 40 + len(name) * 11
        selected = f'String.IsEqual({row},{identity})'
        node = tab(controls, 701 + index, x, 568, width, name, selected,
                   focus=[f'SetProperty(MediaNoche.Row,{identity})',
                          f'SetProperty(MediaNoche.RowTab,{701 + index})'])
        nav(node, left=701 + (index - 1) % len(HOME_ROWS), right=701 + (index + 1) % len(HOME_ROWS),
            up=801, down=[(f'SetFocus({identity})', f'Integer.IsGreater(Container({identity}).NumItems,0)'),
                          ('9100', f'!Integer.IsGreater(Container({identity}).NumItems,0)')])
        x += width + 20
    for identity, name, playlist in HOME_ROWS:
        listing = poster_list(controls, identity, 70, 625, 1780, PLAYLISTS + playlist,
                              visible=f'String.IsEqual({row},{identity})')
        nav(listing, up='SetFocus($INFO[Window.Property(MediaNoche.RowTab)])', down=9100)
        add(listing, 'onfocus', f'SetProperty(MediaNoche.RowTab,{701 + [r[0] for r in HOME_ROWS].index(identity)})')
        item_click(listing)
        empty = lbl(controls, 90, 700, 1400, 60, 'Todavía no hay títulos en esta fila.',
                    'MN_Body', FAINT)
        add(empty, 'visible', f'String.IsEqual({row},{identity}) + !Container({identity}).IsUpdating'
                              f' + Integer.IsEqual(Container({identity}).NumItems,0)')
    dock(controls, '1191', 'SetFocus($INFO[Window.Property(MediaNoche.Row)])')
    return root


# --------------------------------------------------------------- bibliotecas
def build_library(window_id, title, categories):
    root = ET.Element('window', type='window', id=str(window_id))
    add(root, 'defaultcontrol', '101', always='true')
    add(root, 'onload', f'SetProperty(MediaNoche.Page,{window_id})')
    add(root, 'onload', f'SetProperty(MediaNoche.Path,{PLAYLISTS}{categories[0][1]})',
        condition='String.IsEmpty(Window.Property(MediaNoche.Path))')
    add(root, 'onload', 'SetProperty(MediaNoche.Cat,101)',
        condition='String.IsEmpty(Window.Property(MediaNoche.Cat))')
    add(root, 'onload', 'SetFocus($INFO[Window.Property(MediaNoche.Cat)])')
    controls = add(root, 'controls')
    background(controls, '$VAR[MediaNoche.LibraryArt]')
    header(controls)
    hero_texts(controls, 'Container(50).ListItem', 150, title.upper(),
               plot_hidden=hidden_episode_plot(50))
    x = 80
    for index, (name, playlist) in enumerate(categories):
        width = 40 + len(name) * 11
        identity = 101 + index
        selected = f'String.IsEqual(Window.Property(MediaNoche.Cat),{identity})'
        node = tab(controls, identity, x, 568, width, name, selected,
                   focus=[f'SetProperty(MediaNoche.Path,{PLAYLISTS}{playlist})',
                          f'SetProperty(MediaNoche.Cat,{identity})'])
        nav(node, left=identity - 1 if index else 401,
            right=identity + 1 if index + 1 < len(categories) else 401, down=LIB_DOWN)
        x += width + 24
    explore = ctrl(controls, 'button', 1600, 571, 240, 48, 401)
    add(explore, 'texturefocus', MEDIA + 'pill.png', colordiffuse=GOLD, border='32')
    add(explore, 'texturenofocus', MEDIA + 'pill.png', colordiffuse='1CFFFFFF', border='32')
    add(explore, 'font', 'MN_Tab')
    add(explore, 'textcolor', WHITE)
    add(explore, 'focusedcolor', DARK)
    add(explore, 'align', 'center')
    add(explore, 'aligny', 'center')
    add(explore, 'label', 'Explorar')
    add(explore, 'onclick', f'RunScript({EXPLORE_SCRIPT},{"movie" if window_id in (1193, 1194) else "tvshow"})')
    nav(explore, left=100 + len(categories), right=101, down=LIB_DOWN)
    count = lbl(controls, 1240, 520, 600, 30, '$INFO[Container(50).NumItems,, títulos]',
                'MN_Small', FAINT, 'right')
    add(count, 'visible', 'Integer.IsGreater(Container(50).NumItems,0)')
    listing = poster_list(controls, 50, 70, 625, 1780, '$INFO[Window.Property(MediaNoche.Path)]')
    nav(listing, up='SetFocus($INFO[Window.Property(MediaNoche.Cat)])', down=9100)
    item_click(listing)
    lbl(controls, 90, 700, 1400, 60, 'Cargando tu biblioteca…', 'MN_Body', FAINT,
        visible='Container(50).IsUpdating')
    lbl(controls, 90, 700, 1400, 60, 'Todavía no hay títulos en esta categoría.', 'MN_Body', FAINT,
        visible='!Container(50).IsUpdating + Integer.IsEqual(Container(50).NumItems,0)')
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
    lbl(controls, x + 140, y, 1000, 50, f'$INFO[{P}({prefix}.Meta)]', 'MN_Meta', MUTED)


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
                    [f'PlayMedia("$INFO[{P}({f}.File)]",resume)'])
    nav(b, right=1202, down=1301)
    b = round_button(controls, 1202, x + 280, 510, 'film.png',
                     [f'RunScript({TRAILER_SCRIPT},$INFO[{P}({f}.TrailerEsc)])'])
    nav(b, left=1201, right=1203, down=1301)
    b = round_button(controls, 1203, x + 364, 510, 'favourites.png',
                     [f'RunScript({FAV_SCRIPT},movie,$INFO[{P}({f}.DBID)],toggle)'])
    nav(b, left=1202, right=1204, down=1301)
    img(controls, x + 364 + 44, x * 0 + 510 + 6, 14, 14, MEDIA + 'circle.png', GOLD,
        visible='String.IsEqual(Window(home).Property(MediaNoche.FavouriteState),added)')
    b = round_button(controls, 1204, x + 448, 510, 'info.png',
                     [f'RunScript({INFO_SCRIPT},movie,$INFO[{P}({f}.DBID)])'])
    nav(b, left=1203, down=1301)
    lbl(controls, x + 540, 510, 600, 64, f'$INFO[{P}({f}.EndTime)]', 'MN_Small', FAINT)
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
    lbl(controls, x, 100, 640, 230, f'$INFO[{P}({s}.Title)]', 'MN_HeroM', WHITE,
        aligny='top', wrap=True)
    rating_meta(controls, s, x, 330)
    badges(controls, s, x, 392, 640)
    textbox(controls, x, 450, 640, 132, f'$INFO[{P}({s}.Plot)]', 'MN_Body')
    lbl(controls, x, 600, 400, 30, f'$INFO[{P}({s}.NextInfo)]', 'MN_Small', MUTED)
    lbl(controls, x + 340, 600, 300, 30, f'$INFO[{P}({s}.Watched)]', 'MN_Small', MUTED, 'right')
    img(controls, x, 640, 640, 4, 'common/white.png', '26FFFFFF')
    for pct in range(5, 101, 5):
        img(controls, x, 640, int(640 * pct / 100), 4, 'common/white.png', GOLD,
            visible=f'String.IsEqual({P}({s}.Bucket),{pct})')
    b = pill_button(controls, 1201, x, 676, 300, f'$INFO[{P}({s}.PlayLabel)]', 'play2.png',
                    [f'PlayMedia("$INFO[{P}({s}.NextFile)]",resume)'])
    nav(b, right=1202, up=300, down=1202)
    b = round_button(controls, 1202, x + 320, 676, 'film.png',
                     [f'RunScript({TRAILER_SCRIPT},$INFO[{P}({s}.TrailerEsc)])'])
    nav(b, left=1201, right=1203)
    b = round_button(controls, 1203, x + 404, 676, 'favourites.png',
                     [f'RunScript({FAV_SCRIPT},tvshow,$INFO[{P}({s}.DBID)],toggle)'])
    nav(b, left=1202, right=1204)
    img(controls, x + 404 + 44, 682, 14, 14, MEDIA + 'circle.png', GOLD,
        visible='String.IsEqual(Window(home).Property(MediaNoche.FavouriteState),added)')
    b = round_button(controls, 1204, x + 488, 676, 'info.png',
                     [f'RunScript({INFO_SCRIPT},tvshow,$INFO[{P}({s}.DBID)])'])
    nav(b, left=1203, right=300)
    person_row(controls, s, x - 15, 790, 4, 'true')
    # Temporadas (pestañas) y episodios.
    seasons = ctrl(controls, 'list', 830, 70, 1000, 60, 300)
    add(seasons, 'orientation', 'horizontal')
    add(seasons, 'scrolltime', '200')
    nav(seasons, left=1204, down=310, up=310)
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
    add(episodes, 'onclick', 'PlayMedia($ESCINFO[ListItem.FileNameAndPath],resume)')
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
    hero = add(root, 'variable', name='MediaNoche.HeroArt')
    for identity, _, _ in HOME_ROWS:
        on = f'String.IsEqual(Window.Property(MediaNoche.Row),{identity})'
        for field in ('Art(fanart)', 'Art(tvshow.fanart)'):
            add(hero, 'value', f'$INFO[Container({identity}).ListItem.{field}]',
                condition=f'{on} + !String.IsEmpty(Container({identity}).ListItem.{field})')
    add(hero, 'value', '')


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


def apply(base, project):
    directory = base / '1080i'
    make_textures(base / 'extras/medianoche')
    install_fonts(base, project)
    for window_id, (title, categories) in LIBRARIES.items():
        filename = ('Custom_SeriesEstrenos_1190.xml' if window_id == 1190
                    else f'Custom_MediaNoche_{window_id}.xml')
        save(directory / filename, build_library(window_id, title, categories))
    save(directory / 'Custom_MediaNoche_1191.xml', build_home())
    save(directory / 'Custom_MediaNoche_1195.xml', build_preferences())
    save(directory / 'Custom_MediaNoche_1196.xml', build_ficha())
    save(directory / 'Custom_MediaNoche_1197.xml', build_serie())
    includes_path = directory / 'Includes_MediaNoche.xml'
    includes = ET.parse(includes_path).getroot()
    variables(includes)
    save(includes_path, includes)
    for name in ('medianoche_ficha.py', 'medianoche_explore.py'):
        shutil.copyfile(project / 'skin/extras' / name, base / 'extras' / name)
    return {'premium_windows': [1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197],
            'fonts': [name for name, _, _ in FONTS], 'dock_items': len(DOCK)}
