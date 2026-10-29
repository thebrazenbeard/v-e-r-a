"use strict";
const status = document.querySelector("#status");
const modelSelect = document.querySelector("#model");
const sessionSelect = document.querySelector("#sessions");
const sessionLabel = document.querySelector("#session-label");
const newSession = document.querySelector("#new-session");
const connect = document.querySelector("#connect");
const send = document.querySelector("#send");
const form = document.querySelector("#composer");
const prompt = document.querySelector("#prompt");
const history = document.querySelector("#history");

let busy = false;
let connected = false;
let secureMode = false;
let activeSession = null;
const legacySession = crypto.randomUUID().replaceAll("-", "");

function state(message) {
  status.textContent = message;
  send.disabled = !connected || busy;
  connect.disabled = busy;
  newSession.disabled = busy;
  sessionSelect.disabled = busy;
}
function bubble(who, message, css="") {
  const wrap = document.createElement("article");
  wrap.className = "bubble " + css;
  const label = document.createElement("span");
  label.className = "speaker";
  label.textContent = who;
  const body = document.createElement("div");
  body.textContent = message;
  wrap.append(label, body);
  history.append(wrap);
  history.scrollTop = history.scrollHeight;
}
function clearBubbles() {
  history.replaceChildren();
}
async function invoke(command,args={}) {
  if (!window.__TAURI__?.core?.invoke) throw new Error("Tauri IPC unavailable");
  return window.__TAURI__.core.invoke(command,args);
}
function showSessions(show) {
  sessionSelect.hidden = !show;
  sessionLabel.hidden = !show;
  newSession.hidden = !show;
}
function displayModels(names) {
  const prior = modelSelect.value;
  modelSelect.replaceChildren();
  for (const name of names) {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    modelSelect.add(option);
  }
  modelSelect.value = names.includes(prior) ? prior :
    names.includes("vera-local:latest") ? "vera-local:latest" : names[0];
}
function sessionOption(sid) {
  const item = document.createElement("option");
  item.value = sid;
  item.textContent = "Chat " + sid.slice(0, 9);
  return item;
}
async function loadHistory(sid) {
  if (!secureMode || !sid) return;
  const turns = await invoke("v2_history",{sessionId:sid});
  clearBubbles();
  if (turns.length === 0) {
    bubble("VERA", "New private conversation. Your history is encrypted on Lappy.");
  } else {
    for (const item of turns) {
      bubble("YOU", item.user, "you");
      bubble("VERA / " + item.model, item.assistant);
    }
  }
  activeSession = sid;
  state("V2 device verified - " + turns.length + " saved exchanges retrieved");
}
async function load() {
  if (busy) return;
  busy = true;
  connected = false;
  state("Checking private device authentication…");
  try {
    const enrolled = await invoke("v2_enrolled");
    secureMode = enrolled;
    if (enrolled) {
      // There is intentionally no legacy fallback after device enrollment.
      const models = await invoke("v2_models");
      if (!models.length) throw new Error("No installed local models");
      secureMode = true;
      displayModels(models);
      const ids = await invoke("v2_list_sessions");
      sessionSelect.replaceChildren();
      for (const id of ids) sessionSelect.add(sessionOption(id));
      showSessions(true);
      let id = ids.find(x => x === activeSession) || ids[0];
      if (!id) {
        id = await invoke("v2_create_session");
        sessionSelect.add(sessionOption(id));
      }
      sessionSelect.value = id;
      await loadHistory(id);
      connected = true;
      state("Secure V2 connected - encrypted owner-scoped history available");
    } else {
      secureMode = false;
      activeSession = null;
      showSessions(false);
      clearBubbles();
      const names = await invoke("models");
      if (!names.length) throw new Error("No installed local models");
      displayModels(names);
      bubble("VERA","Legacy V1 preview. Shared conversation retrieval is not available without V2 enrollment.");
      connected = true;
      state("Legacy preview only - enroll device to enable secured history");
    }
  } catch (_) {
    connected = false;
    // Deliberately fail closed when enrolled device cannot reach V2.
    state(secureMode
      ? "Secure V2 unavailable. Legacy fallback prohibited."
      : "Gateway unavailable or pairing required.");
  } finally {
    busy = false; state(status.textContent);
  }
}
newSession.addEventListener("click", async () => {
  if (!secureMode || busy || !connected) return;
  busy = true; state("Creating owner-scoped session…");
  try {
    const sid = await invoke("v2_create_session");
    sessionSelect.add(sessionOption(sid));
    sessionSelect.value = sid;
    await loadHistory(sid);
  } catch (_) {
    state("Could not create an authorized session.");
  } finally {
    busy = false; state(status.textContent);
  }
});
sessionSelect.addEventListener("change", async () => {
  if (!secureMode || busy || !connected) return;
  busy = true;
  state("Retrieving encrypted conversation…");
  try {
    await loadHistory(sessionSelect.value);
  } catch (_) {
    connected = false;
    state("History access refused; reconnect required.");
  } finally {
    busy = false; state(status.textContent);
  }
});
form.addEventListener("submit", async event => {
  event.preventDefault();
  if (busy || !connected) return;
  const text = prompt.value.trim();
  if (!text || text.length > 4096) return;
  const model = modelSelect.value;
  const requestId = crypto.randomUUID().replaceAll("-", "");
  const sessionId = secureMode ? activeSession : legacySession;
  if (!sessionId) return;
  prompt.value = "";
  bubble("YOU", text, "you");
  busy = true;
  state("Generating locally on " + model + "…");
  try {
    const reply = secureMode
      ? await invoke("v2_chat",{model,sessionId,requestId,content:text})
      : await invoke("chat",{model,sessionId,requestId,content:text});
    bubble("VERA / " + model, reply);
    state((secureMode ? "Secure V2" : "Legacy V1") + " connected - " + model);
  } catch (_) {
    if (!prompt.value) prompt.value = text;
    bubble("SYSTEM","Delivery uncertain. Draft restored; verify history before resending.");
    state("Inference not confirmed. Check connection and history.");
  } finally {
    busy = false; state(status.textContent);
  }
});
connect.addEventListener("click",load);
prompt.addEventListener("keydown",event => {
  if (event.ctrlKey && event.key === "Enter") {
    event.preventDefault();
    form.requestSubmit();
  }
});
window.addEventListener("DOMContentLoaded",load);
