"use strict";

const transcript = document.getElementById("transcript");
const intro = document.getElementById("intro");
const prompt = document.getElementById("prompt");
const model = document.getElementById("model");
const send = document.getElementById("send");
const connection = document.getElementById("connection");
const modelDetail = document.getElementById("model-detail");
const contextNotice = document.getElementById("context-notice");
const memoryBoundary = document.getElementById("memory-boundary");
const vaultKey = document.getElementById("vault-key");
const vaultSave = document.getElementById("vault-save");
const vaultRestore = document.getElementById("vault-restore");
const vaultDelete = document.getElementById("vault-delete");
const vaultRecall = document.getElementById("vault-recall");
const vaultStatus = document.getElementById("vault-status");
const messages = [];
let sessionToken = "";
let busy = false;
let conversationEpoch = 0;
let activeController = null;
let vaultConfigured = false;
let vaultBusy = false;
let restoredFromVault = false;
let restoredDraftFromVault = false;
let recalledFromVault = false;
let lastVaultKeyValue = vaultKey.value;

// Bound each model request to a contiguous, user-led conversational suffix.
// A naive slice(-12) starts with an assistant message on the seventh user turn.
// It can also exceed the gateway's 16k-character / 24KiB request limits while
// older, no-longer-sent turns still remain visible in the browser transcript.
function recentCoherentHistory(history) {
  // A restored, valid partial transcript can end on a user turn that was
  // never answered. If a new user question follows, omit that unanswered
  // saved turn from this request; never invent an assistant answer to fill it.
  const clean = history.length > 1 && history.at(-1).role === "user" && history.at(-2).role === "user"
    ? [...history.slice(0, -2), history.at(-1)] : history;
  let start = Math.max(0, clean.length - 12);
  if (clean[start]?.role !== "user") start += 1;
  let recent = clean.slice(start);
  const encoder = new TextEncoder();
  while (recent.length > 1) {
    const characters = recent.reduce((sum, item) => sum + item.content.length, 0);
    const jsonBytes = encoder.encode(JSON.stringify({ messages: recent })).length;
    if (characters <= 16000 && jsonBytes <= 20000) break;
    recent = recent.slice(2);
  }
  return recent;
}

function forgetVaultDerivedTab() {
  if (!restoredFromVault && !recalledFromVault) return false;
  conversationEpoch += 1;
  activeController?.abort();
  activeController = null;
  messages.length = 0;
  transcript.replaceChildren();
  intro.hidden = false;
  // An unanswered saved user turn may have been lifted into the composer.
  // Credential rotation/deletion must revoke that plaintext too.
  if (restoredDraftFromVault) prompt.value = "";
  restoredFromVault = false;
  restoredDraftFromVault = false;
  recalledFromVault = false;
  // Changing a key can abort an in-flight request. Do not leave the tab
  // permanently locked behind its now-obsolete request epoch.
  setBusy(false);
  return true;
}

function syncVaultControls() {
  const ready = vaultConfigured && !!vaultKey.value && !!sessionToken && !busy && !vaultBusy;
  vaultSave.disabled = !ready || !messages.length;
  vaultRestore.disabled = !ready;
  vaultDelete.disabled = !ready;
  vaultRecall.disabled = !ready;
  if (!vaultConfigured || !vaultKey.value) vaultRecall.checked = false;
  vaultKey.disabled = vaultBusy;
  send.disabled = busy || vaultBusy;
  prompt.disabled = busy || vaultBusy;
  document.getElementById("clear").disabled = vaultBusy;
}

async function refreshStatus() {
  try {
    const response = await fetch("/api/status", {
      cache: "no-store", headers: { "X-Vera-Session": sessionToken },
    });
    if (!response.ok) throw new Error("Status unavailable");
    const status = await response.json();
    vaultConfigured = status.durable_memory === "opt_in_local_transcript";
    memoryBoundary.textContent = vaultConfigured ? "Opt-in transcript only" : "Not connected";
    vaultStatus.textContent = vaultConfigured
      ? "Available locally, AES-GCM encrypted on disk. Enter operator key; nothing saves automatically."
      : "Not configured on this interface process. No chat is saved.";
  } catch (_) {
    vaultConfigured = false;
    memoryBoundary.textContent = "Unknown / unavailable";
    vaultStatus.textContent = "Vault status unavailable; saving disabled.";
  }
  syncVaultControls();
}

async function vaultRequest(method, body = null, revision = null) {
  if (!vaultConfigured || !vaultKey.value || busy || !sessionToken) {
    throw new Error("Vault is not unlocked");
  }
  const headers = { "Content-Type": "application/json", "X-Vera-Session": sessionToken,
                    "X-Vera-Vault-Key": vaultKey.value };
  if (revision !== null) headers["X-Vera-Vault-Revision"] = String(revision);
  const response = await fetch("/api/transcript", {
    method,
    cache: "no-store",
    headers,
    body: body === null ? undefined : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Vault request failed");
  return data;
}

async function withVaultLock(work) {
  if (vaultBusy || busy || !vaultConfigured || !vaultKey.value || !sessionToken) return;
  vaultBusy = true;
  syncVaultControls();
  try {
    await work();
  } finally {
    vaultBusy = false;
    syncVaultControls();
  }
}

async function saveRecentTranscript() {
  const recent = recentCoherentHistory(messages);
  if (!recent.length) return;
  await withVaultLock(async () => {
    try {
      const snapshot = await vaultRequest("GET");
      await vaultRequest("POST", { messages: recent, expected_revision: snapshot.revision });
      vaultStatus.textContent = `Saved ${recent.length} recent message(s) encrypted by explicit request.`;
    } catch (error) {
      vaultStatus.textContent = `Save not completed: ${error.message}`;
    }
  });
}

async function restoreTranscript() {
  if ((messages.length || prompt.value.trim()) &&
      !window.confirm("Replace this tab's unsaved conversation or draft with the saved copy?")) return;
  await withVaultLock(async () => {
    try {
      const data = await vaultRequest("GET");
      if (data.status !== "saved") {
        vaultStatus.textContent = "No saved transcript is available.";
        return;
      }
      if (!Array.isArray(data.messages) || data.messages.length > 12) throw new Error("Invalid saved transcript");
      const restored = data.messages.map((row) => {
        if ((row.role !== "user" && row.role !== "assistant") || typeof row.content !== "string") {
          throw new Error("Invalid saved message");
        }
        return { role: row.role, content: row.content };
      });
      // A valid saved history can end with an unanswered user turn. Move it
      // into an editable draft, preserving its bytes without forging a model
      // answer or sending two consecutive user roles on the next request.
      const pending = restored.at(-1)?.role === "user" ? restored.pop().content : "";
      if (pending.length > 4000) throw new Error("Saved draft exceeds prompt limit");
      conversationEpoch += 1;
      messages.length = 0;
      transcript.replaceChildren();
      intro.hidden = false;
      for (const row of restored) {
        messages.push({ role: row.role, content: row.content });
        messageBubble(row.role, row.content);
      }
      restoredFromVault = true;
      restoredDraftFromVault = !!pending;
      prompt.value = pending;
      vaultStatus.textContent = pending
        ? `Restored ${messages.length} completed message(s); last unanswered user turn is an editable draft. The unanswered message is in the composer to edit or send. Nothing was sent.`
        : `Restored ${messages.length} operator-saved messages (unverified).`;
      contextNotice.textContent = pending
        ? "An unanswered saved user message is ready in the composer; nothing has been sent."
        : "Restored text is operator-saved context, not independently verified memory.";
      syncVaultControls();
    } catch (error) {
      vaultStatus.textContent = `Restore not completed: ${error.message}`;
    }
  });
}

async function deleteSavedTranscript() {
  if (!window.confirm("Remove the active saved transcript? A conversation restored from this vault will also be cleared from this tab. SQLite remnants, backups, and snapshots may retain old bytes.")) return;
  await withVaultLock(async () => {
    try {
      const snapshot = await vaultRequest("GET");
      await vaultRequest("DELETE", null, snapshot.revision);
      vaultRecall.checked = false;
      // Recalled answers can echo private context even without manual Restore.
      // A deleted DB row is insufficient unless this tab's derived text goes too.
      forgetVaultDerivedTab();
      vaultStatus.textContent = "Active saved entry removed. This is NOT forensic erasure; backups/remnants may persist.";
    } catch (error) {
      vaultStatus.textContent = `Remove not completed: ${error.message}`;
    }
  });
}

function messageBubble(role, content) {
  const wrapper = document.createElement("article");
  wrapper.className = `message ${role}`;
  const name = document.createElement("span");
  name.className = "message-role";
  name.textContent = role === "user" ? "YOU"
    : role === "system" ? "INTERFACE / ERROR"
    : role === "incomplete" ? "LOCAL MODEL / UNVERIFIED PARTIAL"
    : "MODEL OUTPUT / UNVERIFIED";
  const body = document.createElement("p");
  body.textContent = content; // Never interpret model/user content as HTML.
  wrapper.append(name, body);
  transcript.append(wrapper);
  intro.hidden = true;
  wrapper.scrollIntoView({ behavior: "smooth", block: "end" });
  return wrapper;
}

async function refreshModels() {
  model.disabled = true;
  const previouslySelected = model.value;
  try {
    const response = await fetch("/api/models", {
      cache: "no-store", headers: { "X-Vera-Session": sessionToken },
    });
    if (!response.ok) throw new Error("Model endpoint offline");
    const data = await response.json();
    model.replaceChildren();
    for (const name of data.models) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      model.append(option);
    }
    if (data.models.includes(previouslySelected)) model.value = previouslySelected;
    connection.textContent = data.models.length
      ? "ENDPOINT RESPONDING / UNVERIFIED" : "NO MODEL IDS ADVERTISED";
    modelDetail.textContent = `${data.models.length} endpoint-advertised model ID${data.models.length === 1 ? "" : "s"} · weights not attested`;
    model.disabled = !data.models.length;
  } catch (_) {
    model.replaceChildren(new Option("Model endpoint unavailable", ""));
    connection.textContent = "LOCAL MODEL OFFLINE";
    modelDetail.textContent = "Check the local loopback endpoint and refresh; no weights are attested.";
  }
}

function setBusy(value) {
  busy = value;
  send.disabled = value;
  prompt.disabled = value;
  model.disabled = value || !model.options.length || !model.value;
  send.firstChild.textContent = value ? "Thinking " : "Send ";
  syncVaultControls();
}

async function sendMessage(event) {
  event.preventDefault();
  const content = prompt.value.trim();
  if (!content || busy || vaultBusy || !model.value || !sessionToken) return;
  const codepoints = Array.from(content).length;
  if (codepoints > 4000) {
    contextNotice.textContent = `This draft has ${codepoints.toLocaleString()} characters; the local gateway accepts at most 4,000 per message. Nothing was sent or truncated. Shorten or split it first.`;
    prompt.focus();
    return;
  }
  // After an incomplete/filter/unknown reply there is deliberately no
  // assistant turn. Retire that unanswered question from model history *now*
  // before the next question; trimming only the outgoing request would leave
  // a hidden double-user turn that breaks the third request and vault Save.
  const retiredUnanswered = messages.at(-1)?.role === "user";
  if (retiredUnanswered) messages.pop();
  prompt.value = "";
  messages.push({ role: "user", content });
  syncVaultControls();
  messageBubble("user", content);
  const epoch = conversationEpoch;
  const controller = new AbortController();
  activeController = controller;
  const useSaved = vaultRecall.checked && !vaultRecall.disabled && vaultConfigured && !!vaultKey.value;
  // Treat an attempted private recall as tainted immediately. Waiting for
  // recalled_source in the response leaves a window where rotating the key
  // cannot abort a private request that has not yet returned.
  if (useSaved) recalledFromVault = true;
  const requestBody = useSaved
    ? { model: model.value, messages: [{ role: "user", content }], recall_saved: true }
    : { model: model.value, messages: recentCoherentHistory(messages) };
  if (useSaved) {
    contextNotice.textContent = "This reply uses your explicitly saved transcript and current question, not earlier unsaved tab messages.";
  } else {
    const omitted = messages.length - requestBody.messages.length;
    contextNotice.textContent = (retiredUnanswered
      ? "The earlier incomplete question stays visible but is no longer model or saved-chat context. "
      : "") + (omitted
      ? `${omitted} older visible message${omitted === 1 ? " is" : "s are"} outside this reply's model context. Nothing was saved automatically.`
      : "Current visible conversation is included in this request; nothing is saved automatically.");
  }
  const requestHeaders = { "Content-Type": "application/json", "X-Vera-Session": sessionToken };
  if (useSaved) requestHeaders["X-Vera-Vault-Key"] = vaultKey.value;
  setBusy(true);
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: requestHeaders,
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    });
    const data = await response.json();
    if (epoch !== conversationEpoch) return;
    if (!response.ok) throw new Error(data.error || "Local inference failed");
    // An upstream length cut-off, filter, or missing completion reason must
    // never become an ordinary assistant turn in future model context or
    // a trusted transcript Save. Show the raw text as an unverified fragment,
    // and let the next user question replace the unfinished user-led turn.
    const completion = data.response_completion_status ?? "unknown";
    if (completion === "complete") {
      messages.push({ role: "assistant", content: data.reply });
      messageBubble("assistant", data.reply);
    } else {
      messageBubble("incomplete", data.reply);
      const reasons = {
        length_limited: "The upstream reported a length-limited reply.",
        filtered: "The upstream reported a filtered reply.",
        unknown: "Model completion was not reported by the upstream.",
      };
      contextNotice.textContent += " " + (reasons[completion] || "Completion was unverified.")
        + " This fragment will not be included as a completed assistant turn in future context or saved transcript.";
    }
    // Once this draft has been sent, its former vault-derived composer value
    // is no longer pending. The restored history remains tainted and is still
    // revoked by forgetVaultDerivedTab when a key changes.
    restoredDraftFromVault = false;
    syncVaultControls();
    if (data.recalled_source) {
      recalledFromVault = true;
      vaultStatus.textContent = `Explicit saved-context recall used at revision ${data.recalled_source.revision}; operator-saved text is unverified.`;
    }
  } catch (error) {
    if (epoch === conversationEpoch) {
      messageBubble("system", `Not completed: ${error.message}`);
      // Keep the prompt recoverable and avoid claiming a model response occurred.
      messages.pop();
      syncVaultControls();
      prompt.value = content;
    }
  } finally {
    if (epoch === conversationEpoch) {
      activeController = null;
      setBusy(false);
      prompt.focus();
    }
  }
}

document.getElementById("chat-form").addEventListener("submit", sendMessage);
prompt.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    document.getElementById("chat-form").requestSubmit();
  }
});
document.getElementById("refresh").addEventListener("click", refreshModels);
vaultKey.addEventListener("input", () => {
  // A nonempty-to-nonempty credential switch must also revoke all browser
  // history derived from the previous vault. Clearing only on empty leaks it.
  if (vaultKey.value !== lastVaultKeyValue) {
    forgetVaultDerivedTab();
    vaultRecall.checked = false;
  }
  lastVaultKeyValue = vaultKey.value;
  syncVaultControls();
});
vaultSave.addEventListener("click", saveRecentTranscript);
vaultRestore.addEventListener("click", restoreTranscript);
vaultDelete.addEventListener("click", deleteSavedTranscript);
document.getElementById("clear").addEventListener("click", () => {
  conversationEpoch += 1;
  activeController?.abort();
  activeController = null;
  setBusy(false);
  messages.length = 0;
  restoredFromVault = false;
  restoredDraftFromVault = false;
  recalledFromVault = false;
  syncVaultControls();
  transcript.replaceChildren();
  intro.hidden = false;
  prompt.value = "";
  contextNotice.textContent = "The model sees recent messages, not necessarily every older turn visible in this tab.";
  prompt.focus();
});
for (const suggestion of document.querySelectorAll(".suggestion")) {
  suggestion.addEventListener("click", () => {
    prompt.value = suggestion.dataset.prompt;
    prompt.focus();
  });
}

(async () => {
  try {
    const response = await fetch("/api/session", { cache: "no-store" });
    if (!response.ok) throw new Error("Session unavailable");
    sessionToken = (await response.json()).token;
    await refreshModels();
    await refreshStatus();
  } catch (_) {
    connection.textContent = "INTERFACE NOT READY";
    modelDetail.textContent = "Session initialization failed.";
  }
})();
