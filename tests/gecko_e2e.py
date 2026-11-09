# SPDX-License-Identifier: MPL-2.0
"""Run with selenium, AION_FIREFOX_BINARY and AION_GECKODRIVER; never disable the browser sandbox."""
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'work/test-artifacts'
ARTIFACTS.mkdir(parents=True, exist_ok=True)
options = Options()
options.binary_location = os.environ['AION_FIREFOX_BINARY']
options.add_argument('-headless')
options.accept_insecure_certs = False
options.set_preference('browser.shell.checkDefaultBrowser', False)
options.set_preference('datareporting.policy.dataSubmissionEnabled', False)
driver = webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(ARTIFACTS / 'geckodriver.log')))
wait = WebDriverWait(driver, 20)
results = []

FIXTURE = b'''<!doctype html><meta charset="utf-8"><title>Aion test fixture</title>
<style>body{font:18px system-ui;background:#eef4ff;padding:2rem}video{width:640px;max-width:100%;display:block}canvas{display:none}</style>
<h1>Aion synthetic video fixture</h1><p id="selected">Hello Aion</p><button id="start">Start test video</button>
<video src="/video.webm" controls muted loop></video>
<script>document.getElementById('start').onclick=async()=>{const v=document.querySelector('video');const t=v.addTextTrack('subtitles','English','en');t.addCue(new VTTCue(0,3600,'Hello Aion'));t.mode='showing';await v.play();};</script>'''


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = (ROOT / 'tests/fixtures/video.webm').read_bytes() if self.path == '/video.webm' else FIXTURE
        self.send_response(200); self.send_header('Content-Type', 'video/webm' if self.path == '/video.webm' else 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *_args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), FixtureHandler)
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
    package = ROOT / 'dist/fire-axolotl-0.1.0-developer-addon.xpi'
    addon_id = driver.install_addon(str(package), temporary=True)
    driver.set_context('chrome')
    uuid = driver.execute_script("return JSON.parse(Services.prefs.getStringPref('extensions.webextensions.uuids'))[arguments[0]]", addon_id)
    driver.set_context('content')
    base = f'moz-extension://{uuid}/'
    driver.get(base + 'settings.html')
    wait.until(lambda d: d.execute_script('return typeof UI !== "undefined" && !!UI.settings'))
    Select(driver.find_element(By.ID, 'language')).select_by_value('tr')
    wait.until(lambda d: d.find_element(By.TAG_NAME, 'html').get_attribute('lang') == 'tr')
    assert driver.find_element(By.TAG_NAME, 'h1').text == 'Ayarlar'
    record('Turkish UI through normal settings controls')
    Select(driver.find_element(By.ID, 'theme')).select_by_value('contrast'); saved('theme', 'contrast')
    Select(driver.find_element(By.ID, 'font')).select_by_value('dyslexic'); saved('font', 'dyslexic')
    value('textSize-number', 150); saved('textSize', 150)
    value('scale-number', 135); saved('scale', 135)
    assert driver.execute_script('return parseFloat(getComputedStyle(document.documentElement).fontSize)') == 21.6
    record('Independent text size, Lexend, contrast and manual 135% interface scale')
    driver.find_element(By.CSS_SELECTOR, '[data-scale="200"]').click(); saved('scale', 200)
    driver.set_window_size(480, 900)
    assert driver.execute_script('return document.documentElement.scrollWidth <= innerWidth + 2')
    driver.save_screenshot(str(ARTIFACTS / 'settings-tr-200-narrow.png'))
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
    driver.save_screenshot(str(ARTIFACTS / 'settings-en-dark.png'))
    driver.get(base + 'popup.html')
    wait.until(lambda d: d.find_element(By.ID, 'container-name').get_attribute('placeholder'))
    value('container-name', 'İş · Learning')
    driver.find_element(By.CSS_SELECTOR, '#container-form button').click()
    wait.until(lambda d: 'İş · Learning' in d.find_element(By.ID, 'container').text)
    assert not driver.find_element(By.ID, 'progress-section').is_displayed()
    record('Real Firefox contextual identity creation while progress is disabled')
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
    driver.get(base + 'popup.html')
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
    driver.save_screenshot(str(ARTIFACTS / 'video-dual-captions.png'))
    driver.switch_to.window(control_handle)
    video_command({'action':'closeOverlay'})
    driver.switch_to.window(web_handle)
    assert not driver.find_elements(By.CSS_SELECTOR, '[data-aion-captions]')
    record('Real dual-caption overlay and removal without reloading the page')
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
      group.removeAttribute('hidden');
      document.getElementById('mainPrefPane').prepend(group);
      const messages = arguments[1];
      const fetch = async () => ({json: async () => messages});
    ''' + native_script
    driver.execute_script(harness, markup, messages)
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, '[data-aion-l10n="tabLayout"]').text == 'Tab layout')
    for side in ['left', 'right', 'top']:
        Select(driver.find_element(By.ID, 'aion-tab-position')).select_by_value(side)
        driver.set_context('chrome')
        wait.until(lambda d: d.execute_script('return gBrowser.tabContainer.getAttribute("orient")') == ('horizontal' if side == 'top' else 'vertical'))
        if side != 'top':
            def physical_side(d):
                return d.execute_script('const tabs=gBrowser.tabContainer.getBoundingClientRect(); const content=gBrowser.selectedBrowser.getBoundingClientRect(); return tabs.x < content.x ? "left" : "right";')
            wait.until(lambda d: physical_side(d) == side)
        driver.set_context('content')
        record(f'Native {side} tab position through the injected source control and real Firefox layout')
finally:
    (ARTIFACTS / 'results.json').write_text(json.dumps({'passed': results}, ensure_ascii=False, indent=2) + '\n')
    driver.quit()
    server.shutdown()
