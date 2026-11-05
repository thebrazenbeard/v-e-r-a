// Run with: node --test tests/test_vault_ui_state.mjs
// Exercise the actual browser script with a small DOM/fetch boundary double.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { TextEncoder } from 'node:util';
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
  let savedTranscript = null;
  let holdRecall = false;
  let completeHeldRecall = null;
  let completionStatus = "complete";
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
      return reply(saved ? { status: 'saved', revision: 1, messages: savedTranscript } : { status: 'empty', revision: 2 });
    }
    if (path === '/api/chat') {
      const submitted = JSON.parse(options.body);
      forwardedChats.push(submitted);
      if (submitted.recall_saved) {
        assert.equal(options.headers['X-Vera-Vault-Key'], 'synthetic-vault-key');
        if (holdRecall) {
          return new Promise((resolve) => {
            completeHeldRecall = () => resolve(reply({
              reply: 'violet-finch-731', response_completion_status: 'complete',
              recalled_source: { revision: 1 },
            }));
          });
        }
        return reply({ reply: 'violet-finch-731',
                       response_completion_status: 'complete',
                       recalled_source: { revision: 1 } });
      }
      return reply({ reply: 'UNKNOWN', response_completion_status: completionStatus });
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
    AbortController, TextEncoder,
  });
  const script = readFileSync(new URL('../interface/static/app.js', import.meta.url), 'utf8');
  vm.runInContext(script, context);
  for (let i = 0; i < 10; i++) await new Promise((resolve) => setImmediate(resolve));
  assert.equal(byId('memory-boundary').textContent, 'Opt-in transcript only');
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
  completionStatus = "unknown";
  await vm.runInContext('sendMessage({ preventDefault() {} })', context);
  assert.equal(forwardedChats.length, 2);
  assert.match(byId('context-notice').textContent, /Model completion was not reported/);
  assert.equal(vm.runInContext('messages.length', context), 1);
  assert.equal(forwardedChats[1].recall_saved, undefined);
  assert.deepEqual(JSON.parse(JSON.stringify(forwardedChats[1].messages)),
                   [{ role: 'user', content: 'A fresh question after deletion' }]);
  completionStatus = "complete";

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

  // Long ordinary conversations must still reach the model with coherent
  // user-led history and inside the server's 16,000-character request bound.
  // Sending the last 12 entries blindly starts with an assistant turn once
  // the seventh user message arrives, which some chat templates mishandle.
  byId('clear').listeners.get('click')();
  const beforeLongChat = forwardedChats.length;
  for (let turn = 1; turn <= 8; turn += 1) {
    byId('prompt').value = `USER-TURN-${turn} ` + 'p'.repeat(3400);
    await vm.runInContext('sendMessage({ preventDefault() {} })', context);
  }
  for (const request of forwardedChats.slice(beforeLongChat)) {
    assert.equal(request.messages[0].role, 'user');
    assert.equal(request.messages.at(-1).role, 'user');
    assert.equal(request.messages.length % 2, 1);
    for (const [i, item] of request.messages.entries()) {
      assert.equal(item.role, i % 2 === 0 ? 'user' : 'assistant');
    }
    assert.ok(request.messages.reduce((sum, item) => sum + item.content.length, 0) <= 16000);
  }
  assert.ok(forwardedChats.at(-1).messages.at(-1).content.startsWith('USER-TURN-8'));
  assert.match(byId('context-notice').textContent, /older visible messages are outside this reply's model context/);

  // The HTTP gateway also has a byte limit. Non-ASCII turns can be small in
  // JavaScript characters but much larger when encoded as UTF-8 JSON.
  byId('clear').listeners.get('click')();
  const beforeUnicodeChat = forwardedChats.length;
  for (let turn = 1; turn <= 5; turn += 1) {
    byId('prompt').value = `UNICODE-TURN-${turn} ` + '你'.repeat(3350);
    await vm.runInContext('sendMessage({ preventDefault() {} })', context);
  }
  for (const request of forwardedChats.slice(beforeUnicodeChat)) {
    assert.ok(new TextEncoder().encode(JSON.stringify(request)).length <= 22000);
    assert.equal(request.messages[0].role, 'user');
    assert.equal(request.messages.at(-1).role, 'user');
  }

  // A valid operator-saved transcript may end on an unanswered user message.
  // Adding a new question must not forward consecutive user roles to the
  // stricter gateway or invent a missing assistant reply.
  const partialRestore = vm.runInContext(`recentCoherentHistory([
    {role:'user',content:'original'}, {role:'assistant',content:'reply'},
    {role:'user',content:'unanswered saved turn'},
    {role:'user',content:'fresh new question'}])`, context);
  assert.deepEqual(JSON.parse(JSON.stringify(partialRestore)), [
    { role: 'user', content: 'original' }, { role: 'assistant', content: 'reply' },
    { role: 'user', content: 'fresh new question' },
  ]);

  // The actual Restore UI must offer a saved but unanswered last user turn as
  // a draft, not leave a doubled user role hidden in upcoming model context.
  saved = true;
  savedTranscript = [
    { role: 'user', content: 'Earlier question' },
    { role: 'assistant', content: 'Earlier answer' },
    { role: 'user', content: 'Saved unfinished question' },
  ];
  byId('vault-key').value = 'synthetic-vault-key';
  byId('vault-key').listeners.get('input')();
  await vm.runInContext('restoreTranscript()', context);
  assert.equal(vm.runInContext('messages.length', context), 2);
  assert.equal(byId('prompt').value, 'Saved unfinished question');
  assert.match(byId('vault-status').textContent, /unanswered message is in the composer/);
  // Rotating the vault key must also erase this vault-derived unsent draft.
  byId('vault-key').value = 'rotated-secret-key';
  byId('vault-key').listeners.get('input')();
  assert.equal(byId('prompt').value, '');
  assert.equal(vm.runInContext('messages.length', context), 0);

  // Never silently truncate a long pasted draft or submit a request the
  // server would reject. Keep the exact draft editable for Patrick.
  const beforeOversized = forwardedChats.length;
  const oversizedDraft = 'Long pasted draft ' + 'q'.repeat(4001);
  byId('prompt').value = oversizedDraft;
  await vm.runInContext('sendMessage({ preventDefault() {} })', context);
  assert.equal(forwardedChats.length, beforeOversized);
  assert.equal(byId('prompt').value, oversizedDraft);
  assert.match(byId('context-notice').textContent, /4,000/);

  // An incomplete or filtered response may be visible, but is never
  // appended as ordinary assistant history nor included on a future Send.
  for (const kind of ['length_limited', 'filtered', 'unknown']) {
    byId('clear').listeners.get('click')();
    completionStatus = kind;
    byId('prompt').value = 'Question before ' + kind;
    await vm.runInContext('sendMessage({ preventDefault() {} })', context);
    assert.equal(vm.runInContext('messages.length', context), 1);
    assert.equal(byId('transcript').children.at(-1).children[0].textContent,
                 'LOCAL MODEL / UNVERIFIED PARTIAL');
    assert.match(byId('context-notice').textContent, /fragment will not be included/);
    completionStatus = "complete";
    byId('prompt').value = 'Corrected follow-up ' + kind;
    await vm.runInContext('sendMessage({ preventDefault() {} })', context);
    const sent = forwardedChats.at(-1).messages;
    assert.deepEqual(JSON.parse(JSON.stringify(sent)), [
      { role: 'user', content: 'Corrected follow-up ' + kind },
    ]);
    assert.equal(vm.runInContext('messages.length', context), 2,
                 'the unanswered old user turn cannot remain in stored chat history');
    byId('prompt').value = 'Third question ' + kind;
    await vm.runInContext('sendMessage({ preventDefault() {} })', context);
    assert.deepEqual(JSON.parse(JSON.stringify(forwardedChats.at(-1).messages)), [
      { role: 'user', content: 'Corrected follow-up ' + kind },
      { role: 'assistant', content: 'UNKNOWN' },
      { role: 'user', content: 'Third question ' + kind },
    ]);
  }
});
