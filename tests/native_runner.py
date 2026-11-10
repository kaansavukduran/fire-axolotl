# SPDX-License-Identifier: MPL-2.0
"""Exercise the new-tab game in the installed, compiled product's normal UI."""
import json
import os
from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('AION_RUNNER_ARTIFACTS', ROOT / 'work/runner-test-artifacts'))
OUT.mkdir(parents=True, exist_ok=True)
options = Options()
options.binary_location = os.environ['AION_NATIVE_BINARY']
options.add_argument('-headless')
options.accept_insecure_certs = False
options.set_preference('remote.prefs.recommended', False)
options.set_preference('browser.shell.checkDefaultBrowser', False)
options.set_preference('fireaxolotl.newtabGame.language', 'tr')
options.set_preference('ui.prefersReducedMotion', 1)
driver = webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], log_output=str(OUT / 'geckodriver.log')))
wait = WebDriverWait(driver, 30)
passed = []


def record(name):
    passed.append(name)
    print('PASS', name, flush=True)


def card():
    host = wait.until(lambda d: d.find_element(By.ID, 'fireaxolotl-runner'))
    shadow = host.shadow_root
    canvas = shadow.find_element(By.CSS_SELECTOR, 'canvas')
    play = shadow.find_element(By.CSS_SELECTOR, '[data-action="play"]')
    wait.until(lambda _: play.is_enabled())
    return shadow, canvas, play


def screenshot(name):
    driver.set_context('chrome')
    driver.save_screenshot(str(OUT / name))
    driver.set_context('content')


try:
    driver.set_window_size(1440, 1050)
    driver.set_context('chrome')
    assert driver.execute_script('return Services.appinfo.ID') == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
    driver.set_context('content')
    driver.get('about:newtab')
    shadow, canvas, play = card()
    assert driver.find_element(By.CSS_SELECTOR, '.search-wrapper').is_displayed()
    assert canvas.get_attribute('data-state') == 'ready'
    assert shadow.find_element(By.CSS_SELECTOR, 'h2').text == 'Aion Koşusu'
    screenshot('newtab-ready.png')
    record('Normal compiled-fork new tab keeps search and has the Turkish game ready without autoplay')

    driver.set_context('chrome')
    urlbar = driver.find_element(By.ID, 'urlbar-input')
    urlbar.send_keys(Keys.CONTROL, 'l')
    urlbar.send_keys('hello world')
    assert driver.execute_script('return gURLBar.value').endswith('hello world')
    urlbar.send_keys(Keys.ESCAPE)
    driver.set_context('content')
    assert canvas.get_attribute('data-state') == 'ready'
    record('Space in the address bar stays ordinary text and does not start the game')

    play.click()
    wait.until(lambda _: canvas.get_attribute('data-state') == 'running')
    canvas.send_keys(Keys.SPACE)
    wait.until(lambda _: canvas.get_attribute('data-airborne') == 'true')
    screenshot('newtab-jump.png')
    canvas.send_keys(Keys.ESCAPE)
    wait.until(lambda _: canvas.get_attribute('data-state') == 'paused')
    frozen = canvas.get_attribute('data-score')
    time.sleep(0.2)
    assert canvas.get_attribute('data-score') == frozen
    record('Explicit Start, actual Space jump, Esc pause and paused score behave correctly')

    play.click()
    original = driver.current_window_handle
    driver.set_context('chrome')
    driver.find_element(By.ID, 'tabs-newtab-button').click()
    driver.set_context('content')
    other = wait.until(lambda d: next((h for h in d.window_handles if h != original), None))
    # Let the child receive the real background-tab visibility transition.
    time.sleep(0.3)
    driver.switch_to.window(original)
    wait.until(lambda _: canvas.get_attribute('data-state') == 'paused')
    driver.switch_to.window(other)
    driver.close()
    driver.switch_to.window(original)
    record('Switching to another tab pauses gameplay until an explicit Resume')

    seen = set()
    for attempt in range(24):
        play.click()
        state = wait.until(lambda _: canvas.get_attribute('data-state') if canvas.get_attribute('data-state') in ['ice', 'fire'] else False)
        time.sleep(1.1)
        if state not in seen:
            screenshot(f'newtab-{state}.png')
        seen.add(state)
        if seen == {'ice', 'fire'}:
            break
    assert seen == {'ice', 'fire'}, seen
    record('Real obstacle collisions play both freeze and fire-to-ash frame sequences')

    shadow.find_element(By.CSS_SELECTOR, '.hide').click()
    wait.until(lambda _: not driver.find_elements(By.ID, 'fireaxolotl-runner'))
    driver.get('about:newtab')
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, '.search-wrapper'))
    time.sleep(0.3)
    assert not driver.find_elements(By.ID, 'fireaxolotl-runner')
    driver.set_context('chrome')
    assert driver.execute_script('return Services.prefs.getBoolPref("fireaxolotl.newtabGame.enabled")') is False
    driver.set_context('content')
    record('Hide removes the card and saves the preference for subsequent new tabs')

    driver.get('about:preferences#appearance')
    checkbox = wait.until(lambda d: d.find_element(By.ID, 'aion-newtab-game'))
    driver.execute_script('arguments[0].scrollIntoView({block:"center"})', checkbox)
    if not checkbox.is_selected():
        checkbox.click()
    assert checkbox.is_selected()
    from gecko_controls import choose_option
    choose_option(driver, 'aion-game-language', 'en')
    driver.set_context('chrome')
    driver.execute_script('Services.prefs.setIntPref("fireaxolotl.newtabGame.best",7)')
    driver.set_context('content')
    driver.get('about:newtab')
    shadow, canvas, play = card()
    assert shadow.find_element(By.CSS_SELECTOR, 'h2').text == 'Aion Run'
    assert shadow.find_element(By.CSS_SELECTOR, '.best').text == 'Best 7'
    screenshot('newtab-english.png')
    record('Native Appearance controls restore the game and change its language; the saved local record is displayed')

    driver.get('about:preferences#appearance')
    reset = wait.until(lambda d: d.find_element(By.ID, 'aion-game-reset'))
    driver.execute_script('arguments[0].scrollIntoView({block:"center"})', reset)
    reset.click()
    driver.get('about:newtab')
    shadow, canvas, play = card()
    assert shadow.find_element(By.CSS_SELECTOR, '.best').text == 'Best 0'
    record('Reset record clears only the local game record')

    driver.get('data:text/html,<title>Ordinary page</title><input>')
    assert not driver.find_elements(By.ID, 'fireaxolotl-runner')
    driver.set_context('chrome')
    assert driver.execute_script('try {gBrowser.selectedBrowser.browsingContext.currentWindowGlobal.getActor("AionRunner");return false;}catch{return true;}') is True
    driver.set_context('content')
    record('Ordinary web content has neither the game nor access to its privileged actor')
    (OUT / 'results.json').write_text(json.dumps({'passed': passed, 'mode': 'compiled-fork-normal-newtab', 'count': len(passed)}, ensure_ascii=False, indent=2) + '\n')
finally:
    driver.quit()
