"""Local Kodi favourites, using Kodi 21's AddFavourite toggle semantics."""
import json
import sys


def favourite_target(rpc, media_type, database_id):
    database_id = int(database_id)
    if database_id <= 0 or media_type not in ('movie', 'tvshow'):
        raise ValueError('Unsupported library item')
    singular = 'Movie' if media_type == 'movie' else 'TVShow'
    key = 'moviedetails' if media_type == 'movie' else 'tvshowdetails'
    properties = ['title', 'thumbnail']
    if media_type == 'movie':
        properties.append('file')
    detail = rpc('VideoLibrary.Get' + singular + 'Details', {
        media_type + 'id': database_id, 'properties': properties,
    })[key]
    target = {'title': detail['title'], 'thumbnail': detail.get('thumbnail', '')}
    if media_type == 'movie':
        if not detail.get('file'):
            raise ValueError('Movie has no playback path')
        target.update(type='media', path=detail['file'])
    else:
        target.update(type='window', window='videos',
                      windowparameter=f'videodb://tvshows/titles/{database_id}/')
    return target


def find_favourite(rpc, target):
    items = rpc('Favourites.GetFavourites', {
        'properties': ['path', 'window', 'windowparameter', 'thumbnail'],
    }).get('favourites', [])
    for item in items:
        if item.get('type') != target['type']:
            continue
        if target['type'] == 'media' and item.get('path') == target['path']:
            return item
        if target['type'] == 'window' and item.get('window') in ('videos', '10025'):
            if item.get('windowparameter', '').rstrip('/') == target['windowparameter'].rstrip('/'):
                return item
    return None


def update_favourite(rpc, media_type, database_id, toggle=False):
    target = favourite_target(rpc, media_type, database_id)
    existing = find_favourite(rpc, target)
    if toggle:
        # Reuse the original entry when removing, preserving renamed favourites.
        entry = existing or target
        rpc('Favourites.AddFavourite', {
            key: value for key, value in entry.items()
            if key in ('title', 'type', 'path', 'window', 'windowparameter', 'thumbnail')
        })
        actual = find_favourite(rpc, target)
        if (actual is not None) == (existing is not None):
            raise RuntimeError('Favourite state did not change')
        existing = actual
    return existing is not None


def main():
    import xbmc
    import xbmcgui

    home = xbmcgui.Window(10000)
    state_property = 'MediaNoche.FavouriteState'
    media_type, database_id, mode = sys.argv[1:4]

    def rpc(method, params):
        response = json.loads(xbmc.executeJSONRPC(json.dumps({
            'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params,
        })))
        if 'error' in response:
            raise RuntimeError('Kodi JSON-RPC operation failed')
        return response['result']

    try:
        if mode == 'toggle':
            home.setProperty(state_property, 'busy')
        state = update_favourite(rpc, media_type, database_id, mode == 'toggle')
        # An old background refresh must not update another item's dialog.
        if (xbmc.getInfoLabel('ListItem.DBType') == media_type
                and xbmc.getInfoLabel('ListItem.DBID') == database_id):
            home.setProperty(state_property, 'added' if state else 'absent')
    except Exception:
        home.setProperty(state_property, 'error')
        if mode == 'toggle':
            xbmcgui.Dialog().notification('Plex Media Noche',
                'No se pudo actualizar Favoritos. Revisa Kodi.', xbmcgui.NOTIFICATION_ERROR)
        xbmc.log('Plex Media Noche: local favourites operation failed', xbmc.LOGWARNING)


if __name__ == '__main__':
    main()
