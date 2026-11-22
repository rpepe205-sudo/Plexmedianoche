"""Reproduce un tráiler a pantalla completa sin dejar Kodi bloqueado.

- Si el tráiler es de YouTube y no está el addon, avisa en vez de colgarse.
- Si no arranca en 20 s, cierra la espera y avisa.
- Al pulsar Atrás, para el tráiler y vuelve a la ficha.
- Si se pulsa Stop (o termina) y a los 3 s no ha vuelto, vuelve solo.
"""
import sys
import time

START_TIMEOUT = 20
POLL = 0.5
RETURN_DELAY = 3


def ensure_back(xbmc, monitor, dbtype, dbid, from_info):
    """Tras parar, si a los 3 s sigue sin volver, forzar la vuelta a la ficha."""
    if monitor.waitForAbort(RETURN_DELAY):
        return
    if xbmc.getCondVisibility('Window.IsActive(fullscreenvideo)'):
        xbmc.executebuiltin('Action(Back)')
        monitor.waitForAbort(0.5)
    if (from_info and dbtype in ('movie', 'episode') and dbid.isdigit()
            and not xbmc.getCondVisibility('Window.IsVisible(movieinformation)')):
        xbmc.executebuiltin('RunScript(special://skin/extras/medianoche_info.py,'
                            '{},{})'.format(dbtype, dbid))


def needs_youtube(url):
    return 'plugin.video.youtube' in url or 'plugin://plugin.video.youtube' in url


def main():
    import xbmc
    import xbmcgui

    def notify(text):
        xbmcgui.Dialog().notification('Plex Media Noche', text,
                                      xbmcgui.NOTIFICATION_INFO, 4000)

    url = sys.argv[1].strip().strip('"') if len(sys.argv) > 1 else ''
    if not url:
        notify('Este título no tiene tráiler.')
        return
    if needs_youtube(url) and not xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
        notify('Para ver tráilers instala el addon de YouTube.')
        return

    from_info = xbmc.getCondVisibility('Window.IsVisible(movieinformation)')
    dbtype = xbmc.getInfoLabel('ListItem.DBType')
    dbid = xbmc.getInfoLabel('ListItem.DBID')
    player = xbmc.Player()
    monitor = xbmc.Monitor()
    player.play(url)
    start = time.time()
    started = False
    saw_fullscreen = False
    playing_file = ''
    while not monitor.abortRequested():
        playing = player.isPlayingVideo()
        if not started:
            if playing:
                started = True
                start = time.time()
                try:
                    playing_file = player.getPlayingFile()
                except RuntimeError:
                    playing_file = ''
            elif time.time() - start > START_TIMEOUT:
                xbmc.executebuiltin('Dialog.Close(busydialog,true)')
                xbmc.executebuiltin('Dialog.Close(busydialognocancel,true)')
                if player.isPlaying():
                    player.stop()
                notify('No se pudo cargar el tráiler.')
                ensure_back(xbmc, monitor, dbtype, dbid, from_info)
                return
        else:
            if not playing:
                ensure_back(xbmc, monitor, dbtype, dbid, from_info)
                return  # Stop o terminó solo
            try:
                if playing_file and player.getPlayingFile() != playing_file:
                    return  # el usuario puso otra cosa: no tocar
            except RuntimeError:
                return
            fullscreen = xbmc.getCondVisibility('Window.IsActive(fullscreenvideo)')
            if fullscreen:
                saw_fullscreen = True
            elif saw_fullscreen:
                player.stop()  # pulsó Atrás: parar y volver a la ficha
                ensure_back(xbmc, monitor, dbtype, dbid, from_info)
                return
            elif time.time() - start > 3:
                xbmc.executebuiltin('ActivateWindow(fullscreenvideo)')
        monitor.waitForAbort(POLL)


if __name__ == '__main__':
    main()
