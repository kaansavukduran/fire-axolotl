/* SPDX-License-Identifier: MPL-2.0 */
import {AionRunnerCard} from 'chrome://browser/content/aion-runner/card.sys.mjs';

export class AionRunnerChild extends JSWindowActorChild {
  handleEvent() {
    if (this.started) return;
    this.started = true;
    this.sendQuery('Aion:GetConfig').then(config => {
      if (!config?.enabled || !this.contentWindow || !this.document.body) return;
      this.card = new AionRunnerCard(this.document, config, {
        saveBest: score => this.sendAsyncMessage('Aion:Best', score),
        hide: () => {this.observer?.disconnect(); this.sendAsyncMessage('Aion:Hide');}
      });
      const place = () => {
        const search = this.document.querySelector('.search-wrapper');
        if (this.card.dismissed || this.card.host.isConnected) return;
        if (search) search.after(this.card.host);
        else this.document.querySelector('main')?.prepend(this.card.host);
      };
      place();
      this.observer = new this.contentWindow.MutationObserver(place);
      this.observer.observe(this.document.body, {childList: true, subtree: true});
    }).catch(error => console.error('Aion runner initialization failed', error));
  }
  didDestroy() {
    this.observer?.disconnect();
    this.card?.destroy();
  }
}
