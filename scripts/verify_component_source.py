# SPDX-License-Identifier: MPL-2.0
"""Rebuild uBO from the distributed source and compare every package file."""
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from fetch_components import CACHE, fetch_all, sha256


def verify():
    signed, source = fetch_all()
    with tempfile.TemporaryDirectory(prefix='source-roundtrip-', dir=CACHE.parent) as temporary:
        root = Path(temporary)
        with tarfile.open(source) as archive:
            archive.extractall(root, filter='data')
        assets = root / 'uBlock/dist/build/uAssets'
        assets.parent.mkdir(parents=True)
        shutil.copytree(root / 'uAssets', assets)
        with (root / 'build.log').open('w') as log:
            subprocess.run(['bash', 'tools/make-firefox.sh', 'all'], cwd=root / 'uBlock', stdout=log, stderr=subprocess.STDOUT, check=True)
        with zipfile.ZipFile(signed) as official, zipfile.ZipFile(root / 'uBlock/dist/build/uBlock0.firefox.xpi') as rebuilt:
            expected = {name for name in official.namelist() if not name.startswith('META-INF/') and not name.endswith('/') and name != 'mozilla-recommendation.json'}
            actual = {name for name in rebuilt.namelist() if not name.endswith('/')}
            if actual != expected:
                raise ValueError(f'Unexpected rebuilt package files: missing={expected-actual}, extra={actual-expected}')
            for name in sorted(expected):
                first, second = official.read(name), rebuilt.read(name)
                if name == 'manifest.json':
                    if json.loads(first) != json.loads(second):
                        raise ValueError('Rebuilt manifest differs from signed package')
                elif first != second:
                    raise ValueError(f'Rebuilt component differs: {name}')
        report = {'source_sha256': sha256(source), 'compared_files': len(expected), 'status': 'matching', 'excluded': ['META-INF/ (Mozilla signatures)', 'mozilla-recommendation.json (Mozilla recommendation)'], 'manifest_comparison': 'parsed JSON, ignoring serialization formatting'}
        (CACHE / 'source-verification.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
        return report


if __name__ == '__main__':
    verify()
