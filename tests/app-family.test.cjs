/* SPDX-License-Identifier: MPL-2.0 */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
test('remote browser-family detection recognizes the fork without accepting unrelated Gecko applications', () => {
  const patch = JSON.parse(fs.readFileSync('browser/native/remote-app-family.json', 'utf8'));
  const firefox = '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}';
  for (const [id, expected] of [[firefox,true],['{75450dd9-387d-4289-8b23-7ad6609fa530}',true],['{3550f703-e582-4d05-9a08-453d09bdfdc6}',false],['unrelated-app',false]]) {
    assert.equal(vm.runInNewContext(`(() => {${patch.new}})()`, {Services:{appinfo:{ID:id}},ID_FIREFOX:firefox}),expected);
  }
});
