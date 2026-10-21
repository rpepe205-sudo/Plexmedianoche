"""Check generated windows against the pinned skin, without starting Kodi."""
from pathlib import Path
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

from cinematic_design import build_design, ICONS, LIBRARIES


def verify(upstream):
    project = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        directory = base / '1080i'
        directory.mkdir()
        for filename in ('Includes.xml', 'DialogVideoInfo.xml', 'Home.xml'):
            shutil.copyfile(upstream / '1080i' / filename, directory / filename)
        home = (directory / 'Home.xml').read_bytes()
        native_dialog = ET.parse(directory / 'DialogVideoInfo.xml').getroot()
        report = build_design(base, project)
        assert (directory / 'Home.xml').read_bytes() == home
        dialog = ET.parse(directory / 'DialogVideoInfo.xml').getroot()
        assert [ET.tostring(c) for c in list(dialog.find('controls'))[3:]] == [
            ET.tostring(c) for c in native_dialog.find('controls')]
        fonts = {node.text for node in ET.parse(upstream / '1080i/Font.xml').findall('.//font/name')}
        windows = {}
        for path in directory.glob('Custom*.xml'):
            root = ET.parse(path).getroot()
            window_id = int(root.get('id'))
            assert window_id not in windows
            windows[window_id] = root
            identities = [c.get('id') for c in root.findall('.//control') if c.get('id')]
            assert len(identities) == len(set(identities))
            assert root.findtext('defaultcontrol') in identities
            assert all(n.text in fonts for n in root.findall('.//font'))
            for control in root.findall('controls/control'):
                x, y, width, height = [int(control.findtext(tag, '0'))
                                      for tag in ('left', 'top', 'width', 'height')]
                assert x >= 0 and y >= 0 and x + width <= 1920 and y + height <= 1080, (
                    path.name, control.attrib, x, y, width, height)
            for control in root.findall('.//control'):
                for tag in ('onleft', 'onright', 'onup', 'ondown', 'onback'):
                    for action in control.findall(tag):
                        if action.text and action.text.isdecimal():
                            assert action.text in identities, (path.name, tag, action.text)
            xml = ET.tostring(root, encoding='unicode')
            for playlist in re.findall(r'playlists/medianoche/([\w.-]+\.xsp)', xml):
                assert (project / 'skin/playlists' / playlist).is_file(), playlist
                ET.parse(project / 'skin/playlists' / playlist)
        assert set(windows) == {1190, 1191, 1192, 1193, 1194, 1195}
        if (upstream / 'addon.xml').is_file():
            for name in set(ICONS.values()) | {'eye.png', 'play2.png'}:
                assert (upstream / 'extras/icons' / name).is_file(), name
        variables = ET.parse(directory / 'Includes_MediaNoche.xml').getroot()
        poster = variables.find("variable[@name='MediaNoche.Poster']")
        assert [v.text for v in poster.findall('value')] == [
            '$INFO[ListItem.Art(poster)]', '$INFO[ListItem.Art(tvshow.poster)]',
            '$INFO[ListItem.Art(thumb)]', 'DefaultVideo.png']
        for root in windows.values():
            for icon in root.findall("controls/control[@type='image']"):
                visible = icon.findtext('visible', '')
                if 'Control.HasFocus(' in visible:
                    identity = visible.split('Control.HasFocus(')[1].split(')')[0]
                    target = root.find(f"controls/control[@id='{identity}']")
                    assert target is not None and target.findtext('label')
                    assert target.findtext('textoffsetx') == '54'
        home = windows[1191]
        # Empty libraries still have an uninterrupted path through title buttons.
        assert home.findtext("controls/control[@id='301']/ondown") == '601'
        assert home.findtext("controls/control[@id='201']/onup") == '604'
        for identity in range(601, 605):
            assert home.find(f"controls/control[@id='{identity}']/onright").get('condition')
        for identity in (501, 502, 503):
            assert len(home.findall(f"controls/control[@id='{identity}']/ondown")) == 2
        assert len(home.findall("controls/control[@type='list']")) == 4
        assert all(c.get('limit') == '13' for c in home.findall('.//content'))
        for window_id, (_, categories) in LIBRARIES.items():
            root = windows[window_id]
            assert [root.findtext(f"controls/control[@id='{101 + i}']/label")
                    for i in range(len(categories))] == [c[0] for c in categories]
            assert 'SetFocus($INFO[Window.Property(MediaNoche.SeriesCategory)])' in (
                root.findtext("controls/control[@id='50']/onback"))
            assert root.findtext("controls/control[@id='201']/onup") == '101'
            movie = window_id in (1193, 1194)
            prefix = 'Movie' if movie else 'TvShow'
            fields = ['Genres', 'Studios', 'Actors']
            if movie:
                fields.append('Directors')
            fields.append('Years')
            for index, field in enumerate(fields):
                assert root.findtext(f"controls/control[@id='{401+index}']/onclick") == (
                    f'ActivateWindow(Videos,{prefix}{field},return)')
            assert root.find("controls/control[@id='161']") is None
            assert root.findtext("controls/control[@id='50']/onup") == '401'
            assert root.findtext("controls/control[@id='101']/onup") == '401'
        includes = ET.parse(directory / 'Includes.xml').getroot()
        for name in ('defaultcontroltrue', 'defaultcontrolfalse'):
            action = includes.find(f"include[@name='{name}']/onload")
            assert action.text == 'ReplaceWindow(1191)'
            assert action.get('condition') == (
                'Window.IsActive(Home) + !Skin.HasSetting(medianoche.nativehome)')
        preferences = ET.tostring(windows[1195], encoding='unicode')
        assert 'Skin.SetBool(medianoche.nativehome)' in preferences
        assert 'Skin.Reset(medianoche.nativehome)' in preferences
        assert 'ReplaceWindow(Home)' in preferences
        print(report)
        print('PASS: six windows, routes, focus targets, fonts, bounds, Home preservation and classic mode')


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
