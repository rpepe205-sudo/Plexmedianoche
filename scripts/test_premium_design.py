"""Comprobaciones estáticas del diseño premium sobre un skin ya preparado.

Uso: python3 scripts/test_premium_design.py <carpeta del skin preparado>
No sustituye a la prueba en Kodi: revisa ids, saltos del mando, fuentes,
texturas, límites de pantalla y acciones de la barra inferior.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

WINDOWS = {1190: 'Custom_SeriesEstrenos_1190.xml', 1191: 'Custom_MediaNoche_1191.xml',
           1192: 'Custom_MediaNoche_1192.xml', 1193: 'Custom_MediaNoche_1193.xml',
           1194: 'Custom_MediaNoche_1194.xml', 1195: 'Custom_MediaNoche_1195.xml',
           1196: 'Custom_MediaNoche_1196.xml', 1197: 'Custom_MediaNoche_1197.xml'}


def check(base):
    directory = base / '1080i'
    fonts = {n.text for n in ET.parse(directory / 'Font.xml').findall('.//font/name')}
    fontsets = ET.parse(directory / 'Font.xml').getroot().findall('fontset')
    for fontset in fontsets:
        names = {n.text for n in fontset.findall('font/name')}
        assert {f for f in names if f.startswith('MN_')} == {f for f in fonts if f.startswith('MN_')}, \
            fontset.get('id')
    for font in ET.parse(directory / 'Font.xml').findall('.//font'):
        if font.findtext('name', '').startswith('MN_'):
            assert (base / 'fonts' / font.findtext('filename')).is_file(), font.findtext('filename')
    includes = ET.tostring(ET.parse(directory / 'Includes_MediaNoche.xml').getroot(), encoding='unicode')
    for window_id, name in WINDOWS.items():
        root = ET.parse(directory / name).getroot()
        assert root.get('id') == str(window_id), name
        identities = [c.get('id') for c in root.iter('control') if c.get('id')]
        assert len(identities) == len(set(identities)), (name, sorted(identities))
        assert root.findtext('defaultcontrol') in identities, name
        for node in root.iter('font'):
            assert node.text in fonts, (name, node.text)
        for control in root.find('controls'):
            x, y, w, h = [int(control.findtext(t, '0')) for t in ('left', 'top', 'width', 'height')]
            assert x >= 0 and y >= 0 and x + w <= 1920 and y + h <= 1080, (name, control.attrib, x, y, w, h)
        for control in root.iter('control'):
            for tag in ('onleft', 'onright', 'onup', 'ondown'):
                for action in control.findall(tag):
                    text = action.text or ''
                    if text.isdecimal():
                        assert text in identities, (name, control.get('id'), tag, text)
                    for target in re.findall(r'SetFocus\((\d+)', text):
                        assert target in identities, (name, control.get('id'), tag, target)
        xml = ET.tostring(root, encoding='unicode')
        for path in re.findall(r'special://skin/([^\]\)"<,$]+\.(?:png|py))', xml):
            assert (base / path).is_file(), (name, path)
        for path in re.findall(r'playlists/medianoche/([\w.-]+\.xsp)', xml):
            assert (base / 'extras/playlists/medianoche' / path).is_file(), (name, path)
        # Las pestañas de Favoritos apuntan a listas que se crean al marcar el primero.
        for variable in re.findall(r'\$VAR\[([\w.]+)\]', xml):
            assert f'name="{variable}"' in includes, (name, variable)
        if window_id != 1196 and window_id != 1197:
            dock = root.find(".//control[@id='9100']")
            assert dock is not None, name
            labels = [i.findtext('label') for i in dock.find('content')]
            assert labels == ['Inicio', 'Favoritos', 'Series estrenos', 'Series', 'Cine',
                              'Estrenos cine', 'TV', 'Ajustes', 'Apagar'], labels
    home = ET.parse(directory / WINDOWS[1191]).getroot()
    assert len([c for c in home.iter('control') if c.get('type') == 'list' and c.get('id', '').startswith('50')]) == 6
    for script in ('medianoche_ficha.py', 'medianoche_explore.py', 'medianoche_trailer.py',
                   'medianoche_misfavoritos.py', 'medianoche_info.py'):
        assert (base / 'extras' / script).is_file(), script
    print('PASS: 8 pantallas premium, barra inferior, saltos del mando, fuentes y texturas')


if __name__ == '__main__':
    check(Path(sys.argv[1]))
