/* SPDX-License-Identifier: MPL-2.0 */
const PREFIX = 'fireaxolotl.newtabGame.';
let registered = false;

export function register() {
  if (registered) return;
  ChromeUtils.registerWindowActor('AionRunner', {
    parent: {esModuleURI: 'chrome://browser/content/aion-runner/AionRunnerParent.sys.mjs'},
    child: {
      esModuleURI: 'chrome://browser/content/aion-runner/AionRunnerChild.sys.mjs',
      events: {DOMContentLoaded: {}, pageshow: {}}
    },
    matches: ['about:newtab', 'about:home'],
    allFrames: false
  });
  registered = true;
}

export class AionRunnerParent extends JSWindowActorParent {
  configuration() {
    return {
      enabled: Services.prefs.getBoolPref(PREFIX + 'enabled', true),
      best: Services.prefs.getIntPref(PREFIX + 'best', 0),
      language: Services.prefs.getStringPref(PREFIX + 'language', /^tr\b/i.test(Services.locale.appLocaleAsBCP47) ? 'tr' : 'en')
    };
  }
  receiveMessage({name, data}) {
    if (!['about:newtab', 'about:home'].includes(this.manager.documentURI.spec.replace(/[?#].*$/, ''))) return null;
    if (name === 'Aion:GetConfig') return this.configuration();
    if (name === 'Aion:Hide') Services.prefs.setBoolPref(PREFIX + 'enabled', false);
    if (name === 'Aion:Best' && Number.isSafeInteger(data) && data >= 0 && data <= 1000000) {
      Services.prefs.setIntPref(PREFIX + 'best', Math.max(this.configuration().best, data));
    }
    return null;
  }
}
