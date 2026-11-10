# SPDX-License-Identifier: MPL-2.0
"""Verify real on-device translation with public model downloads and fixture text."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlsplit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from gecko_controls import capture_screenshot

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work/translation-test-artifacts'
OUT.mkdir(exist_ok=True)
profile = tempfile.TemporaryDirectory(prefix='translation-profile-')
options = Options()
options.binary_location = os.environ['AION_NATIVE_BINARY']
options.add_argument('-headless')
options.add_argument('-profile'); options.add_argument(profile.name)
options.accept_insecure_certs = False
options.set_preference('remote.prefs.recommended', False)
options.set_preference('browser.shell.checkDefaultBrowser', False)
managed = os.environ.get('AION_MANAGED_TLS_PROXY') == '1'
if managed:
    # Test-profile trust for the managed executor's supplied inspection CA.
    # Never change packaged browser trust or disable certificate verification.
    proxy = urlsplit(os.environ['HTTPS_PROXY'])
    assert not proxy.username and not proxy.password
    ca = Path(os.environ['NODE_EXTRA_CA_CERTS'])
    assert ca.is_file()
    database = 'sql:' + profile.name
    subprocess.run(['certutil','-N','--empty-password','-d',database],check=True)
    subprocess.run(['certutil','-A','-d',database,'-n','Managed executor test CA','-t','C,,','-i',str(ca)],check=True)
    options.set_preference('network.proxy.type',1)
    for protocol in ['http','ssl']:
        options.set_preference('network.proxy.'+protocol,proxy.hostname)
        options.set_preference('network.proxy.'+protocol+'_port',proxy.port)
    options.set_preference('network.proxy.no_proxies_on','localhost,127.0.0.1')
driver = None
report = {'passed':False,'fixture':'Hello world','target':'tr','tls_verification':True,'managed_test_proxy':managed,'limits':'Two synthetic English to Turkish translations, including a new phrase after going offline. Models downloaded by the native Firefox tool; no model is claimed to ship preinstalled.'}
try:
    driver = webdriver.Firefox(options=options,service=Service(os.environ['AION_GECKODRIVER'],service_args=['--allow-system-access'],log_output=str(OUT/'geckodriver.log')))
    driver.set_window_size(1440,1050)
    driver.get('about:translations')
    wait = WebDriverWait(driver,180)
    source = wait.until(lambda d: next((e for e in d.find_elements(By.ID,'about-translations-source-textarea') if e.is_displayed()),None))
    for name,value in [('source','en'),('target','tr')]:
        host = driver.find_element(By.ID,f'about-translations-{name}-select')
        control = wait.until(lambda d: host.shadow_root.find_element(By.CSS_SELECTOR,'select'))
        wait.until(lambda d: any(o.get_attribute('value') == value for o in control.find_elements(By.TAG_NAME,'option')))
        Select(control).select_by_value(value)
    source.send_keys('Hello world')
    result = wait.until(lambda d: (lambda value: value if any(part in value.casefold() for part in ['merhaba','dünya']) else False)(d.find_element(By.ID,'about-translations-target-textarea').get_attribute('value').strip()))
    assert result.casefold() != 'hello world' and any(part in result.casefold() for part in ['merhaba','dünya']), result
    driver.set_context('chrome'); driver.execute_script('Services.io.offline = true;'); driver.set_context('content')
    source.send_keys(Keys.CONTROL,'a'); source.send_keys('Good morning')
    offline = wait.until(lambda d: (lambda value: value if any(part in value.casefold() for part in ['günaydın','sabah']) else False)(d.find_element(By.ID,'about-translations-target-textarea').get_attribute('value').strip()))
    report.update(passed=True,result=result,offline_result=offline,offline_inference_verified=True)
    capture_screenshot(driver,OUT/'real-english-turkish.png')
    print('PASS Actual native on-device English to Turkish inference:',result,flush=True)
finally:
    if driver:
        if not report['passed']:
            report['visible_state'] = driver.execute_script('return document.body.innerText.slice(0,3000);')
            capture_screenshot(driver,OUT/'last-window.png')
        driver.quit()
    profile.cleanup()
    (OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
