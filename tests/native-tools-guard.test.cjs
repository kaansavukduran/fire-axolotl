// SPDX-License-Identifier: MPL-2.0
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
test('native translator bridge accepts only the own tools page and ignores caller-supplied destinations', () => {
  const opened = [];
  let owner = 'another@extension';
  const context = vm.createContext({JSWindowActorParent:class {},WebExtensionPolicy:{getByURI:()=>({id:owner})}});
  vm.runInContext(fs.readFileSync('browser/native/aion-runner/AionToolsParent.sys.mjs','utf8').replace(/^export /gm,''),context);
  const Type = vm.runInContext('AionToolsParent',context), actor = new Type();
  actor.manager={documentURI:{scheme:'moz-extension',pathQueryRef:'/popup.html?view=tab#translation'}};
  actor.browsingContext={top:{embedderElement:{documentGlobal:{openTrustedLinkIn:(url,where)=>opened.push({url,where})}}}};
  const request={name:'AionTools:OpenTranslator',data:{url:'file:///private',code:'arbitrary code'}};
  assert.equal(actor.receiveMessage(request),false);
  owner='aion@fire-axolotl.browser';
  actor.manager.documentURI.scheme='https';assert.equal(actor.receiveMessage(request),false);
  actor.manager.documentURI.scheme='moz-extension';actor.manager.documentURI.pathQueryRef='/settings.html';assert.equal(actor.receiveMessage(request),false);
  actor.manager.documentURI.pathQueryRef='/popup.html?sourceTabId=7#translation';
  assert.equal(actor.receiveMessage({name:'OtherAction'}),false);
  assert.equal(actor.receiveMessage(request),true);
  assert.deepEqual(opened,[{url:'about:translations',where:'tab'}]);
});
