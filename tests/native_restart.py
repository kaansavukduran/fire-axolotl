# SPDX-License-Identifier: MPL-2.0
"""Verify real process restart persistence in a new, isolated fork profile."""
import json
import os
from pathlib import Path
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from gecko_controls import choose_option

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'work/native-test-artifacts'
ARTIFACTS.mkdir(parents=True, exist_ok=True)
profiles = ROOT / 'work/native-test-profiles'
profiles.mkdir(exist_ok=True)
profile = Path(tempfile.mkdtemp(prefix='restart-', dir=profiles))
results = []
driver = None


def start(label):
    options = Options()
    options.binary_location = os.environ['AION_NATIVE_BINARY']
    options.add_argument('-headless')
    options.add_argument('-profile')
    options.add_argument(str(profile))
    options.accept_insecure_certs = False
    options.set_preference('remote.prefs.recommended', False)
    # Required only for Marionette's local file-input fixture, not shipped.
    options.set_preference('dom.file.createInChild', True)
    options.set_preference('browser.shell.checkDefaultBrowser', False)
    return webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(ARTIFACTS / f'restart-{label}.log')))


def record(name):
    results.append(name)
    print('PASS', name, flush=True)


def extension_base():
    driver.set_context('chrome')
    assert driver.execute_script('return Services.appinfo.ID;') == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
    uuid = driver.execute_script('return JSON.parse(Services.prefs.getStringPref("extensions.webextensions.uuids"))["aion@fire-axolotl.browser"];')
    driver.set_context('content')
    WebDriverWait(driver, 30).until(lambda d: d.window_handles)
    driver.switch_to.window(driver.window_handles[-1])
    driver.switch_to.new_window('tab')
    return f'moz-extension://{uuid}/'


try:
    driver = start('before')
    wait = WebDriverWait(driver, 30)
    base = extension_base()
    driver.get(base + 'settings.html')
    wait.until(lambda d: d.find_element(By.ID, 'language').is_displayed())
    Select(driver.find_element(By.ID, 'language')).select_by_value('tr')
    wait.until(lambda d: d.find_element(By.TAG_NAME, 'h1').text == 'Ayarlar')
    driver.get(base + 'popup.html')
    wait.until(lambda d: d.find_element(By.ID, 'container-name').is_displayed())
    driver.find_element(By.ID, 'container-name').send_keys('Tekrar · İş')
    driver.find_element(By.CSS_SELECTOR, '#container-form button').click()
    wait.until(lambda d: 'Tekrar · İş' in d.find_element(By.ID, 'container').text)
    driver.find_element(By.ID, 'source-text').send_keys('Işık ve öğrenme')
    driver.find_element(By.ID, 'save-word').click()
    wait.until(lambda d: d.execute_script('return document.getElementById("status").textContent === UI.t("wordSaved");'))
    driver.get(base + 'characters.html')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == 'aion')
    driver.find_element(By.ID, 'character-file').send_keys(str(ROOT / 'branding/icon-256.png'))
    wait.until(lambda d: d.find_element(By.ID, 'character-import').is_enabled())
    driver.find_element(By.ID, 'character-import').click()
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character').startswith('custom-'))
    character_id = driver.find_element(By.ID, 'character-canvas').get_attribute('data-character')
    driver.set_context('chrome')
    redesigned = driver.execute_script('return Services.prefs.getBoolPref("browser.settings-redesign.enabled",false);')
    driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/PlacesUtils.sys.mjs").PlacesUtils.bookmarks.insert({parentGuid:"unfiled_____",url:"https://example.invalid/fire-axolotl-restart",title:"Aion · Tekrar"}).then(()=>arguments[0](true));')
    driver.set_context('content')
    driver.get('about:preferences#' + ('appearance' if redesigned else 'general'))
    wait.until(lambda d: d.find_element(By.ID, 'aion-tab-position').is_displayed())
    choose_option(driver, 'aion-tab-position', 'left')
    choose_option(driver, 'aion-browser-font', 'opendyslexic')
    record('Normal native controls create local container, vocabulary, character and appearance fixtures')
    driver.quit()
    driver = None
    driver = start('after')
    wait = WebDriverWait(driver, 30)
    assert extension_base() == base
    driver.set_context('chrome')
    assert driver.execute_script('return Services.prefs.getBoolPref("sidebar.verticalTabs");') is True
    assert driver.execute_script('return Services.prefs.getStringPref("fireaxolotl.ui.font");') == 'opendyslexic'
    bookmark = driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/PlacesUtils.sys.mjs").PlacesUtils.bookmarks.fetch({url:"https://example.invalid/fire-axolotl-restart"}).then(b=>arguments[0](b?.title));')
    assert bookmark == 'Aion · Tekrar'
    record('Actual fork process restart preserves a chosen left tab layout, native font and Places bookmark')
    driver.set_context('content')
    driver.get(base + 'settings.html')
    wait.until(lambda d: d.find_element(By.TAG_NAME, 'h1').text == 'Ayarlar')
    assert driver.execute_script('return UI.settings.vocabulary.includes("Işık ve öğrenme");')
    assert driver.execute_script('return UI.settings.character;') == character_id
    driver.get(base + 'popup.html')
    wait.until(lambda d: 'Tekrar · İş' in d.find_element(By.ID, 'container').text)
    record('Language, vocabulary and Firefox contextual identity survive a full browser restart')
    driver.get(base + 'characters.html')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == character_id)
    record('The local custom PNG in IndexedDB survives the browser process restart and renders again')
finally:
    (ARTIFACTS / 'restart-results.json').write_text(json.dumps({'passed': results, 'limits': 'Separate development profile; this is a process restart test, not a signed two-version update test.'}, ensure_ascii=False, indent=2) + '\n')
    if driver is not None:
        driver.quit()
