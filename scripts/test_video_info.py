"""Static regression checks against the actual pinned upstream XML files.

Usage: python scripts/test_video_info.py /path/to/original/skin
These checks do not start Kodi.
"""
import copy
from pathlib import Path
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

from prepare_skin import prepare_video_info


def check(upstream):
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        (base / '1080i').mkdir()
        for name in ('Includes.xml', 'Includes_DialogVideoInfo.xml'):
            shutil.copyfile(upstream / name, base / '1080i' / name)
        original = ET.parse(base / '1080i/Includes.xml').getroot()
        before = original.find("include[@name='DialogVideoInfoNavigation']")
        result = prepare_video_info(base)
        root = ET.parse(base / '1080i/Includes.xml').getroot()
        after = root.find("include[@name='DialogVideoInfoNavigation']")
        old = {c.get('id'): c for c in before.findall('.//control')}
        new = {c.get('id'): c for c in after.findall('.//control')}
        assert old.keys() == new.keys(), 'Control IDs changed'
        for identity, control in new.items():
            if identity == '9000':
                continue
            assert control.findtext('label')
            assert control.findtext('font') == 'Tiny'
            assert control.findtext('textcolor') == 'FFFFFFFF'
            assert not any(n.text == 'buttondimensions' or n.get('content') == 'buttontextures'
                           for n in control.findall('include'))
            if identity not in ('1223', '1224', '9001'):
                for tag in ('onclick', 'visible', 'selected', 'onfocus'):
                    assert [ET.tostring(n) for n in control.findall(tag)] == [
                        ET.tostring(n) for n in old[identity].findall(tag)]
        for identity in ('1223', '1224'):
            control = new[identity]
            assert '!String.IsEmpty(ListItem.Trailer)' in control.findtext('visible')
            assert 'bingie' not in ET.tostring(control).decode()
            assert 'imdb.trailers' not in ET.tostring(control).decode()
        # Other windows using the shared templates must remain unchanged.
        for include in original.findall('include'):
            name = include.get('name')
            if name and name != 'DialogVideoInfoNavigation':
                assert ET.tostring(include) == ET.tostring(root.find(f"include[@name='{name}']"))
        print(result)
        print('PASS: native IDs/actions, persistent labels, trailer gating, unrelated includes')


if __name__ == '__main__':
    check(Path(sys.argv[1]))
