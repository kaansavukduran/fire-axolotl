/* SPDX-License-Identifier: MPL-2.0 */
'use strict';
let queue = Promise.resolve();
function serial(fn) {
  const result = queue.then(fn);
  queue = result.catch(() => {});
  return result;
}
async function readSettings() {return Aion.normalize((await browser.storage.local.get('settings')).settings);}
async function writeSettings(patch) {
  return serial(async () => {
    const settings = Aion.normalize({...await readSettings(), ...patch});
    await browser.storage.local.set({settings});
    return settings;
  });
}
async function milestone(name) {
  return serial(async () => {
    const settings = await readSettings();
    if (settings.progress && !settings.milestones.includes(name)) {
      settings.milestones.push(name);
      await browser.storage.local.set({settings});
    }
  });
}
async function activeTab() {
  const [tab] = await browser.tabs.query({active: true, currentWindow: true});
  if (!tab || !Aion.webURL(tab.url)) throw new Error('restrictedPage');
  return tab;
}
async function onMessage(message, sender) {
  // Content scripts and websites cannot invoke privileged container/storage/network actions.
  const allowedPages = ['popup.html', 'settings.html'].map(page => browser.runtime.getURL(page));
  if (sender.id !== browser.runtime.id || !allowedPages.includes(sender.url)) throw new Error('unauthorized');
  switch (message.type) {
    case 'settings': return readSettings();
    case 'save': return writeSettings(message.patch);
    case 'containers': {
      const temporary = (await browser.storage.local.get('temporaryContainers')).temporaryContainers || [];
      return (await browser.contextualIdentities.query({})).map(identity => ({...identity, temporary: temporary.includes(identity.cookieStoreId)}));
    }
    case 'temporaryContainer': {
      return serial(async () => {
        const tab = await activeTab();
        const identity = await browser.contextualIdentities.create({name: message.name === 'Temporary' ? 'Aion · Temporary' : 'Aion · Geçici', color: 'turquoise', icon: 'circle'});
        const temporary = (await browser.storage.local.get('temporaryContainers')).temporaryContainers || [];
        await browser.storage.local.set({temporaryContainers: [...temporary, identity.cookieStoreId]});
        try {await browser.tabs.create({url: tab.url, cookieStoreId: identity.cookieStoreId});}
        catch (error) {
          await browser.contextualIdentities.remove(identity.cookieStoreId);
          await browser.storage.local.set({temporaryContainers: temporary});
          throw error;
        }
        return true;
      });
    }
    case 'createContainer': {
      const name = String(message.name || '').trim().slice(0, 80);
      if (!name) throw new Error('nameRequired');
      const identity = await browser.contextualIdentities.create({name, color: 'pink', icon: 'fingerprint'});
      await milestone('container');
      return identity;
    }
    case 'openContainer': {
      const identities = await browser.contextualIdentities.query({});
      if (!identities.some(i => i.cookieStoreId === message.id)) throw new Error('containerMissing');
      const tab = await activeTab();
      const created = await browser.tabs.create({url: tab.url, cookieStoreId: message.id});
      await milestone('container');
      return {id: created.id};
    }
    case 'video': {
      const tab = await activeTab();
      await browser.tabs.executeScript(tab.id, {file: 'video.js'});
      const command = {...message.command, language: Aion.language(await readSettings(), browser.i18n.getUILanguage())};
      const result = await browser.tabs.sendMessage(tab.id, {type: 'aionVideo', command});
      if (result.error) throw new Error(result.error);
      if (command.action === 'speed') await milestone('video');
      return result;
    }
    case 'selection': {
      const tab = await activeTab();
      const result = await browser.tabs.executeScript(tab.id, {code: 'window.getSelection().toString().slice(0, 5000)'});
      return result[0] || '';
    }
    case 'translate': {
      const settings = await readSettings();
      const text = String(message.text || '').trim();
      if (!text || text.length > 5000) throw new Error('textRequired');
      const endpoint = Aion.translationEndpoint(settings.endpoint);
      if (!await browser.permissions.contains({origins: [endpoint.origin]})) throw new Error('permissionRequired');
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 20000);
      try {
        const response = await fetch(endpoint.url, {
          method: 'POST', credentials: 'omit', redirect: 'error', referrerPolicy: 'no-referrer',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({q: text, source: 'auto', target: settings.targetLanguage, format: 'text'}),
          signal: controller.signal
        });
        if (!response.ok) throw new Error('translationFailed');
        const data = await response.json();
        if (typeof data.translatedText !== 'string' || data.translatedText.length > 20000) throw new Error('translationFailed');
        return {text: data.translatedText};
      } catch {throw new Error('translationFailed');}
      finally {clearTimeout(timeout);}
    }
    case 'word': {
      const word = String(message.word || '').trim().slice(0, 300);
      if (!word) throw new Error('textRequired');
      await serial(async () => {
        const settings = await readSettings();
        if (!settings.vocabulary.includes(word)) settings.vocabulary.push(word);
        await browser.storage.local.set({settings: Aion.normalize(settings)});
      });
      await milestone('word');
      return true;
    }
    case 'checkUpdates': {
      const response = await fetch('https://api.github.com/repos/kaansavukduran/fire-axolotl/releases/latest', {credentials: 'omit', redirect: 'error', referrerPolicy: 'no-referrer'});
      if (response.status === 404) return {available: false};
      if (!response.ok) throw new Error('updateFailed');
      const release = await response.json();
      return {available: true, version: String(release.tag_name), notes: String(release.body || '').slice(0, 4000), url: 'https://github.com/kaansavukduran/fire-axolotl/releases/latest'};
    }
    default: throw new Error('unknownAction');
  }
}
browser.runtime.onMessage.addListener(onMessage);
async function cleanTemporaryContainers() {
  return serial(async () => {
    const temporary = (await browser.storage.local.get('temporaryContainers')).temporaryContainers || [];
    const live = new Set((await browser.tabs.query({})).map(tab => tab.cookieStoreId));
    const identities = new Set((await browser.contextualIdentities.query({})).map(identity => identity.cookieStoreId));
    const keep = [];
    for (const id of temporary) {
      if (live.has(id)) keep.push(id);
      else if (identities.has(id)) {
        try {await browser.contextualIdentities.remove(id);} catch {keep.push(id);}
      }
    }
    await browser.storage.local.set({temporaryContainers: keep});
  });
}
browser.tabs.onRemoved.addListener(() => {cleanTemporaryContainers().catch(console.error);});
browser.runtime.onStartup.addListener(() => {cleanTemporaryContainers().catch(console.error);});
