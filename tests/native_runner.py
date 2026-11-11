# SPDX-License-Identifier: MPL-2.0
"""Exercise the actual pinned Godot game inside the installed native new tab.

Requires a graphical desktop (Linux CI uses xvfb-run). Windows hosted CI can
explicitly select the CPU-only WARP fixture; product graphics defaults remain
unchanged. No injected game state, certificate exceptions or sandbox changes.
"""
import json
import os
from pathlib import Path
import tempfile
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

ROOT=Path(__file__).resolve().parents[1]
PIN=json.loads((ROOT/'browser/game/PIN.json').read_text())
OUT=Path(os.environ.get('AION_RUNNER_ARTIFACTS',ROOT/'work/runner-test-artifacts'));OUT.mkdir(parents=True,exist_ok=True)
profile=tempfile.TemporaryDirectory(prefix='aion-full-game-');passed=[];driver=None
test_warp=os.environ.get('AION_TEST_WINDOWS_WARP')=='1'
graphics={'windows_ci_cpu_fixture':test_warp}

def launch():
    options=Options();options.binary_location=os.environ['AION_NATIVE_BINARY']
    options.add_argument('-profile');options.add_argument(profile.name)
    options.accept_insecure_certs=False
    options.set_preference('remote.prefs.recommended',False)
    options.set_preference('browser.shell.checkDefaultBrowser',False)
    if test_warp:
        if os.name!='nt' or os.environ.get('GITHUB_ACTIONS')!='true':
            raise RuntimeError('WARP fixture is restricted to isolated Windows CI profiles')
        # Hosted Windows has a Basic Display adapter outside Firefox's WebGL2
        # allowlist. Select Microsoft's CPU renderer, then allow WebGL2 only in
        # this disposable test profile. Never enable its blocked hardware GPU.
        options.set_preference('webgl.angle.force-warp',True)
        options.set_preference('gfx.blacklist.webgl2',1)  # FEATURE_STATUS_OK
    return webdriver.Firefox(options=options,service=Service(os.environ['AION_GECKODRIVER'],service_args=['--allow-system-access'],log_output=str(OUT/'geckodriver.log')))
def record(message):passed.append(message);print('PASS',message,flush=True)
def native():driver.set_context('chrome')
def content():driver.set_context('content')
def enter():
    driver.switch_to.default_content();driver.get('about:newtab')
    host=wait.until(lambda d:d.find_element(By.ID,'fireaxolotl-runner'));shadow=host.shadow_root
    shadow.find_element(By.CSS_SELECTOR,'[data-action="play"]').click()
    frame=wait.until(lambda d:shadow.find_element(By.CSS_SELECTOR,'iframe'))
    driver.switch_to.frame(frame)
    canvas=wait.until(lambda d:d.find_element(By.CSS_SELECTOR,'canvas[data-ui-ready="true"]'))
    return canvas

def data(key):return canvas.get_attribute('data-'+key)
def state(value):wait.until(lambda d:data('state')==value)
def click(text=None,name=None):
    wait.until(lambda d:data('ui-ready')=='true')
    controls=json.loads(data('ui'))
    target=next((b for b in controls if b['name']==name),None) if name else next((b for b in controls if b['text']==text),None)
    assert target, (text,name,controls)
    a,b,c,d,tx,ty=json.loads(data('screen-transform'))
    x=target['x']+target['w']/2;y=target['y']+target['h']/2
    size=driver.execute_script('const r=arguments[0].getBoundingClientRect();return {w:r.width,h:r.height};',canvas)
    ActionChains(driver).move_to_element_with_offset(canvas,round((a*x+c*y+tx)*size['w']/float(data('raw-width'))-size['w']/2),round((b*x+d*y+ty)*size['h']/float(data('raw-height'))-size['h']/2)).click().perform()

def screenshot(name):
    driver.switch_to.default_content();native();driver.save_screenshot(str(OUT/name));content();driver.switch_to.frame(driver.find_element(By.ID,'fireaxolotl-runner').shadow_root.find_element(By.CSS_SELECTOR,'iframe'))

try:
    driver=launch();wait=WebDriverWait(driver,90);driver.set_window_size(1440,1100)
    driver.get('about:newtab');host=wait.until(lambda d:d.find_element(By.ID,'fireaxolotl-runner'));shadow=host.shadow_root
    assert driver.find_element(By.CSS_SELECTOR,'.search-wrapper').is_displayed()
    assert not shadow.find_elements(By.CSS_SELECTOR,'iframe,.hide')
    assert PIN['version'] in shadow.find_element(By.CSS_SELECTOR,'h2').text
    record('Real new tab preserves search and waits for explicit launch; no Hide button or old miniature game')
    native();driver.execute_script('Services.io.offline=true;');content()
    canvas=enter();assert data('version')==PIN['version'] and driver.execute_script('return AION_BUILD.build')==PIN['build']
    graphics['renderer']=driver.execute_script('const gl=document.getElementById("canvas").getContext("webgl2");const info=gl.getExtension("WEBGL_debug_renderer_info");return info?gl.getParameter(info.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER);')
    if test_warp:
        assert any(word in graphics['renderer'].lower() for word in ['basic render','warp','software rasterizer']),graphics
    print('Actual game graphics',graphics,flush=True)
    assert data('state')=='ready' and data('page')=='main'
    record('First-ever full-game launch works with the browser offline and matches the pinned production version/build')
    assert driver.execute_script('try {parent.document.body;return false;}catch(e){return e.name==="SecurityError";}')
    assert driver.execute_script('return typeof browser.tabs==="undefined" && typeof browser.cookies==="undefined" && typeof browser.storage==="undefined";')
    driver.switch_to.default_content();native()
    permissions = driver.execute_async_script('const done=arguments[0];ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs").AddonManager.getAddonByID("aion-game@fire-axolotl.browser").then(a=>done(a.userPermissions));')
    print('Game permissions',permissions,flush=True)
    assert permissions['origins']==[] and permissions['permissions']==[] and not permissions.get('data_collection')
    assert driver.execute_script('const frame=gBrowser.selectedBrowser.browsingContext.children.find(c=>c.currentWindowGlobal?.documentPrincipal?.schemeIs("moz-extension"));return frame && !frame.currentWindowGlobal.documentPrincipal.isSystemPrincipal;')
    content();driver.switch_to.frame(driver.find_element(By.ID,'fireaxolotl-runner').shadow_root.find_element(By.CSS_SELECTOR,'iframe'));canvas=driver.find_element(By.ID,'canvas')
    record('Game has no browser-data permissions, cannot read its parent, and runs with a non-system principal')
    for character in ['owl','sheep','wolf','aion']:
        click(name='StartSelect_'+character);wait.until(lambda d:data('character')==character)
        assert data('pose-source').startswith('canonical-')
    screenshot('newtab-full-game-menu.png')
    record('All four real character buttons select the canonical Aion, owl, sheep and wolf animation sheets')
    click(text='Start running');state('running');canvas.send_keys(Keys.SPACE);wait.until(lambda d:data('airborne')=='true')
    canvas.send_keys(Keys.ESCAPE);state('paused');score=data('score');time.sleep(.3);assert data('score')==score
    record('Actual keyboard Space jumps and Esc pauses the real Godot game with a frozen score')
    click(text='Main menu');state('ready');click(name='StartSelect_wolf');click(text='Start running');state('running')
    ActionChains(driver).key_down(Keys.ARROW_DOWN).perform();wait.until(lambda d:data('ducking')=='true');ActionChains(driver).key_up(Keys.ARROW_DOWN).perform()
    canvas.send_keys(Keys.ESCAPE);state('paused')
    record('The current wolf character and real crouch/roll input work through the embedded game UI')
    click(text='Settings');wait.until(lambda d:data('page')=='settings');click(text='Türkçe');wait.until(lambda d:canvas.get_attribute('lang')=='tr')
    assert data('page')=='settings';screenshot('newtab-full-game-settings.png')
    record('The full in-game Settings menu switches language immediately without a browser translation substitute')
    canvas.send_keys(Keys.ESCAPE);state('paused');canvas.send_keys(Keys.ESCAPE);state('running')
    wait.until(lambda d:data('page')=='finished');assert data('state') in ['ice','fire','bonk']
    screenshot('newtab-full-game-collision.png')
    record('An actual unmodified offline run reaches its own animated collision/result screen')
    time.sleep(2.2);canvas=enter();assert canvas.get_attribute('lang')=='tr' and data('character')=='wolf'
    record('Real game preferences survive a new embedded document through its own IndexedDB save')
    driver.switch_to.default_content();host=driver.find_element(By.ID,'fireaxolotl-runner');shadow=host.shadow_root
    next(b for b in shadow.find_elements(By.CSS_SELECTOR,'button') if b.text=='Full screen').click()
    wait.until(lambda d:d.execute_script('return !!document.fullscreenElement;'))
    driver.execute_script('return document.exitFullscreen();')
    wait.until(lambda d:not d.execute_script('return !!document.fullscreenElement;'))
    assert driver.find_element(By.CSS_SELECTOR,'.search-wrapper').is_displayed()
    record('Real fullscreen control opens the full game and returning preserves the usable new-tab search')
    native();driver.execute_script('Services.io.offline=false;');content();driver.quit();driver=None
    driver=launch();wait=WebDriverWait(driver,90);driver.set_window_size(1440,1100);native();driver.execute_script('Services.io.offline=true;');content()
    canvas=enter();assert data('version')==PIN['version'] and canvas.get_attribute('lang')=='tr' and data('character')=='wolf'
    record('A genuine browser process restart preserves full-game preferences and supports another offline launch')
except Exception as error:
    print('FAIL',type(error).__name__,str(error)[:500],flush=True)
    if driver:
        try:
            print('GAME',driver.execute_script('const c=document.querySelector("canvas");return c?{body:document.body.innerText.slice(0,1500),state:c.dataset.state,page:c.dataset.page,character:c.dataset.character,ui:c.dataset.ui,transform:c.dataset.screenTransform,rect:c.getBoundingClientRect().toJSON()}:document.body.innerText;'),flush=True)
            driver.switch_to.default_content();native();driver.save_screenshot(str(OUT/'failure.png'))
        except Exception as capture_error:print('Capture',str(capture_error)[:200],flush=True)
    raise
finally:
    if driver:
        try:
            native();driver.execute_script('Services.io.offline=false;')
        finally:driver.quit()
    profile.cleanup()
    (OUT/'results.json').write_text(json.dumps({'passed':passed,'mode':'compiled-fork-normal-newtab','game_version':PIN['version'],'game_build':PIN['build'],'source_commit':PIN['source_commit'],'full_game':True,'offline_first_launch_verified':len(passed)>=2,'isolated_principal_verified':len(passed)>=3,'graphics':graphics,'tls_verification':True,'limits':'Real local Godot UI and representative gameplay; not an exhaustive replay of all upstream levels or GPU compatibility. Windows hosted CI explicitly uses Microsoft CPU WARP in this disposable profile; shipped graphics defaults and driver blocking remain unchanged.'},ensure_ascii=False,indent=2)+'\n')
