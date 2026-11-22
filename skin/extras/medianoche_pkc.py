"""Ajusta una sola vez PlexKodiConnect para que Kodi arranque más rápido.

- Sincronización completa: una vez al día (1440 min) en vez de cada hora,
  solo si el usuario no había puesto ya otro valor.
- No descargar todas las carátulas de golpe al iniciar.
- Sincronizar en segundo plano, sin mostrar la barra de progreso ni avisos.
- Kodi: no rastrear la biblioteca al iniciar (PKC ya la mantiene).
Las carpetas a sincronizar las elige el usuario dentro de PKC.
"""
import json

PKC_ID = 'plugin.video.plexkodiconnect'
DONE_FLAG = 'medianoche.pkc.ajustado2'


def tune(pkc):
    """Devuelve la lista de cambios aplicados al objeto de ajustes de PKC."""
    changes = []
    if pkc.getSetting('fullSyncInterval') in ('', '60'):
        pkc.setSetting('fullSyncInterval', '1440')
        changes.append('fullSyncInterval=1440')
    if pkc.getSetting('enableTextureCache') != 'false':
        pkc.setSetting('enableTextureCache', 'false')
        changes.append('enableTextureCache=false')
    for setting in ('dbSyncIndicator', 'playstate_sync_indicator', 'imageSyncNotifications'):
        if pkc.getSetting(setting) != 'false':
            pkc.setSetting(setting, 'false')
            changes.append(setting + '=false')
    return changes


def main():
    import xbmc
    import xbmcaddon
    import xbmcgui

    if xbmc.getCondVisibility('Skin.HasSetting({})'.format(DONE_FLAG)):
        return
    if not xbmc.getCondVisibility('System.HasAddon({})'.format(PKC_ID)):
        return  # se volverá a intentar cuando PKC esté instalado
    try:
        changes = tune(xbmcaddon.Addon(PKC_ID))
        xbmc.executeJSONRPC(json.dumps({
            'jsonrpc': '2.0', 'id': 1, 'method': 'Settings.SetSettingValue',
            'params': {'setting': 'videolibrary.updateonstartup', 'value': False},
        }))
    except Exception as exc:  # no bloquear nunca el arranque
        xbmc.log('Plex Media Noche: no se pudo ajustar PKC: {}'.format(exc), xbmc.LOGWARNING)
        return
    xbmc.executebuiltin('Skin.SetBool({})'.format(DONE_FLAG))
    xbmc.log('Plex Media Noche: PKC ajustado {}'.format(changes), xbmc.LOGINFO)
    if changes:
        xbmcgui.Dialog().notification(
            'Plex Media Noche',
            'Sincronización optimizada. Se aplicará al reiniciar Kodi.',
            xbmcgui.NOTIFICATION_INFO, 6000)


if __name__ == '__main__':
    main()
