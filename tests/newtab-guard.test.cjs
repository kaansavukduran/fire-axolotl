// SPDX-License-Identifier: MPL-2.0
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
test('native new-tab actor rejects websites and has no remote-game or Hide action',()=>{
  const changed=[];
  const context=vm.createContext({JSWindowActorParent:class{},Services:{prefs:{setBoolPref:(...args)=>changed.push(args)},locale:{}}});
  vm.runInContext(fs.readFileSync('browser/native/aion-runner/AionRunnerParent.sys.mjs','utf8').replace(/^export /gm,''),context);
  const actor=new (vm.runInContext('AionRunnerParent',context))();
  actor.manager={documentURI:{spec:'https://example.org/'}};
  for(const name of ['Aion:OpenGame','Aion:Hide','Aion:Show','Aion:GetConfig']) assert.equal(actor.receiveMessage({name,data:{url:'file:///private'}}),null);
  assert.equal(changed.length,0);
  actor.manager.documentURI.spec='about:newtab';
  for(const name of ['Aion:OpenGame','Aion:Hide']) assert.equal(actor.receiveMessage({name}),null);
  assert.equal(changed.length,0);
});
