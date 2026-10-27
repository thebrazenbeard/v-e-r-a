"use strict";

const transcript = document.getElementById("transcript");
const intro = document.getElementById("intro");
const prompt = document.getElementById("prompt");
const model = document.getElementById("model");
const send = document.getElementById("send");
const connection = document.getElementById("connection");
const modelDetail = document.getElementById("model-detail");
const messages = [];
let sessionToken = "";
let busy = false;
let conversationEpoch = 0;
let activeController = null;

function messageBubble(role, content) {
  const wrapper = document.createElement("article");
  wrapper.className = `message ${role}`;
  const name = document.createElement("span");
  name.className = "message-role";
  name.textContent = role === "user" ? "YOU" : role === "system" ? "INTERFACE / ERROR" : "VERA / LOCAL MODEL";
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
    connection.textContent = data.models.length ? "LOCAL MODEL AVAILABLE" : "NO MODELS INSTALLED";
    modelDetail.textContent = `${data.models.length} installed model${data.models.length === 1 ? "" : "s"} · This device`;
    model.disabled = !data.models.length;
  } catch (_) {
    model.replaceChildren(new Option("Model endpoint unavailable", ""));
    connection.textContent = "LOCAL MODEL OFFLINE";
    modelDetail.textContent = "Start your local Ollama service, then refresh.";
  }
}

function setBusy(value) {
  busy = value;
  send.disabled = value;
  prompt.disabled = value;
  model.disabled = value || !model.options.length || !model.value;
  send.firstChild.textContent = value ? "Thinking " : "Send ";
}

async function sendMessage(event) {
  event.preventDefault();
  const content = prompt.value.trim();
  if (!content || busy || !model.value || !sessionToken) return;
  prompt.value = "";
  messages.push({ role: "user", content });
  messageBubble("user", content);
  const epoch = conversationEpoch;
  const controller = new AbortController();
  activeController = controller;
  setBusy(true);
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Vera-Session": sessionToken },
      body: JSON.stringify({ model: model.value, messages: messages.slice(-12) }),
      signal: controller.signal,
    });
    const data = await response.json();
    if (epoch !== conversationEpoch) return;
    if (!response.ok) throw new Error(data.error || "Local inference failed");
    messages.push({ role: "assistant", content: data.reply });
    messageBubble("assistant", data.reply);
  } catch (error) {
    if (epoch === conversationEpoch) {
      messageBubble("system", `Not completed: ${error.message}`);
      // Keep the prompt recoverable and avoid claiming a model response occurred.
      messages.pop();
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
document.getElementById("clear").addEventListener("click", () => {
  conversationEpoch += 1;
  activeController?.abort();
  activeController = null;
  setBusy(false);
  messages.length = 0;
  transcript.replaceChildren();
  intro.hidden = false;
  prompt.value = "";
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
  } catch (_) {
    connection.textContent = "INTERFACE NOT READY";
    modelDetail.textContent = "Session initialization failed.";
  }
})();
