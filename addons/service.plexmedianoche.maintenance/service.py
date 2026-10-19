# -*- coding: utf-8 -*-
"""Daily video-library scan and Tuesday cleanup for Plex de Media Noche."""

import datetime
import os
import time

import xbmc
import xbmcvfs

ADDON_ID = "service.plexmedianoche.maintenance"
POLL_SECONDS = 15
SCAN_TIMEOUT_SECONDS = 60 * 60
START_TIMEOUT_SECONDS = 60


def _profile_dir():
    path = xbmcvfs.translatePath(
        "special://profile/addon_data/{}/".format(ADDON_ID)
    )
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def _read_state(name):
    path = os.path.join(_profile_dir(), name)
    try:
        with open(path, "r", encoding="utf-8") as state_file:
            return state_file.read().strip()
    except (IOError, OSError):
        return ""


def _write_state(name, value):
    path = os.path.join(_profile_dir(), name)
    temporary_path = path + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as state_file:
        state_file.write(value)
    os.replace(temporary_path, path)


def _pkc_installed():
    """Avoid Kodi library maintenance while PlexKodiConnect owns the library."""
    return xbmcvfs.exists(
        "special://home/addons/plugin.video.plexkodiconnect/addon.xml"
    )


def _is_scanning():
    return xbmc.getCondVisibility("Library.IsScanningVideo")


def _wait_for_scan(monitor):
    start_time = time.time()
    saw_scan = False
    while time.time() - start_time < SCAN_TIMEOUT_SECONDS:
        if monitor.abortRequested():
            return False
        scanning = _is_scanning()
        if scanning:
            saw_scan = True
        elif saw_scan:
            return True
        elif time.time() - start_time >= START_TIMEOUT_SECONDS:
            # Kodi had nothing to scan (for example, an empty library).
            return True
        monitor.waitForAbort(POLL_SECONDS)
    return False


def _run_video_update(monitor):
    xbmc.log(
        "[Plex Media Noche] Iniciando actualización diaria de la biblioteca de vídeo.",
        xbmc.LOGINFO,
    )
    xbmc.executebuiltin("UpdateLibrary(video)")
    return _wait_for_scan(monitor)


def _run_weekly_cleanup(monitor):
    xbmc.log(
        "[Plex Media Noche] Iniciando limpieza semanal de entradas sin archivo.",
        xbmc.LOGINFO,
    )
    # Kodi removes stale library records only; it does not delete media files.
    xbmc.executebuiltin("CleanLibrary(video, false)")
    return _wait_for_scan(monitor)


def run():
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        today = datetime.date.today()
        daily_key = today.isoformat()
        week_key = today.strftime("%G-W%V")

        if _pkc_installed():
            # PKC mantiene sincronizada la biblioteca Plex y modifica la base de datos de Kodi.
            # No ejecutar UpdateLibrary/CleanLibrary: una limpieza de Kodi puede romper la sincronización PKC.
            if _read_state("pkc-notice.txt") != "shown":
                xbmc.log(
                    "[Plex Media Noche] PlexKodiConnect detectado; se omite el mantenimiento automático de la biblioteca.",
                    xbmc.LOGINFO,
                )
                _write_state("pkc-notice.txt", "shown")
        elif _read_state("last-daily-update.txt") != daily_key:
            if _run_video_update(monitor):
                _write_state("last-daily-update.txt", daily_key)
                if today.isoweekday() == 2 and _read_state("last-weekly-clean.txt") != week_key:
                    if _run_weekly_cleanup(monitor):
                        _write_state("last-weekly-clean.txt", week_key)
            else:
                xbmc.log(
                    "[Plex Media Noche] La actualización no terminó; se volverá a intentar.",
                    xbmc.LOGWARNING,
                )

        monitor.waitForAbort(POLL_SECONDS)


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        xbmc.log(
            "[Plex Media Noche] Error en mantenimiento de biblioteca: {}".format(exc),
            xbmc.LOGERROR,
        )
        raise
