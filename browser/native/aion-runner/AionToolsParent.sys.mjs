/* SPDX-License-Identifier: MPL-2.0 */
let registered = false;
export function register() {
  if (registered) return;
  ChromeUtils.registerWindowActor('AionTools', {
    parent: {esModuleURI: 'chrome://browser/content/aion-runner/AionToolsParent.sys.mjs'},
    child: {esModuleURI: 'chrome://browser/content/aion-runner/AionToolsChild.sys.mjs', events: {'Aion:OpenTranslator': {capture: true, wantUntrusted: true}}},
    matches: ['moz-extension://*/*'], allFrames: false
  });
  registered = true;
}
export class AionToolsParent extends JSWindowActorParent {
  receiveMessage({name}) {
    const uri = this.manager.documentURI;
    // A fixed native action for our own packaged tools page only. No caller
    // can supply a URL, code, filesystem path, text or translation endpoint.
    if (name !== 'AionTools:OpenTranslator' || uri.scheme !== 'moz-extension' || uri.pathQueryRef.split(/[?#]/)[0] !== '/popup.html') return false;
    if (WebExtensionPolicy.getByURI(uri)?.id !== 'aion@fire-axolotl.browser') return false;
    const window = this.browsingContext.top.embedderElement?.documentGlobal;
    if (typeof window?.openTrustedLinkIn !== 'function') return false;
    window.openTrustedLinkIn('about:translations', 'tab');
    return true;
  }
}
