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
      const toolbar = () => {
        try {ChromeUtils.importESModule('chrome://browser/content/aion-runner/toolbar.sys.mjs').register(window);}
        catch (error) {console.error('Aion toolbar initialization failed', error);}
      };
      if (window.gBrowserInit?.delayedStartupFinished) toolbar();
      else {
        const ready = subject => {
          if (subject !== window) return;
          Services.obs.removeObserver(ready, 'browser-delayed-startup-finished');
          toolbar();
        };
        Services.obs.addObserver(ready, 'browser-delayed-startup-finished');
        window.addEventListener('unload', () => {try {Services.obs.removeObserver(ready, 'browser-delayed-startup-finished');} catch {}}, {once:true});
      }
      Services.prefs.addObserver(preference, controller);
      controller.observe();
      try {ChromeUtils.importESModule('chrome://browser/content/aion-runner/AionRunnerParent.sys.mjs').register();}
      catch (error) {console.error('Aion runner registration failed', error);}
      try {ChromeUtils.importESModule('chrome://browser/content/aion-runner/AionToolsParent.sys.mjs').register();}
      catch (error) {console.error('Aion tools registration failed', error);}
      window.addEventListener('unload', () => Services.prefs.removeObserver(preference, controller), {once: true});
    }
  };
  globalThis.AionChrome = controller;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => controller.init(), {once: true});
  else controller.init();
})();
