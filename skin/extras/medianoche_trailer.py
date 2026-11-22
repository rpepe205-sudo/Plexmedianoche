"""Reproduce un tráiler a pantalla completa sin dejar Kodi bloqueado.

- Si el tráiler es de YouTube y no está el addon, avisa en vez de colgarse.
- Si no arranca en 20 s, cierra la espera y avisa.
- Al pulsar Atrás, para el tráiler y vuelve a la ficha.
"""
import sys
import time

START_TIMEOUT = 20
POLL = 0.5


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
                return
        else:
            if not playing:
                return  # terminó solo
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
                return
            elif time.time() - start > 3:
                xbmc.executebuiltin('ActivateWindow(fullscreenvideo)')
        monitor.waitForAbort(POLL)


if __name__ == '__main__':
    main()
