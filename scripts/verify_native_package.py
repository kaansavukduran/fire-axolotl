# SPDX-License-Identifier: MPL-2.0
"""Verify native package identity and shipped privacy/component source files."""
import argparse
import configparser
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def verify(package):
    pin = json.loads((ROOT / 'upstream.json').read_text())
    component = json.loads((ROOT / 'components.json').read_text())['ublock-origin']
    with tarfile.open(package) as archive:
        members = archive.getmembers()
        for member in members:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts:
                raise ValueError('Unsafe package path')
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate package paths')
        ini_names = [name for name in names if name.endswith('/application.ini')]
        if len(ini_names) != 1:
            raise ValueError('Expected one packaged application.ini')
        prefix = ini_names[0].removesuffix('/application.ini')

        def read(relative):
            member = archive.getmember(prefix + '/' + relative)
            if not member.isfile():
                raise ValueError(f'Expected a regular packaged file: {relative}')
            return archive.extractfile(member).read()

        ini = configparser.ConfigParser()
        ini.read_string(read('application.ini').decode())
        app = ini['App']
        if app['ID'] != '{75450dd9-387d-4289-8b23-7ad6609fa530}' or app['Name'] != 'FireAxolotl':
            raise ValueError('Native package has an upstream or unexpected identity')
        if app['Version'].removesuffix('esr') != pin['version'].removesuffix('esr'):
            raise ValueError('Native package does not match the reviewed ESR pin')
        if json.loads(read('distribution/policies.json')) != json.loads((ROOT / 'browser/policies.json').read_text()):
            raise ValueError('Packaged privacy policy differs from the reviewed policy')
        receipt = json.loads(read('distribution/sources/ublock-origin.json'))
        if any(receipt.get(key) != component[key] for key in component):
            raise ValueError('Packaged component inventory does not match the reviewed pin')
        source_bytes = read(f'distribution/sources/ublock-origin-{component["version"]}-corresponding-source.tar.gz')
        if hashlib.sha256(source_bytes).hexdigest() != receipt['corresponding_source_sha256']:
            raise ValueError('Packaged corresponding source hash mismatch')
        with tarfile.open(fileobj=io.BytesIO(source_bytes)) as source:
            if not {'uBlock/LICENSE.txt', 'uAssets/main/LICENSE', 'README-SOURCE.txt'} <= set(source.getnames()):
                raise ValueError('Component source/licenses missing from native package')
    with Path(package).open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    report = {'package': Path(package).name, 'sha256': digest, 'upstream': pin['version'], 'app_id': app['ID'], 'component': component['version'], 'status': 'package-structure-verified', 'limits': 'Does not replace native startup, platform signing or secure-update tests.'}
    Path(str(package) + '.sha256').write_text(f'{digest}  {Path(package).name}\n')
    Path(str(package) + '.verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    verify(parser.parse_args().package)
