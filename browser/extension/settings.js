/* SPDX-License-Identifier: MPL-2.0 */
'use strict';
const $ = id => document.getElementById(id);
function render() {
  for (const element of document.querySelectorAll('[data-setting]')) {
    const value = UI.settings[element.dataset.setting];
    if (element.type === 'checkbox') element.checked = value; else element.value = value;
  }
  for (const key of ['scale', 'textSize']) $(key + '-number').value = UI.settings[key];
  for (const key of ['lineHeight', 'letterSpacing']) $(key + '-value').textContent = new Intl.NumberFormat(UI.locale).format(UI.settings[key]);
  $('endpoint').value = UI.settings.endpoint;
  document.querySelectorAll('[data-scale]').forEach(button => button.setAttribute('aria-pressed', Number(button.dataset.scale) === UI.settings.scale));
  $('version').textContent = browser.runtime.getManifest().version + ' · ' + UI.t('developmentVersion');
  $('word-count').textContent = `${new Intl.NumberFormat(UI.locale).format(UI.settings.vocabulary.length)} ${UI.t('savedWords')}`;
  $('word-list').replaceChildren(...UI.settings.vocabulary.map(word => {const li = document.createElement('li'); li.textContent = word; return li;}));
}
function action(id, fn) {$(id).addEventListener('click', () => UI.run(fn));}
async function save(patch) {await UI.save(patch); render();}
(async () => {
  await UI.init(); render(); document.addEventListener('aion-settings', render);
  action('open-characters', () => browser.sidebarAction.open());
  for (const element of document.querySelectorAll('[data-setting]')) {
    const update = () => UI.run(() => save({[element.dataset.setting]: element.type === 'checkbox' ? element.checked : ['range', 'number'].includes(element.type) ? Number(element.value) : element.value}));
    element.addEventListener(element.type === 'range' ? 'input' : 'change', update);
  }
  for (const key of ['scale', 'textSize']) $(key + '-number').addEventListener('change', () => UI.run(async () => {
    if (!$(key + '-number').checkValidity()) throw new Error('invalidScale');
    await save({[key]: Number($(key + '-number').value)});
  }));
  document.querySelectorAll('[data-scale]').forEach(button => button.addEventListener('click', () => UI.run(() => save({scale: Number(button.dataset.scale)}))));
  action('reset-scale', () => save({scale: 100})); action('reset-text', () => save({textSize: 100}));
  action('reset-progress', async () => {if (confirm(UI.t('confirmResetProgress'))) await save({milestones: []});});
  action('save-endpoint', async () => {
    // Permission must be requested synchronously from this explicit user action.
    const endpoint = Aion.translationEndpoint($('endpoint').value.trim());
    const previous = UI.settings.endpoint;
    const granted = await browser.permissions.request({origins: [endpoint.origin]});
    if (!granted) throw new Error('permissionRequired');
    await save({endpoint: endpoint.url});
    if (previous) {const old = Aion.translationEndpoint(previous); if (old.origin !== endpoint.origin) await browser.permissions.remove({origins: [old.origin]});}
  });
  action('revoke-endpoint', async () => {
    if (UI.settings.endpoint) await browser.permissions.remove({origins: [Aion.translationEndpoint(UI.settings.endpoint).origin]});
    await save({endpoint: ''});
  });
  action('export', () => {
    const blob = new Blob([JSON.stringify({format: 'fire-axolotl', version: 1, settings: UI.settings}, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob), anchor = document.createElement('a');
    anchor.href = url; anchor.download = 'fire-axolotl-settings.json'; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 30000); UI.status('exported');
  });
  $('import').addEventListener('change', () => UI.run(async () => {
    const file = $('import').files[0]; if (!file) return;
    if (file.size > 3 * 1024 * 1024) throw new Error('fileTooLarge');
    let data; try {data = JSON.parse(await file.text());} catch {throw new Error('invalidBackup');}
    if (data.format !== 'fire-axolotl' || data.version !== 1 || !data.settings || typeof data.settings !== 'object') throw new Error('invalidBackup');
    if (!confirm(UI.t('confirmImport'))) return;
    // Backups never grant network permission or replace a trusted endpoint.
    await save({...Aion.normalize(data.settings), endpoint: UI.settings.endpoint}); UI.status('imported');
    $('import').value = '';
  }));
  action('check-updates', async () => {
    $('check-updates').disabled = true; $('release-notes').textContent = ''; $('update-result').textContent = UI.t('checkingUpdates');
    try {
      const response = await browser.runtime.sendMessage({type: 'checkUpdates'});
      $('update-result').textContent = response.available ? `${UI.t('latestPublished')}: ${response.version}` : UI.t('noRelease');
      $('release-notes').textContent = response.notes || '';
    } finally {$('check-updates').disabled = false;}
  });
})().catch(() => UI.status('operationFailed', true));
