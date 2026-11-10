# SPDX-License-Identifier: MPL-2.0
"""Exercise Aion's actual browser popup, workspace and native context menus."""
import http.server
import json
import os
from pathlib import Path
import threading
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from gecko_controls import capture_screenshot

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work/tools-test-artifacts'
OUT.mkdir(exist_ok=True)
passed = []

class Fixture(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'<!doctype html><meta charset="utf-8"><title>Aion source fixture</title><p id="text" style="width:max-content">Hello world</p><a id="link" href="/other">Open another page</a><video></video>'
        self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers(); self.wfile.write(body)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
threading.Thread(target=server.serve_forever, daemon=True).start()
options = Options()
options.binary_location = os.environ['AION_NATIVE_BINARY']
options.add_argument('-headless')
options.accept_insecure_certs = False
options.set_preference('remote.prefs.recommended', False)
options.set_preference('browser.shell.checkDefaultBrowser', False)
driver = webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(OUT / 'geckodriver.log')))
wait = WebDriverWait(driver, 30)

def record(text):
    passed.append(text); print('PASS', text, flush=True)

def ready(expected=None):
    wait.until(lambda d: d.execute_script('return location.protocol === "moz-extension:" && document.body.dataset.ready === "true" && (!arguments[0] || location.href === arguments[0]);', expected))
    driver.execute_async_script('const done=arguments[0];requestAnimationFrame(()=>requestAnimationFrame(done));')

try:
    driver.set_window_size(1440, 1050)
    driver.set_context('chrome')
    assert driver.execute_script('return Services.appinfo.ID') == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
    addon = driver.execute_async_script('const done=arguments[0];ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonByID("aion@fire-axolotl.browser").then(a=>done({version:a.version,active:a.isActive}));')
    assert addon == {'version':'0.2.0','active':True}, addon
    uuid = driver.execute_script('return JSON.parse(Services.prefs.getStringPref("extensions.webextensions.uuids"))["aion@fire-axolotl.browser"];')
    base = f'moz-extension://{uuid}/'
    driver.set_context('content')
    driver.get(f'http://127.0.0.1:{server.server_port}/')
    source = driver.current_window_handle
    driver.add_cookie({'name':'aion_synthetic','value':'personal'})
    driver.set_context('chrome')
    driver.find_element(By.ID,'aion_fire-axolotl_browser-BAP').click()
    width = wait.until(lambda d: d.execute_script('const b=document.querySelector(".webextension-popup-browser");return b?.getBoundingClientRect().width >= 700 && b.getBoundingClientRect().width;'))
    capture_screenshot(driver, OUT / 'actual-toolbar-popup.png')
    record('Actual toolbar popup opens at least700px wide without disabling native security')
    driver.find_element(By.ID,'aion_fire-axolotl_browser-BAP').click()
    driver.set_context('content')
    driver.switch_to.new_window('tab')
    driver.get(base + 'popup.html#translation'); ready()
    source_id = driver.execute_async_script('const [url,done]=arguments;browser.tabs.query({}).then(t=>done(t.find(t=>t.url===url)?.id));', f'http://127.0.0.1:{server.server_port}/')
    # Capture the source explicitly, just as the popup Expand button does.
    target = base + f'popup.html?sourceTabId={source_id}#translation'
    driver.get(target); ready(target)
    original_control = driver.current_window_handle
    driver.execute_script('window.aionClicks=[];document.addEventListener("click",event=>aionClicks.push(event.target.id),true);')
    wait.until(EC.element_to_be_clickable((By.ID,'expand-tools'))).click()
    control = wait.until(lambda d: next((h for h in d.window_handles if h not in {source,original_control}),None))
    driver.switch_to.window(original_control); driver.close(); driver.switch_to.window(control); ready()
    wait.until(EC.visibility_of_element_located((By.ID,'native-translation')))
    assert 'view=tab' in driver.current_url
    driver.find_element(By.ID,'source-text').send_keys('Öğrenme · Hello world')
    driver.find_element(By.ID,'tab-containers').click()
    driver.find_element(By.ID,'container-name').send_keys('İş · UX')
    driver.find_element(By.CSS_SELECTOR,'#container-form button').click()
    wait.until(lambda d: 'İş · UX' in d.find_element(By.ID,'container').text)
    driver.find_element(By.ID,'tab-translation').click()
    assert driver.find_element(By.ID,'source-text').get_attribute('value') == 'Öğrenme · Hello world'
    driver.refresh(); ready()
    assert driver.find_element(By.ID,'source-text').get_attribute('value') == 'Öğrenme · Hello world'
    capture_screenshot(driver, OUT / 'workspace-translation.png')
    record('Full workspace keeps the captured source and session-only draft across tool changes and reopening')
    driver.find_element(By.ID,'tab-video').click()
    speed = driver.find_element(By.ID,'speed-number');speed.send_keys(Keys.CONTROL,'a');speed.send_keys('1.5',Keys.TAB)
    driver.find_element(By.ID,'apply-speed').click()
    driver.switch_to.window(source)
    wait.until(lambda d: d.execute_script('return document.querySelector("video").playbackRate === 1.5;'))
    driver.switch_to.window(control)
    record('The normal Video panel changes the captured website video rather than the active workspace tab')

    driver.find_element(By.ID,'tab-containers').click()
    driver.find_element(By.ID,'open-container').click()
    before = set(driver.window_handles)
    isolated = wait.until(lambda d: next((h for h in d.window_handles if h not in {source,control}),None))
    driver.switch_to.window(isolated)
    wait.until(lambda d: d.current_url.startswith('http://127.0.0.1:'))
    assert driver.execute_script('return document.cookie') == ''
    driver.execute_script('document.cookie="aion_synthetic=work;path=/";')
    driver.close();driver.switch_to.window(source)
    assert 'aion_synthetic=personal' in driver.execute_script('return document.cookie')
    ActionChains(driver).context_click(driver.find_element(By.ID,'link')).perform()
    driver.set_context('chrome')
    menu = wait.until(lambda d: d.find_element(By.CSS_SELECTOR,'#contentAreaContextMenu menu[id*="aion-open-container"]'))
    ActionChains(driver).move_to_element(menu).perform()
    choice = wait.until(lambda d: next((e for e in d.find_elements(By.CSS_SELECTOR,'#contentAreaContextMenu menuitem[label="İş · UX"]') if e.is_displayed()),None))
    capture_screenshot(driver, OUT / 'container-context-menu.png')
    choice.click(); driver.set_context('content')
    isolated = wait.until(lambda d: next((h for h in d.window_handles if h not in {source,control}),None))
    driver.switch_to.window(isolated)
    wait.until(lambda d: d.current_url.endswith('/other'))
    assert 'aion_synthetic=work' in driver.execute_script('return document.cookie')
    driver.close();driver.switch_to.window(control)
    record('Both workspace and real right-click container action preserve the original page and isolate its login cookie')
    driver.set_context('chrome')
    driver.execute_script('document.getElementById("contentAreaContextMenu").hidePopup();')
    wait.until(lambda d: d.execute_script('return document.getElementById("contentAreaContextMenu").state === "closed";'))
    driver.set_context('content');driver.switch_to.window(source)
    ActionChains(driver).reset_actions()
    paragraph = driver.find_element(By.ID,'text')
    width = int(paragraph.rect['width'])
    ActionChains(driver).move_to_element_with_offset(paragraph, -width // 2 + 2, 0).click_and_hold().move_by_offset(width - 4, 0).release().perform()
    wait.until(lambda d: d.execute_script('return window.getSelection().toString().trim();'))
    ActionChains(driver).context_click(paragraph).perform()
    selected_text = driver.execute_script('return getSelection().toString();')
    assert selected_text.strip()
    driver.set_context('chrome')
    wait.until(lambda d: d.execute_script('return gContextMenu.isTextSelected;'))
    item = wait.until(lambda d: d.find_element(By.CSS_SELECTOR,'#contentAreaContextMenu menuitem[id*="aion-translate-selection"]'))
    item.click();driver.set_context('content')
    selected = wait.until(lambda d: next((h for h in d.window_handles if h not in {source,control}),None))
    driver.switch_to.window(selected);ready()
    assert driver.find_element(By.ID,'source-text').get_attribute('value').strip()
    assert driver.execute_script('return UI.settings.endpoint') == ''
    capture_screenshot(driver, OUT / 'selection-translation.png')
    record('Real selection context menu opens a sourced workspace and pre-fills text without configuring or contacting an external translator')
    driver.close();driver.switch_to.window(control)

    driver.find_element(By.ID,'tab-translation').click()
    driver.find_element(By.ID,'native-translation').click()
    local = wait.until(lambda d: next((h for h in d.window_handles if h not in {source,control}),None))
    driver.switch_to.window(local)
    wait.until(lambda d: d.current_url == 'about:translations')
    wait.until(lambda d: d.find_elements(By.CSS_SELECTOR,'textarea, [contenteditable=true]'))
    capture_screenshot(driver, OUT / 'native-translator.png')
    record('Normal Aion button opens the actual on-device Firefox translation UI')
    driver.close();driver.switch_to.window(control)
    driver.find_element(By.ID,'tab-video').send_keys(Keys.HOME)
    assert driver.find_element(By.ID,'tab-translation').get_attribute('aria-selected') == 'true'
    record('Task tabs support keyboard navigation without clearing a translation draft')
    driver.find_element(By.ID,'settings').click()
    settings = wait.until(lambda d: next((h for h in d.window_handles if h not in {source,control}),None))
    driver.switch_to.window(settings)
    wait.until(lambda d: d.find_element(By.ID,'language'))
    Select(driver.find_element(By.ID,'language')).select_by_value('tr')
    wait.until(lambda d: d.execute_script('return UI.settings.language === "tr";'))
    driver.switch_to.window(control)
    wait.until(lambda d: d.find_element(By.ID,'tab-translation').text == 'Çeviri')
    assert driver.find_element(By.ID,'source-text').get_attribute('value') == 'Öğrenme · Hello world'
    capture_screenshot(driver, OUT / 'workspace-tr.png')
    driver.switch_to.window(settings)
    Select(driver.find_element(By.ID,'font')).select_by_value('opendyslexic')
    field = driver.find_element(By.ID,'scale-number');field.send_keys(Keys.CONTROL,'a');field.send_keys('200',Keys.TAB)
    wait.until(lambda d: d.execute_script('return UI.settings.scale === 200;'))
    driver.set_window_size(480,900);driver.switch_to.window(control)
    wait.until(lambda d: d.execute_script('return document.documentElement.lang === "tr" && parseFloat(getComputedStyle(document.documentElement).fontSize) === 32;'))
    assert driver.execute_script('return document.documentElement.scrollWidth <= innerWidth + 2;')
    capture_screenshot(driver, OUT / 'workspace-tr-200-narrow.png')
    record('Turkish/English switching preserves the open draft; OpenDyslexic and200percent scale fit a narrow workspace')
    driver.switch_to.window(settings)
    driver.find_element(By.ID,'reset-scale').click()
    Select(driver.find_element(By.ID,'font')).select_by_value('system')
    wait.until(lambda d: d.execute_script('return UI.settings.scale === 100;'))
    driver.close();driver.switch_to.window(source);driver.set_window_size(1440,1050)
    driver.get(f'http://127.0.0.1:{server.server_port}/')
    driver.execute_async_script('const done=arguments[0];requestAnimationFrame(()=>requestAnimationFrame(done));')
    before = set(driver.window_handles)
    driver.execute_script('document.dispatchEvent(new CustomEvent("Aion:OpenTranslator",{bubbles:true}));')
    driver.execute_async_script('const done=arguments[0];requestAnimationFrame(()=>requestAnimationFrame(done));')
    assert set(driver.window_handles) == before
    record('An ordinary website cannot invoke the privileged native translation bridge')

finally:
    try:
        driver.set_context('content')
        (OUT / 'ui-state.json').write_text(json.dumps(driver.execute_script('return {href:location.href,status:document.getElementById("status")?.textContent,ready:document.body.dataset.ready,clicks:window.aionClicks,workspace:typeof workspace,source:typeof sourceTabId === "undefined" ? null : sourceTabId};'),indent=2))
    except Exception:
        pass
    try:
        driver.set_context('chrome')
        capture_screenshot(driver, OUT / 'last-window.png')
        (OUT / 'context-menu-state.json').write_text(json.dumps(driver.execute_script('return [...document.querySelectorAll("#contentAreaContextMenu menuitem,#contentAreaContextMenu menu")].filter(e=>e.id.includes("aion")).map(e=>({id:e.id,label:e.getAttribute("label"),hidden:e.hidden}));'),ensure_ascii=False,indent=2))
        (OUT / 'actor-state.json').write_text(json.dumps(driver.execute_script('try {const g=gBrowser.selectedBrowser.browsingContext.currentWindowGlobal;const a=g.getActor("AionTools");return {uri:g.documentURI.spec,scheme:g.documentURI.scheme,path:g.documentURI.pathQueryRef,policy:WebExtensionPolicy.getByURI(g.documentURI)?.id,open:typeof gBrowser.selectedBrowser.documentGlobal.openTrustedLinkIn,actor:a.constructor.name};}catch(e){return {error:String(e)};}'),indent=2))
        (OUT / 'popup-dimensions.json').write_text(json.dumps(driver.execute_script('return [...document.querySelectorAll(".webextension-popup-browser")].map(b=>({width:b.getBoundingClientRect().width,height:b.getBoundingClientRect().height,src:b.getAttribute("src")}));'),indent=2))
    except Exception:
        pass
    (OUT / 'results.json').write_text(json.dumps({'passed':passed,'mode':'actual-compiled-fork-tools','limits':'Synthetic page/cookie/text only. Opening native translation UI alone is not proof that model downloads or inference succeed.'},ensure_ascii=False,indent=2)+'\n')
    driver.quit(); server.shutdown(); server.server_close()
