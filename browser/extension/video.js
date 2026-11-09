/* SPDX-License-Identifier: MPL-2.0 */
(() => {
  'use strict';
  if (globalThis.__aionVideoInstalled) return;
  globalThis.__aionVideoInstalled = true;
  let overlay, stopOverlay;
  function video() {
    const videos = [...document.querySelectorAll('video')].filter(v => v.getBoundingClientRect().width > 0);
    return videos.sort((a, b) => Number(b === document.pictureInPictureElement) - Number(a === document.pictureInPictureElement) || Number(!b.paused) - Number(!a.paused) || b.clientWidth * b.clientHeight - a.clientWidth * a.clientHeight)[0];
  }
  function showOverlay(v, original, translated, language) {
    if (stopOverlay) stopOverlay();
    overlay = document.createElement('div');
    overlay.setAttribute('data-aion-captions', '');
    // Fixed host remains visible when video is inside an arbitrary site layout.
    overlay.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none';
    const shadow = overlay.attachShadow({mode: 'closed'});
    const style = document.createElement('style');
    style.textContent = ':host{all:initial}section{position:relative;width:max-content;box-sizing:border-box;max-width:calc(100% - 16px);margin:auto;padding:10px 62px 10px 16px;background:#06152ff0;color:white;border-radius:12px;font:clamp(16px,2.5vw,28px)/1.5 system-ui;text-align:center;white-space:pre-line;overflow-wrap:anywhere}p{margin:0}p+p{color:#85e7ff}button{position:absolute;top:8px;right:8px;pointer-events:auto;color:white;background:#18355b;border:1px solid white;border-radius:6px;min-width:36px;min-height:36px;font:inherit}button:focus-visible{outline:3px solid #ff83b9}';
    const section = document.createElement('section');
    const close = document.createElement('button'); close.textContent = '×'; close.setAttribute('aria-label', language === 'en' ? 'Close subtitles' : 'Altyazıyı kapat');
    const first = document.createElement('p'), second = document.createElement('p');
    section.append(close, first, second); shadow.append(style, section);
    (document.fullscreenElement || document.body).append(overlay);
    function textAt(cues) {return cues.filter(c => v.currentTime >= c.start && v.currentTime < c.end).map(c => c.text).join('\n');}
    function update() {
      first.textContent = textAt(original); second.textContent = textAt(translated);
      first.hidden = !first.textContent; second.hidden = !second.textContent;
      const rect = v.getBoundingClientRect();
      section.hidden = (!first.textContent && !second.textContent) || rect.bottom < 0 || rect.top > innerHeight;
      const left = Math.max(0, rect.left), right = Math.min(innerWidth, rect.right);
      overlay.style.left = left + 'px'; overlay.style.width = Math.max(0, right - left) + 'px';
      const height = overlay.getBoundingClientRect().height;
      overlay.style.top = Math.max(rect.top, Math.min(innerHeight - height, rect.bottom - height - 12)) + 'px';
    }
    function move() {(document.fullscreenElement || document.body).append(overlay);}
    const timer = setInterval(update, 150); update();
    document.addEventListener('fullscreenchange', move);
    stopOverlay = () => {clearInterval(timer); document.removeEventListener('fullscreenchange', move); overlay.remove(); stopOverlay = null;};
    close.onclick = () => stopOverlay?.();
    window.addEventListener('pagehide', () => stopOverlay?.(), {once: true});
  }
  browser.runtime.onMessage.addListener((message, sender) => {
    if (sender.id !== browser.runtime.id || message.type !== 'aionVideo') return undefined;
    const v = video();
    if (!v) return Promise.resolve({error: 'noVideo'});
    const cmd = message.command || {};
    if (cmd.action === 'speed') {
      const speed = Number(cmd.value);
      if (!Number.isFinite(speed) || speed < 0.25 || speed > 4) return Promise.resolve({error: 'invalidSpeed'});
      v.playbackRate = speed;
      if (Math.abs(v.playbackRate - speed) > 0.001) return Promise.resolve({error: 'unsupportedSpeed'});
    } else if (cmd.action === 'quality') {
      const allowed = ['auto', 'best', 'hd720', 'hd1080', 'hd1440', 'hd2160'];
      if (!allowed.includes(cmd.value)) return Promise.resolve({error: 'unsupportedQuality'});
      if (!/(^|\.)youtube\.com$/.test(location.hostname)) return Promise.resolve({error: 'unsupportedQuality'});
      const player = document.getElementById('movie_player')?.wrappedJSObject;
      if (!player || typeof player.setPlaybackQualityRange !== 'function' || typeof player.getAvailableQualityLevels !== 'function') return Promise.resolve({error: 'unsupportedQuality'});
      const levels = Array.from(player.getAvailableQualityLevels());
      const order = ['highres', 'hd2880', 'hd2160', 'hd1440', 'hd1080', 'hd720', 'large', 'medium', 'small', 'tiny'];
      const requested = cmd.value === 'best' ? order.find(level => levels.includes(level)) : cmd.value;
      if (!requested || (requested !== 'auto' && !levels.includes(requested))) return Promise.resolve({error: 'unavailableQuality'});
      player.setPlaybackQualityRange(requested, requested);
      return Promise.resolve({requested, width: v.videoWidth, height: v.videoHeight});
    } else if (cmd.action === 'captions') {
      const cues = [...v.textTracks].flatMap(t => [...(t.activeCues || [])]).map(c => c.text || '').filter(Boolean);
      return Promise.resolve({text: cues.join('\n').slice(0, 5000)});
    } else if (cmd.action === 'overlay') {
      if (!Array.isArray(cmd.original) || !Array.isArray(cmd.translated)) return Promise.resolve({error: 'invalidCaptions'});
      showOverlay(v, cmd.original, cmd.translated, cmd.language);
    } else if (cmd.action === 'closeOverlay') {if (stopOverlay) stopOverlay();}
    return Promise.resolve({speed: v.playbackRate, width: v.videoWidth, height: v.videoHeight});
  });
})();
