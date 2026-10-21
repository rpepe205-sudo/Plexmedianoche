"""Customize the pinned Arctic base without replacing its native Home window."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

from cinematic_design import build_design


OLD_ID = 'skin.arctic.zephyr.mod'
NEW_ID = 'skin.plexmedianoche'
CUSTOM_VERSION = '3.0.4~beta3'
LABELS = ['Inicio', 'Favoritos', 'Series estrenos', 'Series',
          'Cine', 'Novedades cine', 'TV', 'Ajustes', 'Apagar']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_video_info(base):
    """Change only the native video-info navigation; retain Kodi control IDs."""
    path = base / '1080i/Includes.xml'
    tree = ET.parse(path)
    root = tree.getroot()
    navigation = root.find("include[@name='DialogVideoInfoNavigation']")
    if navigation is None:
        raise ValueError('Missing upstream video-info navigation')
    bar = navigation.find("control[@id='9000']")
    labels = {
        '8': '$VAR[MediaNochePlayLabel]',
        '9078': 'Temporadas y episodios',
        '9201': '$VAR[MediaNochePauseLabel]',
        '9077': 'Reproducir / Continuar', '9001': 'Información',
        '1224': 'Tráiler', '1223': 'Tráiler', '49': 'Preestreno',
        '7': 'Tu valoración', '1236': 'Extras', '9013': 'Wikipedia',
        '9002': 'Similares', '9003': 'Del mismo estudio',
        '9006': 'Del mismo director', '9015': 'Colección',
        '9004': 'YouTube', '9005': 'Imágenes',
        '9011': 'Lista de Trakt', '9010': 'Gestionar',
    }
    controls = bar.findall('control')
    if {c.get('id') for c in controls} != set(labels):
        raise ValueError('Upstream video-info buttons changed')
    textures = root.find("include[@name='buttontextures']/definition")
    if textures is None:
        raise ValueError('Missing upstream button textures')
    import copy
    for control in controls:
        for include in list(control.findall('include')):
            if include.text == 'buttondimensions':
                control.remove(include)
            elif include.get('content') == 'buttontextures':
                icon = include.find("param[@name='icon']").get('value')
                control.remove(include)
                for original in textures:
                    if original.tag in ('font', 'textcolor'):
                        continue
                    node = copy.deepcopy(original)
                    if node.text:
                        node.text = node.text.replace('$PARAM[icon]', icon)
                    for key, value in node.attrib.items():
                        node.set(key, value.replace('$PARAM[color]', 'Dark4'))
                    control.append(node)
        values = {
            'width': '390', 'height': '88', 'radioposx': '16',
            'radioposy': '20', 'radiowidth': '48', 'radioheight': '48',
            'font': 'Tiny', 'textcolor': 'FFFFFFFF',
            'focusedcolor': 'FF101820', 'disabledcolor': 'FF999999',
            'textoffsetx': '78', 'align': 'left', 'aligny': 'center',
            'label': labels[control.get('id')],
        }
        for tag, value in values.items():
            node = control.find(tag)
            if node is None:
                node = ET.SubElement(control, tag)
            node.text = value
        for node in control.findall('texturefocus'):
            node.set('colordiffuse', 'FFE5BC70')
        for tag in ('textureradioonfocus', 'textureradioofffocus'):
            control.find(tag).set('colordiffuse', 'FF101820')
        if control.get('id') == '9001':
            # The local details panel needs no third-party metadata service.
            for node in list(control.findall('onclick')):
                control.remove(node)
            ET.SubElement(control, 'onclick').text = 'SetProperty(moviecontent,1)'
        if control.get('id') in ('1223', '1224'):
            # Do not offer search helpers as if they were a known trailer source.
            for node in list(control.findall('onclick')):
                control.remove(node)
            for node in list(control.findall('visible')):
                control.remove(node)
            windowed = control.get('id') == '1223'
            condition = 'Skin.HasSetting(PlayTrailerWindowed)'
            if not windowed:
                condition = '!' + condition
            ET.SubElement(control, 'visible').text = (
                condition + ' + !String.IsEmpty(ListItem.Trailer)'
                ' + !Skin.HasSetting(hidebutton.video.trailer)')
            ET.SubElement(control, 'onclick').text = (
                'PlayMedia($INFO[ListItem.Trailer],1)' if windowed else 'SendClick(11)')
    # Static labels live on each button, independent of Control.HasFocus.
    for name, condition, selected, fallback in (
        ('MediaNochePlayLabel', 'ListItem.IsResumable', 'Continuar', 'Reproducir'),
        ('MediaNochePauseLabel', 'Player.Playing', 'Pausar', 'Continuar'),
    ):
        variable = ET.SubElement(root, 'variable', {'name': name})
        ET.SubElement(variable, 'value', {'condition': condition}).text = selected
        ET.SubElement(variable, 'value').text = fallback
    favourite = copy.deepcopy(bar.find("control[@id='9001']"))
    favourite.set('id', '9876')
    for tag in ('onclick', 'onfocus', 'visible'):
        for node in list(favourite.findall(tag)):
            favourite.remove(node)
    favourite.find('label').text = '$VAR[MediaNocheFavouriteLabel]'
    for tag in ('textureradioonfocus', 'textureradioonnofocus',
                'textureradioofffocus', 'textureradiooffnofocus',
                'textureradiooffdisabled', 'textureradioondisabled'):
        favourite.find(tag).text = 'special://skin/extras/icons/favourites.png'
    supported = ('[String.IsEqual(ListItem.DBType,movie) | '
                 'String.IsEqual(ListItem.DBType,tvshow)] + !String.IsEmpty(ListItem.DBID)')
    script = ('RunScript(special://skin/extras/medianoche_favourites.py,'
              '$INFO[ListItem.DBType],$INFO[ListItem.DBID],')
    ET.SubElement(favourite, 'visible').text = supported
    ET.SubElement(favourite, 'enable').text = (
        'String.IsEqual(Window(home).Property(MediaNoche.FavouriteState),added) | '
        'String.IsEqual(Window(home).Property(MediaNoche.FavouriteState),absent)')
    ET.SubElement(favourite, 'onclick').text = script + 'toggle)'
    bar.insert(list(bar).index(bar.find("control[@id='9001']")) + 1, favourite)
    variable = ET.SubElement(root, 'variable', {'name': 'MediaNocheFavouriteLabel'})
    ET.SubElement(variable, 'value', {
        'condition': 'String.IsEqual(Window(home).Property(MediaNoche.FavouriteState),added)',
    }).text = 'Quitar de favoritos'
    ET.SubElement(variable, 'value').text = 'Añadir a favoritos'
    tree.write(path, encoding='UTF-8', xml_declaration=True)
    dialog_path = base / '1080i/DialogVideoInfo.xml'
    dialog = ET.parse(dialog_path)
    ET.SubElement(dialog.getroot(), 'onload').text = 'ClearProperty(MediaNoche.FavouriteState,home)'
    ET.SubElement(dialog.getroot(), 'onload', {'condition': supported}).text = script + 'refresh)'
    dialog.write(dialog_path, encoding='UTF-8', xml_declaration=True)
    preview_path = base / '1080i/Includes_DialogVideoInfo.xml'
    preview = ET.parse(preview_path)
    button = preview.getroot().find(".//control[@id='7011']")
    if button is None:
        raise ValueError('Missing upstream trailer preview control')
    for node in list(button.findall('onclick')):
        button.remove(node)
    ET.SubElement(button, 'onclick', {
        'condition': '!String.IsEmpty(ListItem.Trailer)',
    }).text = 'PlayMedia($INFO[ListItem.Trailer],1)'
    preview.write(preview_path, encoding='UTF-8', xml_declaration=True)
    return {'buttons_with_persistent_labels': len(controls) + 1,
            'trailer_requires_listitem_source': True,
            'favorites_button_implemented': True}


def prepare(base, project):
    addon_path = base / 'addon.xml'
    addon = ET.parse(addon_path)
    root = addon.getroot()
    if root.get('id') != OLD_ID or root.get('version') != '3.0.3':
        raise ValueError('Expected original Arctic Reloaded 3.0.3')
    home_path = base / '1080i/Home.xml'
    home_hash = digest(home_path)
    expected_home = home_path.read_text().replace(OLD_ID, NEW_ID)
    dependencies = [dict(node.attrib) for node in root.findall('requires/import')]
    provenance = root.findtext("extension[@point='xbmc.addon.metadata']/source")
    root.set('id', NEW_ID)
    root.set('name', 'Plex Media Noche')
    root.set('version', CUSTOM_VERSION)
    addon.write(addon_path, encoding='UTF-8', xml_declaration=True)
    for path in base.rglob('*'):
        if not path.is_file() or path == addon_path:
            continue
        try:
            text = path.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            continue
        if OLD_ID in text:
            # Keep upstream source/attribution links pointing to the actual project.
            updated = re.sub(r'https?://[^\s<>"\']+',
                             lambda m: m[0].replace(OLD_ID, '__UPSTREAM_ID__'), text)
            updated = updated.replace(OLD_ID, NEW_ID).replace('__UPSTREAM_ID__', OLD_ID)
            path.write_text(updated, encoding='utf-8')
    shutil.copyfile(project / 'skin/shortcuts/mainmenu.DATA.xml',
                    base / 'shortcuts/mainmenu.DATA.xml')
    menu = ET.parse(base / 'shortcuts/mainmenu.DATA.xml').getroot()
    if [node.findtext('label') for node in menu.findall('shortcut')] != LABELS:
        raise ValueError('Unexpected main menu')
    ids = []
    for node in menu.findall('shortcut'):
        ids.append(node.findtext('defaultID'))
        icon = node.findtext('icon', '')
        if not icon.startswith('special://skin/'):
            raise ValueError(f'Non-portable menu icon: {icon}')
        if not (base / icon.removeprefix('special://skin/')).is_file():
            raise ValueError(f'Missing menu icon: {icon}')
    if not all(ids) or len(set(ids)) != len(ids):
        raise ValueError('Missing or duplicate menu IDs')


    # Portable library entry points; PKC populates Kodi's own video database.
    playlist_source = project / 'skin/playlists'
    playlist_target = base / 'extras/playlists/medianoche'
    playlist_target.mkdir(parents=True, exist_ok=True)
    for source in sorted(playlist_source.glob('*.xsp')):
        ET.parse(source)
        shutil.copyfile(source, playlist_target / source.name)

    palette_path = base / 'colors/defaults.xml'
    palette = ET.parse(palette_path)
    colors = {node.get('name'): node for node in palette.getroot().findall('color')}
    overrides = json.loads((project / 'skin/colors/media-noche.json').read_text())
    for name, value in overrides.items():
        if name not in colors or not re.fullmatch('[A-Fa-f0-9]{8}', value):
            raise ValueError(f'Invalid or unknown color: {name}={value}')
        colors[name].text = value
    shutil.copyfile(palette_path, base / 'colors/Arctic Original.xml')
    palette.write(palette_path, encoding='UTF-8', xml_declaration=True)
    palette.write(base / 'colors/Media Noche.xml', encoding='UTF-8', xml_declaration=True)

    startup_path = base / '1080i/Startup.xml'
    startup = ET.parse(startup_path)
    window = startup.getroot()
    first = "!Skin.HasSetting(startup.init)"
    replacements = {
        'Skin.SetString(WidgetLimit,25)': 'Skin.SetString(WidgetLimit,12)',
        'Skin.SetString(HubLimit,25)': 'Skin.SetString(HubLimit,12)',
        'Skin.SetString(squarecolor2.name,ff00b36c)': 'Skin.SetString(squarecolor2.name,FF78B8E8)',
        'Skin.SetString(focuscolorotherbar.name,ff00b36c)': 'Skin.SetString(focuscolorotherbar.name,FFE5BC70)',
        'Skin.SetString(kodilogocolor.name,ff0385B5)': 'Skin.SetString(kodilogocolor.name,FFE5BC70)',
        'Skin.SetString(kodilogocolorgradient.name,ff00b36c)': 'Skin.SetString(kodilogocolorgradient.name,FF78B8E8)',
    }
    found = set()
    for node in list(window.findall('onload')):
        if node.get('condition') != first:
            continue
        if node.text in ('Skin.SetBool(show.reflections)',
                         'Skin.SetBool(home.widgets.show.reflections)'):
            node.text = node.text.replace('Skin.SetBool(', 'Skin.Reset(')
        if node.text in replacements:
            found.add(node.text)
            node.text = replacements[node.text]
    if found != set(replacements):
        raise ValueError(f'Upstream startup settings changed: {set(replacements) - found}')
    startup.write(startup_path, encoding='UTF-8', xml_declaration=True)
    (base / 'extras').mkdir(exist_ok=True)
    shutil.copyfile(project / 'skin/extras/medianoche_favourites.py',
                    base / 'extras/medianoche_favourites.py')
    shutil.copyfile(project / 'skin/extras/medianoche_info.py',
                    base / 'extras/medianoche_info.py')
    video_info = prepare_video_info(base)
    design = build_design(base, project)
    final = ET.parse(addon_path).getroot()
    if [dict(node.attrib) for node in final.findall('requires/import')] != dependencies:
        raise ValueError('Dependency declarations changed')
    if final.findtext("extension[@point='xbmc.addon.metadata']/source") != provenance:
        raise ValueError('Upstream provenance changed')
    if home_path.read_text() != expected_home:
        raise ValueError('Native Home window changed unexpectedly')
    count = 0
    for path in base.rglob('*.xml'):
        ET.parse(path)
        count += 1
    return {'addon_id': NEW_ID, 'version': final.get('version'),
            'dependencies': dependencies, 'upstream_home_sha256': home_hash,
            'packaged_home_sha256': digest(home_path),
            'validated_xml_files': count, 'menu': LABELS,
            'widget_initial_limit': 12, 'video_info': video_info, 'design': design,
            'runtime_tested': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base', type=Path)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.base, args.project)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'{NEW_ID}: palette, lightweight defaults, menu and {result["validated_xml_files"]} XML files checked')

