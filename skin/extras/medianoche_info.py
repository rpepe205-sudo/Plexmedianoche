"""Open Kodi's native information dialog for an item from a cinematic row."""
import json
import sys


def read_details(rpc, media_type, database_id):
    if media_type not in ('movie', 'episode'):
        raise ValueError('Unsupported video type')
    database_id = int(database_id)
    if database_id <= 0:
        raise ValueError('Invalid library ID')
    fields = ['title', 'plot', 'runtime', 'playcount', 'resume', 'file',
              'art', 'thumbnail', 'rating', 'cast']
    if media_type == 'movie':
        fields += ['year', 'genre', 'trailer', 'tagline']
    else:
        fields += ['season', 'episode', 'showtitle', 'firstaired']
    kind = 'Movie' if media_type == 'movie' else 'Episode'
    return rpc('VideoLibrary.Get' + kind + 'Details', {
        media_type + 'id': database_id, 'properties': fields,
    })[media_type + 'details']


def make_item(gui, media_type, database_id, detail):
    if not detail.get('file'):
        raise ValueError('Missing library playback path')
    item = gui.ListItem(label=detail['title'], path=detail['file'], offscreen=True)
    item.setIsFolder(False)
    item.setArt(detail.get('art', {}))
    tag = item.getVideoInfoTag()
    tag.setDbId(int(database_id))
    tag.setMediaType(media_type)
    tag.setTitle(detail['title'])
    tag.setPlot(detail.get('plot', ''))
    tag.setDuration(int(detail.get('runtime', 0)))
    tag.setPlaycount(int(detail.get('playcount', 0)))
    tag.setFilenameAndPath(detail['file'])
    if media_type == 'movie':
        tag.setYear(int(detail.get('year', 0)))
        tag.setGenres(detail.get('genre', []))
        tag.setTrailer(detail.get('trailer', ''))
        tag.setTagLine(detail.get('tagline', ''))
    else:
        tag.setSeason(int(detail.get('season', 0)))
        tag.setEpisode(int(detail.get('episode', 0)))
        tag.setTvShowTitle(detail.get('showtitle', ''))
        if detail.get('firstaired'):
            tag.setPremiered(detail['firstaired'])
    resume = detail.get('resume', {})
    tag.setResumePoint(float(resume.get('position', 0)), float(resume.get('total', 0)))
    if detail.get('rating'):
        tag.setRating(float(detail['rating']))
    item.setCast(detail.get('cast', []))
    item.setProperty('IsPlayable', 'true')
    return item


def main():
    import xbmc
    import xbmcgui

    def rpc(method, params):
        response = json.loads(xbmc.executeJSONRPC(json.dumps({
            'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params,
        })))
        if 'error' in response:
            raise RuntimeError('Local video-library query failed')
        return response['result']

    try:
        media_type, database_id = sys.argv[1:3]
        details = read_details(rpc, media_type, database_id)
        item = make_item(xbmcgui, media_type, database_id, details)
        xbmcgui.Dialog().info(item)
    except Exception:
        xbmc.log('Plex Media Noche: unable to open local video information', xbmc.LOGWARNING)
        xbmcgui.Dialog().notification('Plex Media Noche',
            'No se pudo abrir la ficha de este título.', xbmcgui.NOTIFICATION_ERROR)


if __name__ == '__main__':
    main()
