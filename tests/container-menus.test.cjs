// SPDX-License-Identifier: MPL-2.0
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const Aion = require('../browser/extension/shared.js');

test('container menus preserve other tools and open only the explicitly chosen safe link in its isolated identity', async () => {
  const menu = new Map([['other-tool', {id:'other-tool'}]]), created = [], events = {}, store = {}, session = {};
  let settings = Aion.normalize({language:'tr'});
  const browser = {
    runtime:{id:'test', getURL:p=>'moz-extension://own/'+p, onInstalled:{addListener:f=>events.install=f}, onStartup:{addListener:()=>{}}},
    i18n:{getUILanguage:()=> 'en'},
    menus:{create:(item,done)=>{menu.set(item.id,item);done();}, remove:async id=>{for(const [key,item] of menu) if(key===id||item.parentId===id)menu.delete(key);}, refresh:async()=>{}, onClicked:{addListener:f=>events.click=f}},
    contextualIdentities:{query:async()=>[{cookieStoreId:'firefox-container-2',name:'İş'}], onCreated:{addListener:()=>{}},onUpdated:{addListener:()=>{}},onRemoved:{addListener:()=>{}}},
    storage:{onChanged:{addListener:()=>{}},session:{set:async value=>Object.assign(session,value)}},
    tabs:{create:async value=>{created.push(value);return {id:20};}}
  };
  const context = vm.createContext({browser,Aion,console,readSettings:async()=>settings,
    fetch:async url=>{assert.match(url,/^moz-extension:\/\/own\/_locales\/(tr|en)\/messages.json$/);return {json:async()=>JSON.parse(fs.readFileSync('browser/extension/'+url.split('own/')[1]))};},
    containerForTab:async(tab,id,url)=>{assert.equal(id,'firefox-container-2');created.push({url,cookieStoreId:id});},
    temporaryForTab:async(tab,name,url)=>{store.temporary={name,url};}
  });
  vm.runInContext(fs.readFileSync('browser/extension/container-menus.js','utf8'),context);
  await events.install();
  assert.equal(menu.get('aion-open-container').title,'Aion · Konteyner ile aç');assert.ok(menu.has('other-tool'));assert.equal(created.length,0);
  const tab={id:7,url:'https://example.org/original',windowId:2};
  await events.click({menuItemId:'aion-open-container:firefox-container-2',linkUrl:'https://example.org/next'},tab);
  assert.equal(created[0].url,'https://example.org/next');assert.equal(created[0].cookieStoreId,'firefox-container-2');assert.equal(tab.url,'https://example.org/original');
  for(const url of ['javascript:alert(1)','file:///private','https://user:secret@example.org/'])await events.click({menuItemId:'aion-open-container:firefox-container-2',linkUrl:url},tab);
  assert.equal(created.length,1);
  await events.click({menuItemId:'aion-open-container-temporary',pageUrl:tab.url},tab);assert.equal(store.temporary.url,tab.url);
  await events.click({menuItemId:'aion-translate-selection',selectionText:'Öğrenme · ışık'},tab);
  assert.equal(session['aionDraft-7'].source,'Öğrenme · ışık');assert.match(created[1].url,/sourceTabId=7#translation$/);
  settings=Aion.normalize({language:'en'});await context.AionContainerMenus.synchronize();assert.equal(menu.get('aion-open-container').title,'Aion · Open in container');assert.ok(menu.has('other-tool'));
});
