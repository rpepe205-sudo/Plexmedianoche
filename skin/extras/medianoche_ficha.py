"""Rellena y abre la ficha de película (1196) o de serie (1197) de Plex Media Noche.

Uso desde el skin:
  RunScript(medianoche_ficha.py, movie, <id>)          ficha de película
  RunScript(medianoche_ficha.py, tvshow, <id>)         pantalla de serie
  RunScript(medianoche_ficha.py, play, <tipo>, <id>)   reproducir (con reanudación)
Todos los datos salen de la biblioteca de Kodi (la que llena PlexKodiConnect).
"""
import datetime
import json
import sys
from urllib.parse import quote

MOVIE_FIELDS = ['title', 'plot', 'genre', 'year', 'rating', 'mpaa', 'runtime', 'director',
                'writer', 'studio', 'country', 'art', 'cast', 'trailer', 'file', 'resume',
                'streamdetails', 'playcount', 'tagline']
SHOW_FIELDS = ['title', 'plot', 'genre', 'year', 'rating', 'mpaa', 'studio', 'art', 'cast',
               'episode', 'watchedepisodes', 'season', 'premiered']
EPISODE_FIELDS = ['title', 'season', 'episode', 'playcount', 'resume', 'file', 'runtime',
                  'streamdetails']
PREFIXES = ('MN.F.', 'MN.S.')


# ---------------------------------------------------------- formato (puro)
def rating_text(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''
    return '' if value <= 0 else '{:.1f}'.format(value).replace('.', ',')


def runtime_text(seconds):
    minutes = int(seconds or 0) // 60
    if minutes <= 0:
        return ''
    hours, rest = divmod(minutes, 60)
    if not hours:
        return '{} min'.format(rest)
    return '{} h {:02d} min'.format(hours, rest)


def end_time(seconds, now=None):
    if not seconds or seconds <= 0:
        return ''
    now = now or datetime.datetime.now()
    return 'Termina a las ' + (now + datetime.timedelta(seconds=int(seconds))).strftime('%H:%M')


def badges(streamdetails):
    """Hasta tres etiquetas: 4K/HD, HDR/Dolby Vision y canales de audio."""
    video = (streamdetails or {}).get('video') or [{}]
    audio = (streamdetails or {}).get('audio') or [{}]
    result = []
    width = int(video[0].get('width') or 0)
    if width >= 3200:
        result.append('4K')
    elif width >= 1200:
        result.append('HD')
    hdr = (video[0].get('hdrtype') or '').lower()
    if hdr == 'dolbyvision':
        result.append('DOLBY VISION')
    elif hdr:
        result.append('HDR')
    channels = int(audio[0].get('channels') or 0)
    if channels >= 8:
        result.append('7.1')
    elif channels >= 6:
        result.append('5.1')
    elif channels:
        result.append('ESTÉREO')
    return result[:3]


def audio_text(streamdetails):
    seen = []
    for track in (streamdetails or {}).get('audio') or []:
        language = (track.get('language') or '').upper()
        channels = int(track.get('channels') or 0)
        text = language + (' {}'.format({8: '7.1', 6: '5.1', 2: 'estéreo'}.get(channels, ''))
                           if channels else '')
        if text.strip() and text not in seen:
            seen.append(text.strip())
    return ' · '.join(seen[:4])


def cast_entries(cast, limit):
    people = sorted(cast or [], key=lambda person: person.get('order', 999))[:limit]
    return [(p.get('name', ''), p.get('role', ''), p.get('thumbnail', '')) for p in people]


def similar_path(media, genre, title):
    rules = [{'field': 'genre', 'operator': 'is', 'value': [genre]},
             {'field': 'title', 'operator': 'isnot', 'value': [title]}]
    xsp = {'rules': {'and': rules}, 'type': media,
           'order': {'direction': 'descending', 'method': 'rating'}}
    folder = 'movies' if media == 'movies' else 'tvshows'
    return 'videodb://{}/titles/?xsp={}'.format(folder, quote(json.dumps(xsp, ensure_ascii=False)))


def next_episode(episodes):
    """Episodio en curso; si no hay, el primero sin ver; si no, el primero."""
    ordered = sorted((e for e in episodes if int(e.get('season', 0)) > 0),
                     key=lambda e: (int(e['season']), int(e['episode'])))
    if not ordered:
        return None
    for episode in ordered:
        if float((episode.get('resume') or {}).get('position', 0)) > 0:
            return episode
    for episode in ordered:
        if not int(episode.get('playcount', 0)):
            return episode
    return ordered[0]


def movie_props(detail, now=None):
    resume = detail.get('resume') or {}
    position = float(resume.get('position', 0))
    runtime = int(detail.get('runtime') or 0)
    genres = detail.get('genre') or []
    meta = [str(detail.get('year') or ''), runtime_text(runtime), detail.get('mpaa', '')]
    credits = []
    if detail.get('director'):
        credits.append('[COLOR 80DDE6EF]Dirección[/COLOR] ' + ', '.join(detail['director'][:2]))
    if detail.get('writer'):
        credits.append('[COLOR 80DDE6EF]Guion[/COLOR] ' + ', '.join(detail['writer'][:2]))
    audio = audio_text(detail.get('streamdetails'))
    if audio:
        credits.append('[COLOR 80DDE6EF]Audio[/COLOR] ' + audio)
    details = []
    for caption, value in (('Título', detail.get('title')), ('Lema', detail.get('tagline')),
                           ('Estudio', ', '.join(detail.get('studio') or [])),
                           ('País', ', '.join(detail.get('country') or [])),
                           ('Dirección', ', '.join(detail.get('director') or [])),
                           ('Guion', ', '.join(detail.get('writer') or [])),
                           ('Audio', audio)):
        if value:
            details.append('[COLOR 80DDE6EF]{}:[/COLOR] {}'.format(caption, value))
    props = {
        'Title': detail.get('title', ''),
        'Kicker': ' · '.join(g.upper() for g in genres[:2]),
        'Rating': rating_text(detail.get('rating')),
        'Meta': '  ·  '.join(m for m in meta if m),
        'Plot': detail.get('plot', ''),
        'Credits': '     '.join(credits),
        'Details': '[CR]'.join(details),
        'File': detail.get('file', ''),
        'Trailer': detail.get('trailer', ''),
        'TrailerEsc': '"{}"'.format(detail.get('trailer', '').replace('"', '')),
        'PlayLabel': 'Continuar' if position > 0 else 'Reproducir',
        'EndTime': end_time(runtime - position, now) if runtime else '',
        'Poster': (detail.get('art') or {}).get('poster', ''),
        'Fanart': (detail.get('art') or {}).get('fanart', ''),
        'SimilarPath': similar_path('movies', genres[0], detail.get('title', '')) if genres else '',
    }
    for index, text in enumerate(badges(detail.get('streamdetails')), 1):
        props['Badge{}'.format(index)] = text
    for index, (name, role, thumb) in enumerate(cast_entries(detail.get('cast'), 8), 1):
        props.update({'Cast{}.Name'.format(index): name, 'Cast{}.Role'.format(index): role,
                      'Cast{}.Thumb'.format(index): thumb})
    return props


def show_props(detail, episodes, seasons, all_item=False):
    genres = detail.get('genre') or []
    total = int(detail.get('episode') or 0)
    watched = int(detail.get('watchedepisodes') or 0)
    nxt = next_episode(episodes)
    seasons_count = len([s for s in seasons if int(s.get('season', 0)) > 0])
    meta = [str(detail.get('year') or ''),
            '{} temporada{}'.format(seasons_count, '' if seasons_count == 1 else 's') if seasons_count else '',
            detail.get('mpaa', '')]
    props = {
        'Title': detail.get('title', ''),
        'Kicker': ' · '.join(['SERIE'] + [g.upper() for g in genres[:2]]),
        'Rating': rating_text(detail.get('rating')),
        'Meta': '  ·  '.join(m for m in meta if m),
        'Plot': detail.get('plot', ''),
        'Fanart': (detail.get('art') or {}).get('fanart', ''),
        'Watched': '{} de {} vistos'.format(watched, total) if total else '',
        'Bucket': str(int(round(watched * 20.0 / total)) * 5) if total else '0',
        'Trailer': '',
        'TrailerEsc': '""',
        'PlayLabel': 'Reproducir',
        'NextInfo': '',
        'NextFile': '',
        'NextDBID': '',
        'SeasonPos': '0',
    }
    if nxt:
        season, number = int(nxt['season']), int(nxt['episode'])
        resume = nxt.get('resume') or {}
        position = float(resume.get('position', 0))
        total_time = float(resume.get('total', 0)) or float(nxt.get('runtime') or 0)
        in_progress = position > 0
        props['PlayLabel'] = '{} T{} E{}'.format('Continuar' if in_progress else 'Ver', season, number)
        left = runtime_text(total_time - position) if in_progress and total_time else ''
        props['NextInfo'] = 'T{} · E{}'.format(season, number) + (' · quedan ' + left if left else '')
        props['NextFile'] = nxt.get('file', '')
        props['NextDBID'] = str(nxt.get('episodeid', ''))
        ordered = sorted(int(x.get('season', 0)) for x in seasons)
        if season in ordered:
            props['SeasonPos'] = str(ordered.index(season) + (1 if all_item else 0))
        props.update(dict(('Badge{}'.format(i), t) for i, t in
                          enumerate(badges(nxt.get('streamdetails')), 1)))
    for index, (name, role, thumb) in enumerate(cast_entries(detail.get('cast'), 4), 1):
        props.update({'Cast{}.Name'.format(index): name, 'Cast{}.Role'.format(index): role,
                      'Cast{}.Thumb'.format(index): thumb})
    return props


# ------------------------------------------------------------------- Kodi
def main():
    import xbmc
    import xbmcgui

    def rpc(method, params):
        answer = json.loads(xbmc.executeJSONRPC(json.dumps(
            {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})))
        if 'error' in answer:
            raise RuntimeError(method)
        return answer['result']

    home = xbmcgui.Window(10000)

    def publish(prefix, props):
        for key in list(props):
            home.setProperty(prefix + key, str(props[key]))

    def clear(prefix):
        keys = ['Title', 'Kicker', 'Rating', 'Meta', 'Plot', 'Credits', 'Details', 'File',
                'Trailer', 'TrailerEsc', 'PlayLabel', 'EndTime', 'Poster', 'Fanart',
                'SimilarPath', 'Watched', 'Bucket', 'NextInfo', 'NextFile', 'NextDBID', 'SeasonPos', 'DBID']
        keys += ['Badge{}'.format(i) for i in range(1, 4)]
        keys += ['Cast{}.{}'.format(i, part) for i in range(1, 9) for part in ('Name', 'Role', 'Thumb')]
        for key in keys:
            home.clearProperty(prefix + key)

    try:
        action = sys.argv[1]
        if action == 'play':
            media, dbid = sys.argv[2], int(sys.argv[3])
            if media == 'tvshow':
                action, sys.argv[2] = 'tvshow', str(dbid)
            else:
                # Reproducir como elemento de la biblioteca (así lo espera PlexKodiConnect).
                rpc('Player.Open', {'item': {media + 'id': dbid}, 'options': {'resume': True}})
                return
        dbid = int(sys.argv[2])
        if action == 'movie':
            detail = rpc('VideoLibrary.GetMovieDetails',
                         {'movieid': dbid, 'properties': MOVIE_FIELDS})['moviedetails']
            clear('MN.F.')
            props = movie_props(detail)
            props['DBID'] = dbid
            publish('MN.F.', props)
            xbmc.executebuiltin('ActivateWindow(1196)')
        elif action == 'tvshow':
            detail = rpc('VideoLibrary.GetTVShowDetails',
                         {'tvshowid': dbid, 'properties': SHOW_FIELDS})['tvshowdetails']
            episodes = rpc('VideoLibrary.GetEpisodes',
                           {'tvshowid': dbid, 'properties': EPISODE_FIELDS}).get('episodes', [])
            seasons = rpc('VideoLibrary.GetSeasons',
                          {'tvshowid': dbid, 'properties': ['season']}).get('seasons', [])
            try:
                all_item = bool(rpc('Settings.GetSettingValue',
                                    {'setting': 'videolibrary.showallitems'}).get('value'))
            except RuntimeError:
                all_item = True
            clear('MN.S.')
            props = show_props(detail, episodes, seasons, all_item and len(seasons) > 1)
            props['DBID'] = dbid
            publish('MN.S.', props)
            xbmc.executebuiltin('ActivateWindow(1197)')
    except Exception as error:  # nunca dejar la pantalla bloqueada
        xbmc.log('Plex Media Noche: ficha no disponible ({})'.format(error), xbmc.LOGWARNING)
        xbmcgui.Dialog().notification('Plex Media Noche', 'No se pudo abrir este título.',
                                      xbmcgui.NOTIFICATION_ERROR, 4000)


if __name__ == '__main__':
    main()
