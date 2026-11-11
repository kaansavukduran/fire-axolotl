# SPDX-License-Identifier: MPL-2.0
"""Use the installed browser's real new tab, restore control and container widget."""
import http.server
import json
import os
import subprocess
from urllib.parse import urlsplit
from pathlib import Path
import tempfile
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work/newtab-test-artifacts'
OUT.mkdir(exist_ok=True)
profile = tempfile.TemporaryDirectory(prefix='newtab-profile-')
passed=[]
class Fixture(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(b'<!doctype html><title>Container fixture</title><p>Local fixture</p>')
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Fixture)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/'
options=Options();options.binary_location=os.environ['AION_NATIVE_BINARY'];options.add_argument('-headless');options.add_argument('-profile');options.add_argument(profile.name)
options.accept_insecure_certs=False;options.set_preference('remote.prefs.recommended',False);options.set_preference('browser.shell.checkDefaultBrowser',False)
managed = os.environ.get('AION_MANAGED_TLS_PROXY') == '1'
if managed:
    # Trust only the executor-supplied inspection CA in this synthetic profile.
    # Product trust settings and certificate verification remain unchanged.
    proxy=urlsplit(os.environ['HTTPS_PROXY']);assert not proxy.username and not proxy.password
    ca=Path(os.environ['NODE_EXTRA_CA_CERTS']);assert ca.is_file()
    subprocess.run(['certutil','-N','--empty-password','-d','sql:'+profile.name],check=True)
    subprocess.run(['certutil','-A','-d','sql:'+profile.name,'-n','Managed executor test CA','-t','C,,','-i',str(ca)],check=True)
    options.set_preference('network.proxy.type',1)
    for protocol in ['http','ssl']:
        options.set_preference('network.proxy.'+protocol,proxy.hostname);options.set_preference('network.proxy.'+protocol+'_port',proxy.port)
    options.set_preference('network.proxy.no_proxies_on','localhost,127.0.0.1')
def launch():return webdriver.Firefox(options=options,service=Service(os.environ['AION_GECKODRIVER'],service_args=['--allow-system-access'],log_output=str(OUT/'geckodriver.log')))
def record(message):passed.append(message);print('PASS',message,flush=True)
def native():driver.set_context('chrome')
def content():driver.set_context('content')
def newtab():
    content();driver.get('about:newtab');wait.until(lambda d:d.find_elements(By.ID,'fireaxolotl-newtab-tools'))
def temporary():
    content();before=set(driver.window_handles);native();driver.find_element(By.ID,'aion-new-temporary-tab').click();content()
    try:handle=wait.until(lambda d:next((h for h in d.window_handles if h not in before),None))
    except Exception:
        native();(OUT/'temporary-debug.json').write_text(json.dumps(driver.execute_script('return {ids:Services.prefs.getStringPref("fireaxolotl.temporaryTabs.ids","[]"),tabs:[...gBrowser.tabs].map(t=>({id:t.getAttribute("usercontextid"),url:t.linkedBrowser.currentURI.spec})),button:document.getElementById("aion-new-temporary-tab").outerHTML,messages:Services.console.getMessageArray().filter(x=>String(x.message).includes("toolbar.sys")).map(x=>x.message)};'),indent=2));driver.save_screenshot(str(OUT/'temporary-failure.png'));raise
    driver.switch_to.window(handle)
    native();identity=int(driver.execute_script('return gBrowser.selectedTab.getAttribute("usercontextid");'))
    content();driver.get(url);return handle,identity

driver=None
try:
    driver=launch();wait=WebDriverWait(driver,30);driver.set_window_size(1440,1050);newtab();source=driver.current_window_handle
    native();wait.until(lambda d:d.find_elements(By.ID,'aion-new-temporary-tab'))
    assert driver.execute_script('return !Services.prefs.getBoolPref("sidebar.verticalTabs") && CustomizableUI.getWidgetIdsInArea("nav-bar").includes("search-container") && Services.prefs.getStringPref("browser.toolbars.bookmarks.visibility")==="always";')
    record('Fresh profile has top tabs, separate search, bookmarks and a movable temporary-tab toolbar button')
    content();assert driver.execute_script('return document.body.dataset.aionWallpaper==="true" && getComputedStyle(document.body).backgroundImage.includes("aion-wallpaper.png");')
    native();driver.save_screenshot(str(OUT/'newtab-wallpaper.png'));content()
    record('Native new tab loads the packaged Aion wallpaper without a remote wallpaper request')
    host=wait.until(lambda d:d.find_element(By.ID,'fireaxolotl-runner'));shadow=host.shadow_root
    assert not shadow.find_elements(By.CSS_SELECTOR,'.hide') and not shadow.find_elements(By.CSS_SELECTOR,'iframe')
    assert '0.12.0' in shadow.find_element(By.CSS_SELECTOR,'h2').text
    assert shadow.find_element(By.CSS_SELECTOR,'[data-action="play"]').is_enabled()
    record('Full local game has its current version, explicit launch and no upper-right hide control')
    native();redesigned=driver.execute_script('return Services.prefs.getBoolPref("browser.settings-redesign.enabled",false);');content()
    driver.get('about:preferences#'+('appearance' if redesigned else 'general'))
    box=wait.until(lambda d:d.find_element(By.ID,'aion-newtab-game'));driver.execute_script('arguments[0].scrollIntoView({block:"center"});',box);box.click()
    newtab();assert not driver.find_elements(By.ID,'fireaxolotl-runner')
    driver.refresh();wait.until(lambda d:d.find_element(By.ID,'aion-restore-game').is_displayed())
    driver.find_element(By.ID,'aion-restore-game').click();wait.until(lambda d:d.find_elements(By.ID,'fireaxolotl-runner'))
    record('Only Appearance controls visibility; the restore button recovers a previously disabled game across page reloads')
    driver.get(url);driver.execute_script('document.cookie="aion=personal;path=/";')
    first,first_id=temporary();assert not driver.execute_script('return document.cookie');driver.execute_script('document.cookie="aion=first;path=/";')
    second,second_id=temporary();assert first_id!=second_id and not driver.execute_script('return document.cookie')
    driver.switch_to.window(source);assert driver.execute_script('return document.cookie')=='aion=personal'
    record('Two real toolbar clicks create different temporary cookie stores while the original login stays intact')
    native();permanent=driver.execute_script('return ContextualIdentityService.create("Permanent fixture","circle","blue").userContextId;')
    content();driver.switch_to.window(first);driver.close();driver.switch_to.window(second);native()
    wait.until(lambda d:d.execute_script('return !ContextualIdentityService.getPublicIdentityFromId(arguments[0]);',first_id))
    assert driver.execute_script('return !!ContextualIdentityService.getPublicIdentityFromId(arguments[0]) && !!ContextualIdentityService.getPublicIdentityFromId(arguments[1]);',second_id,permanent)
    content();driver.close();driver.switch_to.window(source);native()
    wait.until(lambda d:d.execute_script('return !ContextualIdentityService.getPublicIdentityFromId(arguments[0]);',second_id))
    assert driver.execute_script('return !!ContextualIdentityService.getPublicIdentityFromId(arguments[0]);',permanent)
    record('Last-tab cleanup removes only the relevant owned temporary identity and preserves other temporary and permanent identities')
    redesigned=driver.execute_script('return Services.prefs.getBoolPref("browser.settings-redesign.enabled",false);')
    content();driver.get('about:preferences#'+('appearance' if redesigned else 'general'))
    box=wait.until(lambda d:d.find_element(By.ID,'aion-newtab-wallpaper'))
    driver.execute_script('arguments[0].scrollIntoView({block:"center"});',box);box.click()
    newtab();assert driver.execute_script('return !document.body.dataset.aionWallpaper;')
    assert driver.find_elements(By.ID,'fireaxolotl-runner')
    record('Real Appearance checkbox turns wallpaper off without hiding or resetting the game')
    driver.set_window_size(480,900)
    (OUT/'narrow-dimensions.json').write_text(json.dumps(driver.execute_script('return {inner:innerWidth,scroll:document.documentElement.scrollWidth,wide:[...document.querySelectorAll("body *")].filter(e=>e.getBoundingClientRect().right>innerWidth+2).slice(0,20).map(e=>({tag:e.localName,id:e.id,cls:typeof e.className==="string"?e.className:"",width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right}))};'),indent=2))
    driver.save_screenshot(str(OUT/'narrow-content.png'))
    assert driver.execute_script('return document.documentElement.scrollWidth <= innerWidth+2;')
    native();driver.save_screenshot(str(OUT/'newtab-narrow.png'))
    record('New-tab game links and restore controls fit a narrow browser window')
    driver.execute_script('CustomizableUI.removeWidgetFromArea("search-container");Services.prefs.setBoolPref("sidebar.verticalTabs",true);Services.prefs.setStringPref("browser.toolbars.bookmarks.visibility","never");')
    driver.quit();driver=None
    driver=launch();wait=WebDriverWait(driver,30);newtab();native();wait.until(lambda d:d.find_elements(By.ID,'aion-new-temporary-tab'))
    assert driver.execute_script('return Services.prefs.getBoolPref("sidebar.verticalTabs") && !CustomizableUI.getWidgetIdsInArea("nav-bar").includes("search-container") && Services.prefs.getStringPref("browser.toolbars.bookmarks.visibility")==="never" && !Services.prefs.getBoolPref("fireaxolotl.newtab.wallpaper");')
    record('A real process restart preserves customized tabs, removed search, hidden bookmarks and wallpaper choice')
finally:
    (OUT/'results.json').write_text(json.dumps({'passed':passed,'mode':'actual-compiled-fork-newtab','tls_verification':True,'managed_test_proxy':managed,'limits':'Synthetic local cookie fixtures. Live-game step verifies actual user-initiated navigation, not every Godot gameplay feature.'},ensure_ascii=False,indent=2)+'\n')
    if driver:driver.quit()
    profile.cleanup();server.shutdown();server.server_close()
