/* SPDX-License-Identifier: MPL-2.0 */
(() => {
  'use strict';
  const prefs = ['sidebar.verticalTabs', 'sidebar.position_start', 'layout.css.prefers-color-scheme.content-override', 'fireaxolotl.ui.font', 'fireaxolotl.newtabGame.enabled', 'fireaxolotl.newtabGame.language'];
  let initialized = false;
  async function initialize() {
    const group = document.getElementById('aionLayoutGroup');
    if (!group || initialized) return;
    initialized = true;
    const category = Services.prefs.getBoolPref('browser.settings-redesign.enabled', false) ? 'paneAppearance' : 'paneGeneral';
    group.dataset.category = category;
    // Keep the native pane heading and controls before our additional group.
    // The preferences search/category machinery manages the group's visibility.
    function placeGroup() {
      const pane = document.querySelector(`setting-pane[name="${category}"]`);
      if (pane && pane.nextElementSibling !== group) pane.after(group);
    }
    placeGroup();
    document.addEventListener('paneshown', placeGroup);
    const locale = /^en(?:-|$)/i.test(Services.locale.appLocaleAsBCP47) ? 'en' : 'tr';
    const response = await fetch(`chrome://browser/content/preferences/aion-${locale}.json`);
    const messages = await response.json();
    group.querySelectorAll('[data-aion-l10n]').forEach(element => {element.textContent = messages[element.dataset.aionL10n].message;});
    const select = document.getElementById('aion-tab-position');
    function sync() {
      const vertical = Services.prefs.getBoolPref(prefs[0], false);
      // sidebar.position_start is relative to text direction; labels mean physical sides.
      const start = Services.prefs.getBoolPref(prefs[1], true);
      const rtl = Services.locale.isAppLocaleRTL;
      select.value = !vertical ? 'top' : start !== rtl ? 'left' : 'right';
      document.getElementById('aion-website-theme').value = Services.prefs.getIntPref(prefs[2], 2);
      document.getElementById('aion-browser-font').value = Services.prefs.getStringPref(prefs[3], 'system');
      document.getElementById('aion-newtab-game').checked = Services.prefs.getBoolPref(prefs[4], true);
      document.getElementById('aion-game-language').value = Services.prefs.getStringPref(prefs[5], locale);
    }
    select.addEventListener('change', () => {
      if (!['top', 'left', 'right'].includes(select.value)) return;
      if (select.value !== 'top') {
        Services.prefs.setBoolPref('sidebar.revamp', true);
        Services.prefs.setBoolPref(prefs[1], (select.value === 'left') !== Services.locale.isAppLocaleRTL);
      }
      Services.prefs.setBoolPref(prefs[0], select.value !== 'top');
      document.getElementById('aion-layout-status').textContent = messages.saved.message;
    });
    document.getElementById('aion-website-theme').addEventListener('change', event => {
      const value = Number(event.target.value);
      if ([0, 1, 2].includes(value)) Services.prefs.setIntPref(prefs[2], value);
      document.getElementById('aion-layout-status').textContent = messages.saved.message;
    });
    document.getElementById('aion-browser-font').addEventListener('change', event => {
      if (['system', 'opendyslexic', 'lexend', 'sans', 'serif'].includes(event.target.value)) Services.prefs.setStringPref(prefs[3], event.target.value);
      document.getElementById('aion-layout-status').textContent = messages.saved.message;
    });
    document.getElementById('aion-customize-toolbar').addEventListener('click', () => {
      Services.wm.getMostRecentWindow('navigator:browser')?.gCustomizeMode.enter();
    });
    document.getElementById('aion-newtab-game').addEventListener('change', event => {
      Services.prefs.setBoolPref(prefs[4], event.target.checked);
      document.getElementById('aion-layout-status').textContent = messages.saved.message;
    });
    document.getElementById('aion-game-language').addEventListener('change', event => {
      if (['tr', 'en'].includes(event.target.value)) Services.prefs.setStringPref(prefs[5], event.target.value);
      document.getElementById('aion-layout-status').textContent = messages.saved.message;
    });
    document.getElementById('aion-game-reset').addEventListener('click', () => {
      Services.prefs.clearUserPref('fireaxolotl.newtabGame.best');
      document.getElementById('aion-layout-status').textContent = messages.saved.message;
    });
    const observer = {observe: sync};
    prefs.forEach(pref => Services.prefs.addObserver(pref, observer));
    window.addEventListener('unload', () => {
      prefs.forEach(pref => Services.prefs.removeObserver(pref, observer));
      document.removeEventListener('paneshown', placeGroup);
    }, {once: true});
    sync();
  }
  const observer = new MutationObserver(() => {
    if (document.getElementById('aionLayoutGroup')) {
      observer.disconnect();
      initialize().catch(console.error);
    }
  });
  observer.observe(document.documentElement, {childList: true, subtree: true});
  initialize().catch(console.error);
})();
