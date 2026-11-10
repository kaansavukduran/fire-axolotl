/* SPDX-License-Identifier: MPL-2.0 */
import {AionRunnerCard} from 'chrome://browser/content/aion-runner/card.sys.mjs';

export class AionRunnerChild extends JSWindowActorChild {
  handleEvent() {
    if (this.started) return;
    this.started = true;
    this.sendQuery('Aion:GetConfig').then(config => {
      if (!config?.newtabEnabled || !this.contentWindow || !this.document.body) return;
      const tr = config.language === 'tr';
      const style = this.document.createElement('style');
      style.textContent = `
        body[data-aion-wallpaper]{background:#071522 url("chrome://browser/content/aion-runner/aion-wallpaper.png") left center/cover fixed no-repeat!important}
        body[data-aion-wallpaper] .search-wrapper{filter:drop-shadow(0 2px 12px #0009)}
        #fireaxolotl-newtab-tools{display:flex;justify-content:center;align-items:center;gap:12px;flex-wrap:wrap;margin:16px auto;width:min(760px,calc(100vw - 48px));box-sizing:border-box;max-width:100%;padding:12px;border:1px solid #6e8b9c66;border-radius:16px;background:#081628e8;color:#eef5ff;font:14px system-ui}
        #fireaxolotl-newtab-tools button{font:inherit;padding:10px 16px;border:1px solid #7298a9;border-radius:10px;background:#17354b;color:#fff;cursor:pointer}
        #fireaxolotl-newtab-tools button:focus-visible{outline:3px solid #ff93c4;outline-offset:3px}
        #fireaxolotl-newtab-tools small{display:block;font-size:11px;color:#c9dce6}
        @media(prefers-contrast:more){body[data-aion-wallpaper]{background:#071522!important}}
        @media(min-width:1200px){body[data-aion-wallpaper] .nova-enabled.container{grid-template-columns:minmax(0,1fr) minmax(0,620px) 150px}body[data-aion-wallpaper] main.content{margin:0!important;width:100%!important;max-width:100%!important}}
        @media(max-width:900px){
          .nova-enabled.container{grid-template-columns:minmax(0,1fr)!important;grid-auto-rows:auto!important;padding-inline:16px!important;gap:16px!important}
          .nova-enabled :is(.content,.sidebar-inline-start,.sidebar-inline-end){grid-column:1!important;grid-row:auto!important;min-width:0;width:100%;max-width:100%}
          .nova-enabled main.content{grid-row:1!important;grid-template-columns:minmax(0,1fr)!important;margin-inline:0!important}
          .top-sites-list{display:flex!important;flex-wrap:wrap;justify-content:center;max-width:100%;width:100%;margin-inline:0!important}
        }
      `;
      this.document.head.append(style);
      if (config.wallpaper) this.document.body.dataset.aionWallpaper = 'true';
      this.tools = this.document.createElement('section');
      this.tools.id = 'fireaxolotl-newtab-tools';
      this.tools.lang = tr ? 'tr' : 'en';
      const latest = this.document.createElement('button');
      latest.id = 'aion-latest-game';
      latest.textContent = tr ? 'Aion Endless Run · Güncel oyunu aç' : 'Aion Endless Run · Open latest game';
      latest.addEventListener('click', () => this.sendAsyncMessage('Aion:OpenGame'));
      const help = this.document.createElement('small');
      help.textContent = tr ? 'Vercel’de açılır · ilk yükleme internet ister' : 'Opens on Vercel · internet needed for first load';
      this.restore = this.document.createElement('button');
      this.restore.id = 'aion-restore-game';
      this.restore.textContent = tr ? 'Çevrimdışı mini oyunu göster' : 'Show offline mini game';
      this.restore.hidden = config.enabled;
      this.restore.addEventListener('click', async () => {
        this.restore.disabled = true;
        try {this.mount(await this.sendQuery('Aion:Show')); this.place();}
        catch {help.textContent = tr ? 'Oyun açılamadı. Tekrar dene.' : 'Could not show the game. Try again.';}
        finally {this.restore.disabled = false;}
      });
      this.tools.append(latest, this.restore, help);
      if (config.enabled) this.mount(config);
      this.place = () => {
        if (!this.tools.isConnected) {
          const search = this.document.querySelector('.search-wrapper');
          if (search) search.after(this.tools);
          else this.document.querySelector('main')?.prepend(this.tools);
        }
        if (this.card && !this.card.dismissed && !this.card.host.isConnected && this.tools.isConnected) this.tools.after(this.card.host);
      };
      this.place();
      this.observer = new this.contentWindow.MutationObserver(this.place);
      this.observer.observe(this.document.body, {childList: true, subtree: true});
    }).catch(error => console.error('Aion runner initialization failed', error));
  }
  mount(config) {
    this.card?.destroy();
    this.card?.host.remove();
    this.card = new AionRunnerCard(this.document, config, {
      saveBest: score => this.sendAsyncMessage('Aion:Best', score),
      hide: () => {this.sendAsyncMessage('Aion:Hide'); this.restore.hidden = false;}
    });
    this.restore.hidden = true;
  }
  didDestroy() {
    this.observer?.disconnect();
    this.card?.destroy();
  }
}
