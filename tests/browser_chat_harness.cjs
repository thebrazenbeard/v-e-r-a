"use strict";

// Dependency-free DOM double executes the *real* interface/static/app.js.
// This is a source/protocol test, never a real-browser or model-quality test.
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const base = process.argv[2];
const mode = process.argv[3];
if (!base || !["three_turns", "seven_turns", "eight_turns", "restore_odd", "truncated", "busy", "one_turn"].includes(mode)) {
  throw Error("test harness requires local gateway URL and test mode");
}

class Element {
  constructor(id = "") {
    this.id = id;
    this.children = [];
    this.listeners = new Map();
    this.value = "";
    this.textContent = "";
    this.disabled = false;
    this.hidden = false;
    this.dataset = {};
    this.firstChild = { textContent: "" };
  }
  get options() { return this.children; }
  addEventListener(name, listener) { this.listeners.set(name, listener); }
  append(...children) {
    this.children.push(...children);
    if (this.id === "model" && !this.value && this.children.length) {
      this.value = this.children[0].value;
    }
  }
  replaceChildren(...children) {
    this.children = [...children];
    if (this.id === "model") this.value = children[0]?.value || "";
  }
  scrollIntoView() {}
  focus() {}
  requestSubmit() { return this.listeners.get("submit")({ preventDefault() {} }); }
}

const elements = new Map();
const element = (id) => {
  if (!elements.has(id)) elements.set(id, new Element(id));
  return elements.get(id);
};
const document = {
  getElementById: element,
  createElement: (name) => new Element(name),
  querySelectorAll: () => [],
};

const originalFetch = fetch;
const localFetch = (resource, init = {}) => {
  if (typeof resource !== "string" || !resource.startsWith("/")) {
    throw Error("UI attempted a nonlocal or nonrelative fetch");
  }
  const headers = { ...init.headers };
  if (init.method && init.method !== "GET") headers.Origin = base;
  return originalFetch(base + resource, { ...init, headers });
};

const context = vm.createContext({
  document, window: { confirm: () => true }, fetch: localFetch,
  AbortController, Option: class extends Element {
    constructor(text, value) { super("option"); this.textContent = text; this.value = value; }
  }, console,
});

const source = fs.readFileSync(path.resolve(__dirname, "../interface/static/app.js"), "utf8");
vm.runInContext(source, context, { filename: "interface/static/app.js" });

async function ready() {
  const until = Date.now() + 2500;
  while (Date.now() < until) {
    if (element("model").value && element("connection").textContent.includes("UNVERIFIED")) return;
    await new Promise((done) => setTimeout(done, 10));
  }
  throw Error("UI model/session init did not finish");
}

async function submit(content) {
  element("prompt").value = content;
  await element("chat-form").listeners.get("submit")({ preventDefault() {} });
}

async function main() {
  await ready();
  let restoredDraft = null;
  let restoredHistoryBeforeSubmit = null;
  let restoredVaultStatus = null;
  let afterKeyRotation = null;
  if (mode === "three_turns") {
    await submit("I prefer the name Iris.");
    await submit("Correction: call me Nova.");
    await submit("What name should you use?");
  } else if (mode === "seven_turns") {
    await submit("I prefer the name Iris.");
    await submit("Correction: call me Nova.");
    await submit("What name should you use?");
    await submit("What would a dry reply sound like?");
    await submit("Tell me the limits of your memory.");
    await submit("What is one honest uncertainty?");
    await submit("What name should you use?");
  } else if (mode === "eight_turns") {
    await submit("I prefer the name Iris.");
    await submit("What would a dry reply sound like?");
    await submit("What do you know about our context?");
    await submit("Correction: call me Nova.");
    await submit("Explain one limitation in a sentence.");
    await submit("Do you have durable memory?");
    await submit("What is one honest uncertainty?");
    await submit("What name should you use?");
  } else if (mode === "restore_odd") {
    const until = Date.now() + 2500;
    // The real button remains disabled until a key is entered; this DOM
    // double does not reproduce markup attributes. Await completed status
    // independently of the control's pre-key disabled state.
    while (!element("vault-status").textContent.includes("Available locally") &&
           Date.now() < until) {
      await new Promise((done) => setTimeout(done, 10));
    }
    if (!element("vault-status").textContent.includes("Available locally")) {
      throw Error("Vault configuration did not become available");
    }
    element("vault-key").value = "synthetic-owner-vault-key-0123456789";
    element("vault-key").listeners.get("input")();
    if (element("vault-restore").disabled) throw Error("Vault restore not enabled after key");
    await element("vault-restore").listeners.get("click")();
    restoredDraft = element("prompt").value;
    restoredHistoryBeforeSubmit = vm.runInContext(
      "messages.map(x => ({role: x.role, content: x.content}))", context);
    restoredVaultStatus = element("vault-status").textContent;
    // The browser must submit a single final user turn from the restored
    // draft, not two adjacent user turns from an unpaired saved history.
    await element("chat-form").listeners.get("submit")({ preventDefault() {} });
    // Restore the same odd history again, then rotate keys without submitting.
    await element("vault-restore").listeners.get("click")();
    element("vault-key").value = "different-owner-vault-key-0123456789";
    element("vault-key").listeners.get("input")();
    afterKeyRotation = { prompt: element("prompt").value,
      messages: vm.runInContext("messages.length", context),
      bubbles: element("transcript").children.length };
  } else if (mode === "truncated") {
    await submit("Tell me what to do about the correction.");
  } else if (mode === "busy") {
    await submit("Briefly acknowledge me.");
  } else {
    await submit("Hello Vera.");
  }
  const messages = vm.runInContext("messages.map(x => ({role: x.role, content: x.content}))", context);
  const bubbles = element("transcript").children.map((article) => ({
    roleLabel: article.children[0].textContent,
    content: article.children[1].textContent,
  }));
  const statusResult = await localFetch("/api/status", {
    headers: { "X-Vera-Session": vm.runInContext("sessionToken", context) },
  });
  const status = await statusResult.json();
  process.stdout.write(JSON.stringify({ mode, messages, bubbles,
    restoredDraft, restoredHistoryBeforeSubmit, restoredVaultStatus, afterKeyRotation,
    promptRecovered: element("prompt").value, status,
    connection: element("connection").textContent,
    modelDetail: element("model-detail").textContent,
    vaultStatus: element("vault-status").textContent,
  }));
}

main().catch((error) => { console.error(error.stack || String(error)); process.exitCode = 1; });
