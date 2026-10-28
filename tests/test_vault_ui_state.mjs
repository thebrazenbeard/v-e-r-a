// Run with: node --test tests/test_vault_ui_state.mjs
// Exercise the actual browser script with a small DOM/fetch boundary double.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

class Element {
  constructor(id = '') {
    this.id = id;
    this.listeners = new Map();
    this.children = [];
    this.firstChild = { textContent: '' };
    this.options = [];
    this.value = '';
    this.disabled = false;
    this.checked = false;
    this.hidden = false;
    this.textContent = '';
    this.dataset = {};
  }
  addEventListener(name, callback) { this.listeners.set(name, callback); }
  append(...children) {
    this.children.push(...children);
    this.options = this.children;
  }
  replaceChildren() { this.children = []; this.options = []; }
  scrollIntoView() {}
  focus() {}
}

test('Delete clears transcript tainted by explicit recall before a normal Send', async () => {
  const elements = new Map();
  const byId = (id) => {
    if (!elements.has(id)) elements.set(id, new Element(id));
    return elements.get(id);
  };
  const forwardedChats = [];
  let saved = true;
  let holdRecall = false;
  let completeHeldRecall = null;
  const reply = (body) => ({ ok: true, json: async () => body });
  const fetch = async (path, options = {}) => {
    if (path === '/api/session') return reply({ token: 'session-test' });
    if (path === '/api/models') return reply({ models: ['vera-local:latest'] });
    if (path === '/api/status') return reply({ durable_memory: 'opt_in_local_transcript' });
    if (path === '/api/transcript' && options.method === 'DELETE') {
      saved = false;
      return reply({ status: 'removed_from_active_vault', revision: 2 });
    }
    if (path === '/api/transcript') {
      return reply(saved ? { status: 'saved', revision: 1 } : { status: 'empty', revision: 2 });
    }
    if (path === '/api/chat') {
      const submitted = JSON.parse(options.body);
      forwardedChats.push(submitted);
      if (submitted.recall_saved) {
        assert.equal(options.headers['X-Vera-Vault-Key'], 'synthetic-vault-key');
        if (holdRecall) {
          return new Promise((resolve) => {
            completeHeldRecall = () => resolve(reply({
              reply: 'violet-finch-731', recalled_source: { revision: 1 },
            }));
          });
        }
        return reply({ reply: 'violet-finch-731', recalled_source: { revision: 1 } });
      }
      return reply({ reply: 'UNKNOWN' });
    }
    throw new Error(`Unexpected fetch path: ${path}`);
  };
  const document = {
    getElementById: byId,
    createElement: () => new Element(),
    querySelectorAll: () => [],
  };
  const context = vm.createContext({
    document, fetch, window: { confirm: () => true },
    Option: class { constructor(text, value) { this.text = text; this.value = value; } },
    AbortController,
  });
  const script = readFileSync(new URL('../interface/static/app.js', import.meta.url), 'utf8');
  vm.runInContext(script, context);
  for (let i = 0; i < 10; i++) await new Promise((resolve) => setImmediate(resolve));
  byId('model').value = 'vera-local:latest';
  byId('vault-key').value = 'synthetic-vault-key';
  vm.runInContext('syncVaultControls()', context);
  assert.equal(byId('vault-recall').disabled, false);
  byId('vault-recall').checked = true;
  byId('prompt').value = 'What is the operator marker?';
  await vm.runInContext('sendMessage({ preventDefault() {} })', context);
  assert.equal(forwardedChats[0].recall_saved, true);
  assert.equal(vm.runInContext('messages[1].content', context), 'violet-finch-731');

  await vm.runInContext('deleteSavedTranscript()', context);
  assert.equal(saved, false);
  assert.equal(vm.runInContext('messages.length', context), 0);
  assert.equal(vm.runInContext('recalledFromVault', context), false);
  assert.equal(byId('vault-recall').checked, false);

  byId('prompt').value = 'A fresh question after deletion';
  await vm.runInContext('sendMessage({ preventDefault() {} })', context);
  assert.equal(forwardedChats.length, 2);
  assert.equal(forwardedChats[1].recall_saved, undefined);
  assert.deepEqual(JSON.parse(JSON.stringify(forwardedChats[1].messages)),
                   [{ role: 'user', content: 'A fresh question after deletion' }]);

  // Recreate a saved entry and recall it to test nonempty-to-nonempty key
  // rotation independently of the deletion path above.
  saved = true;
  byId('vault-recall').checked = true;
  byId('prompt').value = 'Recall the marker again';
  await vm.runInContext('sendMessage({ preventDefault() {} })', context);
  assert.equal(forwardedChats[2].recall_saved, true);
  assert.equal(vm.runInContext('recalledFromVault', context), true);
  vm.runInContext('setBusy(true)', context);
  byId('vault-key').value = 'a-different-still-nonempty-key';
  byId('vault-key').listeners.get('input')();
  assert.equal(vm.runInContext('messages.length', context), 0);
  assert.equal(vm.runInContext('busy', context), false);
  assert.equal(vm.runInContext('recalledFromVault', context), false);

  byId('prompt').value = 'Fresh request after credential change';
  await vm.runInContext('sendMessage({ preventDefault() {} })', context);
  assert.equal(forwardedChats[3].recall_saved, undefined);
  assert.deepEqual(JSON.parse(JSON.stringify(forwardedChats[3].messages)),
                   [{ role: 'user', content: 'Fresh request after credential change' }]);

  // The browser must revoke an IN-FLIGHT private recall before the response
  // becomes vault-derived history. The mock deliberately ignores abort so
  // this also verifies the epoch guard against a late server reply.
  byId('vault-key').value = 'synthetic-vault-key';
  byId('vault-key').listeners.get('input')();
  byId('vault-recall').checked = true;
  byId('prompt').value = 'Pending recall while changing keys';
  holdRecall = true;
  const pendingReply = vm.runInContext('sendMessage({ preventDefault() {} })', context);
  assert.equal(vm.runInContext('busy', context), true);
  byId('vault-key').value = 'another-nonempty-key';
  byId('vault-key').listeners.get('input')();
  assert.equal(vm.runInContext('messages.length', context), 0);
  assert.equal(vm.runInContext('busy', context), false);
  assert.equal(byId('vault-recall').checked, false);
  completeHeldRecall();
  await pendingReply;
  assert.equal(vm.runInContext('messages.length', context), 0);
});
