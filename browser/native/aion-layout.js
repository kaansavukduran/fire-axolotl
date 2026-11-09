/* SPDX-License-Identifier: MPL-2.0 */
(() => {
  'use strict';
  const prefs = ['sidebar.verticalTabs', 'sidebar.position_start'];
  let initialized = false;
  async function initialize() {
    const group = document.getElementById('aionLayoutGroup');
    if (!group || initialized) return;
    initialized = true;
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
    const observer = {observe: sync};
    prefs.forEach(pref => Services.prefs.addObserver(pref, observer));
    window.addEventListener('unload', () => {prefs.forEach(pref => Services.prefs.removeObserver(pref, observer));}, {once: true});
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
