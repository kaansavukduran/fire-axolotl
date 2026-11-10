# SPDX-License-Identifier: MPL-2.0
"""Resolve the actual XUL imports using only the bundled dynamic CRT copies."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from windows_runtime import PIN, augment, pe_imports, CRT_NAME
from verify_native_package import verify

if '--package' in sys.argv:
    package = next((ROOT / 'work/windows-inputs').glob('*.win64.zip'))
    verify(package)
    augment(package)
    extracted = ROOT / 'work/runtime-fallback-browser'
    with zipfile.ZipFile(package) as archive:
        archive.extractall(extracted)
    binary = next(extracted.rglob('fire-axolotl.exe'))
else:
    binary = Path(os.environ['AION_NATIVE_BINARY'])
directory = binary.resolve().parent
build = ROOT / 'work/runtime-fallback-probe'
build.mkdir(parents=True, exist_ok=True)
for name in ['windows_runtime_probe.cpp', 'windows_runtime_probe.vcxproj']:
    shutil.copyfile(ROOT / 'tests' / name, build / name)
vswhere = Path(os.environ['ProgramFiles(x86)']) / 'Microsoft Visual Studio/Installer/vswhere.exe'
vs = Path(subprocess.check_output([str(vswhere), '-latest', '-products', '*', '-requires', 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64', '-property', 'installationPath'], text=True).strip())
subprocess.run([str(vs / 'MSBuild/Current/Bin/MSBuild.exe'), str(build / 'windows_runtime_probe.vcxproj'), '/p:Configuration=Release', '/p:Platform=x64', '/verbosity:minimal'], check=True)
probe = build / 'bin/runtime-probe.exe'
machine, imports = pe_imports(probe.read_bytes())
assert machine == 0x8664 and not any(CRT_NAME.match(name) for name in imports), 'The probe itself must not depend on a dynamic Visual C++ runtime'
first = ['vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll']
order = first + [name for name in PIN['files'] if name not in first]
result = subprocess.run([str(probe), str(directory), *order], check=True, capture_output=True, text=True)
loaded = {}
for line in result.stdout.splitlines():
    name, path = line.split('|', 1)
    file = Path(path).resolve()
    assert file.parent == directory
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    assert digest == PIN['files'][name]['sha256']
    loaded[name] = {'path': str(file), 'sha256': digest}
assert set(loaded) == set(PIN['files'])
out = ROOT / 'work/windows-installer-test'
out.mkdir(parents=True, exist_ok=True)
(out / 'runtime-fallback.json').write_text(json.dumps({'local_crt_fallback_verified': True, 'core_library_loaded': True, 'prefer_system32_mitigation_enabled': True, 'probe_has_no_dynamic_crt_imports': True, 'loaded': loaded}, indent=2) + '\n')
print('Static probe loaded actual xul.dll with every pinned dynamic CRT from the application directory, with PreferSystem32 enabled')
