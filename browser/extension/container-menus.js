/* SPDX-License-Identifier: MPL-2.0 */
(() => {
  'use strict';
  const root = 'aion-open-container', temporary = root + '-temporary', selection = 'aion-translate-selection';
  let queue = Promise.resolve();
  const catalogs = {};
  async function messages() {
    const language = Aion.language(await readSettings(), browser.i18n.getUILanguage());
    catalogs[language] ||= await (await fetch(browser.runtime.getURL(`_locales/${language}/messages.json`))).json();
    return {language, t: key => catalogs[language][key].message};
  }
  function create(item) {
    return new Promise((resolve, reject) => browser.menus.create(item, () => browser.runtime.lastError ? reject(new Error('menuCreationFailed')) : resolve()));
  }
  function synchronize() {
    queue = queue.catch(() => {}).then(async () => {
      const {t} = await messages();
      for (const id of [root, selection]) {try {await browser.menus.remove(id);} catch {}}
      const contexts = ['page', 'link'];
      await create({id: root, title: t('containerContextMenu'), contexts, documentUrlPatterns: ['http://*/*', 'https://*/*']});
      for (const identity of await browser.contextualIdentities.query({})) {
        await create({id: root + ':' + identity.cookieStoreId, parentId: root, title: identity.name, contexts});
      }
      await create({id: temporary, parentId: root, title: t('temporaryContextMenu'), contexts});
      await create({id: selection, title: t('selectionContextMenu'), contexts: ['selection'], documentUrlPatterns: ['http://*/*', 'https://*/*']});
      await browser.menus.refresh();
    });
    queue.catch(() => console.error('Aion container menus could not be updated'));
    return queue;
  }
  async function click(info, tab) {
    if (!Number.isInteger(tab?.id) || !Aion.webURL(tab.url)) return;
    if (info.menuItemId === selection) {
      await browser.storage.session.set({['aionDraft-' + tab.id]: {source: String(info.selectionText || '').slice(0, 5000), result: '', tool: 'translation'}});
      await browser.tabs.create({url: browser.runtime.getURL('popup.html') + `?view=tab&sourceTabId=${tab.id}#translation`, windowId: tab.windowId});
      return;
    }
    const url = Aion.webURL(info.linkUrl || info.pageUrl || tab.url);
    if (!url || tab.incognito) return;
    if (info.menuItemId === temporary) {
      const {language} = await messages();
      return temporaryForTab(tab, language === 'en' ? 'Temporary' : 'Geçici', url);
    }
    if (typeof info.menuItemId === 'string' && info.menuItemId.startsWith(root + ':')) {
      return containerForTab(tab, info.menuItemId.slice(root.length + 1), url);
    }
  }
  browser.menus.onClicked.addListener((info, tab) => click(info, tab).catch(() => console.error('Aion menu action could not be completed')));
  browser.runtime.onInstalled.addListener(synchronize);
  browser.runtime.onStartup.addListener(synchronize);
  for (const event of ['onCreated', 'onUpdated', 'onRemoved']) browser.contextualIdentities[event].addListener(synchronize);
  browser.storage.onChanged.addListener((changes, area) => {
    if (area === 'local' && changes.settings && Aion.normalize(changes.settings.oldValue).language !== Aion.normalize(changes.settings.newValue).language) synchronize();
  });
  // A waking background page retains the persisted menu that woke it.
  globalThis.AionContainerMenus = {synchronize};
})();
