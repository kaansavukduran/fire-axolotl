# SPDX-License-Identifier: MPL-2.0
"""Exercise packaged native languages through the real Settings picker."""
import json
import os
from pathlib import Path
import tempfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from gecko_controls import choose_option, capture_screenshot

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work/localization-test-artifacts'
OUT.mkdir(parents=True, exist_ok=True)
profile = Path(tempfile.mkdtemp(prefix='locale-', dir=OUT))
passed, states = [], []
driver = None


def start():
    options = Options()
    options.binary_location = os.environ['AION_NATIVE_BINARY']
    options.add_argument('-headless')
    options.add_argument('-profile')
    options.add_argument(str(profile))
    options.accept_insecure_certs = False
    options.set_preference('remote.prefs.recommended', False)
    options.set_preference('browser.shell.checkDefaultBrowser', False)
    # Do not seed intl.locale.requested: user.js would override the real picker.
    return webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(OUT / 'geckodriver.log')))


def state():
    driver.set_context('chrome')
    result = driver.execute_script('return {locale:Services.locale.appLocaleAsBCP47, requested:Services.locale.requestedLocales, available:Services.locale.availableLocales, best:Services.prefs.getIntPref("fireaxolotl.newtabGame.best",0), font:Services.prefs.getStringPref("fireaxolotl.ui.font","system"), vertical:Services.prefs.getBoolPref("sidebar.verticalTabs",false)};')
    driver.set_context('content')
    return result


def choose(code):
    driver.get('about:preferences#languages')
    wait = WebDriverWait(driver, 30)
    host = wait.until(lambda _: driver.find_element(By.ID, 'browserLanguagePreferred'))
    # moz-select's actual HTML control: use trusted option clicks.
    select = wait.until(lambda _: driver.execute_script('return arguments[0].shadowRoot.querySelector("select")', host))
    Select(select).select_by_value(code)
    wait.until(lambda _: state()['locale'] == code)
    expected = json.loads((ROOT / f'browser/extension/_locales/{"tr" if code == "tr" else "en"}/messages.json').read_text(encoding='utf-8'))['tabLayout']['message']
    wait.until(lambda _: driver.execute_script('return document.querySelector("[data-aion-l10n=tabLayout]")?.textContent') == expected)
    driver.get('about:preferences#appearance')
    wait.until(lambda _: driver.find_element(By.CSS_SELECTOR, '[data-aion-l10n="tabLayout"]').text == expected)
    driver.set_context('chrome')
    capture_screenshot(driver, str(OUT / f'native-settings-{code}.png'))
    driver.set_context('content')
    states.append(state())


def record(message):
    passed.append(message)
    print('PASS', message, flush=True)


try:
    driver = start()
    driver.set_window_size(1440, 1050)
    driver.set_context('chrome')
    addon = driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonByID("langpack-tr@fire-axolotl.browser").then(a=>arguments[0](a&&{id:a.id,type:a.type,isBuiltin:a.isBuiltin,isActive:a.isActive,appDisabled:a.appDisabled}));')
    assert addon and addon['isBuiltin'] and addon['isActive'] and not addon['appDisabled']
    assert driver.execute_script('return Services.appinfo.ID') == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
    assert driver.execute_script('return Services.prefs.getDefaultBranch("").getStringPref("intl.locale.requested")') == ''
    for pref in ['extensions.langpacks.signatures.required', 'xpinstall.signatures.required', 'browser.safebrowsing.malware.enabled', 'browser.safebrowsing.phishing.enabled']:
        assert driver.execute_script('return Services.prefs.getBoolPref(arguments[0])', pref)
    driver.set_context('content')
    record('Fresh own-product profile automatically enables the pinned built-in Turkish language with external signature checks and OS-language default intact')
    expected_locales = set(json.loads((ROOT / 'localization.json').read_text(encoding='utf-8'))['official_locales'])
    WebDriverWait(driver, 60).until(lambda _: expected_locales <= set(state()['available']))
    driver.set_context('chrome')
    addons = driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonsByTypes(["locale"]).then(list=>arguments[0](list.map(a=>({id:a.id,builtin:a.isBuiltin,disabled:a.appDisabled}))));')
    actual = {a['id']: a for a in addons}
    for code in expected_locales - {'en-US'}:
        addon = actual[f'langpack-{code}@fire-axolotl.browser']
        assert addon['builtin'] and not addon['disabled']
    driver.set_context('content')
    record(f'All {len(expected_locales)} official desktop languages are locally available; every added language has an independent built-in identity')
    driver.get('about:preferences#appearance')
    wait = WebDriverWait(driver, 30)
    wait.until(lambda _: driver.find_element(By.ID, 'aionLayoutGroup').get_attribute('data-aion-ready') == 'true')
    choose_option(driver, 'aion-tab-position', 'right')
    wait.until(lambda _: state()['vertical'])
    choose_option(driver, 'aion-browser-font', 'opendyslexic')
    driver.set_context('chrome')
    driver.execute_script('Services.prefs.setIntPref("fireaxolotl.newtabGame.best",13);')
    driver.set_context('content')
    for code in ['de', 'ja', 'ar']:
        choose(code)
        driver.set_context('chrome')
        title = driver.execute_async_script('new Localization(["browser/preferences/preferences.ftl"],true).formatValue("settings-page-title").then(arguments[0]);')
        assert title and title != 'Settings'
        driver.set_context('content')
        record(f'Native Settings selects {code} from the normal language picker and resolves its own translated strings')
    driver.quit()
    driver = start()
    after = state()
    assert after['locale'] == 'ar' and after['best'] == 13 and after['font'] == 'opendyslexic' and after['vertical']
    driver.set_context('chrome')
    assert driver.execute_script('return getComputedStyle(document.documentElement).direction') == 'rtl'
    driver.set_context('content')
    states.append(after)
    record('Arabic survives a real restart with right-to-left native chrome and existing user choices preserved')
    choose('tr')
    driver.set_context('chrome')
    strings = driver.execute_async_script('new Localization(["browser/preferences/preferences.ftl","branding/brand.ftl"],true).formatValues([{id:"settings-page-title"},{id:"pane-about-firefox-title"}]).then(arguments[0]);')
    assert strings[0] == 'Ayarlar' and 'Fire Axolotl' in strings[1]
    driver.set_context('content')
    record('Native Settings switches to Turkish with independent product branding and translated Appearance controls')
    driver.quit()
    driver = start()
    after = state()
    states.append(after)
    print('RESTART STATE', after, flush=True)
    assert after['locale'] == 'tr' and after['best'] == 13 and after['font'] == 'opendyslexic' and after['vertical']
    record('Actual process restart preserves Turkish, the chosen vertical tabs, accessibility font and local game record')
    choose('en-US')
    record('Native Settings switches back to English and the own Appearance controls follow')
    driver.quit()
    driver = start()
    after = state()
    states.append(after)
    print('RESTART STATE', after, flush=True)
    assert after['locale'] == 'en-US' and after['best'] == 13 and after['font'] == 'opendyslexic' and after['vertical']
    record('A second actual process restart preserves English and existing user choices')
finally:
    (OUT / 'results.json').write_text(json.dumps({'mode': 'compiled-fork-native-languages', 'passed': passed, 'states': states, 'limits': 'Complete official desktop locale availability and representative de/ja/ar/tr/en-US switching are covered. New Aion strings remain TR/EN. Remote language downloads and signed two-version updates are not covered.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if driver:
        driver.quit()
