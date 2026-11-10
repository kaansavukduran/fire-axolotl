# SPDX-License-Identifier: MPL-2.0
"""Run the real AppImage entry point and verify extracted installer payloads."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import socket
import signal
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def manifest(directory):
    files = {}
    for path in sorted(directory.rglob('*')):
        if path.is_file():
            with path.open('rb') as stream:
                files[path.relative_to(directory).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return files


def test(image, deb):
    artifacts = ROOT / 'work/installer-test-artifacts'
    artifacts.mkdir(parents=True, exist_ok=True)
    stage = ROOT / 'work/linux-package-stage'
    expected = manifest(stage / 'FireAxolotl.AppDir/usr/lib/fire-axolotl-preview')
    with tempfile.TemporaryDirectory(prefix='aion-appimage-') as temporary:
        temporary = Path(temporary)
        environment = dict(os.environ, APPIMAGE_EXTRACT_AND_RUN='1')
        version = subprocess.check_output([str(image), '--version'], env=environment, text=True, timeout=60)
        expected_version = json.loads((ROOT / 'upstream.json').read_text())['version'].removesuffix('esr')
        if expected_version not in version:
            raise ValueError('AppImage does not run the expected native browser')
        launch_image(image, temporary / 'profile', artifacts, environment)
        subprocess.run([str(image), '--appimage-extract'], cwd=temporary, check=True, stdout=subprocess.DEVNULL, timeout=90)
        if manifest(temporary / 'squashfs-root/usr/lib/fire-axolotl-preview') != expected:
            raise ValueError('AppImage payload differs from the verified native package')
        debroot = temporary / 'deb'
        subprocess.run(['dpkg-deb', '--extract', str(deb), str(debroot)], check=True)
        if manifest(debroot / 'usr/lib/fire-axolotl-preview') != expected:
            raise ValueError('Debian payload differs from the verified native package')
    report = {'passed': ['AppImage --version executes the expected native browser', 'Normal AppImage entry point renders Turkish Aion settings in a real browser window', 'Aion and uBO start as active built-ins through AppImage', 'Extracted AppImage and Debian payloads match the verified native files'], 'limits': 'FUSE-free AppImage runtime path tested; .deb installation and native smoke are separate CI steps.'}
    (artifacts / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


def launch_image(image, profile, artifacts, environment):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.support.ui import Select, WebDriverWait
    profile.mkdir()
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    (profile / 'user.js').write_text(f'user_pref("marionette.port", {port});\nuser_pref("remote.prefs.recommended", false);\n')
    environment = dict(environment, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS='1')
    driver = None
    with (artifacts / 'appimage-launch.log').open('w') as log:
        process = subprocess.Popen([str(image), '--marionette', '--headless', '--no-remote', '--profile', str(profile)], env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            options = Options()
            options.accept_insecure_certs = False
            service = Service(os.environ['AION_GECKODRIVER'], service_args=['--connect-existing', '--marionette-port', str(port), '--allow-system-access'], log_output=str(artifacts / 'geckodriver.log'))
            driver = webdriver.Firefox(options=options, service=service)
            wait = WebDriverWait(driver, 40)
            driver.set_context('chrome')
            if driver.execute_script('return Services.appinfo.ID;') != '{75450dd9-387d-4289-8b23-7ad6609fa530}':
                raise ValueError('AppImage opened a different browser')
            for identity in ['aion@fire-axolotl.browser', 'uBlock0@raymondhill.net']:
                addon = driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonByID(arguments[0]).then(a=>arguments[1](a?{isBuiltin:a.isBuiltin,isActive:a.isActive}:null));', identity)
                if not addon or not addon['isBuiltin'] or not addon['isActive']:
                    raise ValueError(f'AppImage did not activate {identity}: {addon}')
            uuid = driver.execute_script('return JSON.parse(Services.prefs.getStringPref("extensions.webextensions.uuids"))["aion@fire-axolotl.browser"];')
            driver.set_context('content')
            wait.until(lambda d: d.window_handles)
            driver.switch_to.window(driver.window_handles[-1])
            driver.switch_to.new_window('tab')
            driver.get(f'moz-extension://{uuid}/settings.html')
            wait.until(lambda d: d.find_element(By.ID, 'language').is_displayed())
            Select(driver.find_element(By.ID, 'language')).select_by_value('tr')
            wait.until(lambda d: d.find_element(By.TAG_NAME, 'h1').text == 'Ayarlar')
            driver.set_context('chrome')
            driver.save_screenshot(str(artifacts / 'appimage-native-settings.png'))
        finally:
            if driver:
                driver.quit()
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            process.wait(timeout=30)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('deb', type=Path)
    args = parser.parse_args()
    test(args.image.resolve(), args.deb.resolve())
