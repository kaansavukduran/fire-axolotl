/* SPDX-License-Identifier: MPL-2.0 */
'use strict';
const $ = id => document.getElementById(id);
let sourceTabId = null, selectedTool = 'translation', sourceHost = '', draftKey = 'aionDraft-none';
const send = message => browser.runtime.sendMessage({...message, ...(Number.isInteger(sourceTabId) ? {tabId: sourceTabId} : {})});
function chooseTool(name, focus = false) {
  if (!['translation', 'containers', 'video'].includes(name)) name = 'translation';
  selectedTool = name;
  document.querySelectorAll('[data-tool]').forEach(button => {
    const active = button.dataset.tool === name;
    button.setAttribute('aria-selected', String(active)); button.tabIndex = active ? 0 : -1;
    $('panel-' + button.dataset.tool).hidden = !active;
    if (active && focus) button.focus();
  });
  history.replaceState(null, '', '#' + name);
}
async function saveDraft() {
  await browser.storage.session.set({[draftKey]: {source: $('source-text').value, result: $('translation-result').value, tool: selectedTool, containerId: $('container').value}});
}
async function workspace() {
  await saveDraft();
  const url = new URL(browser.runtime.getURL('popup.html'));
  url.searchParams.set('view', 'tab');
  if (Number.isInteger(sourceTabId)) url.searchParams.set('sourceTabId', sourceTabId);
  url.hash = selectedTool;
  await browser.tabs.create({url: url.href});
}
async function sourceContext() {
  const params = new URLSearchParams(location.search);
  document.body.dataset.workspace = String(params.get('view') === 'tab');
  $('expand-tools').hidden = params.get('view') === 'tab';
  if (params.get('view') !== 'tab') {
    const window = await browser.windows.getCurrent();
    document.body.style.width = Math.min(760, Math.max(280, window.width - 48)) + 'px';
    document.body.style.maxWidth = 'none';
  }
  const id = params.get('sourceTabId');
  let tab;
  try {
    tab = id !== null && /^\d+$/.test(id) ? await browser.tabs.get(Number(id)) : (await browser.tabs.query({active: true, currentWindow: true}))[0];
    if (tab && Aion.webURL(tab.url)) sourceTabId = tab.id;
  } catch {}
  sourceHost = sourceTabId === null ? '' : new URL(tab.url).host;
  $('source-context').textContent = sourceHost ? `${UI.t('sourceContext')}: ${sourceHost}` : UI.t('noSourceTab');
  draftKey = 'aionDraft-' + (sourceTabId ?? 'none');
  const draft = (await browser.storage.session.get(draftKey))[draftKey];
  if (draft) {$('source-text').value = String(draft.source || '').slice(0, 5000); $('translation-result').value = String(draft.result || '').slice(0, 20000);}
  if (draft?.containerId && [...$('container').options].some(option => option.value === draft.containerId)) $('container').value = draft.containerId;
  $('open-container').disabled = !$('container').value;
  chooseTool(location.hash.slice(1) || draft?.tool || 'translation');
}
async function refresh() {
  $('provider').textContent = UI.settings.endpoint ? `${UI.t('provider')}: ${UI.settings.endpoint} · ${UI.settings.targetLanguage}` : UI.t('noProvider');
  $('progress-section').hidden = !UI.settings.progress;
  $('progress-count').textContent = `${new Intl.NumberFormat(UI.locale).format(UI.settings.milestones.length)} / 3`;
  $('progress-bar').value = UI.settings.milestones.length;
  $('quality').value = UI.settings.quality;
  $('translation-target').value = UI.settings.targetLanguage;
  $('source-context').textContent = sourceHost ? `${UI.t('sourceContext')}: ${sourceHost}` : UI.t('noSourceTab');
  $('translate').textContent = UI.t(UI.settings.endpoint ? 'sendTranslation' : 'setupBeforeTranslation');
}
async function containers() {
  const select = $('container'), previous = select.value; select.replaceChildren();
  const identities = await send({type: 'containers'});
  const placeholder = document.createElement('option'); placeholder.value = ''; placeholder.disabled = true; placeholder.selected = true; placeholder.dataset.i18n = 'containerChoice'; placeholder.textContent = UI.t('containerChoice'); select.append(placeholder);
  for (const identity of identities) {
    const option = document.createElement('option'); option.value = identity.cookieStoreId; option.textContent = identity.name + (identity.temporary ? ` · ${UI.t('temporary')}` : ''); select.append(option);
  }
  if (!identities.length) {const option = document.createElement('option'); option.textContent = UI.t('noContainers'); select.append(option);}
  if (identities.some(identity => identity.cookieStoreId === previous)) select.value = previous;
  $('open-container').disabled = !select.value;
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
  await UI.init(); await refresh(); await containers(); await sourceContext();
  document.querySelectorAll('[data-tool]').forEach(button => {
    button.addEventListener('click', () => {chooseTool(button.dataset.tool); UI.run(saveDraft);});
    button.addEventListener('keydown', event => {
      const tabs = [...document.querySelectorAll('[data-tool]')], index = tabs.indexOf(button);
      const target = {ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1}[event.key];
      if (target === undefined) return;
      event.preventDefault(); chooseTool(tabs[target].dataset.tool, true); UI.run(saveDraft);
    });
  });
  $('source-text').addEventListener('input', () => UI.run(saveDraft));
  $('container').addEventListener('change', () => {$('open-container').disabled = !$('container').value; UI.run(saveDraft);});
  action('expand-tools', workspace);
  action('native-translation', () => new Promise((resolve, reject) => {
    const done = event => {clearTimeout(timeout); event.detail?.ok ? resolve() : reject(new Error('nativeTranslationUnavailable'));};
    const timeout = setTimeout(() => {window.removeEventListener('Aion:TranslatorReady', done); reject(new Error('nativeTranslationUnavailable'));}, 5000);
    window.addEventListener('Aion:TranslatorReady', done, {once: true});
    document.dispatchEvent(new CustomEvent('Aion:OpenTranslator', {bubbles: true}));
  }));
  const setupTranslation = () => browser.tabs.create({url: browser.runtime.getURL('settings.html') + '#translation-settings'});
  action('translation-settings', setupTranslation);
  $('translation-target').addEventListener('change', () => UI.run(() => UI.save({targetLanguage: $('translation-target').value})));
  document.addEventListener('aion-settings', refresh);
  action('settings', () => browser.runtime.openOptionsPage());
  action('open-characters', () => browser.sidebarAction.open());
  $('container-form').addEventListener('submit', event => {event.preventDefault(); UI.run(async () => {
    const identity = await send({type: 'createContainer', name: $('container-name').value});
    $('container-name').value = ''; await containers(); $('container').value = identity.cookieStoreId; $('open-container').disabled = false; await saveDraft(); UI.status('created');
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
  action('read-selection', async () => {$('source-text').value = await send({type: 'selection'}); await saveDraft(); UI.status($('source-text').value ? 'selectionRead' : 'textRequired');});
  action('read-caption', async () => {const response = await video({action: 'captions'}); $('source-text').value = response.text; await saveDraft(); UI.status(response.text ? 'selectionRead' : 'noCaptions');});
  action('translate', async () => {
    if (!UI.settings.endpoint) {await saveDraft(); return setupTranslation();}
    $('translate').disabled = true; $('translation-result').value = ''; UI.status('translating');
    try {const response = await send({type: 'translate', text: $('source-text').value}); $('translation-result').value = response.text; await saveDraft(); UI.status('translated');}
    finally {$('translate').disabled = false;}
  });
  action('save-word', async () => {await send({type: 'word', word: $('source-text').value}); UI.status('wordSaved');});
  action('show-subtitles', async () => {
    const original = await fileCues('original-file'), translated = await fileCues('translated-file');
    if (!original.length && !translated.length) throw new Error('chooseSubtitle');
    await video({action: 'overlay', original, translated});
  });
  action('hide-subtitles', () => video({action: 'closeOverlay'}));
  document.body.dataset.ready = 'true';
})().catch(() => UI.status('operationFailed', true));
