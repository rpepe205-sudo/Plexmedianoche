"""Exercise favourite lifecycle and failures without a Kodi installation."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('favourites',
    Path(__file__).resolve().parents[1] / 'skin/extras/medianoche_favourites.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FavouritesTests(unittest.TestCase):
    def setUp(self):
        self.items = []
        self.ignore_write = False
        self.calls = []

    def rpc(self, method, params):
        self.calls.append((method, params))
        if method.startswith('VideoLibrary.Get'):
            key = 'moviedetails' if 'Movie' in method else 'tvshowdetails'
            return {key: {'title': 'Título, con acentos',
                          'file': 'plugin://pkc/item?id=8&title=a,b', 'thumbnail': ''}}
        if method == 'Favourites.GetFavourites':
            return {'favourites': list(self.items)}
        if method == 'Favourites.AddFavourite':
            if not self.ignore_write:
                if params in self.items:
                    self.items.remove(params)
                else:
                    self.items.append(dict(params))
            return 'OK'
        raise AssertionError(method)

    def test_movie_lifecycle_preserves_plugin_path_and_renamed_title(self):
        self.assertFalse(module.update_favourite(self.rpc, 'movie', '8'))
        self.assertTrue(module.update_favourite(self.rpc, 'movie', '8', True))
        self.assertEqual(self.items[0]['path'], 'plugin://pkc/item?id=8&title=a,b')
        self.items[0]['title'] = 'Nombre cambiado en Kodi'
        self.assertTrue(module.update_favourite(self.rpc, 'movie', '8'))
        self.assertFalse(module.update_favourite(self.rpc, 'movie', '8', True))
        self.assertEqual(self.items, [])

    def test_series_favourite_opens_native_seasons(self):
        self.assertTrue(module.update_favourite(self.rpc, 'tvshow', '42', True))
        self.assertEqual(self.items[0]['windowparameter'], 'videodb://tvshows/titles/42/')
        self.assertEqual(self.items[0]['window'], 'videos')
        self.assertFalse(module.update_favourite(self.rpc, 'tvshow', '42', True))

    def test_ack_without_actual_write_is_failure(self):
        self.ignore_write = True
        with self.assertRaises(RuntimeError):
            module.update_favourite(self.rpc, 'movie', '8', True)

    def test_invalid_items_cannot_write(self):
        for media_type, identity in (('episode', '8'), ('movie', '-1'), ('movie', 'invalid')):
            with self.assertRaises(ValueError):
                module.update_favourite(self.rpc, media_type, identity, True)
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
