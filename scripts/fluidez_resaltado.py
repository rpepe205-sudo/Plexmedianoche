"""Fluidez y resaltado de pósters en las pantallas de Plex Media Noche.

- Fluidez: carátulas cargadas en segundo plano (no frenan al moverse) y
  desplazamiento suave de las filas.
- Resaltado: la peli/serie enfocada crece un poco, lleva marco dorado con
  brillo y el resto de la fila se atenúa.
"""
import xml.etree.ElementTree as ET

ART_HINTS = ('ListItem.Art', 'MediaNoche.Poster', 'MediaNoche.LibraryArt')
GOLD_GLOW = '66E5BC70'
ZOOM = '108'
HALO = 8
ROOM = 24  # margen extra para que el zoom no se corte
FOCUS_TIME = '160'
SCROLL_TIME = '220'


def _sub(parent, tag, text=None, **attrs):
    node = ET.SubElement(parent, tag, attrs)
    if text is not None:
        node.text = str(text)
    return node


def _is_art(texture):
    return texture is not None and any(h in (texture.text or '') for h in ART_HINTS)


def _num(node, tag):
    try:
        return int(node.findtext(tag))
    except (TypeError, ValueError):
        return None


def _make_room(listing, normal, focused):
    """Agranda la fila sin mover nada visible, para que el zoom no se recorte."""
    if listing.findtext('orientation') != 'horizontal':
        return
    top, height = _num(listing, 'top'), _num(listing, 'height')
    if top is None or height is None:
        return
    listing.find('top').text = str(top - ROOM)
    listing.find('height').text = str(height + 2 * ROOM)
    for layout in (normal, focused):
        if layout.get('height', '').isdigit():
            layout.set('height', str(int(layout.get('height')) + 2 * ROOM))
        for child in layout.findall('control'):
            value = _num(child, 'top')
            if value is not None:
                child.find('top').text = str(value + ROOM)


def _polish_list(listing):
    changed = False
    focused_mark = listing.find('focusedlayout')
    if focused_mark is not None and focused_mark.get('medianoche') == 'resaltado':
        return False
    if listing.find('scrolltime') is None:
        _sub(listing, 'scrolltime', SCROLL_TIME, tween='cubic', easing='out')
        changed = True
    list_id = listing.get('id')
    focused = listing.find('focusedlayout')
    normal = listing.find('itemlayout')
    if focused is None or normal is None:
        return changed

    # Resaltado: zoom con marco dorado y halo.
    if focused.get('medianoche') != 'resaltado':
        focused.set('medianoche', 'resaltado')
        _make_room(listing, normal, focused)
        poster = next((c for c in focused.findall("control[@type='image']")
                       if _is_art(c.find('texture'))), None)
        if poster is not None:
            left, top = _num(poster, 'left'), _num(poster, 'top')
            width, height = _num(poster, 'width'), _num(poster, 'height')
            if None not in (left, top, width, height):
                halo = ET.Element('control', {'type': 'image'})
                for tag, value in (('left', left - HALO), ('top', top - HALO),
                                   ('width', width + 2 * HALO), ('height', height + 2 * HALO)):
                    _sub(halo, tag, value)
                _sub(halo, 'texture', 'common/white.png', colordiffuse=GOLD_GLOW)
                focused.insert(0, halo)
            centre = None
            if None not in (left, top, width, height):
                centre = f'{left + width // 2},{top + height // 2}'
            for child in focused.findall('control'):
                if child.get('type') == 'image':
                    attrs = {'effect': 'zoom', 'start': '100', 'end': ZOOM,
                             'time': FOCUS_TIME, 'tween': 'cubic', 'easing': 'out'}
                    if centre:
                        attrs['center'] = centre
                    _sub(child, 'animation', 'Focus', **attrs)
                    _sub(child, 'animation', 'Unfocus', **{**attrs, 'start': ZOOM, 'end': '100'})
        changed = True

    # Atenuar el resto de la fila mientras la fila tiene el foco.
    if list_id and normal.get('medianoche') != 'atenuado':
        normal.set('medianoche', 'atenuado')
        for child in normal.findall("control[@type='image']"):
            if _is_art(child.find('texture')):
                _sub(child, 'animation', 'Conditional', effect='fade', start='100',
                     end='60', time='150', condition=f'Control.HasFocus({list_id})')
        changed = True
    return changed


def apply(base):
    files = sorted(base.glob('1080i/Custom_MediaNoche_*.xml')) + \
        sorted(base.glob('1080i/Custom_SeriesEstrenos_*.xml'))
    async_images = lists = 0
    for path in files:
        tree = ET.parse(path)
        root = tree.getroot()
        for texture in root.iter('texture'):
            if _is_art(texture) and texture.get('background') != 'true':
                texture.set('background', 'true')
                async_images += 1
        for listing in root.iter('control'):
            if listing.get('type') in ('list', 'panel', 'fixedlist', 'wraplist'):
                if _polish_list(listing):
                    lists += 1
        tree.write(path, encoding='UTF-8', xml_declaration=True)
    return {'async_artwork': async_images, 'polished_lists': lists,
            'files': len(files)}
