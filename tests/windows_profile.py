# SPDX-License-Identifier: MPL-2.0
"""Check the installed browser's real default product profile namespace."""
import json
import hashlib
import os
from pathlib import Path
import uuid
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

ROOT = Path(__file__).resolve().parents[1]
options = Options()
options.binary_location = os.environ['AION_NATIVE_BINARY']
options.add_argument('-headless')
options.accept_insecure_certs = False
options.set_preference('remote.prefs.recommended', False)
options.set_preference('browser.shell.checkDefaultBrowser', False)
driver = webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access']))
try:
    driver.set_context('chrome')
    assert driver.execute_script('return Services.appinfo.ID;') == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
    assert driver.execute_script('return Cc["@mozilla.org/default-agent;1"].getService(Ci.nsIDefaultAgent).agentDisabled();') is True
    browser_pid = int(driver.execute_script('return Services.appinfo.processID;'))
    command = r'''$ErrorActionPreference="Stop";
      $items=@(); foreach ($m in (Get-Process -Id __PID__).Modules) {
        if ($m.ModuleName -match "^(msvcp140|vcruntime140|vcruntime140_1)\.dll$") {
          $signature=Get-AuthenticodeSignature $m.FileName; $v=(Get-Item $m.FileName).VersionInfo;
          $items+=@{ModuleName=$m.ModuleName;FileName=$m.FileName;Signature=[string]$signature.Status;Signer=$signature.SignerCertificate.Subject;Version=@($v.FileMajorPart,$v.FileMinorPart,$v.FileBuildPart,$v.FilePrivatePart)}
        }
      }; ConvertTo-Json -Compress -InputObject @($items)'''.replace('__PID__', str(browser_pid))
    modules = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-NonInteractive', '-Command', command], text=True))
    expected = {'msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll'}
    assert {m['ModuleName'].lower() for m in modules} == expected
    pins = json.loads((ROOT / 'windows-runtime.json').read_text())
    runtime = {}
    for module in modules:
        local = Path(module['FileName']).resolve()
        digest = hashlib.sha256(local.read_bytes()).hexdigest()
        if local.parent == Path(options.binary_location).resolve().parent:
            assert digest == pins['files'][local.name.lower()]['sha256']
            source = 'application-local'
        else:
            # Firefox deliberately prefers compatible newer System32 images.
            # Keep that mitigation; verify the system selection instead.
            assert local.parent == (Path(os.environ['WINDIR']) / 'System32').resolve()
            assert module['Signature'] == 'Valid' and 'O=Microsoft Corporation' in module['Signer']
            assert tuple(module['Version']) >= tuple(int(n) for n in pins['version'].split('.'))
            source = 'compatible-microsoft-system-runtime'
        runtime[local.name.lower()] = {'path': str(local), 'sha256': digest, 'source': source}
    path = Path(driver.execute_script('return Services.dirsvc.get("DefProfRt",Ci.nsIFile).path;')).resolve()
    firefox = Path(os.environ['APPDATA']) / 'Mozilla/Firefox'
    assert not path.is_relative_to(firefox.resolve())
    assert 'fireaxolotl' in str(path).replace(' ', '').lower()
    path.mkdir(parents=True, exist_ok=True)
    marker = path / f'installer-data-check-{uuid.uuid4()}.txt'
    marker.write_text('Kullanıcı verisi: Çç Ğğ İı Öö Şş Üü', encoding='utf-8')
    (ROOT / 'work/windows-installer-test/profile-probe.json').write_text(json.dumps({'default_profile_root': str(path), 'marker': str(marker), 'marker_sha256': hashlib.sha256(marker.read_bytes()).hexdigest(), 'verified_crt_modules': runtime}, indent=2) + '\n')
    print('Installed product has an independent default profile; user-data sentinel created')
finally:
    driver.quit()
