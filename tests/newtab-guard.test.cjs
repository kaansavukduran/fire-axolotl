// SPDX-License-Identifier: MPL-2.0
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
test('native new-tab actions reject websites and keep the official game in the source container',()=>{
  const opened=[],changed=[];
  const context=vm.createContext({JSWindowActorParent:class{},Services:{prefs:{setBoolPref:(...args)=>changed.push(args)},locale:{}}});
  vm.runInContext(fs.readFileSync('browser/native/aion-runner/AionRunnerParent.sys.mjs','utf8').replace(/^export /gm,''),context);
  const Type=vm.runInContext('AionRunnerParent',context), actor=new Type();
  actor.manager={documentURI:{spec:'https://example.org/'}};
  actor.browsingContext={top:{embedderElement:{getAttribute:()=> '7',documentGlobal:{openTrustedLinkIn:(...args)=>opened.push(args)}}}};
  assert.equal(actor.receiveMessage({name:'Aion:OpenGame',data:{url:'file:///private'}}),null);assert.equal(opened.length,0);
  actor.receiveMessage({name:'Aion:Hide'});assert.equal(changed.length,0);
  actor.manager.documentURI.spec='about:newtab';
  actor.receiveMessage({name:'Aion:OpenGame',data:{url:'file:///private',userContextId:99}});
  assert.equal(opened[0][0],'https://aionendlessrun.vercel.app/');assert.equal(opened[0][1],'tab');assert.equal(opened[0][2].userContextId,7);
});
