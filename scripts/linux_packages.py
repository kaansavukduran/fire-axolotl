# SPDX-License-Identifier: MPL-2.0
"""Package a verified native browser as actual Linux AppImage and Debian files."""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
from verify_native_package import verify

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'linux-packaging.json').read_text())
VERSION = json.loads((ROOT / 'release.json').read_text())['version']


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inputs():
    cache = ROOT / 'work/appimage-inputs'
    cache.mkdir(parents=True, exist_ok=True)
    for name, record in PIN['inputs'].items():
        path = cache / name
        if not path.exists():
            temporary = path.with_suffix('.download')
            try:
                with urllib.request.urlopen(record['url'], timeout=60) as response:
                    data = response.read(25_000_001)
                if len(data) > 25_000_000:
                    raise ValueError('Packaging input exceeds the reviewed limit')
                temporary.write_bytes(data)
                if digest(temporary) != record['sha256']:
                    raise ValueError(f'Packaging input hash mismatch: {name}')
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)
        if digest(path) != record['sha256']:
            raise ValueError(f'Packaging input hash mismatch: {name}')
    return cache


def license_text(archive, names):
    with tarfile.open(archive) as source:
        members = source.getmembers()
        for name in names:
            candidates = [m for m in members if m.isfile() and len(Path(m.name).parts) == 2 and Path(m.name).name == name]
            if len(candidates) == 1:
                return source.extractfile(candidates[0]).read()
    raise ValueError(f'License missing from {archive}')


def support_sources(cache, destination, notices):
    sources = {name: cache / name for name in PIN['inputs'] if name.endswith('-source')}
    instructions = b'''AppImage type2 runtime and library source/support materials.
Runtime commit and exact download hashes: linux-packaging.json.
The runtime is MIT; its libfuse 3.15.0 dependency is LGPL and squashfuse is BSD.
Runtime source includes the libfuse patch and full linker/build scripts.
Use runtime-source/scripts/common/install-dependencies.sh with the supplied
libfuse and squashfuse source, then scripts/build-runtime.sh to rebuild/relink.
See the upstream BUILD.md for the Alpine 3.21 build environment and Docker flow.
musl/zstd/zlib sources and notices accompany their permissive library licenses.
The engine's applied source is the separate fire-axolotl-applied-source archive.
The AppImage packing tool runs during packaging and is not embedded as payload.
No private signing key is included. This is not a signed browser update channel.
'''
    with destination.open('wb') as raw, gzip.GzipFile(fileobj=raw, filename='', mode='wb', mtime=0) as compressed, tarfile.open(fileobj=compressed, mode='w|') as archive:
        data = {'README-SOURCE.txt': instructions, 'linux-packaging.json': (ROOT / 'linux-packaging.json').read_bytes()}
        data.update({name + ('.tar.xz' if name == 'libfuse-source' else '.tar.gz'): path.read_bytes() for name, path in sources.items()})
        for name, body in sorted(data.items()):
            item = tarfile.TarInfo(name)
            item.size, item.mode, item.mtime = len(body), 0o644, 0
            archive.addfile(item, io.BytesIO(body))
    licenses = {'runtime': ['LICENSE'], 'libfuse': ['LGPL2.txt', 'COPYING.LIB', 'LICENSE'], 'squashfuse': ['LICENSE'], 'musl': ['COPYRIGHT'], 'zstd': ['LICENSE'], 'zlib': ['zlib.h', 'README'], 'mimalloc': ['LICENSE']}
    notices.mkdir(parents=True, exist_ok=True)
    for name, alternatives in licenses.items():
        (notices / (name + '.txt')).write_bytes(license_text(cache / (name + '-source'), alternatives))


def package(native, output):
    native, output = native.resolve(), output.resolve()
    report = verify(native)
    output.mkdir(parents=True, exist_ok=True)
    stage = ROOT / 'work/linux-package-stage'
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    with tarfile.open(native) as archive:
        if any(member.mode & 0o6000 for member in archive.getmembers()):
            raise ValueError('Unexpected privileged file in native payload')
        archive.extractall(stage / 'native', filter='data')
    payloads = list((stage / 'native').glob('*/application.ini'))
    if len(payloads) != 1:
        raise ValueError('Expected exactly one native browser')
    payload = payloads[0].parent
    with (payload / 'fire-axolotl').open('rb') as executable:
        header = executable.read(20)
    if header[:6] != b'\x7fELF\x02\x01' or header[18:20] != b'\x3e\x00':
        raise ValueError('Expected a real x86_64 native executable')
    appdir = stage / 'FireAxolotl.AppDir'
    library = appdir / 'usr/lib/fire-axolotl-preview'
    shutil.copytree(payload, library, symlinks=True)
    binary_dir = appdir / 'usr/bin'
    binary_dir.mkdir(parents=True)
    (binary_dir / 'fire-axolotl-preview').symlink_to('../lib/fire-axolotl-preview/fire-axolotl')
    desktop = '''[Desktop Entry]
Type=Application
Name=Fire Axolotl Developer Preview
Name[tr]=Fire Axolotl Geliştirici Önizlemesi
Comment=Experimental browser; automatic updates are disabled
Comment[tr]=Deneysel tarayıcı; otomatik güncellemeler kapalı
Exec=fire-axolotl-preview %u
Icon=fire-axolotl-preview
Terminal=false
Categories=Network;WebBrowser;
MimeType=text/html;x-scheme-handler/http;x-scheme-handler/https;
StartupWMClass=fire-axolotl
'''
    applications = appdir / 'usr/share/applications'
    applications.mkdir(parents=True)
    (applications / 'fire-axolotl-preview.desktop').write_text(desktop)
    (appdir / 'fire-axolotl-preview.desktop').write_text(desktop)
    icon = appdir / 'usr/share/pixmaps/fire-axolotl-preview.png'
    icon.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / 'branding/icon-128.png', icon)
    shutil.copyfile(icon, appdir / 'fire-axolotl-preview.png')
    (appdir / '.DirIcon').symlink_to('fire-axolotl-preview.png')
    (appdir / 'AppRun').write_text('''#!/bin/sh
set -eu
aion_appdir="${APPDIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}"
exec "$aion_appdir/usr/lib/fire-axolotl-preview/fire-axolotl" "$@"
''')
    (appdir / 'AppRun').chmod(0o755)
    cache = inputs()
    support = output / f'fire-axolotl-{VERSION}-appimage-support-source.tar.gz'
    support_sources(cache, support, appdir / 'usr/share/doc/fire-axolotl-preview/licenses')
    documentation = appdir / 'usr/share/doc/fire-axolotl-preview'
    shutil.copyfile(ROOT / 'LICENSE', documentation / 'copyright')
    shutil.copyfile(ROOT / 'THIRD_PARTY_NOTICES.md', documentation / 'THIRD_PARTY_NOTICES.md')
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', '1794243600'))
    appdir.chmod(0o755)
    for path in sorted(appdir.rglob('*')):
        if not path.is_symlink():
            path.chmod(0o755 if path.is_dir() or path.stat().st_mode & 0o111 else 0o644)
            os.utime(path, (epoch, epoch))
    env = dict(os.environ, ARCH='x86_64', APPIMAGE_EXTRACT_AND_RUN='1', SOURCE_DATE_EPOCH=str(epoch))
    (cache / 'appimagetool').chmod(0o755)
    image = output / f'fire-axolotl-{VERSION}-linux-x86_64.AppImage'
    subprocess.run([str(cache / 'appimagetool'), '--runtime-file', str(cache / 'runtime'), '--comp', 'zstd', '--mksquashfs-opt=-processors', '--mksquashfs-opt=2', str(appdir), str(image)], env=env, check=True)
    image.chmod(0o755)
    debroot = stage / 'deb'
    shutil.copytree(appdir / 'usr', debroot / 'usr', symlinks=True)
    debroot.chmod(0o755)
    control = debroot / 'DEBIAN'
    control.mkdir()
    (control / 'control').write_text(f'''Package: fire-axolotl-preview
Version: {VERSION.replace('-dev.', '~dev')}
Section: web
Priority: optional
Architecture: amd64
Maintainer: Fire Axolotl contributors
Depends: libc6 (>= 2.38), libstdc++6 (>= 13.1), libgtk-3-0t64, libasound2t64, libdbus-1-3, libx11-xcb1, libxt6t64
Homepage: https://github.com/kaansavukduran/fire-axolotl
Description: Fire Axolotl experimental browser
 Developer preview based on Firefox ESR. Automatic updates are disabled.
 Separate browser identity and profile; not a stable daily-use release.
''')
    for path in debroot.rglob('*'):
        if not path.is_symlink():
            path.chmod(0o755 if path.is_dir() or path.stat().st_mode & 0o111 else 0o644)
            os.utime(path, (epoch, epoch))
    deb = output / f'fire-axolotl-{VERSION}-linux-amd64.deb'
    subprocess.run(['dpkg-deb', '--root-owner-group', '--build', str(debroot), str(deb)], env=env, check=True)
    package_report = {'native': report, 'version': VERSION, 'architecture': 'x86_64', 'runtime': PIN, 'files': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in [image, deb, support]}, 'limits': 'Developer preview; updater disabled. Ubuntu 24.04 x86_64 is the clean-install test target. Other platforms are not provided.'}
    (output / 'linux-package-report.json').write_text(json.dumps(package_report, indent=2) + '\n')
    print(json.dumps(package_report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    package(args.native, args.output)
