"use strict";
const status = document.querySelector("#status");
const modelSelect = document.querySelector("#model");
const connect = document.querySelector("#connect");
const send = document.querySelector("#send");
const form = document.querySelector("#composer");
const prompt = document.querySelector("#prompt");
const history = document.querySelector("#history");
const sessionId = crypto.randomUUID().replaceAll("-", "");
let busy = false;
let connected = false;

function state(message) {
  status.textContent = message;
  send.disabled = !connected || busy;
  connect.disabled = busy;
}
function bubble(who, message, css="") {
  const wrap = document.createElement("article");
  wrap.className = "bubble " + css;
  const label = document.createElement("span");
  label.className = "speaker";
  label.textContent = who;
  const body = document.createElement("div");
  body.textContent = message;
  wrap.append(label,body);
  history.append(wrap);
  history.scrollTop = history.scrollHeight;
}
async function invoke(command,args={}) {
  if (!window.__TAURI__?.core?.invoke) throw new Error("Tauri IPC unavailable");
  return window.__TAURI__.core.invoke(command,args);
}
async function load() {
  busy=true;state("Connecting to Lappy's local inference gateway…");
  try {
    const prior=modelSelect.value;
    const names=await invoke("models");
    if (!names.length) throw new Error("No installed local models");
    modelSelect.replaceChildren();
    for (const name of names) {
      const option=document.createElement("option");
      option.value=name;option.textContent=name;
      modelSelect.add(option);
    }
    modelSelect.value=names.includes(prior)?prior: names.includes("vera-local:latest")?"vera-local:latest":names[0];
    connected=true;
    state("Connected • "+names.length+" local models");
  } catch (_) {
    connected=false;state("Gateway unavailable. Check Lappy inference and pairing.");
  } finally {busy=false;state(status.textContent);}
}
form.addEventListener("submit",async event => {
  event.preventDefault();
  if(busy||!connected)return;
  const text=prompt.value.trim();
  if(!text||text.length>4096)return;
  const model=modelSelect.value;
  const requestId=crypto.randomUUID().replaceAll("-","");
  prompt.value="";
  bubble("YOU",text,"you");
  busy=true;state("Generating locally on "+model+"…");
  try {
    const reply=await invoke("chat",{model,sessionId,requestId,content:text});
    bubble("VERA  /  "+model,reply);
    state("Connected • "+model);
  } catch (_) {
    prompt.value=text;
    bubble("SYSTEM","Message not delivered. Draft restored.");
    state("Inference failed; pairing remains unchanged.");
  } finally {busy=false;state(status.textContent);}
});
connect.addEventListener("click",load);
prompt.addEventListener("keydown",event => {
  if(event.ctrlKey&&event.key==="Enter"){
    event.preventDefault();
    form.requestSubmit();
  }
});
window.addEventListener("DOMContentLoaded",load);
