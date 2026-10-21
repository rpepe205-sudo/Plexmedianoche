"""Check local info-dialog data handling with Kodi's API replaced by doubles."""
import importlib.util
from pathlib import Path
import types
import unittest

spec = importlib.util.spec_from_file_location('details',
    Path(__file__).resolve().parents[1] / 'skin/extras/medianoche_info.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FakeItem:
    def __init__(self, **values):
        self.values = values
        self.tag_values = {}

    def getVideoInfoTag(self):
        class Tag:
            def __getattr__(tag_self, name):
                return lambda *args: self.tag_values.update({name: args})
        return Tag()

    def setIsFolder(self, value):
        self.values['folder'] = value

    def setArt(self, value):
        self.values['art'] = value

    def setCast(self, value):
        self.values['cast'] = value

    def setProperty(self, key, value):
        self.values[key] = value


class DetailsTests(unittest.TestCase):
    def test_movie_retains_plugin_path_library_id_resume_and_actual_trailer(self):
        details = {
            'title': 'Una película, con título', 'file': 'plugin://pkc/item?id=8&part=a,b',
            'resume': {'position': 123.5, 'total': 7200}, 'trailer': 'plugin://trailer/id',
            'art': {'poster': 'special://profile/poster.jpg'}, 'playcount': 1,
        }
        item = module.make_item(types.SimpleNamespace(ListItem=FakeItem), 'movie', '8', details)
        self.assertEqual(item.values['path'], details['file'])
        self.assertEqual(item.tag_values['setDbId'], (8,))
        self.assertEqual(item.tag_values['setResumePoint'], (123.5, 7200.0))
        self.assertEqual(item.tag_values['setTrailer'], (details['trailer'],))
        self.assertEqual(item.values['art'], details['art'])

    def test_episode_query_does_not_request_movie_only_fields(self):
        def rpc(method, params):
            self.assertEqual(method, 'VideoLibrary.GetEpisodeDetails')
            self.assertEqual(params['episodeid'], 42)
            for field in ('trailer', 'genre', 'tagline', 'year'):
                self.assertNotIn(field, params['properties'])
            return {'episodedetails': {'title': 'Episodio'}}
        self.assertEqual(module.read_details(rpc, 'episode', '42')['title'], 'Episodio')

    def test_invalid_library_item_never_calls_rpc(self):
        def rpc(*args):
            self.fail('Invalid item reached the local API')
        for media_type, identity in (('tvshow', '8'), ('movie', 'invalid'), ('movie', '0')):
            with self.assertRaises(ValueError):
                module.read_details(rpc, media_type, identity)

    def test_absent_playback_path_cannot_open_a_broken_item(self):
        with self.assertRaises(ValueError):
            module.make_item(types.SimpleNamespace(ListItem=FakeItem),
                             'movie', '8', {'title': 'Sin archivo'})


if __name__ == '__main__':
    unittest.main()
