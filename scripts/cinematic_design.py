"""Build the cinematic windows using the existing series screen as a template.

Keep native Home.xml and video-info control IDs. All content comes from local
Kodi playlists; no Plex account, network requests, or library mutation here.
"""
import copy
import xml.etree.ElementTree as ET


PLAYLISTS = 'special://skin/extras/playlists/medianoche/'
ICONS = {
    'Inicio': 'home.png', 'Series': 'tv.png', 'Cine': 'film.png',
    'Series estrenos': 'recentlyadded.png', 'Novedades cine': 'recent.png',
    'TV': 'livetv.png', 'Favoritos': 'favourites.png', 'Diseño': 'paintbrush.png',
    'Ajustes': 'configure.png', 'Apagar': 'power.png',
}
LIBRARIES = {
    1190: ('Series estrenos', [
        ('Series completas', 'series-completas.xsp'),
        ('Episodios recientes', 'episodios-recientes.xsp'),
    ]),
    1192: ('Series', [
        ('Todas las series', 'series.xsp'),
        ('Finalizadas', 'series-completas.xsp'),
        ('Episodios recientes', 'episodios-recientes.xsp'),
    ]),
    1193: ('Cine', [
        ('Todas las películas', 'cine.xsp'),
        ('Añadidas recientemente', 'cine-reciente.xsp'),
        ('Sin ver', 'cine-sin-ver.xsp'),
    ]),
    1194: ('Novedades cine', [
        ('Últimas incorporaciones', 'cine-reciente.xsp'),
        ('Pendientes de ver', 'cine-sin-ver.xsp'),
    ]),
}
ROWS = [
    (501, 'Series', 'Tu colección', 'series.xsp', 1192),
    (502, 'Cine', 'Tu colección', 'cine.xsp', 1193),
    (503, 'Series estrenos', 'Finalizadas · recién añadidas', 'series-completas.xsp', 1190),
    (504, 'Novedades cine', 'Últimas incorporaciones', 'cine-reciente.xsp', 1194),
]


def add(parent, tag, text=None, **attributes):
    node = ET.SubElement(parent, tag, attributes)
    if text is not None:
        node.text = str(text)
    return node


def control(parent, kind, x, y, width, height, identity=None):
    attributes = {'type': kind}
    if identity is not None:
        attributes['id'] = str(identity)
    node = add(parent, 'control', **attributes)
    for tag, value in (('left', x), ('top', y), ('width', width), ('height', height)):
        add(node, tag, value)
    return node


def image(parent, x, y, width, height, texture, color=None):
    node = control(parent, 'image', x, y, width, height)
    add(node, 'texture', texture, **({'colordiffuse': color} if color else {}))
    return node


def label(parent, x, y, width, height, value, font='Tiny', color='FFFFFFFF'):
    node = control(parent, 'label', x, y, width, height)
    for tag, text in (('font', font), ('textcolor', color), ('label', value), ('aligny', 'center')):
        add(node, tag, text)
    return node


def button(parent, identity, x, y, width, height, value, action):
    node = control(parent, 'button', x, y, width, height, identity)
    for tag, text in (
        ('font', 'Tiny'), ('textcolor', 'FFFFFFFF'), ('focusedcolor', 'FF101820'),
        ('label', value), ('align', 'left'), ('textoffsetx', '20'),
    ):
        add(node, tag, text)
    add(node, 'texturenofocus', 'common/white.png', colordiffuse='FF142130')
    add(node, 'texturefocus', 'common/white.png', colordiffuse='FFE5BC70')
    add(node, 'onclick', action)
    if value in ICONS:
        node.find('textoffsetx').text = '54'
        # Icons are decoration; the button retains its text, ID and actions.
        for focused, color in ((False, 'FFE5BC70'), (True, 'FF101820')):
            icon = image(parent, x + 16, y + (height - 24) // 2, 24, 24,
                         'special://skin/extras/icons/' + ICONS[value], color)
            add(icon, 'visible', ('' if focused else '!') + f'Control.HasFocus({identity})')
    return node


def state_badges(layout, compact=False):
    conditions = (
        ('ListItem.IsResumable', 'play2.png', 'Continuar'),
        ('String.IsEqual(ListItem.Overlay,OverlayWatched.png) + !ListItem.IsResumable',
         'eye.png', 'Visto'),
    )
    for condition, icon_name, text in conditions:
        group = add(layout, 'control', type='group')
        add(group, 'visible', condition)
        if compact:
            image(group, 66, 6, 24, 24, 'common/white.png', 'E6080F18')
            image(group, 70, 10, 16, 16,
                  'special://skin/extras/icons/' + icon_name, 'FFE5BC70')
        else:
            image(group, 31, 296, 218, 36, 'common/white.png', 'E6080F18')
            image(group, 41, 304, 20, 20,
                  'special://skin/extras/icons/' + icon_name, 'FFE5BC70')
            label(group, 73, 296, 160, 36, text, 'Small20', 'FFFFFFFF')


def save(path, root):
    ET.indent(root, space='    ')
    ET.ElementTree(root).write(path, encoding='UTF-8', xml_declaration=True)


def footer(controls, selected, upper):
    entries = [
        ('Inicio', 'ReplaceWindow(1191)', 1191),
        ('Series', 'ReplaceWindow(1192)', 1192),
        ('Cine', 'ReplaceWindow(1193)', 1193),
        ('TV', 'ActivateWindow(Tvchannels)', None),
        ('Favoritos', 'ActivateWindow(Favourites)', None),
        ('Diseño', 'ActivateWindow(1195)', None),
        ('Ajustes', 'ActivateWindow(Settings)', None),
        ('Apagar', 'ActivateWindow(shutdownmenu)', None),
    ]
    for index, (title, action, window_id) in enumerate(entries):
        node = button(controls, 201 + index, 70 + index * 224, 1030, 210, 40, title, action)
        add(node, 'onleft', 201 + (index - 1) % len(entries))
        add(node, 'onright', 201 + (index + 1) % len(entries))
        add(node, 'onup', upper)
        add(node, 'onback', 'ReplaceWindow(1191)')
        if window_id == selected:
            image(controls, 90 + index * 224, 1073, 170, 2, 'common/white.png', 'FFE5BC70')


def item_actions(container, identity):
    for node in list(container.findall('onclick')):
        container.remove(node)
    prefix = f'Container({identity}).ListItem'
    add(container, 'onclick',
        f'ActivateWindow(Videos,videodb://tvshows/titles/$INFO[{prefix}.DBID]/,return)',
        condition=f'String.IsEqual({prefix}.DBType,tvshow)')
    add(container, 'onclick',
        f'RunScript(special://skin/extras/medianoche_info.py,$INFO[{prefix}.DBType],$INFO[{prefix}.DBID])',
        condition=f'[String.IsEqual({prefix}.DBType,movie) | String.IsEqual({prefix}.DBType,episode)] + !String.IsEmpty({prefix}.DBID)')


def build_library(template, window_id, title, categories):
    root = copy.deepcopy(template)
    root.set('id', str(window_id))
    controls = root.find('controls')
    for node in root.findall('onload'):
        if (node.text or '').startswith('SetProperty(MediaNoche.SeriesPlaylist,'):
            node.text = f'SetProperty(MediaNoche.SeriesPlaylist,{PLAYLISTS}{categories[0][1]})'
    for node in controls.findall("control[@type='label']/label"):
        if node.text == 'Series estrenos':
            node.text = title
    original_button = copy.deepcopy(controls.find("control[@id='101']"))
    for node in list(controls):
        visible = node.findtext('visible', '')
        if node.get('id') in ('101', '102') or 'String.IsEqual(Window.Property(MediaNoche.SeriesCategory),' in visible:
            controls.remove(node)
        elif node.findtext('top') == '1030':
            controls.remove(node)
    for index, (category, playlist) in enumerate(categories):
        identity = 101 + index
        node = copy.deepcopy(original_button)
        node.set('id', str(identity))
        node.find('top').text = str(608 + 76 * index)
        node.find('height').text = '70'
        node.find('label').text = category
        for old in list(node.findall('onfocus')):
            node.remove(old)
        add(node, 'onfocus', f'SetProperty(MediaNoche.SeriesPlaylist,{PLAYLISTS}{playlist})')
        add(node, 'onfocus', f'SetProperty(MediaNoche.SeriesCategory,{identity})')
        node.find('onclick').text = f'ActivateWindow(Videos,{PLAYLISTS}{playlist},return)'
        node.find('onup').text = str(101 + (index - 1) % len(categories))
        node.find('ondown').text = str(identity + 1 if index + 1 < len(categories) else 201)
        add(node, 'onback', 'ReplaceWindow(1191)')
        controls.append(node)
        marker = image(controls, 56, 608 + 76 * index, 4, 70, 'common/white.png', 'FFE5BC70')
        add(marker, 'visible', f'String.IsEqual(Window.Property(MediaNoche.SeriesCategory),{identity})')
        header = label(controls, 470, 548, 1050, 44, category, 'Small')
        add(header, 'visible', f'String.IsEqual(Window.Property(MediaNoche.SeriesCategory),{identity})')
    listing = controls.find("control[@id='50']")
    for layout in (listing.find('itemlayout'), listing.find('focusedlayout')):
        for texture in layout.findall("control[@type='image']/texture"):
            if texture.text and 'ListItem.Art(poster)' in texture.text:
                texture.text = '$VAR[MediaNoche.Poster]'
        state_badges(layout)
    for texture in controls.findall("control[@type='image']/texture"):
        if texture.text == '$INFO[Container(50).ListItem.Art(fanart)]':
            texture.text = '$VAR[MediaNoche.LibraryArt]'
    clearlogo = image(controls, 1390, 365, 430, 100,
                      '$INFO[Container(50).ListItem.Art(clearlogo)]')
    add(clearlogo, 'aspectratio', 'keep')
    add(clearlogo, 'visible', '!String.IsEmpty(Container(50).ListItem.Art(clearlogo))')
    add(listing, 'preloaditems', '1')
    item_actions(listing, 50)
    footer(controls, window_id, 50)
    return root


def home_variables(root):
    poster = add(root, 'variable', name='MediaNoche.Poster')
    for field in ('Art(poster)', 'Art(tvshow.poster)', 'Art(thumb)'):
        add(poster, 'value', f'$INFO[ListItem.{field}]',
            condition=f'!String.IsEmpty(ListItem.{field})')
    add(poster, 'value', 'DefaultVideo.png')
    for name, identity in [('LibraryArt', 50)] + [(f'Art{row[0]}', row[0]) for row in ROWS]:
        variable = add(root, 'variable', name='MediaNoche.' + name)
        for field in ('Art(fanart)', 'Art(tvshow.fanart)'):
            add(variable, 'value', f'$INFO[Container({identity}).ListItem.{field}]',
                condition=f'!String.IsEmpty(Container({identity}).ListItem.{field})')
        add(variable, 'value', '')
    fields = {
        'Title': 'Label', 'Plot': 'Plot', 'Art': 'Art(fanart)',
        'Year': 'Year', 'Genre': 'Genre',
    }
    for name, field in fields.items():
        variable = add(root, 'variable', name='MediaNoche.Home' + name)
        for identity, *_ in ROWS:
            value = (f'$VAR[MediaNoche.Art{identity}]' if name == 'Art'
                     else f'$INFO[Container({identity}).ListItem.{field}]')
            add(variable, 'value', value,
                condition=(f'String.IsEqual(Window.Property(MediaNoche.ActiveList),{identity})'
                           f' + !String.IsEmpty(Container({identity}).ListItem.Label)'))
        add(variable, 'value', 'Buenas historias, siempre.' if name == 'Title' else '')
    metadata = add(root, 'variable', name='MediaNoche.HomeMetadata')
    for identity, *_ in ROWS:
        add(metadata, 'value',
            f'$INFO[Container({identity}).ListItem.Year]$INFO[Container({identity}).ListItem.Genre,  ·  ]',
            condition=f'String.IsEqual(Window.Property(MediaNoche.ActiveList),{identity})')
    add(metadata, 'value', '')


def build_home():
    root = ET.Element('window', {'type': 'window', 'id': '1191'})
    add(root, 'defaultcontrol', '301', always='true')
    add(root, 'onload', 'SetProperty(MediaNoche.ActiveList,501)')
    add(root, 'onunload', 'ClearProperty(MediaNoche.ActiveList)')
    controls = add(root, 'controls')
    image(controls, 0, 0, 1920, 1080, 'common/white.png', 'FF080F18')
    node = image(controls, 590, 0, 1330, 338, '$VAR[MediaNoche.HomeArt]')
    add(node, 'aspectratio', 'scale')
    add(node, 'fadetime', '350')
    image(controls, 0, 0, 970, 338, 'common/white.png', 'E6080F18')
    image(controls, 0, 210, 1920, 150, 'common/shadowbottom.png', 'FF080F18')
    image(controls, 0, 0, 1920, 96, 'common/white.png', 'D9080F18')
    label(controls, 70, 16, 150, 42, 'PLEX', 'MediumBold', 'FFE5BC70')
    label(controls, 70, 58, 280, 27, 'DE MEDIA NOCHE', 'Small20', 'FFC2CDD9')
    label(controls, 390, 27, 950, 50, 'Cine. Series. Tu momento.', 'Small')
    node = label(controls, 1490, 16, 360, 42, '$INFO[System.Time]', 'SmallBold')
    add(node, 'align', 'right')
    node = label(controls, 1320, 59, 530, 30, '$INFO[System.Date]', 'Mini', 'FFC2CDD9')
    add(node, 'align', 'right')
    node = label(controls, 70, 113, 900, 75, '$VAR[MediaNoche.HomeTitle]', 'Large')
    add(node, 'scroll', 'true')
    label(controls, 70, 191, 900, 38, '$VAR[MediaNoche.HomeMetadata]',
          'Tiny', 'FFC2CDD9')
    node = control(controls, 'textbox', 70, 238, 820, 76)
    add(node, 'font', 'Tiny')
    add(node, 'textcolor', 'FFE1E7EE')
    add(node, 'label', '$VAR[MediaNoche.HomePlot]')
    nav = [
        ('Favoritos', 'ActivateWindow(Favourites)'),
        ('Series estrenos', 'ReplaceWindow(1190)'),
        ('Series', 'ReplaceWindow(1192)'), ('Cine', 'ReplaceWindow(1193)'),
        ('Novedades cine', 'ReplaceWindow(1194)'), ('TV', 'ActivateWindow(Tvchannels)'),
        ('Ajustes', 'ActivateWindow(Settings)'),
    ]
    for index, (name, action) in enumerate(nav):
        node = button(controls, 301 + index, 70 + index * 254, 350, 238, 68, name, action)
        add(node, 'onleft', 301 + (index - 1) % len(nav))
        add(node, 'onright', 301 + (index + 1) % len(nav))
        add(node, 'ondown', '501')
        add(node, 'onup', '504')
        add(node, 'onback', 'SetFocus(301)')
    image(controls, 70, 440, 1780, 1, 'common/white.png', '8878B8E8')
    for index, (identity, name, description, playlist, target) in enumerate(ROWS):
        top = 468 + index * 134
        node = button(controls, 601 + index, 70, top + 16, 250, 54, name,
                      f'ReplaceWindow({target})')
        add(node, 'onright', identity)
        add(node, 'onup', 601 + index - 1 if index else 301)
        add(node, 'ondown', 601 + index + 1 if index < 3 else 201)
        add(node, 'onback', 'SetFocus(301)')
        label(controls, 90, top + 77, 230, 40, description, 'Small20', 'FF91A5BB')
        listing = control(controls, 'list', 340, top, 1512, 120, identity)
        add(listing, 'orientation', 'horizontal')
        add(listing, 'preloaditems', '1')
        add(listing, 'onfocus', f'SetProperty(MediaNoche.ActiveList,{identity})')
        add(listing, 'onleft', 601 + index, condition=f'Container({identity}).Position(0)')
        add(listing, 'onup', identity - 1 if index else 301)
        add(listing, 'ondown', identity + 1 if index < 3 else 201)
        add(listing, 'onback', 'SetFocus(301)')
        item_actions(listing, identity)
        for tag in ('itemlayout', 'focusedlayout'):
            layout = add(listing, tag, width='112', height='120')
            if tag == 'focusedlayout':
                image(layout, 15, 0, 82, 120, 'common/white.png', 'FFE5BC70')
            artwork = image(layout, 18, 3, 76, 114, '$VAR[MediaNoche.Poster]')
            artwork.find('texture').set('fallback', 'DefaultVideo.png')
            add(artwork, 'aspectratio', 'keep')
            state_badges(layout, compact=True)
        add(listing, 'content', PLAYLISTS + playlist, target='videos', limit='13')
        empty = label(controls, 360, top + 35, 1400, 50, 'Todavía no hay títulos en esta fila.',
                      'Tiny', 'FF91A5BB')
        add(empty, 'visible', f'!Container({identity}).IsUpdating + Integer.IsEqual(Container({identity}).NumItems,0)')
    image(controls, 70, 1014, 1780, 1, 'common/white.png', '4478B8E8')
    footer(controls, 1191, 504)
    return root


def build_preferences():
    root = ET.Element('window', {'type': 'window', 'id': '1195'})
    add(root, 'defaultcontrol', '101', always='true')
    controls = add(root, 'controls')
    image(controls, 0, 0, 1920, 1080, 'common/white.png', 'FF080F18')
    label(controls, 110, 90, 1600, 90, 'Tu forma de ver la noche', 'Large', 'FFE5BC70')
    label(controls, 110, 200, 1600, 60, 'Elige el inicio que prefieres.', 'Small', 'FFC2CDD9')
    entries = [
        ('Inicio cinematográfico', ['Skin.Reset(medianoche.nativehome)', 'ReplaceWindow(1191)']),
        ('Inicio clásico', ['Skin.SetBool(medianoche.nativehome)', 'ReplaceWindow(Home)']),
        ('Ajustes del skin', ['ActivateWindow(SkinSettings)']),
    ]
    for index, (title, actions) in enumerate(entries):
        node = button(controls, 101 + index, 110, 340 + index * 110, 760, 86, title, actions[0])
        for action in actions[1:]:
            add(node, 'onclick', action)
        add(node, 'onup', 101 + (index - 1) % len(entries))
        add(node, 'ondown', 101 + (index + 1) % len(entries))
        add(node, 'onback', 'ReplaceWindow(1191)')
    return root


def build_design(base, project):
    directory = base / '1080i'
    template = ET.parse(project / 'skin/1080i/Custom_SeriesEstrenos_1190.xml').getroot()
    for window_id, (title, categories) in LIBRARIES.items():
        filename = ('Custom_SeriesEstrenos_1190.xml' if window_id == 1190
                    else f'Custom_MediaNoche_{window_id}.xml')
        save(directory / filename, build_library(template, window_id, title, categories))
    save(directory / 'Custom_MediaNoche_1191.xml', build_home())
    save(directory / 'Custom_MediaNoche_1195.xml', build_preferences())
    variables = ET.Element('includes')
    home_variables(variables)
    save(directory / 'Includes_MediaNoche.xml', variables)
    includes_path = directory / 'Includes.xml'
    includes = ET.parse(includes_path)
    add(includes.getroot(), 'include', file='Includes_MediaNoche.xml')
    for name in ('defaultcontroltrue', 'defaultcontrolfalse'):
        definition = includes.getroot().find(f"include[@name='{name}']")
        if definition is None:
            raise ValueError('Native Home default-control include changed')
        add(definition, 'onload', 'ReplaceWindow(1191)',
            condition='Window.IsActive(Home) + !Skin.HasSetting(medianoche.nativehome)')
    save(includes_path, includes.getroot())
    # Background only: leave video-info native controls and actions untouched.
    dialog_path = directory / 'DialogVideoInfo.xml'
    dialog = ET.parse(dialog_path)
    controls = dialog.getroot().find('controls')
    background = ET.Element('controls')
    image(background, 0, 0, 1920, 1080, 'common/white.png', 'FF080F18')
    art = image(background, 570, 0, 1350, 1080, '$INFO[ListItem.Art(fanart)]', '557F8FA8')
    add(art, 'aspectratio', 'scale')
    image(background, 0, 0, 550, 1080, 'common/white.png', 'F0080F18')
    for index, node in enumerate(background):
        controls.insert(index, node)
    save(dialog_path, dialog.getroot())
    return {'cinematic_windows': [1190, 1191, 1192, 1193, 1194, 1195],
            'home_rows': 4, 'home_items_per_row': 13,
            'native_home_preserved': True, 'classic_home_available': True,
            'runtime_tested': False}
