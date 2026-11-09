# SPDX-License-Identifier: MPL-2.0
"""Fresh-profile smoke test for the compiled fork, without temporary add-ons.

Requires AION_NATIVE_BINARY and AION_GECKODRIVER. Upstream Firefox must fail
this test: compiled product identity and native built-in loading are required.
"""
import json
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from gecko_controls import choose_option

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path(os.environ.get('AION_NATIVE_ARTIFACTS', ROOT / 'work/native-test-artifacts'))
ARTIFACTS.mkdir(parents=True, exist_ok=True)
options = Options()
options.binary_location = os.environ['AION_NATIVE_BINARY']
options.add_argument('-headless')
options.accept_insecure_certs = False
options.set_preference('remote.prefs.recommended', False)
options.set_preference('browser.shell.checkDefaultBrowser', False)
driver = webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(ARTIFACTS / 'geckodriver.log')))
wait = WebDriverWait(driver, 30)
results = []


def record(name):
    results.append(name)
    print('PASS', name, flush=True)


try:
    driver.set_context('chrome')
    identity = driver.execute_script('return {id:Services.appinfo.ID, name:Services.appinfo.name, version:Services.appinfo.version,buildID:Services.appinfo.appBuildID};')
    assert identity['id'] == '{75450dd9-387d-4289-8b23-7ad6609fa530}', identity
    assert identity['name'] == 'FireAxolotl', identity
    record('Compiled fork has its own application identity')
    assert driver.execute_script('return Services.prefs.getBoolPref("sidebar.verticalTabs",false);') is False
    assert driver.execute_script('return gBrowser.tabContainer.getAttribute("orient");') == 'horizontal'
    record('Fresh native profile defaults to top horizontal tabs')
    components = json.loads((ROOT / 'components.json').read_text())
    addons = []
    for addon_id in ['aion@fire-axolotl.browser', components['ublock-origin']['id']]:
        addon = driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonByID(arguments[0]).then(a=>arguments[1](a ? {id:a.id,version:a.version,isBuiltin:a.isBuiltin,isActive:a.isActive} : null));', addon_id)
        assert addon and addon['isBuiltin'] and addon['isActive'], addon
        addons.append(addon)
    assert addons[1]['version'] == components['ublock-origin']['version']
    record('Aion and uBlock Origin are active built-ins without user installation')
    for pref in ['datareporting.healthreport.uploadEnabled', 'datareporting.policy.dataSubmissionEnabled', 'browser.newtabpage.activity-stream.showSponsored']:
        assert driver.execute_script('return Services.prefs.getBoolPref(arguments[0]);', pref) is False, pref
    for pref in ['identity.fxaccounts.enabled', 'browser.safebrowsing.malware.enabled', 'xpinstall.signatures.required']:
        assert driver.execute_script('return Services.prefs.getBoolPref(arguments[0]);', pref) is True, pref
    assert driver.execute_script('return Services.policies.getActivePolicies().DisableTelemetry;') is True
    assert driver.execute_script('return Services.policies.isAllowed("fxaccounts");') is True
    record('Shipped privacy policies preserve account capability, Safe Browsing and extension signing')
    proxy = driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/ServiceRequest.sys.mjs").ServiceRequest.logProxySource({proxyInfo:{}}, "aion-test").then(()=>arguments[0]({ok:true}), error=>arguments[0]({error:String(error)}));')
    assert proxy == {'ok': True}, proxy
    record('Compiled ServiceRequest handles active privacy policies without the upstream dictionary exception')
    assert driver.execute_script('return Services.prefs.getStringPref("extensions.activeThemeID");') == 'firefox-compact-dark@mozilla.org'
    record('Fresh native profile starts with the dark browser theme')
    uuid = driver.execute_script('return JSON.parse(Services.prefs.getStringPref("extensions.webextensions.uuids"))["aion@fire-axolotl.browser"];')
    redesigned = driver.execute_script('return Services.prefs.getBoolPref("browser.settings-redesign.enabled",false);')
    driver.save_screenshot(str(ARTIFACTS / 'native-first-window.png'))
    driver.set_context('content')
    # Normal first-run/new-tab initialization can replace the initial browsing
    # context. Start from an explicit live tab rather than a cached context.
    wait.until(lambda d: d.window_handles)
    driver.switch_to.window(driver.window_handles[-1])
    driver.switch_to.new_window('tab')
    driver.get(f'moz-extension://{uuid}/settings.html')
    wait.until(lambda d: d.find_element(By.ID, 'language').is_displayed())
    Select(driver.find_element(By.ID, 'language')).select_by_value('tr')
    wait.until(lambda d: d.find_element(By.TAG_NAME, 'h1').text == 'Ayarlar')
    record('Packaged Aion settings open and switch to Turkish')
    driver.find_element(By.ID, 'open-characters').click()
    driver.set_context('chrome')
    wait.until(lambda d: d.execute_script('return SidebarController.currentID?.includes("aion_fire-axolotl_browser");'))
    driver.save_screenshot(str(ARTIFACTS / 'native-companion-sidebar.png'))
    driver.execute_script('SidebarController.hide();')
    driver.set_context('content')
    driver.get(f'moz-extension://{uuid}/characters.html')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == 'aion')
    for character in ['aion', 'sheep', 'wolf', 'owl']:
        wait.until(lambda d: d.find_element(By.ID, 'character').is_displayed())
        Select(driver.find_element(By.ID, 'character')).select_by_value(character)
        wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == character)
    record('Compiled built-in sidebar opens and all four packaged character atlases decode')
    driver.get('about:preferences#' + ('appearance' if redesigned else 'general'))
    wait.until(lambda d: d.find_element(By.ID, 'aionLayoutGroup').is_displayed())
    for side in ['left', 'right', 'top']:
        choose_option(driver, 'aion-tab-position', side)
        driver.set_context('chrome')
        wait.until(lambda d: d.execute_script('return gBrowser.tabContainer.getAttribute("orient");') == ('horizontal' if side == 'top' else 'vertical'))
        if side != 'top':
            wait.until(lambda d: d.execute_script('return gBrowser.tabContainer.getBoundingClientRect().x < gBrowser.selectedBrowser.getBoundingClientRect().x;') == (side == 'left'))
        driver.save_screenshot(str(ARTIFACTS / f'native-tabs-{side}.png'))
        driver.set_context('content')
    record('Packaged native controls move actual browser tabs left, right and top')
    choose_option(driver, 'aion-browser-font', 'opendyslexic')
    driver.set_context('chrome')
    wait.until(lambda d: 'OpenDyslexic' in d.execute_script('return getComputedStyle(gURLBar.inputField).fontFamily;'))
    assert driver.execute_async_script('document.fonts.load("16px OpenDyslexic").then(fonts=>arguments[0](fonts.length));') > 0
    record('Compiled chrome resources supply OpenDyslexic to the native address field')
    driver.set_context('content')
    driver.execute_async_script('window.gotoPref("sync").then(()=>arguments[0](true));')
    assert not driver.find_element(By.ID, 'aionLayoutGroup').is_displayed()
    record('Aion appearance controls do not leak into Account/Sync settings')
finally:
    (ARTIFACTS / 'results.json').write_text(json.dumps({'identity': locals().get('identity'), 'addons': locals().get('addons'), 'passed': results}, ensure_ascii=False, indent=2) + '\n')
    driver.quit()
