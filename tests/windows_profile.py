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
    command = f'$ErrorActionPreference="Stop"; ConvertTo-Json -Compress -InputObject @((Get-Process -Id {browser_pid}).Modules | Where-Object {{$_.ModuleName -match "^(msvcp140|vcruntime140|vcruntime140_1)\\.dll$"}} | Select-Object ModuleName,FileName)'
    modules = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-NonInteractive', '-Command', command], text=True))
    expected = {'msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll'}
    assert {m['ModuleName'].lower() for m in modules} == expected
    pins = json.loads((ROOT / 'windows-runtime.json').read_text())
    runtime = {}
    for module in modules:
        local = Path(module['FileName']).resolve()
        assert local.parent == Path(options.binary_location).resolve().parent, local
        digest = hashlib.sha256(local.read_bytes()).hexdigest()
        assert digest == pins['files'][local.name.lower()]['sha256']
        runtime[local.name.lower()] = {'path': str(local), 'sha256': digest}
    path = Path(driver.execute_script('return Services.dirsvc.get("DefProfRt",Ci.nsIFile).path;')).resolve()
    firefox = Path(os.environ['APPDATA']) / 'Mozilla/Firefox'
    assert not path.is_relative_to(firefox.resolve())
    assert 'fireaxolotl' in str(path).replace(' ', '').lower()
    path.mkdir(parents=True, exist_ok=True)
    marker = path / f'installer-data-check-{uuid.uuid4()}.txt'
    marker.write_text('Kullanıcı verisi: Çç Ğğ İı Öö Şş Üü', encoding='utf-8')
    (ROOT / 'work/windows-installer-test/profile-probe.json').write_text(json.dumps({'default_profile_root': str(path), 'marker': str(marker), 'marker_sha256': hashlib.sha256(marker.read_bytes()).hexdigest(), 'application_local_crt': runtime}, indent=2) + '\n')
    print('Installed product has an independent default profile; user-data sentinel created')
finally:
    driver.quit()
