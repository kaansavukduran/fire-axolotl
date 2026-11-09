/* SPDX-License-Identifier: MPL-2.0 */
((root) => {
  'use strict';
  const defaults = Object.freeze({
    schema: 1, language: '', theme: 'dark', scale: 100, textSize: 100,
    font: 'system', lineHeight: 1.5, letterSpacing: 0,
    progress: true, animations: true, sounds: false,
    targetLanguage: 'tr', endpoint: '', vocabulary: [], milestones: [], quality: 'auto'
  });
  const clamp = (v, lo, hi, fallback) => Number.isFinite(Number(v)) ? Math.min(hi, Math.max(lo, Number(v))) : fallback;
  function normalize(input = {}) {
    const out = {...defaults, vocabulary: [], milestones: []};
    for (const key of ['progress', 'animations', 'sounds']) if (typeof input[key] === 'boolean') out[key] = input[key];
    for (const [key, values] of Object.entries({language: ['', 'tr', 'en'], theme: ['system', 'light', 'dark', 'contrast'], font: ['system', 'sans', 'serif', 'dyslexic', 'opendyslexic'], quality: ['auto', 'best', 'hd720', 'hd1080', 'hd1440', 'hd2160']})) {
      if (values.includes(input[key])) out[key] = input[key];
    }
    out.scale = Math.round(clamp(input.scale ?? 100, 80, 200, 100));
    out.textSize = Math.round(clamp(input.textSize ?? 100, 80, 200, 100));
    out.lineHeight = clamp(input.lineHeight ?? 1.5, 1, 2.5, 1.5);
    out.letterSpacing = clamp(input.letterSpacing ?? 0, 0, 0.2, 0);
    if (typeof input.targetLanguage === 'string' && /^[a-z]{2,3}(-[A-Za-z]{2,4})?$/.test(input.targetLanguage)) out.targetLanguage = input.targetLanguage;
    if (typeof input.endpoint === 'string') out.endpoint = input.endpoint.slice(0, 2048);
    if (Array.isArray(input.vocabulary)) out.vocabulary = input.vocabulary.filter(v => typeof v === 'string' && v.trim()).map(v => v.slice(0, 300)).slice(0, 5000);
    if (Array.isArray(input.milestones)) out.milestones = [...new Set(input.milestones.filter(v => ['container', 'video', 'word'].includes(v)))];
    return out;
  }
  function language(settings, deviceLanguage = 'tr') {
    return settings.language || (/^en(?:-|$)/i.test(deviceLanguage) ? 'en' : 'tr');
  }
  function webURL(value) {
    try {const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) && !u.username && !u.password ? u.href : null;} catch {return null;}
  }
  function translationEndpoint(value) {
    const u = new URL(value);
    if (u.protocol !== 'https:' || u.username || u.password || u.search || u.hash || u.port) throw new Error('invalidEndpoint');
    // An endpoint is deliberately user-selected. Never accept one from page content.
    if (u.hostname === 'localhost' || !u.hostname.includes('.') || /^[\d.]+$/.test(u.hostname) || u.hostname.includes(':') || /\.(local|internal)$/.test(u.hostname)) throw new Error('invalidEndpoint');
    return {url: u.href, origin: u.origin + '/*'};
  }
  function parseVTT(raw) {
    const text = String(raw).replace(/^\uFEFF/, '').replace(/\r/g, '');
    const stamp = v => {
      const p = v.replace(',', '.').split(':').map(Number);
      if (p.some(n => !Number.isFinite(n) || n < 0) || p.length < 2 || p.length > 3 || p.at(-1) >= 60 || p.at(-2) >= 60) return NaN;
      return p.reduce((n, x) => n * 60 + x, 0);
    };
    const cues = [];
    for (const block of text.split(/\n\s*\n/)) {
      const lines = block.split('\n');
      const i = lines.findIndex(line => line.includes('-->'));
      if (i < 0) continue;
      const match = lines[i].match(/^\s*([\d:.,]+)\s+-->\s+([\d:.,]+)/);
      if (!match) continue;
      const start = stamp(match[1]), end = stamp(match[2]);
      const content = lines.slice(i + 1).join('\n').replace(/<[^>]*>/g, '').trim();
      if (Number.isFinite(start) && Number.isFinite(end) && end > start && content) cues.push({start, end, text: content.slice(0, 2000)});
      if (cues.length >= 10000) break;
    }
    return cues.sort((a, b) => a.start - b.start);
  }
  const api = {defaults, normalize, language, clamp, webURL, translationEndpoint, parseVTT};
  root.Aion = api;
  if (typeof module !== 'undefined') module.exports = api;
})(globalThis);
