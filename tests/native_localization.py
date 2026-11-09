# SPDX-License-Identifier: MPL-2.0
"""Native localization gate; draft integration must not pass on missing resources."""
import json
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'work/native-test-artifacts/localization'
ARTIFACTS.mkdir(parents=True, exist_ok=True)
options = Options()
options.binary_location = os.environ['AION_NATIVE_BINARY']
options.add_argument('-headless')
options.accept_insecure_certs = False
options.set_preference('remote.prefs.recommended', False)
options.set_preference('extensions.logging.enabled', True)
driver = webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(ARTIFACTS / 'geckodriver.log')))
report = {'stage': 'draft, not release-ready', 'passed': []}
try:
    driver.set_context('chrome')
    assert driver.execute_script('return Services.appinfo.ID;') == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
    report['available'] = driver.execute_script('return Services.locale.availableLocales;')
    report['registry'] = driver.execute_async_script('fetch("chrome://browser/content/built_in_addons.json").then(r=>r.json()).then(arguments[0],e=>arguments[0]({error:String(e)}));')
    report['resource_manifest'] = driver.execute_async_script('fetch("resource://builtin-addons/fireaxolotl-locale-tr/manifest.json").then(r=>r.json()).then(arguments[0],e=>arguments[0]({error:String(e)}));')
    addon = driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonByID("langpack-tr@fire-axolotl.browser").then(a=>arguments[0](a?{id:a.id,type:a.type,isBuiltin:a.isBuiltin,isActive:a.isActive,appDisabled:a.appDisabled,signedState:a.signedState}:null));')
    report['addon'] = addon
    assert addon and addon['isBuiltin'] and addon['isActive'] and addon['type'] == 'locale', addon
    assert {'en-US', 'tr'} <= set(report['available'])
    report['passed'].append('Turkish native resource is active without a user installation')
    strings = driver.execute_async_script('new Localization(["browser/preferences/preferences.ftl","branding/brand.ftl"],false,undefined,["tr","en-US"]).formatValues([{id:"settings-page-title"},{id:"pane-about-firefox-title"}]).then(arguments[0]);')
    report['strings'] = strings
    assert strings[0] == 'Ayarlar' and 'Fire Axolotl' in strings[1], strings
    report['passed'].append('Real Turkish Fluent messages retain the independent product brand')
    for pref in ['extensions.langpacks.signatures.required', 'xpinstall.signatures.required', 'browser.safebrowsing.malware.enabled']:
        assert driver.execute_script('return Services.prefs.getBoolPref(arguments[0]);', pref)
    report['passed'].append('External signature verification and Safe Browsing stay enabled')
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
finally:
    (ARTIFACTS / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    driver.quit()
