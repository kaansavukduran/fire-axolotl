/* SPDX-License-Identifier: MPL-2.0 */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('browser/native/aion-chrome.js', 'utf8');
test('native first-run language never overwrites an existing choice and uses Turkish fallback only for new profiles', () => {
  for (const hasChoice of [true, false]) {
    let writes = 0;
    const locale = {availableLocales: ['en-US', 'tr'], langNegStrategyLookup: 2,
      negotiateLanguages(system, available, fallback, strategy) {
        assert.deepEqual(Array.from(system), ['zz-ZZ']);
        assert.equal(fallback, 'tr'); assert.equal(strategy, 2);
        return ['tr'];
      }, set requestedLocales(value) {writes++; assert.equal(value[0], 'tr');}};
    vm.runInNewContext(source, {Services: {locale, prefs: {prefHasUserValue: () => hasChoice}},
      Cc: {'@mozilla.org/intl/ospreferences;1': {getService: () => ({systemLocales: ['zz-ZZ']})}}, Ci: {mozIOSPreferences: {}},
      document: {readyState: 'loading', addEventListener() {}}});
    assert.equal(writes, hasChoice ? 0 : 1);
  }
});
