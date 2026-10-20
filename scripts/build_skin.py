"""Build the same Kodi skin locally and in Actions; no Android compilation."""
import argparse
import hashlib
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile

UPSTREAM_COMMIT = '27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51'
ADDON_ID = 'skin.plexmedianoche'
LABELS = ['Inicio', 'Favoritos', 'Series estrenos', 'Series',
          'Novedades cine', 'TV', 'Ajustes', 'Apagar']


def build(source, destination):
    project = Path(__file__).resolve().parents[1]
    original = ET.parse(source / 'addon.xml').getroot()
    if (original.get('id'), original.get('version')) != ('skin.arctic.zephyr.mod', '3.0.3'):
        raise ValueError('Base Arctic inesperada')
    destination.mkdir(parents=True, exist_ok=True)
    root = destination / ADDON_ID
    # Refuse to overwrite an earlier build or any installed Kodi profile.
    shutil.copytree(source, root, ignore=shutil.ignore_patterns('.git'))
    shutil.copyfile(project / 'skin/shortcuts/mainmenu.DATA.xml',
                    root / 'shortcuts/mainmenu.DATA.xml')
    tree = ET.parse(root / 'addon.xml')
    addon = tree.getroot()
    addon.set('id', ADDON_ID)
    addon.set('name', 'Plex Media Noche')
    tree.write(root / 'addon.xml', encoding='UTF-8', xml_declaration=True)
    # Preserve attribution, source URLs and dependency declarations in addon.xml.
    for path in root.rglob('*'):
        if not path.is_file() or path == root / 'addon.xml' or path.suffix.lower() not in {'.xml', '.po', '.txt', '.md', '.py'}:
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        if 'skin.arctic.zephyr.mod' in content:
            path.write_text(content.replace('skin.arctic.zephyr.mod', ADDON_ID), encoding='utf-8')
    menu = ET.parse(root / 'shortcuts/mainmenu.DATA.xml').getroot()
    if [x.findtext('label') for x in menu.findall('shortcut')] != LABELS:
        raise ValueError('Menú inesperado')
    for item in menu.findall('shortcut'):
        if not item.findtext('action'):
            raise ValueError('Acceso sin acción')
        icon = item.findtext('icon', '').removeprefix('special://skin/')
        if not (root / icon).is_file():
            raise ValueError(f'Icono ausente: {icon}')
    assert ET.tostring(original.find('requires')) == ET.tostring(addon.find('requires'))
    expected_home = (source / '1080i/Home.xml').read_text(encoding='utf-8').replace('skin.arctic.zephyr.mod', ADDON_ID)
    assert expected_home == (root / '1080i/Home.xml').read_text(encoding='utf-8')
    xml_files = list(root.rglob('*.xml'))
    for path in xml_files:
        ET.parse(path)
    archive = destination / 'PlexMediaNoche-skin-Omega.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for path in sorted(root.rglob('*')):
            if path.is_file():
                output.write(path, path.relative_to(destination).as_posix())
    with zipfile.ZipFile(archive) as output:
        if output.testzip() is not None:
            raise ValueError('ZIP dañado')
        if any(not name.startswith(ADDON_ID + '/') for name in output.namelist()):
            raise ValueError('Carpeta de instalación incorrecta')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(f'{digest}  {archive.name}\n', encoding='utf-8')
    print(f'{len(xml_files)} XML válidos; dependencias y Home originales conservados; ZIP íntegro.')
    print(f'SHA256 {digest}')
    print('Pendiente: instalación, navegación, Plex compartido e IPTV en dispositivos reales.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve())
