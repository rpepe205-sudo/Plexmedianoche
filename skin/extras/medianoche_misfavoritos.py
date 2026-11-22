"""Favoritos de Cine y Series de Plex Media Noche (aparte de los Favoritos de Kodi).

Uso: RunScript(medianoche_misfavoritos.py, movie|tvshow, <id>, toggle|refresh)
Guarda los títulos en el perfil y genera una lista inteligente por tipo, que
las pestañas «Favoritos» muestran como una fila más de la biblioteca.
"""
import json
import os
import sys
from xml.sax.saxutils import escape

FOLDER = 'special://profile/addon_data/skin.plexmedianoche/'
STATE = 'MediaNoche.FavouriteState'


def playlist_xml(media, titles):
    kind = 'movies' if media == 'movie' else 'tvshows'
    values = ''.join('<value>{}</value>'.format(escape(t)) for t in titles) or '<value>⁣</value>'
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<smartplaylist type="{}"><name>Favoritos</name><match>all</match>'
            '<rule field="title" operator="is">{}</rule>'
            '<order direction="ascending">sorttitle</order></smartplaylist>\n').format(kind, values)


def toggle(titles, title):
    if title in titles:
        return [t for t in titles if t != title], False
    return titles + [title], True


def main():
    import xbmc
    import xbmcgui
    import xbmcvfs

    media, dbid, action = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    folder = xbmcvfs.translatePath(FOLDER)
    os.makedirs(folder, exist_ok=True)
    store = os.path.join(folder, 'favoritos-{}.json'.format(media))
    try:
        with open(store, encoding='utf-8') as handle:
            titles = json.load(handle)
    except (OSError, ValueError):
        titles = []
    kind = 'Movie' if media == 'movie' else 'TVShow'
    key = 'moviedetails' if media == 'movie' else 'tvshowdetails'
    reply = json.loads(xbmc.executeJSONRPC(json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': 'VideoLibrary.Get{}Details'.format(kind),
        'params': {media + 'id': dbid, 'properties': ['title']}})))
    title = reply.get('result', {}).get(key, {}).get('title')
    if not title:
        return
    home = xbmcgui.Window(10000)
    if action == 'toggle':
        titles, added = toggle(titles, title)
        with open(store, 'w', encoding='utf-8') as handle:
            json.dump(titles, handle, ensure_ascii=False)
        with open(os.path.join(folder, 'favoritos-{}.xsp'.format(media)), 'w', encoding='utf-8') as handle:
            handle.write(playlist_xml(media, titles))
        xbmcgui.Dialog().notification('Favoritos', ('Añadido: ' if added else 'Quitado: ') + title,
                                      xbmcgui.NOTIFICATION_INFO, 2500)
    home.setProperty(STATE, 'added' if title in titles else 'absent')


if __name__ == '__main__':
    main()
