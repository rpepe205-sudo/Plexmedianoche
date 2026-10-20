"""Check the installed ARM32 archives before spending time compiling Kodi."""

import pathlib
import re
import subprocess
import sys


def check(root):
    prefixes = [
        path for path in root.glob('arm-linux-androideabi-*')
        if path.is_dir() and (path / 'lib').is_dir()
    ]
    if len(prefixes) != 1:
        raise SystemExit(f'Expected one ARM32 dependency prefix in {root}: {prefixes}')
    print(f'ARM32 dependency prefix: {prefixes[0]}', flush=True)
    for name in ('libzip.a', 'libmicrohttpd.a'):
        archive = prefixes[0] / 'lib' / name
        if not archive.is_file() or archive.stat().st_size == 0:
            raise SystemExit(f'Missing installed archive: {archive}')
        result = subprocess.run(
            ['nm', '-u', str(archive)], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        forbidden = sorted(set(re.findall(
            r'\b(?:gnutls_|nettle_|mbedtls_)[A-Za-z0-9_]+', result.stdout
        )))
        if forbidden:
            raise SystemExit(f'{archive}: unexpected crypto references: {forbidden}')
        print(f'{archive}: OK', flush=True)


if __name__ == '__main__':
    check(pathlib.Path(sys.argv[1]))
