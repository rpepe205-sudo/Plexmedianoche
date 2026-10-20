"""Native Kodi controls for the user's approved Media Noche reference photo.

No OS paths, browser widgets, remote scripts or extra Android dependencies.
"""
import struct
import zlib
import xml.etree.ElementTree as ET

GOLD = 'FFE4B75B'
WHITE = 'FFF4F3EF'
MUTED = 'FF94A7B8'


def tag(parent, name, text=None, **attrs):
    node = ET.SubElement(parent, name, {k: str(v) for k, v in attrs.items()})
    if text is not None:
        node.text = str(text)
    return node


def control(parent, kind, x=0, y=0, w=0, h=0, ident=None, **fields):
    attrs = {'type': kind}
    if ident is not None:
        attrs['id'] = str(ident)
    node = tag(parent, 'control', **attrs)
    for key, val in [('left', x), ('top', y), ('width', w), ('height', h), *fields.items()]:
        tag(node, key, val)
    return node


def image(parent, x, y, w, h, texture, **fields):
    return control(parent, 'image', x, y, w, h, texture=texture, **fields)


def label(parent, x, y, w, h, text, font='pmn.body', color=WHITE, **fields):
    return control(parent, 'label', x, y, w, h, label=text, font=font,
                   textcolor=color, **fields)


def button(parent, ident, x, y, w, h, title, action, up, down, left, right, small=False):
    node = control(parent, 'button', x, y, w, h, ident, label=title,
                   font='pmn.small' if small else 'pmn.body', textcolor=WHITE,
                   focusedcolor=GOLD, texturefocus='pmn/focus.png',
                   texturenofocus='pmn/panel.png', align='center', aligny='center',
                   onup=up, ondown=down, onleft=left, onright=right)
    for item in action if isinstance(action, list) else [action]:
        tag(node, 'onclick', item)
    return node


def png(path, width, height, pixel):
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data) & 0xffffffff)
    raw = b''.join(b'\x00' + bytes(c for x in range(width) for c in pixel(x, y)) for y in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 6, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def generate(root):
    media = root / 'media/pmn'
    media.mkdir(parents=True, exist_ok=True)
    png(media / 'night.png', 256, 144, lambda x, y: (3 + x // 80, 9 + y // 20, 17 + y // 12, 255))
    png(media / 'panel.png', 32, 32, lambda x, y: (9, 19, 29, 135))
    png(media / 'focus.png', 128, 64, lambda x, y: (228, 183, 91, 255) if x == 0 or y == 0 or x == 127 or y == 63 else (40, 32, 16, 230))
    png(media / 'line.png', 128, 4, lambda x, y: (42, 112, 159, max(0, 230 - abs(y - 1) * 60)))
    png(media / 'shade.png', 256, 8, lambda x, y: (2, 7, 13, max(50, 250 - x)))
    png(media / 'white.png', 1, 1, lambda x, y: (255, 255, 255, 255))
    # Keep the upstream pointer but remove its desktop-only warning overlay.
    pointer = ET.Element('window')
    pointer_controls = tag(pointer, 'controls')
    for ident in range(1, 5):
        image_node = control(pointer_controls, 'image', 0, 0, 40, 40, ident, texture='mouse2.png')
    ET.ElementTree(pointer).write(root / '1080i/Pointer.xml', encoding='UTF-8', xml_declaration=True)
    fonts = ET.parse(root / '1080i/Font.xml')
    for fontset in fonts.getroot().findall('fontset'):
        for name, size in [('body', 23), ('small', 18), ('tiny', 15), ('title', 48), ('section', 27), ('brand', 29), ('clock', 38)]:
            node = tag(fontset, 'font')
            tag(node, 'name', 'pmn.' + name)
            tag(node, 'filename', 'MC360.ttf')
            tag(node, 'size', size)
    fonts.write(root / '1080i/Font.xml', encoding='UTF-8', xml_declaration=True)
    window = ET.Element('window', {'id': '0'})
    tag(window, 'defaultcontrol', '9000', always='true')
    tag(window, 'allowoverlay', 'no')
    controls = tag(window, 'controls')
    image(controls, 0, 0, 1920, 1080, 'pmn/night.png')
    other_rows = 'Control.HasFocus(9100) | Control.HasFocus(9300) | Control.HasFocus(9400)'
    # Show real selected artwork. Default hero follows the movie row.
    for cid in (9100, 9200, 9300, 9400):
        condition = f'Control.HasFocus({cid})' if cid != 9200 else f'![{other_rows}]'
        group = control(controls, 'group', 0, 0, 1920, 280, visible=condition)
        image(group, 0, 0, 1660, 280, f'$INFO[Container({cid}).ListItem.Art(fanart)]', aspectratio='scale')
        image(group, 0, 0, 1100, 280, 'pmn/shade.png')
        label(group, 194, 70, 800, 62, f'$INFO[Container({cid}).ListItem.Label]', 'pmn.title')
        label(group, 194, 132, 760, 26, f'$INFO[Container({cid}).ListItem.Genre]   $INFO[Container({cid}).ListItem.Year]', 'pmn.small', MUTED)
        control(group, 'textbox', 194, 165, 650, 62, label=f'$INFO[Container({cid}).ListItem.Plot]', font='pmn.small', textcolor=WHITE)
    label(controls, 28, 12, 145, 40, 'KODI', 'pmn.brand', 'FF4CA9D1')
    label(controls, 194, 10, 600, 35, 'PLEX', 'pmn.brand', GOLD)
    label(controls, 194, 42, 600, 24, 'D E  M E D I A  N O C H E', 'pmn.small', MUTED)
    label(controls, 195, 96, 830, 58, 'Tu cine. Tus series. Tu noche.', 'pmn.title', visible='!Library.HasContent(movies) + !Library.HasContent(tvshows)')
    label(controls, 195, 166, 870, 48, 'Conecta tu cuenta Plex desde Complementos para ver aquí tu biblioteca.', 'pmn.small', MUTED, visible='!Library.HasContent(movies) + !Library.HasContent(tvshows)')
    image(controls, 1630, 0, 290, 278, 'pmn/panel.png')
    label(controls, 1648, 10, 248, 25, '$INFO[System.Date]', 'pmn.small', MUTED, align='right')
    label(controls, 1648, 38, 248, 47, '$INFO[System.Time]', 'pmn.clock', align='right')
    label(controls, 1648, 94, 248, 24, '$INFO[Weather.Temperature]  $INFO[Weather.Conditions]', 'pmn.small', MUTED, visible='Weather.IsFetched')
    label(controls, 1648, 133, 248, 25, 'Novedades de tu biblioteca', 'pmn.small', GOLD)
    label(controls, 1648, 162, 248, 25, 'PlexKodiConnect', 'pmn.small')
    label(controls, 1648, 206, 248, 44, 'Buenas historias, siempre.', 'pmn.small', MUTED)
    play = button(controls, 9050, 194, 232, 185, 40, 'Reproducir', 'PlayMedia($INFO[Container(9200).ListItem.FileNameAndPath])', 9000, 9000, 9051, 9051, True)
    tag(play, 'enable', 'Library.HasContent(movies)')
    info = button(controls, 9051, 390, 232, 210, 40, 'Más información', ['SetFocus(9200)', 'Action(Info)'], 9000, 9000, 9050, 9050, True)
    tag(info, 'enable', 'Library.HasContent(movies)')
    nav = [('Favoritos', 'ActivateWindow(FavouritesBrowser)', 9100), ('Estrenos de series', 'SetFocus(9310)', 9300),
           ('Series', 'ActivateWindow(Videos,videodb://tvshows/titles/,return)', 9100),
           ('Cine', 'ActivateWindow(Videos,videodb://movies/titles/,return)', 9200),
           ('Estrenos de cine', 'SetFocus(9410)', 9400), ('TV', 'ActivateWindow(TVChannels)', 9200),
           ('Tráilers', 'PlayMedia($INFO[Container(9200).ListItem.Trailer])', 9200),
           ('Subtítulos', 'ActivateWindow(OSDSubtitleSettings)', 9400)]
    for i, (title, action, row) in enumerate(nav):
        x = 36 + i * 232
        if i in (1, 2, 3, 4, 5):
            cid = 9100 if i < 3 else 9200
            image(controls, x, 288, 222, 87, f'$INFO[Container({cid}).ListItem.Art(fanart)]', aspectratio='scale')
        navbutton = button(controls, 9000 + i, x, 288, 222, 87, title, action, 9890, row + 10,
                           9000 + (i - 1) % 8, 9000 + (i + 1) % 8, True)
        if i == 7:
            tag(navbutton, 'enable', 'Player.HasVideo')
        elif i == 6:
            tag(navbutton, 'enable', '!String.IsEmpty(Container(9200).ListItem.Trailer)')
    rows = [
        (9100, 392, 174, 'Series', 'videodb://tvshows/titles/', 'tvshows', ['Todas las series', 'Géneros', 'Años', 'Mis listas']),
        (9200, 575, 174, 'Cine', 'videodb://movies/titles/', 'movies', ['Películas', 'Añadidas recientemente', 'Géneros', 'Años', 'Mis listas']),
        (9300, 758, 118, 'Estrenos de series', 'videodb://recentlyaddedepisodes/', 'tvshows', ['Todos', 'Géneros', 'Años']),
        (9400, 885, 118, 'Estrenos de cine', 'videodb://recentlyaddedmovies/', 'movies', ['Todos', 'Géneros', 'Años'])]
    for index, (cid, y, height, title, path, media_type, filters) in enumerate(rows):
        image(controls, 30, y - 8, 1860, 3, 'pmn/line.png')
        label(controls, 42, y, 520, 32, title, 'pmn.section')
        label(controls, 1540, y, 345, 26, 'Añadidos recientemente', 'pmn.small', MUTED, align='right')
        panel_y = y + 38
        up = 9002 if index == 0 else rows[index - 1][0] + 10
        down = 9800 if index == 3 else rows[index + 1][0] + 10
        # Sidebar shortcuts use Kodi video database nodes, not OS-dependent paths.
        for j, text in enumerate(filters):
            if j * 22 + 22 > height - 36:
                break
            fid = cid + 10 + j
            kind = 'tvshows' if media_type == 'tvshows' else 'movies'
            target = path
            if text == 'Géneros':
                target = f'videodb://{kind}/genres/'
            elif text == 'Años':
                target = f'videodb://{kind}/years/'
            elif text == 'Añadidas recientemente':
                target = 'videodb://recentlyaddedmovies/'
            elif text == 'Mis listas':
                target = 'special://profile/playlists/video/'
            # Filter completed/airing needs server metadata; expose it through the library.
            button(controls, fid, 42, panel_y + j * 22, 220, 22, text,
                   f'ActivateWindow(Videos,{target},return)', up if j == 0 else fid - 1,
                   down if j == len(filters) - 1 or (j + 2) * 22 > height - 36 else fid + 1,
                   cid, cid, True)
        p = control(controls, 'panel', 292, panel_y, 1595, height - 35, cid,
                    orientation='horizontal', scrolltime='180', preloaditems='2',
                    onup=up, ondown=down, onleft=cid + 10, onright=cid)
        poster_h = height - 61
        poster_w = int(poster_h * 0.69)
        for focused in (False, True):
            layout = tag(p, 'focusedlayout' if focused else 'itemlayout', width=159, height=height - 35)
            image(layout, 2, 0, 153, poster_h + 4, 'pmn/focus.png' if focused else 'pmn/panel.png')
            image(layout, (157 - poster_w) // 2, 2, poster_w, poster_h,
                  '$INFO[ListItem.Art(poster)]', aspectratio='keep')
            label(layout, 4, poster_h + 4, 149, 22, '$INFO[ListItem.Label]', 'pmn.tiny', GOLD if focused else WHITE, align='center')
        tag(p, 'content', path, target='videos', sortby='dateadded', sortorder='descending', limit='20', browse='auto')
        label(controls, 300, panel_y + 15, 1470, 45, 'La biblioteca aparecerá cuando PlexKodiConnect termine de sincronizar.', 'pmn.body', MUTED,
              visible=f'!Library.HasContent({media_type})')
    image(controls, 30, 1016, 1860, 2, 'pmn/line.png')
    label(controls, 40, 1027, 265, 30, 'PLEX', 'pmn.brand', GOLD)
    label(controls, 40, 1056, 265, 20, 'DE MEDIA NOCHE  ·  by Pepe', 'pmn.tiny', MUTED)
    footer = [('Favoritos', 'ActivateWindow(FavouritesBrowser)'), ('Estrenos de series', 'SetFocus(9310)'),
              ('Series', 'ActivateWindow(Videos,videodb://tvshows/titles/,return)'), ('Cine', 'ActivateWindow(Videos,videodb://movies/titles/,return)'),
              ('Estrenos de cine', 'SetFocus(9410)'), ('TV', 'ActivateWindow(TVChannels)'),
              ('Ajustes', 'ActivateWindow(Settings)'), ('Apagar', 'ActivateWindow(ShutdownMenu)')]
    for i, (text, action) in enumerate(footer):
        footbutton = button(controls, 9800 + i, 320 + 195 * i, 1027, 188, 45, text, action,
                            9410, 9000, 9800 + (i - 1) % 8, 9800 + (i + 1) % 8, True)
        footbutton.find('font').text = 'pmn.tiny'
    # Always reachable even with all library panels empty.
    button(controls, 9890, 1640, 250, 250, 28, 'Complementos', 'ActivateWindow(AddonBrowser)', 9050, 9007, 9051, 9007, True)
    ET.indent(window)
    ET.ElementTree(window).write(root / '1080i/Home.xml', encoding='UTF-8', xml_declaration=True)
