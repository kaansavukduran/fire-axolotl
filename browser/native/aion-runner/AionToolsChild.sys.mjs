/* SPDX-License-Identifier: MPL-2.0 */
export class AionToolsChild extends JSWindowActorChild {
  async handleEvent(event) {
    if (event.type !== 'Aion:OpenTranslator') return;
    let ok = false;
    try {ok = await this.sendQuery('AionTools:OpenTranslator');} catch {}
    if (!this.contentWindow) return;
    const options = Cu.cloneInto({detail: {ok: Boolean(ok)}}, this.contentWindow);
    this.contentWindow.dispatchEvent(new this.contentWindow.CustomEvent('Aion:TranslatorReady', options));
  }
}
