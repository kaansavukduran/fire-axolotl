# SPDX-License-Identifier: MPL-2.0
"""Sample actual default startup/new-tab HTTP attempts without weakening TLS."""
import http.server
import json
import os
from pathlib import Path
import threading
import tempfile
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from network_policy import endpoints, forbidden

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work/network-test-artifacts'
PRIVATE = ROOT / 'work/private-network-logs'
OUT.mkdir(parents=True, exist_ok=True)
PRIVATE.mkdir(parents=True, exist_ok=True)
PRIVATE = Path(tempfile.mkdtemp(prefix='sample-', dir=PRIVATE))
hits = []


class Canary(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        hits.append(self.path)
        body = b'<!doctype html><title>Fire Axolotl local network canary</title>'
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Canary)
threading.Thread(target=server.serve_forever, daemon=True).start()
environment = dict(os.environ, MOZ_LOG='timestamp,sync,nsHttp:5', MOZ_LOG_FILE=str(PRIVATE / 'http.log'))
options = Options()
options.binary_location = os.environ['AION_NATIVE_BINARY']
options.add_argument('-headless')
options.accept_insecure_certs = False
options.set_preference('remote.prefs.recommended', False)
options.set_preference('browser.shell.checkDefaultBrowser', False)
driver, identity, completed = None, None, False
try:
    driver = webdriver.Firefox(options=options, service=Service(os.environ['AION_GECKODRIVER'], service_args=['--allow-system-access'], env=environment, log_output=str(PRIVATE / 'geckodriver.log')))
    driver.set_context('chrome')
    identity = driver.execute_script('return {id:Services.appinfo.ID,version:Services.appinfo.version,build:Services.appinfo.appBuildID};')
    assert identity['id'] == '{75450dd9-387d-4289-8b23-7ad6609fa530}'
    assert identity['version'].removesuffix('esr') == json.loads((ROOT / 'upstream.json').read_text())['version'].removesuffix('esr')
    driver.set_context('content')
    driver.get(f'http://127.0.0.1:{server.server_port}/fire-axolotl-network-canary')
    driver.get('about:newtab')
    time.sleep(30)
    completed = True
finally:
    if driver:
        try:
            driver.quit()
        except Exception:
            completed = False
    server.shutdown()
    server.server_close()
    files = list(PRIVATE.glob('http.log*'))
    observed = set()
    for file in files:
        observed.update(endpoints(file.read_text(encoding='utf-8', errors='replace')))
    canary = ('127.0.0.1', '/fire-axolotl-network-canary') in observed and '/fire-axolotl-network-canary' in hits
    denied = sorted({host for host, path in observed if forbidden(host)})
    passed = completed and canary and not denied
    (OUT / 'results.json').write_text(json.dumps({'passed': passed, 'identity': identity, 'sample_seconds': 30, 'log_canary_verified': canary, 'observed': [{'host': host, 'path': path} for host, path in sorted(observed)], 'forbidden_hosts': denied, 'tls_verification': True, 'recommended_automation_prefs_disabled': True, 'limits': 'Fresh synthetic profile; startup and idle new tab only. HTTP initialization attempts, not proof of successful delivery. No account, real-user browsing or later scheduled traffic tested. Raw logs stay private and are excluded from release evidence.'}, indent=2) + '\n')
assert passed, f'Fresh-profile network sampling failed: canary={canary}, forbidden_hosts={denied}'
print('Actual network-log canary verified; no known telemetry, studies or sponsored-content HTTP attempts observed in the bounded startup/new-tab sample')
