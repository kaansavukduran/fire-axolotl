# SPDX-License-Identifier: MPL-2.0
"""Upgrade the actual historical Setup to the new one using synthetic data only."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import winreg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work/windows-upgrade'
WORK.mkdir(parents=True, exist_ok=True)
OLD_URL = 'https://github.com/kaansavukduran/fire-axolotl/releases/download/v0.3.1-dev.20261110-windows/fire-axolotl-0.3.1-dev.20261110.1-windows-x86_64-Setup.exe'
OLD_SHA = '120cfbae0e815247da7f66ceb7fb6767adb2b3468f705475c04d012f45ed86ce'
destination = Path(os.environ['RUNNER_TEMP']) / 'FireAxolotlUpgrade'
assert not destination.exists(), 'The synthetic upgrade installation target must be fresh'
binary = destination / 'fire-axolotl.exe'
profile = Path(tempfile.mkdtemp(prefix='profile-', dir=WORK))
marker = profile / 'user-data-sentinel.txt'
marker.write_text('Güncelleme · Çç Ğğ İı Öö Şş Üü', encoding='utf-8')
marker_sha = hashlib.sha256(marker.read_bytes()).hexdigest()
pwsh = shutil.which('pwsh') or 'powershell'
ini = WORK / 'install.ini'
ini.write_text(f'[Install]\nInstallDirectoryPath={destination}\nDesktopShortcut=false\nStartMenuShortcuts=false\nTaskbarShortcut=false\nMaintenanceService=false\nPreventRebootRequired=true\n')
driver = None
report = {'mode': 'actual-offline-installer-cross-version', 'fixture_only': True, 'passed': False}


def choices():
    result = {}
    for scheme in ['http', 'https']:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\{scheme}\UserChoice') as key:
                result[scheme] = winreg.QueryValueEx(key, 'ProgId')[0]
        except FileNotFoundError:
            result[scheme] = None
    return result


def install(setup):
    environment = dict(os.environ, AION_UPGRADE_SETUP=str(setup), AION_UPGRADE_INI=str(ini))
    subprocess.run([pwsh, '-NoProfile', '-NonInteractive', '-Command', '$ErrorActionPreference="Stop"; $p=Start-Process -FilePath $env:AION_UPGRADE_SETUP -ArgumentList @("/S", ("/INI="+$env:AION_UPGRADE_INI)) -Wait -PassThru; exit $p.ExitCode'], env=environment, check=True, timeout=240)
    assert binary.is_file()


def start():
    options = Options()
    options.binary_location = str(binary)
    options.add_argument('-headless')
    options.add_argument('-profile')
    options.add_argument(str(profile))
    options.accept_insecure_certs = False
    options.set_preference('remote.prefs.recommended', False)
    options.set_preference('browser.shell.checkDefaultBrowser', False)
    # Only the existing local PNG fixture uses Marionette's file-input bridge.
    options.set_preference('dom.file.createInChild', True)
    return webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(WORK / 'geckodriver.log')))


def identity():
    driver.set_context('chrome')
    value = driver.execute_script('return {id:Services.appinfo.ID,version:Services.appinfo.version};')
    assert value['id'] == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
    return value


def companion():
    driver.set_context('chrome')
    uuid = driver.execute_script('return JSON.parse(Services.prefs.getStringPref("extensions.webextensions.uuids"))["aion@fire-axolotl.browser"];')
    assert uuid
    driver.set_context('content')
    return f'moz-extension://{uuid}/'


before_choice = choices()
try:
    old = WORK / 'previous-Setup.exe'
    with urllib.request.urlopen(OLD_URL, timeout=120) as response, old.open('wb') as output:
        while block := response.read(1024 * 1024):
            output.write(block)
    with old.open('rb') as source:
        assert hashlib.file_digest(source, 'sha256').hexdigest() == OLD_SHA
    install(old)
    driver = start()
    before = identity()
    before_tools = driver.execute_async_script('const done=arguments[0];ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonByID("aion@fire-axolotl.browser").then(a=>done(a.version));')
    assert before_tools == "0.3.1"
    driver.execute_script('CustomizableUI.removeWidgetFromArea("downloads-button");')
    assert before['version'].removesuffix('esr') == '153.7.0'
    driver.execute_script('Services.prefs.setIntPref("fireaxolotl.newtabGame.best",37); Services.prefs.setStringPref("fireaxolotl.ui.font","opendyslexic"); Services.prefs.setBoolPref("sidebar.position_start",true); Services.prefs.setBoolPref("sidebar.verticalTabs",true); Services.locale.requestedLocales=["tr"];')
    seeded = driver.execute_async_script('const done=arguments[0]; (async()=>{const info=Cc["@mozilla.org/login-manager/loginInfo;1"].createInstance(Ci.nsILoginInfo);info.init("https://example.invalid","https://example.invalid",null,"upgrade-fixture","local-fixture-not-a-user-password","username","password");await Services.logins.addLoginAsync(info);await ChromeUtils.importESModule("resource://gre/modules/PlacesUtils.sys.mjs").PlacesUtils.bookmarks.insert({parentGuid:"unfiled_____",url:"https://example.invalid/fire-axolotl-upgrade",title:"Güncelleme · Yer imi"});return true;})().then(done);')
    assert seeded
    base = companion()
    driver.get(base + 'popup.html')
    wait = WebDriverWait(driver, 30)
    if driver.find_elements(By.ID, 'tab-containers'):
        wait.until(lambda d: d.execute_script('return document.body.dataset.ready === "true";'))
        driver.find_element(By.ID, 'tab-containers').click()
    wait.until(lambda d: d.find_element(By.ID, 'container-name').is_displayed())
    driver.find_element(By.ID, 'container-name').send_keys('Güncelleme · İş')
    driver.find_element(By.CSS_SELECTOR, '#container-form button').click()
    wait.until(lambda d: 'Güncelleme · İş' in d.find_element(By.ID, 'container').text)
    if driver.find_elements(By.ID, 'tab-translation'): driver.find_element(By.ID, 'tab-translation').click()
    driver.find_element(By.ID, 'source-text').send_keys('Sürüm · ışık')
    driver.find_element(By.ID, 'save-word').click()
    wait.until(lambda d: d.execute_script('return document.getElementById("status").textContent===UI.t("wordSaved");'))
    driver.get(base + 'characters.html')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == 'aion')
    driver.find_element(By.ID, 'character-file').send_keys(str(ROOT / 'branding/icon-256.png'))
    wait.until(lambda d: d.find_element(By.ID, 'character-import').is_enabled())
    driver.find_element(By.ID, 'character-import').click()
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character').startswith('custom-'))
    character = driver.find_element(By.ID, 'character-canvas').get_attribute('data-character')
    driver.quit()
    driver = None
    current = list((ROOT / 'dist/windows-release').glob('*-Setup.exe'))
    assert len(current) == 1
    install(current[0])
    payload = WORK / 'payload.json'
    subprocess.run([sys.executable, str(ROOT / 'scripts/verify_windows_installation.py'), '--evidence-file', str(payload)], env=dict(os.environ, AION_INSTALLED_DIRECTORY=str(destination)), check=True)
    driver = start()
    after = identity()
    after_tools = driver.execute_async_script('const done=arguments[0];ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonByID("aion@fire-axolotl.browser").then(a=>done(a.version));')
    assert after_tools == "0.4.0"
    assert after['version'].removesuffix('esr') == json.loads((ROOT / 'upstream.json').read_text())['version'].removesuffix('esr')
    state = driver.execute_async_script('const done=arguments[0];(async()=>{const b=await ChromeUtils.importESModule("resource://gre/modules/PlacesUtils.sys.mjs").PlacesUtils.bookmarks.fetch({url:"https://example.invalid/fire-axolotl-upgrade"});const logins=await Services.logins.getAllLogins();return {bookmark:b?.title,password:logins.some(l=>l.username==="upgrade-fixture"&&l.password==="local-fixture-not-a-user-password"),best:Services.prefs.getIntPref("fireaxolotl.newtabGame.best"),font:Services.prefs.getStringPref("fireaxolotl.ui.font"),vertical:Services.prefs.getBoolPref("sidebar.verticalTabs"),locale:Services.locale.appLocaleAsBCP47,toolbarCustomized:!CustomizableUI.getWidgetIdsInArea("nav-bar").includes("downloads-button")};})().then(done);')
    assert state == {'bookmark': 'Güncelleme · Yer imi', 'password': True, 'best': 37, 'font': 'opendyslexic', 'vertical': True, 'locale': 'tr', 'toolbarCustomized': True}
    assert companion() == base
    driver.get(base + 'settings.html')
    wait = WebDriverWait(driver, 30)
    wait.until(lambda d: d.find_element(By.ID, 'version').text)
    assert driver.execute_script('return UI.settings.vocabulary.includes("Sürüm · ışık");')
    assert driver.execute_script('return UI.settings.character;') == character
    driver.get(base + 'characters.html')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == character)
    driver.get(base + 'popup.html#containers')
    wait.until(lambda d: d.execute_script('return document.body.dataset.ready === "true";'))
    wait.until(lambda d: 'Güncelleme · İş' in d.find_element(By.ID, 'container').text)
    driver.find_element(By.ID, 'tab-translation').click()
    before_windows = set(driver.window_handles)
    driver.find_element(By.ID, 'native-translation').click()
    translated_window = wait.until(lambda d: next((h for h in d.window_handles if h not in before_windows), None))
    driver.switch_to.window(translated_window)
    wait.until(lambda d: d.current_url.split('#', 1)[0] == 'about:translations')
    bridge_after_upgrade_verified = True
    driver.quit()
    driver = None
    assert hashlib.sha256(marker.read_bytes()).hexdigest() == marker_sha
    assert choices() == before_choice
    report.update(passed=True, toolbar_customization_preserved=True, from_identity=before, to_identity=after, from_tools_version=before_tools, to_tools_version=after_tools, bridge_after_upgrade_verified=bridge_after_upgrade_verified, previous_installer_sha256=OLD_SHA, installed_payload=json.loads(payload.read_text()), profile_data_preserved=True, password_fixture_preserved=True, companion_data_preserved=True, default_browser_preserved=True, same_install_directory=True, limits='Manual offline Setup upgrade with a synthetic profile. This is not a signed MAR, automatic updater, real account or real-user password test.')
finally:
    try:
        if driver:
            driver.quit()
        helper = destination / 'uninstall/helper.exe'
        if helper.is_file():
            environment = dict(os.environ, AION_UPGRADE_HELPER=str(helper))
            subprocess.run([pwsh, '-NoProfile', '-NonInteractive', '-Command', '$p=Start-Process -FilePath $env:AION_UPGRADE_HELPER -ArgumentList "/S" -Wait -PassThru; exit $p.ExitCode'], env=environment, check=True, timeout=180)
        assert not binary.exists()
        assert hashlib.sha256(marker.read_bytes()).hexdigest() == marker_sha
        assert choices() == before_choice
        report['upgrade_uninstallation_preserved_data'] = True
    except Exception:
        report['passed'] = False
        raise
    finally:
        (WORK / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert report['passed']
print('Actual Setup upgrade Aion0.3.1 →0.4.0 on ESR153.7 preserved synthetic native passwords, bookmarks, language, appearance, local record, containers, vocabulary and custom PNG without changing the default browser')
