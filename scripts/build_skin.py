"""Build the same Kodi skin locally and in Actions; no Android compilation."""
import argparse
import hashlib
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile
from photo_layout import generate

UPSTREAM_COMMIT = '27b7bd7f31b8f111a8adfb21f9bbdce835ac3e51'
ADDON_ID = 'skin.plexmedianoche'
LABELS = ['Inicio', 'Favoritos', 'Series estrenos', 'Series',
          'Novedades cine', 'TV', 'Ajustes', 'Apagar']


def build(source, destination, photo=False):
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
    if photo:
        addon.set('version', '0.5.0')
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
    if photo:
        shutil.copyfile(root / '1080i/Home.xml', root / 'resources/upstream-Home.xml')
        generate(root)
        home = ET.parse(root / '1080i/Home.xml').getroot()
        ids = [node.get('id') for node in home.findall('.//control[@id]')]
        if len(ids) != len(set(ids)):
            raise ValueError('Identificadores de controles duplicados')
        for node in home.findall('.//control'):
            for direction in ('onup', 'ondown', 'onleft', 'onright'):
                target = node.findtext(direction, '')
                if target.isdigit() and target not in ids:
                    raise ValueError(f'Navegación hacia control inexistente: {target}')
        defined_fonts = {node.text for node in ET.parse(root / '1080i/Font.xml').findall('.//font/name')}
        if any(node.text not in defined_fonts for node in home.findall('.//font')):
            raise ValueError('La portada usa una fuente no definida')
        for texture in home.findall('.//texture'):
            if texture.text and texture.text.startswith('pmn/') and not (root / 'media' / texture.text).is_file():
                raise ValueError(f'Textura ausente: {texture.text}')
    xml_files = list(root.rglob('*.xml'))
    for path in xml_files:
        ET.parse(path)
    archive = destination / 'PlexMediaNoche-skin-Omega.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as output:
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
    print(f'{len(xml_files)} XML válidos; dependencias conservadas; ZIP íntegro; diseño foto={photo}.')
    print(f'SHA256 {digest}')
    print('Pendiente: instalación, navegación, Plex compartido e IPTV en dispositivos reales.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--photo', action='store_true', help='Portada nativa basada en la foto aprobada')
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve(), args.photo)
