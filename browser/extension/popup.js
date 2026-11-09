/* SPDX-License-Identifier: MPL-2.0 */
'use strict';
const $ = id => document.getElementById(id);
const send = message => browser.runtime.sendMessage(message);
async function refresh() {
  $('provider').textContent = UI.settings.endpoint ? `${UI.t('provider')}: ${UI.settings.endpoint} · ${UI.settings.targetLanguage}` : UI.t('noProvider');
  $('progress-section').hidden = !UI.settings.progress;
  $('progress-count').textContent = `${new Intl.NumberFormat(UI.locale).format(UI.settings.milestones.length)} / 3`;
  $('progress-bar').value = UI.settings.milestones.length;
  $('quality').value = UI.settings.quality;
}
async function containers() {
  const select = $('container'); select.replaceChildren();
  const identities = await send({type: 'containers'});
  for (const identity of identities) {
    const option = document.createElement('option'); option.value = identity.cookieStoreId; option.textContent = identity.name + (identity.temporary ? ` · ${UI.t('temporary')}` : ''); select.append(option);
  }
  if (!identities.length) {const option = document.createElement('option'); option.textContent = UI.t('noContainers'); select.append(option);}
  $('open-container').disabled = !identities.length;
}
function action(id, fn) {$(id).addEventListener('click', () => UI.run(fn));}
async function video(command) {
  const response = await send({type: 'video', command});
  UI.status('applied'); return response;
}
async function fileCues(id) {
  const file = $(id).files[0];
  if (!file) return [];
  if (file.size > 2 * 1024 * 1024) throw new Error('fileTooLarge');
  const cues = Aion.parseVTT(await file.text());
  if (!cues.length) throw new Error('invalidCaptions');
  return cues;
}
(async () => {
  await UI.init(); await refresh(); await containers();
  document.addEventListener('aion-settings', refresh);
  action('settings', () => browser.runtime.openOptionsPage());
  $('container-form').addEventListener('submit', event => {event.preventDefault(); UI.run(async () => {
    const identity = await send({type: 'createContainer', name: $('container-name').value});
    $('container-name').value = ''; await containers(); $('container').value = identity.cookieStoreId; UI.status('created');
  });});
  action('open-container', async () => {await send({type: 'openContainer', id: $('container').value}); UI.status('opened');});
  action('temporary-container', async () => {await send({type: 'temporaryContainer', name: UI.locale === 'en' ? 'Temporary' : 'Geçici'}); UI.status('opened');});
  for (const [a, b] of [['speed', 'speed-number'], ['speed-number', 'speed']]) $(a).addEventListener('input', () => {$(b).value = $(a).value;});
  action('apply-speed', () => video({action: 'speed', value: Number($('speed-number').value)}));
  action('reset-speed', async () => {$('speed').value = $('speed-number').value = 1; await video({action: 'speed', value: 1});});
  $('quality').addEventListener('change', () => UI.run(() => UI.save({quality: $('quality').value})));
  action('apply-quality', async () => {await video({action: 'quality', value: $('quality').value}); UI.status('qualityRequested');});
  action('read-resolution', async () => {
    const result = await video({action: 'info'});
    $('resolution').textContent = result.width && result.height ? `${UI.t('actualResolution')}: ${result.width} × ${result.height}` : UI.t('resolutionUnknown');
  });
  action('read-selection', async () => {$('source-text').value = await send({type: 'selection'}); UI.status($('source-text').value ? 'selectionRead' : 'textRequired');});
  action('read-caption', async () => {const response = await video({action: 'captions'}); $('source-text').value = response.text; UI.status(response.text ? 'selectionRead' : 'noCaptions');});
  action('translate', async () => {
    if (!UI.settings.endpoint) throw new Error('noProvider');
    $('translate').disabled = true; $('translation-result').value = ''; UI.status('translating');
    try {const response = await send({type: 'translate', text: $('source-text').value}); $('translation-result').value = response.text; UI.status('translated');}
    finally {$('translate').disabled = false;}
  });
  action('save-word', async () => {await send({type: 'word', word: $('source-text').value}); UI.status('wordSaved');});
  action('show-subtitles', async () => {
    const original = await fileCues('original-file'), translated = await fileCues('translated-file');
    if (!original.length && !translated.length) throw new Error('chooseSubtitle');
    await video({action: 'overlay', original, translated});
  });
  action('hide-subtitles', () => video({action: 'closeOverlay'}));
})().catch(() => UI.status('operationFailed', true));
