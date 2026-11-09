# SPDX-License-Identifier: MPL-2.0
"""Build the same deterministic add-on that the Firefox source overlay embeds."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def package(destination=None):
    source = ROOT / 'browser/extension'
    version = json.loads((source / 'manifest.json').read_text())['version']
    output = Path(destination or ROOT / f'dist/fire-axolotl-{version}-developer-addon.xpi')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in sorted(source.rglob('*')):
            if not file.is_file():
                continue
            info = zipfile.ZipInfo(file.relative_to(source).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file.read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + '.sha256').write_text(f'{digest}  {output.name}\n')
    print(output)
    return output


if __name__ == '__main__':
    package()
