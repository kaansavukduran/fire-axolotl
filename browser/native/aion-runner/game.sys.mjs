/* SPDX-License-Identifier: MPL-2.0 */
// No game script executes in this document or in the companion extension.
export class BundledGameCard {
  constructor(document, config) {
    this.host = document.createElement('section');
    this.host.id = 'fireaxolotl-runner';
    const tr = config.language === 'tr';
    this.host.lang = tr ? 'tr' : 'en';
    this.host.style.cssText = 'box-sizing:border-box;width:min(1024px,calc(100vw - 48px));max-width:100%;margin:16px auto;border:1px solid #6e8b9c66;border-radius:16px;overflow:hidden;background:#081628ee;color:#eef5ff;font:14px system-ui';
    this.shadow = this.host.attachShadow({mode:'open'});
    const style = document.createElement('style');
    style.textContent = ':host{display:block}header{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:16px}h2{font-size:18px;margin:0}p{margin:6px 0 0;color:#c9dce6}button{font:inherit;padding:12px 18px;border:1px solid #7298a9;border-radius:10px;background:#17354b;color:#fff;cursor:pointer}button:focus-visible{outline:3px solid #ff93c4;outline-offset:3px}iframe{display:block;width:100%;aspect-ratio:16/10;min-height:310px;border:0;background:#000}iframe:fullscreen{height:100%;aspect-ratio:auto}button[hidden]{display:none}';
    const header = document.createElement('header');
    const info = document.createElement('div');
    const title = document.createElement('h2');
    title.textContent = 'Aion Endless Run · ' + config.gameVersion;
    const help = document.createElement('p');
    help.textContent = tr ? 'Tam oyun · çevrimdışı · Boşluk: zıpla · Esc: duraklat' : 'Full game · offline · Space: jump · Esc: pause';
    info.append(title, help);
    const start = document.createElement('button');
    start.dataset.action = 'play';
    start.textContent = tr ? 'Oyunu başlat' : 'Launch game';
    start.disabled = !config.gameURL;
    const fullscreen = document.createElement('button');
    fullscreen.hidden = true;
    fullscreen.textContent = tr ? 'Tam ekran' : 'Full screen';
    start.addEventListener('click', () => {
      if (this.frame || !config.gameURL?.startsWith('moz-extension://')) return;
      const frame = document.createElement('iframe');
      frame.title = 'Aion Endless Run';
      frame.setAttribute('allow', 'fullscreen');
      frame.setAttribute('allowfullscreen', '');
      frame.referrerPolicy = 'no-referrer';
      frame.src = config.gameURL;
      this.frame = frame;
      this.shadow.append(frame);
      start.hidden = true;
      fullscreen.hidden = false;
      // Focus only after an explicit user request, never on new-tab load.
      frame.addEventListener('load', () => frame.focus(), {once:true});
    });
    fullscreen.addEventListener('click', () => this.frame?.requestFullscreen().catch(console.error));
    header.append(info, start, fullscreen);
    this.shadow.append(style, header);
  }
  destroy() { this.frame?.remove(); }
}
