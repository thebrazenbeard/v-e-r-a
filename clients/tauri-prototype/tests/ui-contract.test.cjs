const {test} = require('node:test');
const assert = require('node:assert/strict');
const {JSDOM} = require('jsdom');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname,'../src/index.html'),'utf8');
const app = fs.readFileSync(path.join(__dirname,'../src/app.js'),'utf8');
const sessionId = 'abcdefghijklmnopqrstuvwx12345678';
const settle = () => new Promise(resolve => setTimeout(resolve, 15));

function ui(handlers) {
  const dom = new JSDOM(html, {url:'https://tauri.localhost/',runScripts:'outside-only'});
  const {window} = dom;
  Object.defineProperty(window.crypto,'randomUUID',{value:()=>'feecd0a0-1234-4321-a0d0-123456789012'});
  const calls = [];
  window.__TAURI__={core:{invoke:(name,args) => {
    calls.push({name,args});
    const method=handlers[name];
    return method ? method(args) : Promise.reject(Error('unexpected '+name));
  }}};
  window.eval(app);
  window.dispatchEvent(new window.Event('DOMContentLoaded'));
  return {window,calls,dom};
}

test('Enrolled V2 never silently falls back to legacy when offline', async () => {
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>{throw Error('offline')}
  });
  await settle();
  assert.equal(calls.some(x=>x.name==='models'),false);
  assert.match(window.document.querySelector('#status').textContent,/fallback prohibited/i);
  assert.equal(window.document.querySelector('#send').disabled,true);
  window.close();
});
test('V2 session inventory and encrypted history are restored', async()=>{
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>['vera-local:latest'],
    v2_list_sessions:async()=>[sessionId],
    v2_history:async()=>[{user:'private question',assistant:'private answer',model:'vera-local:latest'}]
  });
  await settle();
  const d=window.document;
  assert.equal(d.querySelector('#sessions').hidden,false);
  assert.equal(d.querySelector('#sessions').value,sessionId);
  assert.match(d.querySelector('#history').textContent,/private question/);
  assert.match(d.querySelector('#history').textContent,/private answer/);
  assert.equal(calls.some(c=>c.name==='models'),false);
  window.close();
});
test('V2 send clears composer immediately and keeps response scoped to server session',async()=>{
  let complete;
  const promise=new Promise(resolve=>{complete=resolve});
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>['vera-local:latest'],
    v2_list_sessions:async()=>[sessionId],
    v2_history:async()=>[],
    v2_chat:async()=>promise
  });
  await settle();
  const d=window.document;
  d.querySelector('#prompt').value='synthetic prompt';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
  assert.equal(d.querySelector('#prompt').value,'');
  assert.match(d.querySelector('#history').textContent,/synthetic prompt/);
  await settle();
  const request=calls.find(x=>x.name==='v2_chat');
  assert.equal(request.args.sessionId,sessionId);
  assert.equal(calls.some(c=>c.name==='chat'),false);
  complete('model reply');
  await settle();
  assert.match(d.querySelector('#history').textContent,/model reply/);
  window.close();
});
test('When unpaired, client explicitly identifies legacy mode without offering V2 history',async()=>{
  const {window,calls}=ui({
    v2_enrolled:async()=>false,
    models:async()=>['vera-local:latest']
  });
  await settle();
  const d=window.document;
  assert.match(d.querySelector('#status').textContent,/Legacy preview/i);
  assert.equal(d.querySelector('#sessions').hidden,true);
  assert.equal(calls.some(c=>c.name==='v2_history'),false);
  window.close();
});
