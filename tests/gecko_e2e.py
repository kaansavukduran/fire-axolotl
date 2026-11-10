# SPDX-License-Identifier: MPL-2.0
"""Run with selenium, AION_FIREFOX_BINARY and AION_GECKODRIVER; never disable the browser sandbox."""
import json
import os
import base64
import shutil
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gecko_controls import choose_option, capture_screenshot

ROOT = Path(__file__).resolve().parents[1]
NATIVE = bool(os.environ.get('AION_NATIVE_BINARY'))
ARTIFACTS = ROOT / ('work/native-e2e-artifacts' if NATIVE else 'work/test-artifacts')
ARTIFACTS.mkdir(parents=True, exist_ok=True)
options = Options()
original_binary = Path(os.environ.get('AION_NATIVE_BINARY') or os.environ['AION_FIREFOX_BINARY']).resolve()
runtime_copy = original_binary.parent if NATIVE else ROOT / 'work/policy-test-runtime'
if not NATIVE:
    if not (runtime_copy / original_binary.name).is_file():
        shutil.copytree(original_binary.parent, runtime_copy, dirs_exist_ok=True)
    (runtime_copy / 'distribution').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'browser/policies.json', runtime_copy / 'distribution/policies.json')
options.binary_location = str(runtime_copy / original_binary.name)
options.add_argument('-headless')
options.accept_insecure_certs = False
options.set_preference('remote.prefs.recommended', False)
# Exercise normal animation and reduced motion explicitly in this test profile;
# Windows CI can inherit an OS preference that disables animations by default.
options.set_preference('ui.prefersReducedMotion', 0)
# Marionette's uploadFiles uses File.createFromFileName in its privileged
# content actor. Opt into this one automation capability, not the recommended
# preference bundle that also disables browser security services.
options.set_preference('dom.file.createInChild', True)
downloads = ARTIFACTS / 'downloads'
downloads.mkdir(exist_ok=True)
options.set_preference('browser.download.folderList', 2)
options.set_preference('browser.download.dir', str(downloads))
options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')
options.set_preference('browser.download.alwaysOpenPanel', False)
options.set_preference('browser.shell.checkDefaultBrowser', False)
options.set_preference('datareporting.policy.dataSubmissionEnabled', False)
driver = webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(ARTIFACTS / 'geckodriver.log')))
wait = WebDriverWait(driver, 20)
results = []

FIXTURE = b'''<!doctype html><meta charset="utf-8"><title>Aion test fixture</title>
<style>body{font:18px system-ui;background:#eef4ff;padding:2rem}video{width:640px;max-width:100%;display:block}canvas{display:none}</style>
<h1>Aion synthetic video fixture</h1><p id="selected">Hello Aion</p><button id="start">Start test video</button><button id="fullscreen-video">Fullscreen video</button>
<video src="/video.webm" controls muted loop></video><img id="search-image" src="/image.png" alt="Aion test image" width="48" height="48">
<script>document.getElementById('fullscreen-video').onclick=()=>document.querySelector('video').requestFullscreen();document.getElementById('start').onclick=async()=>{const v=document.querySelector('video');const t=v.addTextTrack('subtitles','English','en');t.addCue(new VTTCue(0,3600,'Hello Aion'));t.mode='showing';await v.play();};</script>'''


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        special = {
            '/blocking-fixture.html': b'<!doctype html><title>Blocking fixture</title><script src="/allowed-script.js"></script><script src="/blocked-script.js"></script><h1>Normal page</h1>',
            '/allowed-script.js': b'window.normalScriptRan=true;',
            '/blocked-script.js': b'window.blockedScriptRan=true;',
        }
        if self.path == '/blocked-script.js':
            self.server.blocked_requests += 1
        files = {'/video.webm': ROOT / 'tests/fixtures/video.webm', '/image.png': ROOT / 'branding/icon-48.png'}
        body = files[self.path].read_bytes() if self.path in files else special.get(self.path, FIXTURE)
        content_type = 'video/webm' if self.path == '/video.webm' else 'image/png' if self.path == '/image.png' else 'application/javascript' if self.path.endswith('.js') else 'text/html; charset=utf-8'
        self.send_response(200); self.send_header('Content-Type', content_type); self.send_header('Cache-Control', 'no-store'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *_args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), FixtureHandler)
server.blocked_requests = 0
Thread(target=server.serve_forever, daemon=True).start()


def record(name):
    results.append(name)
    print('PASS', name, flush=True)


def value(element_id, text):
    element = driver.find_element(By.ID, element_id)
    element.send_keys(Keys.CONTROL, 'a')
    element.send_keys(str(text), Keys.TAB)


def saved(key, expected):
    wait.until(lambda d: d.execute_script('return UI.settings[arguments[0]]', key) == expected)


try:
    wait.until(lambda d: d.window_handles)
    driver.switch_to.window(driver.window_handles[-1])
    driver.switch_to.new_window('tab')
    # Exercise the policy regression in the actual Gecko module/API. This is
    # an isolated resource alias, not a replacement of the installed runtime.
    patch = json.loads((ROOT / 'browser/native/service-request-proxy.json').read_text())
    driver.set_context('chrome')
    module_source = driver.execute_async_script('fetch("resource://gre/modules/ServiceRequest.sys.mjs").then(response=>response.text()).then(arguments[0]);')
    # Windows source preparation writes CRLF; compare the same code on both OSes.
    module_source = module_source.replace('\r\n', '\n')
    if NATIVE:
        assert patch['new'] in module_source and patch['old'] not in module_source
        assert driver.execute_script('return Services.appinfo.ID;') == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
        proxy_result = driver.execute_async_script('ChromeUtils.importESModule("resource://gre/modules/ServiceRequest.sys.mjs").ServiceRequest.logProxySource({proxyInfo:{}}, "aion-test").then(()=>arguments[0]({ok:true}), error=>arguments[0]({error:String(error)}));')
    else:
        assert module_source.count(patch['old']) == 1
        local_module = ARTIFACTS / 'ServiceRequest.sys.mjs'
        local_module.write_text(module_source.replace(patch['old'], patch['new'], 1))
        driver.set_context('chrome')
        proxy_result = driver.execute_async_script('''
          const [path, done] = arguments;
          const handler = Services.io.getProtocolHandler('resource').QueryInterface(Ci.nsIResProtocolHandler);
          const directory = Cc['@mozilla.org/file/local;1'].createInstance(Ci.nsIFile);
          directory.initWithPath(path);
          handler.setSubstitution('aion-service-test', Services.io.newFileURI(directory));
          ChromeUtils.importESModule('resource://aion-service-test/ServiceRequest.sys.mjs').ServiceRequest
            .logProxySource({proxyInfo:{}}, 'aion-test').then(()=>done({ok:true}), error=>done({error:String(error)}))
            .finally(()=>handler.setSubstitution('aion-service-test', null));
        ''', str(ARTIFACTS))
    assert proxy_result == {'ok': True}, proxy_result
    record('Patched Gecko ServiceRequest accepts the real active-policy dictionary without a proxy fallback exception')
    driver.set_context('content')
    import sys
    sys.path.insert(0, str(ROOT / 'scripts'))
    from fetch_components import fetch_xpi, PIN as UBLOCK_PIN
    blocking_url = f'http://127.0.0.1:{server.server_port}/blocking-fixture.html'
    driver.get(blocking_url)
    assert driver.execute_script('return window.normalScriptRan && window.blockedScriptRan')
    ublock_id = UBLOCK_PIN['id'] if NATIVE else driver.install_addon(str(fetch_xpi()), temporary=False)
    assert ublock_id == UBLOCK_PIN['id']
    driver.set_context('chrome')
    ublock_uuid = driver.execute_script("return JSON.parse(Services.prefs.getStringPref('extensions.webextensions.uuids'))[arguments[0]]", ublock_id)
    driver.set_context('content')
    driver.get(f'moz-extension://{ublock_uuid}/1p-filters.html')
    wait.until(lambda d: d.execute_script('return !!document.querySelector(".CodeMirror")?.CodeMirror'))
    # First launch compiles the real bundled filter lists. Give that work time
    # on a four-core host that is also compiling Firefox; do not skip the lists.
    driver.set_script_timeout(120)
    driver.execute_async_script('vAPI.messaging.send("dashboard", {what:"getLists"}).then(()=>arguments[0](true));')
    driver.set_script_timeout(30)
    driver.refresh()
    wait.until(lambda d: d.execute_script('return typeof self.hasUnsavedData === "function" && self.hasUnsavedData() === false;'))
    if not driver.find_element(By.CSS_SELECTOR, '#enableMyFilters input').is_selected():
        driver.find_element(By.CSS_SELECTOR, '#enableMyFilters input').click()
    rule = f'|http://127.0.0.1:{server.server_port}/blocked-script.js$script'
    driver.execute_script('document.querySelector(".CodeMirror").CodeMirror.setValue(arguments[0]);', rule + '\n')
    wait.until(lambda d: d.find_element(By.ID, 'userFiltersApply').is_enabled())
    driver.find_element(By.ID, 'userFiltersApply').click()
    WebDriverWait(driver, 120).until(lambda d: not d.find_element(By.ID, 'userFiltersApply').is_enabled())
    driver.set_script_timeout(120)
    driver.execute_async_script('vAPI.messaging.send("dashboard", {what:"reloadAllFilters"}).then(()=>arguments[0](true));')
    driver.set_script_timeout(30)
    stored_filters = driver.execute_async_script('vAPI.messaging.send("dashboard", {what:"readUserFilters"}).then(arguments[0]);')
    assert stored_filters['enabled'] and rule in stored_filters['content'], stored_filters
    before = server.blocked_requests
    driver.get(blocking_url)
    state = driver.execute_script('return {normal: window.normalScriptRan === true, blocked: window.blockedScriptRan === true};')
    assert state == {'normal': True, 'blocked': False}, state
    assert server.blocked_requests == before, 'The blocked request must not reach the local server'
    record('Official hash-pinned uBlock Origin blocks a real script request while the normal page still runs')
    # This test covers the official component engine, not native built-in loading.
    package = ROOT / f'dist/fire-axolotl-{json.loads((ROOT / "package.json").read_text())["version"]}-developer-addon.xpi'
    addon_id = 'aion@fire-axolotl.browser' if NATIVE else driver.install_addon(str(package), temporary=True)
    driver.set_context('chrome')
    assert driver.execute_script("return Services.policies.getActivePolicies().DisableTelemetry") is True
    assert driver.execute_script("return Services.prefs.getBoolPref('datareporting.healthreport.uploadEnabled')") is False
    assert driver.execute_script("return Services.prefs.prefIsLocked('datareporting.healthreport.uploadEnabled')") is True
    assert driver.execute_script("return Services.prefs.getBoolPref('identity.fxaccounts.enabled')") is True
    assert driver.execute_script("return Services.policies.isAllowed('fxaccounts')") is True
    assert driver.execute_script("return Services.prefs.getBoolPref('browser.newtabpage.activity-stream.showSponsored')") is False
    record('Shipped privacy policy disables telemetry and sponsored content while preserving Mozilla account capability')
    uuid = driver.execute_script("return JSON.parse(Services.prefs.getStringPref('extensions.webextensions.uuids'))[arguments[0]]", addon_id)
    driver.set_context('content')
    base = f'moz-extension://{uuid}/'
    driver.get(base + 'settings.html')
    wait.until(lambda d: d.execute_script('return typeof UI !== "undefined" && !!UI.settings'))
    assert driver.execute_script('return UI.settings.theme') == 'dark'
    record('New companion profile defaults to dark')
    Select(driver.find_element(By.ID, 'language')).select_by_value('tr')
    wait.until(lambda d: d.find_element(By.TAG_NAME, 'html').get_attribute('lang') == 'tr')
    assert driver.find_element(By.TAG_NAME, 'h1').text == 'Ayarlar'
    record('Turkish UI through normal settings controls')
    Select(driver.find_element(By.ID, 'theme')).select_by_value('contrast'); saved('theme', 'contrast')
    Select(driver.find_element(By.ID, 'font')).select_by_value('dyslexic'); saved('font', 'dyslexic')
    Select(driver.find_element(By.ID, 'font')).select_by_value('opendyslexic'); saved('font', 'opendyslexic')
    assert driver.execute_async_script("document.fonts.load('16px OpenDyslexic').then(fonts=>arguments[0](fonts.length));") > 0
    record('Bundled OpenDyslexic loads without a network font request')
    value('textSize-number', 150); saved('textSize', 150)
    value('scale-number', 135); saved('scale', 135)
    assert driver.execute_script('return parseFloat(getComputedStyle(document.documentElement).fontSize)') == 21.6
    record('Independent text size, Lexend, contrast and manual 135% interface scale')
    driver.find_element(By.CSS_SELECTOR, '[data-scale="200"]').click(); saved('scale', 200)
    driver.set_window_size(480, 900)
    assert driver.execute_script('return document.documentElement.scrollWidth <= innerWidth + 2')
    capture_screenshot(driver, str(ARTIFACTS / 'settings-tr-200-narrow.png'))
    record('200% interface scale on a narrow viewport without horizontal clipping')
    driver.find_element(By.ID, 'reset-scale').click(); saved('scale', 100)
    assert driver.execute_script('return UI.settings.textSize') == 150
    driver.find_element(By.ID, 'scale').send_keys(Keys.ARROW_RIGHT); saved('scale', 105)
    driver.find_element(By.ID, 'reset-text').click(); saved('textSize', 100)
    driver.find_element(By.ID, 'reset-scale').click(); saved('scale', 100)
    record('Keyboard slider step and independent per-setting resets')
    driver.find_element(By.ID, 'progress').click(); saved('progress', False)
    Select(driver.find_element(By.ID, 'language')).select_by_value('en'); saved('language', 'en')
    Select(driver.find_element(By.ID, 'theme')).select_by_value('dark'); saved('theme', 'dark')
    driver.refresh()
    wait.until(lambda d: d.find_element(By.TAG_NAME, 'h1').text == 'Settings')
    assert driver.execute_script('return UI.settings.theme') == 'dark'
    record('English UI and settings persistence after reopening the page')
    driver.set_window_size(1280, 1000)
    capture_screenshot(driver, str(ARTIFACTS / 'settings-en-dark.png'))
    driver.get(base + 'popup.html#containers')
    wait.until(lambda d: d.find_element(By.ID, 'container-name').get_attribute('placeholder'))
    value('container-name', 'İş · Learning')
    driver.find_element(By.CSS_SELECTOR, '#container-form button').click()
    wait.until(lambda d: 'İş · Learning' in d.find_element(By.ID, 'container').text)
    assert not driver.find_element(By.ID, 'progress-section').is_displayed()
    record('Real Firefox contextual identity creation while progress is disabled')
    driver.find_element(By.ID, 'tab-translation').click()
    value('source-text', 'Işık, öğrenme, özgürlük')
    driver.find_element(By.ID, 'save-word').click()
    wait.until(lambda d: 'vocabulary' in d.find_element(By.ID, 'status').text.lower())
    driver.find_element(By.ID, 'save-word').click()
    driver.get(base + 'settings.html')
    wait.until(lambda d: '1 ' in d.find_element(By.ID, 'word-count').text)
    assert driver.execute_script('return UI.settings.vocabulary.length') == 1
    record('Real persistent vocabulary, duplicate prevention and optional progress')
    driver.set_context('chrome'); driver.execute_script('Services.io.offline = true'); driver.set_context('content')
    driver.refresh()
    wait.until(lambda d: d.find_element(By.TAG_NAME, 'h1').text == 'Settings')
    Select(driver.find_element(By.ID, 'language')).select_by_value('tr'); saved('language', 'tr')
    record('Offline settings and language switching')
    driver.set_context('chrome'); driver.execute_script('Services.io.offline = false'); driver.set_context('content')
    driver.switch_to.new_window('tab')
    web_handle = driver.current_window_handle
    driver.get(f'http://127.0.0.1:{server.server_port}/')
    driver.find_element(By.ID, 'start').click()
    wait.until(lambda d: d.execute_script('return document.querySelector("video").videoWidth') == 320)
    driver.set_context('chrome')
    driver.find_element(By.ID, 'aion_fire-axolotl_browser-BAP').click()
    driver.set_context('content')
    driver.switch_to.new_window('tab')
    control_handle = driver.current_window_handle
    driver.get(base + 'popup.html#containers')
    wait.until(lambda d: d.execute_script('return typeof UI !== "undefined" && !!UI.settings'))
    web_tab_id = driver.execute_async_script('const [url,done]=arguments;browser.tabs.query({}).then(tabs=>done(tabs.find(tab=>tab.url===url)?.id));', f'http://127.0.0.1:{server.server_port}/')
    assert web_tab_id is not None, 'Toolbar activation must grant access to the original web tab'

    def video_command(command):
        return driver.execute_async_script('''
          const [tabId, command, done] = arguments;
          (async () => {
            await browser.tabs.executeScript(tabId, {file:'video.js'});
            return browser.tabs.sendMessage(tabId, {type:'aionVideo', command});
          })().then(done, error => done({error:error.message}));
        ''', web_tab_id, command)

    response = video_command({'action': 'speed', 'value': 1.35})
    assert response.get('speed') == 1.35, response
    assert response['width'] == 320 and response['height'] == 180, response
    assert video_command({'action': 'speed', 'value': 9})['error'] == 'invalidSpeed'
    assert video_command({'action': 'info'})['speed'] == 1.35
    record('Real activeTab permission, injected video control, 1.35x speed and decoded 320x180 resolution')
    assert 'Hello Aion' in video_command({'action': 'captions'})['text']
    assert video_command({'action': 'quality', 'value': 'hd1080'})['error'] == 'unsupportedQuality'
    record('Real current caption extraction and honest unsupported-quality result')
    response = video_command({'action': 'overlay', 'language': 'tr', 'original': [{'start':0,'end':3600,'text':'Hello Aion'}], 'translated': [{'start':0,'end':3600,'text':'Merhaba Aion'}]})
    assert not response.get('error'), response
    driver.switch_to.window(web_handle)
    assert driver.find_element(By.CSS_SELECTOR, '[data-aion-captions]').is_displayed()
    capture_screenshot(driver, str(ARTIFACTS / 'video-dual-captions.png'))
    assert driver.execute_script('return [...document.querySelector("video").textTracks].find(t=>t.label==="English").mode') == 'hidden'
    driver.find_element(By.ID, 'fullscreen-video').click()
    wait.until(lambda d: d.execute_script('return document.fullscreenElement === document.querySelector("video");'))
    wait.until(lambda d: d.execute_script('const track=[...document.querySelector("video").textTracks].find(t=>t.label==="Aion");return track?.mode==="showing" && [...(track.activeCues||[])].some(c=>c.text.includes("Merhaba Aion"));'))
    assert not driver.find_element(By.CSS_SELECTOR, '[data-aion-captions]').is_displayed()
    assert driver.execute_script('return [...document.querySelector("video").textTracks].find(t=>t.label==="Aion").activeCues.length') == 2
    capture_screenshot(driver, str(ARTIFACTS / 'video-native-fullscreen-captions.png'))
    record('Native video-element fullscreen displays both local subtitle tracks through Gecko text rendering')
    driver.execute_async_script('document.exitFullscreen().then(()=>arguments[0](true));')
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, '[data-aion-captions]').is_displayed())
    assert driver.execute_script('return [...document.querySelector("video").textTracks].find(t=>t.label==="Aion").mode') == 'disabled'
    record('Leaving native fullscreen restores the custom subtitle overlay')
    driver.switch_to.window(control_handle)
    video_command({'action':'closeOverlay'})
    driver.switch_to.window(web_handle)
    assert not driver.find_elements(By.CSS_SELECTOR, '[data-aion-captions]')
    assert driver.execute_script('return [...document.querySelector("video").textTracks].some(t=>t.label==="Aion")') is False
    assert driver.execute_script('return [...document.querySelector("video").textTracks].find(t=>t.label==="English").mode') == 'showing'
    record('Real dual-caption overlay and removal without reloading the page')
    handles_before_search = set(driver.window_handles)
    driver.set_context('chrome'); driver.execute_script('Services.io.offline = true;'); driver.set_context('content')
    ActionChains(driver).context_click(driver.find_element(By.ID, 'search-image')).perform()
    driver.set_context('chrome')
    menu_selector = '#contentAreaContextMenu menu[id*="aion-image-search"]'
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, menu_selector).is_displayed())
    menu = driver.find_element(By.CSS_SELECTOR, menu_selector)
    ActionChains(driver).move_to_element(menu).perform()
    bing_selector = '#contentAreaContextMenu menuitem[label="Bing"]'
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, bing_selector).is_displayed())
    capture_screenshot(driver, str(ARTIFACTS / 'image-search-context-menu.png'))
    driver.find_element(By.CSS_SELECTOR, bing_selector).click()
    driver.set_context('content')
    wait.until(lambda d: len(set(d.window_handles) - handles_before_search) == 1)
    driver.switch_to.window(next(iter(set(driver.window_handles) - handles_before_search)))
    wait.until(lambda d: d.current_url.startswith('https://www.bing.com/'))
    target = urlparse(driver.current_url)
    assert parse_qs(target.query)['imgurl'] == [f'http://127.0.0.1:{server.server_port}/image.png']
    driver.close(); driver.switch_to.window(control_handle)
    driver.set_context('chrome'); driver.execute_script('Services.io.offline = false;'); driver.set_context('content')
    record('Actual native image menu opens the explicitly chosen provider URL; offline test sends no image to a provider')
    driver.get(base + 'settings.html')
    wait.until(lambda d: d.find_element(By.ID, 'imageSearch').is_selected())
    driver.find_element(By.ID, 'imageSearch').click(); saved('imageSearch', False)
    driver.switch_to.window(web_handle)
    ActionChains(driver).context_click(driver.find_element(By.ID, 'search-image')).perform()
    driver.set_context('chrome')
    wait.until(lambda d: d.find_element(By.ID, 'contentAreaContextMenu').get_attribute('state') == 'open')
    try:
        wait.until(lambda d: not any(item.is_displayed() for item in d.find_elements(By.CSS_SELECTOR, menu_selector)))
    except Exception:
        capture_screenshot(driver, str(ARTIFACTS / 'image-menu-disable-failure.png'))
        print('Menu DOM diagnostic:', driver.execute_script('return [...document.querySelectorAll(arguments[0])].map(m=>({id:m.id,hidden:m.hidden,collapsed:m.collapsed,display:getComputedStyle(m).display}));', menu_selector), flush=True)
        driver.set_context('content'); driver.switch_to.window(control_handle)
        print('Menu settings diagnostic:', driver.execute_async_script('browser.runtime.getBackgroundPage().then(async w=>arguments[0]({imageSearch:(await w.readSettings()).imageSearch,controller:!!w.AionImageMenus}));'), flush=True)
        raise
    driver.find_element(By.ID, 'contentAreaContextMenu').send_keys(Keys.ESCAPE)
    driver.set_context('content')
    record('Disabling image search through Aion settings removes its native context menu')
    driver.get('about:preferences')
    wait.until(lambda d: d.find_element(By.ID, 'mainPrefPane'))
    # Upstream Firefox does not contain our chrome resources. Supply only those
    # local resources to the harness; exercise the real native preferences/UI.
    native_script = (ROOT / 'browser/native/aion-layout.js').read_text()
    markup = (ROOT / 'browser/native/aion-layout.inc.xhtml').read_text()
    messages = json.loads((ROOT / 'browser/extension/_locales/en/messages.json').read_text())
    harness = '''
      const markup = '<root xmlns="urn:aion-test" xmlns:html="http://www.w3.org/1999/xhtml">' + arguments[0] + '</root>';
      const parsed = new DOMParser().parseFromString(markup, 'application/xml');
      function importNode(node) {
        if (node.nodeType === Node.TEXT_NODE) return document.createTextNode(node.textContent);
        const element = node.prefix === 'html' ? document.createElementNS('http://www.w3.org/1999/xhtml', node.localName) : document.createXULElement(node.localName);
        for (const attr of node.attributes) element.setAttribute(attr.name, attr.value);
        for (const child of node.childNodes) if ([Node.ELEMENT_NODE, Node.TEXT_NODE].includes(child.nodeType)) element.append(importNode(child));
        return element;
      }
      const group = importNode(parsed.documentElement.firstElementChild);
      document.getElementById('mainPrefPane').prepend(group);
      const messages = arguments[1];
      const fetch = async () => ({json: async () => messages});
    ''' + native_script
    if not NATIVE:
        driver.execute_script(harness, markup, messages)
    driver.execute_async_script('window.gotoPref(Services.prefs.getBoolPref("browser.settings-redesign.enabled", false) ? "appearance" : "general").then(()=>arguments[0](true));')
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, '[data-aion-l10n="tabLayout"]').text == 'Tab layout')
    assert driver.find_element(By.ID, 'aionLayoutGroup').is_displayed()
    driver.execute_async_script('window.gotoPref("sync").then(()=>arguments[0](true));')
    assert not driver.find_element(By.ID, 'aionLayoutGroup').is_displayed()
    driver.execute_async_script('window.gotoPref(Services.prefs.getBoolPref("browser.settings-redesign.enabled", false) ? "appearance" : "general").then(()=>arguments[0](true));')
    assert driver.find_element(By.ID, 'aionLayoutGroup').is_displayed()
    record('Aion native layout controls stay in their own section and remain hidden in Account/Sync')
    for side in ['left', 'right', 'top']:
        choose_option(driver, 'aion-tab-position', side)
        driver.set_context('chrome')
        wait.until(lambda d: d.execute_script('return gBrowser.tabContainer.getAttribute("orient")') == ('horizontal' if side == 'top' else 'vertical'))
        if side != 'top':
            def physical_side(d):
                return d.execute_script('const tabs=gBrowser.tabContainer.getBoundingClientRect(); const content=gBrowser.selectedBrowser.getBoundingClientRect(); return tabs.x < content.x ? "left" : "right";')
            wait.until(lambda d: physical_side(d) == side)
        driver.set_context('content')
        record(f'Native {side} tab position through the {"compiled" if NATIVE else "injected source"} control and real browser layout')
    preferences_handle = driver.current_window_handle
    driver.set_context('chrome')
    chrome_css = (ROOT / 'browser/native/aion-chrome.css').read_text()
    for font_name in ['OpenDyslexic-Regular.otf', 'OpenDyslexic-Bold.otf', 'Lexend.ttf']:
        encoded = base64.b64encode((ROOT / 'browser/extension/fonts' / font_name).read_bytes()).decode()
        chrome_css = chrome_css.replace('chrome://browser/content/aion-fonts/' + font_name, 'data:font/otf;base64,' + encoded)
    if not NATIVE:
        driver.execute_script("const style=document.createElementNS('http://www.w3.org/1999/xhtml','style');style.textContent=arguments[0];document.head.append(style);" + (ROOT / 'browser/native/aion-chrome.js').read_text(), chrome_css)
    driver.set_context('content')
    choose_option(driver, 'aion-browser-font', 'opendyslexic')
    driver.set_context('chrome')
    wait.until(lambda d: d.execute_script('return document.documentElement.dataset.aionFont') == 'opendyslexic')
    assert 'OpenDyslexic' in driver.execute_script('return getComputedStyle(gURLBar.inputField).fontFamily')
    assert driver.execute_async_script("document.fonts.load('16px OpenDyslexic').then(fonts=>arguments[0](fonts.length));") > 0
    record('Native toolbar and address field use OpenDyslexic through the saved preference')
    driver.set_context('content')
    for mode, expects_dark in [('0', True), ('1', False)]:
        choose_option(driver, 'aion-website-theme', mode)
        driver.switch_to.new_window('tab')
        driver.get(f'http://127.0.0.1:{server.server_port}/')
        assert driver.execute_script("return matchMedia('(prefers-color-scheme:dark)').matches") == expects_dark
        assert driver.execute_script('return getComputedStyle(document.body).backgroundColor') == 'rgb(238, 244, 255)'
        assert driver.execute_script('return getComputedStyle(document.body).fontFamily') == 'system-ui'
        driver.close(); driver.switch_to.window(preferences_handle)
    record('Independent site color preference changes media queries while preserving site CSS and fonts')
    choose_option(driver, 'aion-website-theme', '2')
    driver.set_context('chrome')
    driver.execute_async_script("ChromeUtils.importESModule('resource://gre/modules/AddonManager.sys.mjs').AddonManager.getAddonByID('firefox-compact-dark@mozilla.org').then(theme=>theme.enable()).then(()=>arguments[0](true));")
    driver.set_context('content')
    driver.switch_to.new_window('tab'); driver.get(f'http://127.0.0.1:{server.server_port}/')
    wait.until(lambda d: d.execute_script("return matchMedia('(prefers-color-scheme:dark)').matches"))
    assert driver.execute_script('return getComputedStyle(document.body).backgroundColor') == 'rgb(238, 244, 255)'
    driver.close(); driver.switch_to.window(preferences_handle)
    record('Automatic website preference follows dark browser theme without forced site recoloring')
    driver.find_element(By.ID, 'aion-customize-toolbar').click()
    driver.set_context('chrome')
    wait.until(lambda d: d.execute_script('return document.documentElement.hasAttribute("customizing")'))
    driver.execute_script('gCustomizeMode.exit()')
    record('Native toolbar editor opens from the new preferences control')
    driver.set_context('content')
    driver.switch_to.new_window('tab')
    character_handle = driver.current_window_handle
    driver.get(base + 'characters.html')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == 'aion')
    assert driver.find_element(By.TAG_NAME, 'h1').text == 'Yol arkadaşları'
    for character in ['aion', 'sheep', 'wolf', 'owl']:
        Select(driver.find_element(By.ID, 'character')).select_by_value(character)
        wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == character)
        assert driver.execute_script('return document.getElementById("character-canvas").getContext("2d").getImageData(0,0,480,480).data.some((v,i)=>i%4===3 && v>0);')
    Select(driver.find_element(By.ID, 'character-activity')).select_by_value('read')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-activity') == 'read')
    capture_screenshot(driver, str(ARTIFACTS / 'character-owl-reading-tr.png'))
    record('All four whole-character companions render locally with an actual reading animation and Turkish controls')
    Select(driver.find_element(By.ID, 'character')).select_by_value('aion')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == 'aion')
    start_frame = driver.find_element(By.ID, 'character-canvas').get_attribute('data-frame')
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-frame') != start_frame)
    driver.find_element(By.ID, 'character-pause').click(); saved('animations', False)
    assert driver.execute_async_script('const c=document.getElementById("character-canvas"),f=c.dataset.frame;setTimeout(()=>arguments[0](c.dataset.frame===f),550);')
    driver.find_element(By.ID, 'character-pause').send_keys(Keys.ENTER); saved('animations', True)
    driver.set_context('chrome'); driver.execute_script('Services.prefs.setIntPref("ui.prefersReducedMotion",1);'); driver.set_context('content')
    wait.until(lambda d: not d.find_element(By.ID, 'character-pause').is_enabled())
    assert driver.execute_async_script('const c=document.getElementById("character-canvas"),f=c.dataset.frame;setTimeout(()=>arguments[0](c.dataset.frame===f),550);')
    driver.set_context('chrome'); driver.execute_script('Services.prefs.setIntPref("ui.prefersReducedMotion",0);'); driver.set_context('content')
    record('Companion frames advance, pause through the normal button/keyboard and honor OS reduced motion')
    driver.find_element(By.ID, 'character-file').send_keys(str(ROOT / 'browser/extension/characters/aion.png'))
    wait.until(lambda d: d.find_element(By.ID, 'character-import').is_enabled())
    value('character-name', 'Kişisel Aion · Test')
    for key, number in [('columns',8),('rows',11),('row',1),('frames',6)]:
        driver.find_element(By.CSS_SELECTOR, 'details summary').click() if key == 'columns' else None
        value('character-' + key, number)
    driver.find_element(By.ID, 'character-import').click()
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character').startswith('custom-'))
    custom_id = driver.find_element(By.ID, 'character-canvas').get_attribute('data-character')
    driver.refresh()
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == custom_id)
    assert Select(driver.find_element(By.ID, 'character')).first_selected_option.text == 'Kişisel Aion · Test'
    record('A user PNG sprite sheet imports through the file picker and persists with its grid after page reopen')
    export = downloads / 'fire-axolotl-character.json'
    export.unlink(missing_ok=True)
    driver.find_element(By.ID, 'character-export').click()
    # Firefox may create an empty destination before the download completes.
    # Wait for the browser's completion signal before reading or importing it.
    driver.set_context('chrome')
    try:
        wait.until(lambda d: d.execute_async_script('''
            const target = arguments[0], done = arguments[arguments.length - 1];
            const {Downloads} = ChromeUtils.importESModule('resource://gre/modules/Downloads.sys.mjs');
            Downloads.getList(Downloads.ALL).then(list => list.getAll()).then(
                items => done(items.some(item => item.target.path === target && item.succeeded)),
                () => done(false));
        ''', str(export)))
    finally:
        driver.set_context('content')
    backup = json.loads(export.read_text())
    assert backup['format'] == 'fire-axolotl-character' and backup['name'] == 'Kişisel Aion · Test'
    assert base64.b64decode(backup['png']) == (ROOT / 'browser/extension/characters/aion.png').read_bytes()
    driver.find_element(By.ID, 'character-delete').click()
    wait.until(EC.alert_is_present()).accept()
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character') == 'aion')
    driver.find_element(By.ID, 'character-file').send_keys(str(export))
    wait.until(lambda d: d.find_element(By.ID, 'character-import').is_enabled())
    driver.find_element(By.ID, 'character-import').click()
    wait.until(lambda d: d.find_element(By.ID, 'character-canvas').get_attribute('data-character').startswith('custom-'))
    assert Select(driver.find_element(By.ID, 'character')).first_selected_option.text == 'Kişisel Aion · Test'
    record('Actual character export, confirmed removal and JSON reimport preserve PNG bytes and animation settings')
    driver.get(base + 'settings.html')
    wait.until(lambda d: d.find_element(By.ID, 'language').is_displayed())
    Select(driver.find_element(By.ID, 'language')).select_by_value('en'); saved('language', 'en')
    value('scale-number', 200); saved('scale', 200)
    driver.get(base + 'characters.html')
    wait.until(lambda d: d.find_element(By.TAG_NAME, 'h1').text == 'Companions')
    driver.set_window_size(480, 900)
    assert driver.execute_script('return document.documentElement.scrollWidth <= innerWidth + 2;')
    capture_screenshot(driver, str(ARTIFACTS / 'characters-en-200-narrow.png'))
    record('English companion controls remain usable on a narrow screen at 200 percent interface scale')
    driver.set_window_size(1280, 1000)
    driver.get(base + 'settings.html')
    wait.until(lambda d: d.find_element(By.ID, 'reset-scale').is_displayed())
    driver.find_element(By.ID, 'reset-scale').click(); saved('scale', 100)
    wait.until(lambda d: d.find_element(By.ID, 'open-characters').is_displayed())
    driver.find_element(By.ID, 'open-characters').click()
    driver.set_context('chrome')
    wait.until(lambda d: d.execute_script('return SidebarController.currentID?.includes("aion_fire-axolotl_browser");'))
    capture_screenshot(driver, str(ARTIFACTS / 'character-native-sidebar.png'))
    record('The optional native companion sidebar opens through the normal settings button')
finally:
    (ARTIFACTS / 'results.json').write_text(json.dumps({'mode': 'compiled-fork' if NATIVE else 'stock-firefox-fixture', 'passed': results}, ensure_ascii=False, indent=2) + '\n')
    driver.quit()
    server.shutdown()
