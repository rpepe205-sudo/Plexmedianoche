"""Descarga películas, episodios o temporadas desde tu servidor Plex (vía PlexKodiConnect).

Uso: RunScript(medianoche_descargar.py, movie|episode|tvshow, <id>)
Usa la conexión y el permiso que ya tiene PlexKodiConnect. Solo funciona si el
dueño del servidor permite descargas. Los archivos van a la carpeta elegida
(se pregunta la primera vez y se cambia en Ajustes del skin).
"""
import json
import os
import re
import ssl
import sys
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import Request, urlopen

PKC = 'plugin.video.plexkodiconnect'
FOLDER_SETTING = 'medianoche.descargas'
CHUNK = 1024 * 512


def plex_id(path):
    match = re.search(r'plex_id=(\d+)', path or '')
    return match.group(1) if match else None


def safe_name(name):
    return re.sub(r'[\\/:*?"<>|]+', ' ', name).strip() or 'video'


def server_base(settings):
    scheme = 'https' if settings('https') == 'true' else 'http'
    return '{}://{}:{}'.format(scheme, settings('ipaddress'), settings('port') or '32400')


def main():
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcvfs

    dialog = xbmcgui.Dialog()

    def rpc(method, params):
        reply = json.loads(xbmc.executeJSONRPC(json.dumps(
            {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})))
        return reply.get('result', {})

    try:
        pkc = xbmcaddon.Addon(PKC)
    except RuntimeError:
        dialog.ok('Descargas', 'Necesitas PlexKodiConnect instalado y conectado.')
        return
    token = pkc.getSetting('accessToken') or pkc.getSetting('plexToken')
    base = server_base(pkc.getSetting)
    context = ssl.create_default_context()
    if pkc.getSetting('sslverify') == 'false':
        context = ssl._create_unverified_context()

    media, dbid = sys.argv[1], int(sys.argv[2])
    files = []  # (nombre base, plex_id)
    if media == 'movie':
        d = rpc('VideoLibrary.GetMovieDetails', {'movieid': dbid, 'properties': ['title', 'year', 'file']})['moviedetails']
        files.append(('{} ({})'.format(d['title'], d.get('year', '')), plex_id(d['file'])))
    elif media == 'episode':
        d = rpc('VideoLibrary.GetEpisodeDetails', {'episodeid': dbid, 'properties': ['showtitle', 'season', 'episode', 'title', 'file']})['episodedetails']
        files.append(('{} T{:02d}E{:02d} {}'.format(d['showtitle'], d['season'], d['episode'], d['title']), plex_id(d['file'])))
    else:
        eps = rpc('VideoLibrary.GetEpisodes', {'tvshowid': dbid, 'properties': ['showtitle', 'season', 'episode', 'title', 'file']}).get('episodes', [])
        seasons = sorted({e['season'] for e in eps})
        if not seasons:
            return
        choice = dialog.select('¿Qué temporada descargas?', ['Temporada {}'.format(s) for s in seasons] + ['Todas'])
        if choice < 0:
            return
        wanted = seasons if choice == len(seasons) else [seasons[choice]]
        for e in sorted(eps, key=lambda e: (e['season'], e['episode'])):
            if e['season'] in wanted:
                files.append(('{} T{:02d}E{:02d} {}'.format(e['showtitle'], e['season'], e['episode'], e['title']), plex_id(e['file'])))
    files = [f for f in files if f[1]]
    if not files:
        dialog.ok('Descargas', 'Este título no viene de Plex o no se puede descargar.')
        return

    folder = xbmc.getInfoLabel('Skin.String({})'.format(FOLDER_SETTING))
    if not folder:
        folder = dialog.browse(3, 'Elige la carpeta para tus descargas', 'files')
        if not folder:
            return
        xbmc.executebuiltin('Skin.SetString({},{})'.format(FOLDER_SETTING, folder))
    if not dialog.yesno('Descargar', '{} archivo(s) a:[CR]{}'.format(len(files), folder)):
        return

    progress = xbmcgui.DialogProgressBG()
    progress.create('Descargando', files[0][0])
    done = 0
    try:
        for index, (name, pid) in enumerate(files, 1):
            meta = urlopen(Request('{}/library/metadata/{}?X-Plex-Token={}'.format(base, pid, quote(token)),
                                   headers={'Accept': 'application/xml'}), context=context, timeout=30).read()
            part = ET.fromstring(meta).find('.//Part')
            if part is None:
                continue
            extension = os.path.splitext(part.get('file', ''))[1] or '.mkv'
            target = folder.rstrip('/\\') + '/' + safe_name(name) + extension
            url = '{}{}?download=1&X-Plex-Token={}'.format(base, part.get('key'), quote(token))
            response = urlopen(Request(url), context=context, timeout=60)
            total = int(response.headers.get('Content-Length') or part.get('size') or 0)
            written = 0
            out = xbmcvfs.File(target, 'w')
            try:
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    out.write(bytearray(chunk))
                    written += len(chunk)
                    percent = int(written * 100 / total) if total else 0
                    progress.update(percent, 'Descargando {}/{}'.format(index, len(files)), name)
                    if xbmc.Monitor().abortRequested():
                        return
            finally:
                out.close()
            done += 1
    except Exception as error:  # permiso denegado, red, espacio…
        text = str(error)
        if '401' in text or '403' in text:
            text = 'El dueño del servidor no permite descargas.'
        xbmc.log('Plex Media Noche: descarga fallida ({})'.format(error), xbmc.LOGWARNING)
        dialog.notification('Descargas', 'No se pudo descargar: ' + text[:80], xbmcgui.NOTIFICATION_ERROR, 6000)
    finally:
        progress.close()
    if done:
        dialog.notification('Descargas', '{} descarga(s) terminada(s)'.format(done), xbmcgui.NOTIFICATION_INFO, 5000)


if __name__ == '__main__':
    main()
