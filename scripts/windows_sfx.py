# SPDX-License-Identifier: MPL-2.0
"""Rebuild the public-domain extraction wrapper with our own icon and branding."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MAGIC = b"7z\xbc\xaf'\x1c"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare(sdk, icon):
    shutil.copyfile(icon, sdk / 'firefox/setup.ico')
    resource = sdk / 'firefox/resource.rc'
    text = resource.read_text()
    for key, previous, replacement in [('CompanyName', 'Mozilla', 'Fire Axolotl'), ('FileDescription', 'Firefox', 'Fire Axolotl Setup'), ('ProductName', 'Firefox', 'Fire Axolotl')]:
        old, new = f'VALUE "{key}", "{previous}"', f'VALUE "{key}", "{replacement}"'
        if new not in text:
            if text.count(old) != 1:
                raise ValueError(f'Unexpected upstream SFX resource: {key}')
            text = text.replace(old, new)
    resource.write_text(text)
    project = sdk / 'firefox/SFXSetup.vcxproj'
    text = project.read_text()
    # VS 2022 adds C5286 for the SDK's existing enum-to-enum conversions.
    warning = '<DisableSpecificWarnings>5286;%(DisableSpecificWarnings)</DisableSpecificWarnings>'
    if warning not in text:
        text = text.replace('<ClCompile>', '<ClCompile>\n      ' + warning)
        project.write_text(text)


def extract(source, destination):
    import zstandard
    prefix = 'other-licenses/7zstub/'
    tag = None
    with source.open('rb') as raw, zstandard.ZstdDecompressor().stream_reader(raw) as stream:
        with tarfile.open(fileobj=stream, mode='r|') as archive:
            for member in archive:
                name = member.name.removeprefix('./')
                if name == 'browser/installer/windows/app.tag':
                    tag = archive.extractfile(member).read()
                if not name.startswith(prefix) or member.isdir():
                    continue
                relative = PurePosixPath(name[len(prefix):])
                if not member.isfile() or relative.is_absolute() or '..' in relative.parts or any(':' in part for part in relative.parts):
                    raise ValueError('Unsafe SFX source member')
                path = destination.joinpath(*relative.parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.extractfile(member).read())
    if not tag or b'Fire Axolotl' not in tag:
        raise ValueError('Reviewed Fire Axolotl installer tag missing')
    return tag


def build(sdk):
    vswhere = Path(os.environ['ProgramFiles(x86)']) / 'Microsoft Visual Studio/Installer/vswhere.exe'
    installation = subprocess.check_output([str(vswhere), '-latest', '-products', '*', '-requires', 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64', '-property', 'installationPath'], text=True).strip()
    msbuild = Path(installation) / 'MSBuild/Current/Bin/MSBuild.exe'
    if not installation or not msbuild.is_file():
        raise ValueError('Visual Studio C++ build tools required')
    command = [str(msbuild), str(sdk / 'firefox/SFXSetup.vcxproj'), '/m', '/p:Configuration=ReleaseD', '/p:Platform=Win32', '/p:PlatformToolset=v143', '/p:WindowsTargetPlatformVersion=10.0', f'/p:SolutionDir={sdk / "firefox"}{os.sep}', '/verbosity:minimal']
    subprocess.run(command, check=True)
    stub = sdk / 'firefox/Win32/ReleaseD/7zSD.Win32.sfx'
    data = stub.read_bytes()
    if len(data) < 50_000 or data[:2] != b'MZ':
        raise ValueError('Expected a real compiled Windows extraction wrapper')
    return data, command


def replace_stub(installer, tag, stub):
    if not tag.startswith(b';!@Install@!UTF-8!') or b'Fire Axolotl' not in tag or not tag.rstrip().endswith(b';!@InstallEnd@!'):
        raise ValueError('Invalid reviewed installer tag')
    if installer[:2] != b'MZ' or stub[:2] != b'MZ' or installer.count(tag) != 1:
        raise ValueError('Expected exactly one full tag boundary in a native PE installer')
    tail = installer.split(tag, 1)[1]
    if not tail.startswith(MAGIC):
        raise ValueError('Expected the unchanged native 7z payload immediately after its tag')
    return stub + tag + tail, digest(tail)


def frontend_payload(installer, tag, native, work, repack=True):
    directory = work / 'ui-payload'
    if directory.exists():
        raise ValueError('The installer repack directory must be new')
    directory.mkdir()
    sevenzip = shutil.which('7z') or str(Path(os.environ['ProgramFiles']) / '7-Zip/7z.exe')
    if not Path(sevenzip).is_file():
        raise ValueError('The Windows runner 7-Zip build tool is required')
    # Validate the complete tag boundary, then extract only the reviewed inner
    # NSIS installer. Never execute an installer during this packaging step.
    replace_stub(installer, tag, b'MZboundary-check')
    original_archive = directory / 'original.7z'
    original_archive.write_bytes(installer.split(tag, 1)[1])
    subprocess.run([sevenzip, 'e', str(original_archive), 'setup.exe', '-o' + str(directory), '-y', '-bso0'], check=True)
    inner = directory / 'setup.exe'
    inner_hash = digest(inner.read_bytes())
    if inner.read_bytes()[:2] != b'MZ':
        raise ValueError('Native NSIS installer missing')
    if not repack:
        return original_archive.read_bytes(), inner_hash
    with zipfile.ZipFile(native) as archive:
        roots = [name.rsplit('/', 1)[0] for name in archive.namelist() if name.endswith('/application.ini')]
        if len(roots) != 1:
            raise ValueError('One reviewed runtime is required')
        archive.extractall(directory / 'runtime')
    shutil.move(str(directory / 'runtime' / roots[0]), directory / 'core')
    output = directory / 'app.7z'
    subprocess.run([sevenzip, 'a', '-t7z', str(output), 'core', 'setup.exe', '-m0=LZMA2', '-mx=7', '-mmt=2', '-bso0'], cwd=directory, check=True)
    subprocess.run([sevenzip, 't', str(output), '-bso0'], check=True)
    if digest(inner.read_bytes()) != inner_hash:
        raise ValueError('Inner native NSIS installer changed')
    return output.read_bytes(), inner_hash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdk', type=Path)
    args = parser.parse_args()
    work = ROOT / 'work/windows-sfx'
    work.mkdir(parents=True, exist_ok=True)
    if args.sdk:
        sdk = work / 'sdk'
        shutil.copytree(args.sdk, sdk, dirs_exist_ok=True)
        tag = None
    else:
        sdk = work / 'sdk'
        tag = extract(ROOT / 'work/windows-inputs/fire-axolotl-windows-applied-source.tar.zst', sdk)
    prepare(sdk, ROOT / 'branding/aion.ico')
    stub, command = build(sdk)
    (work / 'fire-axolotl-setup.sfx').write_bytes(stub)
    if tag is None:
        print('Original-brand Windows extraction wrapper compiled')
        return
    installers = list((ROOT / 'dist/windows-release').glob('*-Setup.exe'))
    if len(installers) != 1:
        raise ValueError('One verified native installer is required')
    installer = installers[0]
    original = installer.read_bytes()
    native = installer.with_name(installer.name.removesuffix('-Setup.exe') + '.zip')
    overlay = json.loads((installer.parent / 'newtab-ui-overlay.json').read_text())
    repack = overlay['only_native_member_changed'] is not None
    runtime_report = installer.parent / 'windows-runtime-build.json'
    if runtime_report.exists():
        repack = repack or bool(json.loads(runtime_report.read_text())['added'])
    payload, inner_hash = frontend_payload(original, tag, native, work, repack=repack)
    updated = stub + tag + payload
    payload_sha256 = digest(payload)
    installer.write_bytes(updated)
    dist = installer.parent
    report = {'original_installer_sha256': digest(original), 'installer_sha256': digest(updated), 'native_7z_payload_unchanged': not repack, 'frontend_zip_sha256': digest(native.read_bytes()), 'inner_nsis_preserved': True, 'inner_nsis_sha256': inner_hash, 'native_7z_payload_sha256': payload_sha256, 'sfx_sha256': digest(stub), 'icon_sha256': digest((ROOT / 'branding/aion.ico').read_bytes()), 'sdk_license': 'LZMA SDK 18.05 public domain; Mozilla notices retained', 'build_command': command}
    (dist / 'windows-sfx-build.json').write_text(json.dumps(report, indent=2) + '\n')
    with zipfile.ZipFile(dist / 'windows-sfx-corresponding-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(sdk.rglob('*')):
            if path.is_file() and not set(path.relative_to(sdk).parts).intersection({'Win32', 'ARM64', '.vs'}) and path.suffix.lower() not in {'.sfx', '.exe', '.obj', '.pdb'}:
                archive.write(path, str(Path('7zstub') / path.relative_to(sdk)))
        archive.write(Path(__file__), 'windows_sfx.py')
        archive.writestr('README.txt', 'Public-domain LZMA SDK 18.05 extraction wrapper, with Mozilla changes and original notices. Icon and product strings replaced with Fire Axolotl. Build using windows_sfx.py --sdk ./7zstub from the packaging-source checkout. Full native browser source is distributed separately. windows-sfx-build.json records the actual command, unchanged inner NSIS installer digest and updated UI payload archive digest.\n')
    print('Original-brand SFX rebuilt; unchanged native NSIS installer packages the audited UI overlay')


if __name__ == '__main__':
    main()
