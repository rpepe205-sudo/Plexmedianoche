"""Menú «Explorar» de Cine y Series: géneros, años, actores… (índices nativos de Kodi)."""
import sys

OPTIONS = {
    'movie': [('Géneros', 'MovieGenres'), ('Años', 'MovieYears'), ('Actores', 'MovieActors'),
              ('Directores', 'MovieDirectors'), ('Estudios', 'MovieStudios'),
              ('Colecciones', 'MovieSets')],
    'tvshow': [('Géneros', 'TvShowGenres'), ('Años', 'TvShowYears'), ('Actores', 'TvShowActors'),
               ('Estudios', 'TvShowStudios')],
}


def main():
    import xbmc
    import xbmcgui
    options = OPTIONS.get(sys.argv[1] if len(sys.argv) > 1 else 'movie', OPTIONS['movie'])
    choice = xbmcgui.Dialog().select('Explorar', [name for name, _ in options])
    if choice >= 0:
        xbmc.executebuiltin('ActivateWindow(Videos,{},return)'.format(options[choice][1]))


if __name__ == '__main__':
    main()
