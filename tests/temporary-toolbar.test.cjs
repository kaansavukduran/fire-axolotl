// SPDX-License-Identifier: MPL-2.0
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
test('temporary toolbar removes only owned unused identities and rolls back failed creation', () => {
  let stored='[6,7]', next=8;
  const removed=[], windows=[{gBrowser:{tabs:[{getAttribute:()=> '7'}]}}];
  const context=vm.createContext({
    Services:{locale:{appLocaleAsBCP47:'tr'},prefs:{getStringPref:()=>stored,setStringPref:(_,value)=>stored=value},wm:{getEnumerator:()=>windows}},
    CustomizableUI:{},SessionStore:{},PrivateBrowsingUtils:{isWindowPrivate:window=>!!window.private},
    ContextualIdentityService:{create:()=>({userContextId:next++}),remove:id=>removed.push(id)}
  });
  vm.runInContext(fs.readFileSync('browser/native/aion-runner/toolbar.sys.mjs','utf8').replace(/^import .*;\n/gm,'').replace(/^export /gm,''),context);
  context.cleanTemporary();assert.deepEqual(removed,[6]);assert.equal(stored,'[7]');
  assert.equal(context.openTemporary({private:true,gBrowser:{}}),false);assert.equal(stored,'[7]');
  assert.throws(()=>context.openTemporary({gBrowser:{addTrustedTab:()=>{throw Error('failed');}}}));
  assert.deepEqual(removed,[6,8]);assert.equal(stored,'[7]');
  windows[0].gBrowser.tabs=[];context.cleanTemporary();assert.deepEqual(removed,[6,8,7]);assert.equal(stored,'[]');
});
