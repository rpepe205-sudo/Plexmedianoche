# -*- coding: utf-8 -*-
"""Listas mixtas (cine + series) para el Inicio de Plex Media Noche.

plugin://plugin.video.medianoche/?lista=milista    favoritos de cine y series
plugin://plugin.video.medianoche/?lista=continuar  pelis y episodios a medias
"""
import json
import os
import sys
from urllib.parse import parse_qsl

MOVIE = ['title', 'year', 'art', 'plot', 'genre', 'rating', 'runtime', 'file', 'dateadded',
         'resume', 'playcount', 'trailer', 'mpaa', 'streamdetails', 'lastplayed']
SHOW = ['title', 'year', 'art', 'plot', 'genre', 'rating', 'dateadded', 'mpaa', 'playcount']
EPISODE = ['title', 'showtitle', 'season', 'episode', 'art', 'plot', 'runtime', 'file', 'resume',
           'playcount', 'streamdetails', 'lastplayed', 'tvshowid', 'rating']
FAVS = 'special://profile/addon_data/skin.plexmedianoche/favoritos-{}.json'


def by_title_filter(titles):
    return {'or': [{'field': 'title', 'operator': 'is', 'value': t} for t in titles]}


def merge_recent(groups, key, limit=40):
    items = [item for group in groups for item in group]
    return sorted(items, key=lambda i: i.get(key) or '', reverse=True)[:limit]


def main():
    import xbmc
    import xbmcgui
    import xbmcplugin
    import xbmcvfs

    handle = int(sys.argv[1])
    args = dict(parse_qsl(sys.argv[2].lstrip('?')))

    def rpc(method, params):
        reply = json.loads(xbmc.executeJSONRPC(json.dumps(
            {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})))
        return reply.get('result') or {}

    def titles(media):
        try:
            with open(xbmcvfs.translatePath(FAVS.format(media)), encoding='utf-8') as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return []

    def item_for(data, media):
        label = data.get('title', '')
        li = xbmcgui.ListItem(label, offscreen=True)
        art = dict(data.get('art') or {})
        if media == 'movie':
            art.setdefault('thumb', art.get('fanart', ''))
            art['thumb'] = art.get('fanart') or art.get('thumb', '')
        li.setArt(art)
        tag = li.getVideoInfoTag()
        tag.setMediaType(media)
        tag.setDbId(int(data.get(media + 'id', 0)))
        tag.setTitle(label)
        tag.setPlot(data.get('plot', ''))
        if data.get('year'):
            tag.setYear(int(data['year']))
        tag.setGenres(data.get('genre') or [])
        if data.get('rating'):
            tag.setRating(float(data['rating']))
        if data.get('runtime'):
            tag.setDuration(int(data['runtime']))
        if data.get('mpaa'):
            tag.setMpaa(data['mpaa'])
        if data.get('trailer'):
            tag.setTrailer(data['trailer'])
        tag.setPlaycount(int(data.get('playcount') or 0))
        resume = data.get('resume') or {}
        if resume.get('position'):
            tag.setResumePoint(float(resume['position']), float(resume.get('total') or 0))
        if media == 'episode':
            tag.setTvShowTitle(data.get('showtitle', ''))
            tag.setSeason(int(data.get('season', 0)))
            tag.setEpisode(int(data.get('episode', 0)))
        streams = data.get('streamdetails') or {}
        for video in streams.get('video') or []:
            tag.addVideoStream(xbmc.VideoStreamDetail(
                int(video.get('width') or 0), int(video.get('height') or 0), 0.0, 0,
                video.get('codec', ''), '', '', video.get('hdrtype', '')))
        for audio in streams.get('audio') or []:
            tag.addAudioStream(xbmc.AudioStreamDetail(
                int(audio.get('channels') or 0), audio.get('codec', ''), audio.get('language', '')))
        path = data.get('file') or 'videodb://tvshows/titles/{}/'.format(data.get('tvshowid', ''))
        li.setPath(path)
        return path, li

    lista = args.get('lista', 'milista')
    entries = []
    if lista == 'continuar':
        movies = rpc('VideoLibrary.GetMovies', {
            'filter': {'field': 'inprogress', 'operator': 'true', 'value': ''},
            'properties': MOVIE}).get('movies', [])
        episodes = rpc('VideoLibrary.GetEpisodes', {
            'filter': {'field': 'inprogress', 'operator': 'true', 'value': ''},
            'properties': EPISODE}).get('episodes', [])
        for data in merge_recent([[dict(m, _t='movie') for m in movies],
                                  [dict(e, _t='episode') for e in episodes]], 'lastplayed'):
            entries.append(item_for(data, data['_t']))
    else:
        groups = []
        movie_titles, show_titles = titles('movie'), titles('tvshow')
        if movie_titles:
            groups.append([dict(m, _t='movie') for m in rpc('VideoLibrary.GetMovies', {
                'filter': by_title_filter(movie_titles), 'properties': MOVIE}).get('movies', [])])
        if show_titles:
            groups.append([dict(s, _t='tvshow') for s in rpc('VideoLibrary.GetTVShows', {
                'filter': by_title_filter(show_titles), 'properties': SHOW}).get('tvshows', [])])
        for data in merge_recent(groups, 'dateadded', 100):
            entries.append(item_for(data, data['_t']))
    xbmcplugin.setContent(handle, 'videos')
    for path, li in entries:
        xbmcplugin.addDirectoryItem(handle, path, li, False)
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)


if __name__ == '__main__':
    main()
