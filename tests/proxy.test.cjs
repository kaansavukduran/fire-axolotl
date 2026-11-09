/* SPDX-License-Identifier: MPL-2.0 */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const patch = JSON.parse(fs.readFileSync('browser/native/service-request-proxy.json', 'utf8'));

async function sourceFor(policies) {
  const context = vm.createContext({Services: {policies: {getActivePolicies: () => policies}}});
  // Exercise the exact replacement in the surrounding branch. The prior
  // implementation throws on the actual dictionary-shaped policy API.
  return vm.runInContext(`(async () => {${patch.new}
    return 'policy';
  }
  return 'prefs';
  })()`, context);
}

test('privacy-only policies do not break service-request proxy fallback', async () => {
  assert.equal(await sourceFor({DisableTelemetry: true}), 'prefs');
});
test('a configured enterprise proxy is still identified as policy-controlled', async () => {
  assert.equal(await sourceFor({DisableTelemetry: true, Proxy: {Mode: 'system'}}), 'policy');
});
