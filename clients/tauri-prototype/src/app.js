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
// Keep an uncertain V2 request ID for an explicit retry of precisely the same
// owner/session/model/content. Never replay automatically: the gateway's
// in-process dedupe is not a durable exactly-once guarantee after a restart.
let uncertainV2Request = null;
const legacySession = crypto.randomUUID().replaceAll("-", "");

function state(message) {
  status.textContent = message;
  send.disabled = !connected || busy;
  modelSelect.disabled = !connected || busy;
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
function unavailableModels() {
  modelSelect.replaceChildren();
  const option = document.createElement("option");
  option.value = "";
  option.textContent = "Unavailable — reconnect";
  modelSelect.add(option);
}
function discoveryFailure(error) {
  // Bounded non-sensitive categories only: never display raw IPC errors.
  const reason = String(error ?? "");
  if (/Tauri IPC unavailable/i.test(reason)) return "Desktop bridge unavailable. Reopen the desktop preview.";
  if (/Local profile unavailable|Local Vera is not paired|Invalid local pairing credential/i.test(reason))
    return "Local pairing missing or invalid for this Windows account.";
  if (/No installed local models/i.test(reason)) return "No installed local models were reported.";
  if (/Unexpected gateway authority|Invalid models JSON|Invalid inventory|Inventory too large|Invalid model name/i.test(reason))
    return "Incompatible gateway inventory response.";
  if (/Vera gateway unavailable|Gateway refused models/i.test(reason))
    return "Gateway request failed; check the local service and pairing.";
  return "Model discovery failed. Reconnect after checking the local gateway.";
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
  // Only a persisted result with the SAME server request ID, owner session,
  // model, and submitted text resolves an uncertain send. Similar text alone
  // is not evidence of delivery. Missing results in bounded recent history
  // do not prove non-delivery either.
  const confirmedPending = uncertainV2Request
    && uncertainV2Request.sessionId === sid
    && turns.some(item => item.request_id === uncertainV2Request.requestId
      && item.user === uncertainV2Request.content
      && item.model === uncertainV2Request.model
      && typeof item.assistant === "string" && item.assistant.length > 0);
  if (confirmedPending) {
    if (prompt.value === uncertainV2Request.content) prompt.value = "";
    uncertainV2Request = null;
  }
  clearBubbles();
  if (turns.length === 0) {
    bubble("VERA", "New private conversation. History is protected by the owner-scoped gateway.");
  } else {
    for (const item of turns) {
      bubble("YOU", item.user, "you");
      bubble("VERA / " + item.model, item.assistant);
    }
  }
  activeSession = sid;
  state(uncertainV2Request?.sessionId === sid
    ? "V2 history retrieved; uncertain delivery not confirmed. Review before manual retry."
    : "V2 device verified - " + turns.length + " saved exchanges retrieved");
}
async function load() {
  if (busy) return;
  busy = true;
  connected = false;
  let enrollmentChecked = false;
  unavailableModels();
  state("Checking private device authentication…");
  try {
    const enrolled = await invoke("v2_enrolled");
    enrollmentChecked = true;
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
      state(uncertainV2Request?.sessionId === id
        ? "Secure V2 connected; uncertain delivery not confirmed in recent history. Review before retry."
        : "Secure V2 connected - encrypted owner-scoped history available");
    } else {
      secureMode = false;
      activeSession = null;
      showSessions(false);
      const names = await invoke("models");
      if (!names.length) throw new Error("No installed local models");
      displayModels(names);
      // Preserve the visible conversation when model discovery fails.
      clearBubbles();
      bubble("VERA","Legacy V1 preview. Shared conversation retrieval is not available without V2 enrollment.");
      connected = true;
      state("Legacy preview only - enroll device to enable secured history");
    }
  } catch (error) {
    connected = false;
    unavailableModels();
    // Deliberately fail closed when enrolled device cannot reach V2.
    state(!enrollmentChecked ? "Device enrollment check failed. Legacy fallback not attempted. " + discoveryFailure(error) : secureMode
      ? "Secure V2 unavailable. Legacy fallback prohibited."
      : discoveryFailure(error));
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
  const sessionId = secureMode ? activeSession : legacySession;
  if (!sessionId) return;
  const sameUncertainV2Request = secureMode && uncertainV2Request
    && uncertainV2Request.model === model
    && uncertainV2Request.sessionId === sessionId
    && uncertainV2Request.content === text;
  const requestId = sameUncertainV2Request
    ? uncertainV2Request.requestId : crypto.randomUUID().replaceAll("-", "");
  if (!sameUncertainV2Request) uncertainV2Request = null;
  prompt.value = "";
  if (!sameUncertainV2Request) bubble("YOU", text, "you");
  else bubble("SYSTEM", "Explicit retry of an uncertain V2 request; checking history first is recommended.");
  busy = true;
  state("Generating locally on " + model + "…");
  try {
    const reply = secureMode
      ? await invoke("v2_chat",{model,sessionId,requestId,content:text})
      : await invoke("chat",{model,sessionId,requestId,content:text});
    if (secureMode) uncertainV2Request = null;
    bubble("VERA / " + model, reply);
    state((secureMode ? "Secure V2" : "Legacy V1") + " connected - " + model);
  } catch (_) {
    if (secureMode) uncertainV2Request = {model,sessionId,content:text,requestId};
    if (!prompt.value) prompt.value = text;
    if (secureMode) {
      bubble("SYSTEM","Delivery uncertain. Draft restored. Reconnect and verify V2 history before any explicit retry; gateway restarts may defeat in-process deduplication.");
      state("Delivery uncertain. Verify owner history before manually retrying.");
    } else {
      bubble("SYSTEM","Legacy delivery uncertain. Draft restored; the V1 preview cannot retrieve shared history.");
      state("Legacy inference not confirmed. Inspect any visible reply before retrying.");
    }
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
