"""Customize the pinned Arctic base without replacing its native Home window."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET


OLD_ID = 'skin.arctic.zephyr.mod'
NEW_ID = 'skin.plexmedianoche'
LABELS = ['Inicio', 'Favoritos', 'Series estrenos', 'Series',
          'Cine', 'Novedades cine', 'TV', 'Ajustes', 'Apagar']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            'widget_initial_limit': 12, 'runtime_tested': False}


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
