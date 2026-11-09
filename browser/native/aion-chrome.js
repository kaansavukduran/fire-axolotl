/* SPDX-License-Identifier: MPL-2.0 */
(() => {
  'use strict';
  if (globalThis.AionChrome) return;
  const preference = 'fireaxolotl.ui.font';
  const fonts = {opendyslexic: 'OpenDyslexic,system-ui,sans-serif', lexend: 'Lexend,system-ui,sans-serif', sans: 'Arial,Helvetica,sans-serif', serif: 'Georgia,serif'};
  const controller = {
    observe() {
      const font = Services.prefs.getStringPref(preference, 'system');
      const root = document.documentElement;
      if (Object.hasOwn(fonts, font)) {
        root.dataset.aionFont = font;
        root.style.setProperty('--aion-ui-font', fonts[font]);
      } else {
        delete root.dataset.aionFont;
        root.style.removeProperty('--aion-ui-font');
      }
    },
    init() {
      Services.prefs.addObserver(preference, controller);
      controller.observe();
      window.addEventListener('unload', () => Services.prefs.removeObserver(preference, controller), {once: true});
    }
  };
  globalThis.AionChrome = controller;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => controller.init(), {once: true});
  else controller.init();
})();
