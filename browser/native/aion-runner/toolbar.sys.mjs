/* SPDX-License-Identifier: MPL-2.0 */
import {CustomizableUI} from 'moz-src:///browser/components/customizableui/CustomizableUI.sys.mjs';
import {ContextualIdentityService} from 'resource://gre/modules/ContextualIdentityService.sys.mjs';
import {PrivateBrowsingUtils} from 'resource://gre/modules/PrivateBrowsingUtils.sys.mjs';
import {SessionStore} from 'resource:///modules/sessionstore/SessionStore.sys.mjs';

const IDS = 'fireaxolotl.temporaryTabs.ids';
let registered = false;
const text = () => /^tr\b/i.test(Services.locale.appLocaleAsBCP47)
  ? {label:'Yeni geçici sekme', help:'Her tıklamada ayrı geçici konteyner aç. Son sekmesi kapanınca o alan temizlenir.', name:'Aion · Geçici'}
  : {label:'New temporary tab', help:'Open a separate temporary container each time. Its area is removed after its last tab closes.', name:'Aion · Temporary'};
function identities() {
  try {return JSON.parse(Services.prefs.getStringPref(IDS, '[]')).filter(id => Number.isSafeInteger(id) && id > 0);} catch {return [];}
}
function save(ids) {Services.prefs.setStringPref(IDS, JSON.stringify(ids));}
export function cleanTemporary() {
  const used = new Set();
  for (const window of Services.wm.getEnumerator('navigator:browser')) {
    for (const tab of window.gBrowser?.tabs || []) used.add(Number(tab.getAttribute('usercontextid')));
  }
  save(identities().filter(id => {
    if (used.has(id)) return true;
    try {ContextualIdentityService.remove(id); return false;} catch {return true;}
  }));
}
export function openTemporary(window) {
  if (!window?.gBrowser || PrivateBrowsingUtils.isWindowPrivate(window)) return false;
  const identity = ContextualIdentityService.create(text().name, 'circle', 'turquoise');
  save([...identities(), identity.userContextId]);
  try {
    window.gBrowser.selectedTab = window.gBrowser.addTrustedTab('about:newtab', {userContextId:identity.userContextId});
    window.gURLBar.focus();
  } catch (error) {
    ContextualIdentityService.remove(identity.userContextId);
    save(identities().filter(id => id !== identity.userContextId));
    throw error;
  }
  return true;
}
export function applyLayout(window) {
  Services.prefs.setBoolPref('sidebar.verticalTabs', false);
  Services.prefs.setStringPref('browser.toolbars.bookmarks.visibility', 'always');
  const ids = CustomizableUI.getWidgetIdsInArea(CustomizableUI.AREA_NAVBAR);
  CustomizableUI.addWidgetToArea('search-container', CustomizableUI.AREA_NAVBAR, ids.indexOf('urlbar-container') + 1);
  window.setToolbarVisibility(window.document.getElementById('PersonalToolbar'), true);
}
export function register(window) {
  if (!registered) {
    registered = true;
    CustomizableUI.createWidget({
      id:'aion-new-temporary-tab', defaultArea:CustomizableUI.AREA_NAVBAR,
      label:text().label, tooltiptext:text().help,
      onCreated(node) {
        node.style.listStyleImage = 'url("chrome://browser/skin/new-tab.svg")';
        node.disabled = PrivateBrowsingUtils.isWindowPrivate(node.ownerDocument.defaultView);
      },
      onCommand(event) {openTemporary(event.target.ownerDocument.defaultView);}
    });
    SessionStore.promiseAllWindowsRestored.then(cleanTemporary).catch(console.error);
  }
  window.gBrowser.tabContainer.addEventListener('TabClose', () => Services.tm.dispatchToMainThread(cleanTemporary));
}
