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
  let uuidCounter=0;
  Object.defineProperty(window.crypto,'randomUUID',{value:()=>
    'feecd0a0-1234-4321-a0d0-'+(++uuidCounter).toString(16).padStart(12,'0')});
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

test('Uncertain V2 delivery retains request ID only for explicit identical retry',async()=>{
  let attempts=0;
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>['vera-local:latest'],
    v2_list_sessions:async()=>[sessionId],
    v2_history:async()=>[],
    v2_chat:async()=>{
      if (++attempts === 1) throw Error('connection dropped after possible commit');
      return 'confirmed on explicit retry';
    }
  });
  await settle();
  const d=window.document;
  d.querySelector('#prompt').value='same uncertain question';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  assert.equal(calls.filter(x=>x.name==='v2_chat').length,1,'no automatic retransmission');
  assert.equal(d.querySelector('#prompt').value,'same uncertain question');
  assert.match(d.querySelector('#history').textContent,/verify V2 history before any explicit retry/i);
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  const requests=calls.filter(x=>x.name==='v2_chat');
  assert.equal(requests.length,2);
  assert.equal(requests[0].args.requestId,requests[1].args.requestId,
    'manual same-payload retry must reuse server deduplication key');
  assert.match(d.querySelector('#history').textContent,/confirmed on explicit retry/);
  assert.equal(d.querySelectorAll('#history .you').length,1,'no duplicate pending user bubble');
  window.close();
});

test('Edited V2 payload cannot inherit uncertain request ID',async()=>{
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>['vera-local:latest'],
    v2_list_sessions:async()=>[sessionId],
    v2_history:async()=>[],
    v2_chat:async()=>{throw Error('synthetic delivery uncertainty')}
  });
  await settle();
  const d=window.document;
  d.querySelector('#prompt').value='first draft';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  d.querySelector('#prompt').value='changed draft';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  const requests=calls.filter(x=>x.name==='v2_chat');
  assert.equal(requests.length,2);
  assert.notEqual(requests[0].args.requestId,requests[1].args.requestId,
    'changed request is a distinct inference event');
  window.close();
});

test('Unavailable V1 gateway replaces Loading placeholder and reconnect recovers',async()=>{
  let available=false;
  const {window,calls}=ui({
    v2_enrolled:async()=>false,
    models:async()=>{
      if (!available) throw Error('Vera gateway unavailable');
      return ['vera-local:latest'];
    }
  });
  await settle();
  const d=window.document;
  assert.match(d.querySelector('#status').textContent,/gateway request failed/i);
  assert.equal(d.querySelector('#model').disabled,true);
  assert.doesNotMatch(d.querySelector('#model').textContent,/loading/i);
  assert.equal(d.querySelector('#send').disabled,true);
  available=true;
  d.querySelector('#connect').click();
  await settle();
  assert.equal(calls.filter(c=>c.name==='models').length,2);
  assert.equal(d.querySelector('#model').disabled,false);
  assert.equal(d.querySelector('#model').value,'vera-local:latest');
  assert.equal(d.querySelector('#send').disabled,false);
  window.close();
});

test('Legacy reconnect failure preserves visible conversation without replay',async()=>{
  let available=true;
  const {window,calls}=ui({
    v2_enrolled:async()=>false,
    models:async()=>{
      if (!available) throw Error('Vera gateway unavailable');
      return ['vera-local:latest'];
    },
    chat:async()=> 'synthetic reply'
  });
  await settle();
  const d=window.document;
  d.querySelector('#prompt').value='synthetic question';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  const prior=d.querySelector('#history').textContent;
  assert.match(prior,/synthetic question/);
  assert.match(prior,/synthetic reply/);
  available=false;
  d.querySelector('#connect').click();
  await settle();
  assert.equal(d.querySelector('#history').textContent,prior);
  assert.equal(calls.filter(c=>c.name==='chat').length,1);
  assert.equal(d.querySelector('#send').disabled,true);
  window.close();
});

test('Enrollment check failure forbids V1 fallback and raw error exposure',async()=>{
  const {window,calls}=ui({v2_enrolled:async()=>{
    throw Error('Tauri IPC unavailable: sensitive-local-path');
  }});
  await settle();
  const d=window.document;
  assert.equal(calls.some(c=>c.name==='models'),false);
  assert.match(d.querySelector('#status').textContent,/desktop bridge unavailable/i);
  assert.doesNotMatch(d.querySelector('#status').textContent,/sensitive-local-path/i);
  assert.equal(d.querySelector('#send').disabled,true);
  assert.equal(d.querySelector('#model').disabled,true);
  window.close();
});

test('Enrolled V2 model failure keeps inventory unavailable and never calls V1',async()=>{
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>{throw Error('Vera gateway unavailable')}
  });
  await settle();
  const d=window.document;
  assert.match(d.querySelector('#status').textContent,/fallback prohibited/i);
  assert.equal(d.querySelector('#model').disabled,true);
  assert.equal(calls.some(c=>c.name==='models'),false);
  window.close();
});

test('Reconnect reconciles matching persisted V2 request without retry or duplicate bubble',async()=>{
  let saved=[];
  let submitted;
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>['vera-local:latest'],
    v2_list_sessions:async()=>[sessionId],
    v2_history:async()=>saved,
    v2_chat:async args=>{
      submitted=args;
      throw Error('response lost after server committed exchange');
    }
  });
  await settle();
  const d=window.document;
  d.querySelector('#prompt').value='uncertain saved question';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  assert.equal(d.querySelector('#prompt').value,'uncertain saved question');
  saved=[{request_id:submitted.requestId,user:submitted.content,
    assistant:'persisted answer',model:submitted.model}];
  d.querySelector('#connect').click();
  await settle();
  assert.equal(calls.filter(c=>c.name==='v2_chat').length,1,'reconnect must never replay');
  assert.equal(d.querySelector('#prompt').value,'','persisted request clears only matching draft');
  assert.equal(d.querySelectorAll('#history .you').length,1,'history is rendered once');
  assert.match(d.querySelector('#history').textContent,/persisted answer/);
  assert.doesNotMatch(d.querySelector('#status').textContent,/uncertain/i);
  // A new question after reconciliation must receive a new server request ID.
  d.querySelector('#prompt').value='new question';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  const sends=calls.filter(c=>c.name==='v2_chat');
  assert.notEqual(sends[0].args.requestId,sends[1].args.requestId);
  window.close();
});

test('Unmatched V2 history does not resolve uncertainty or automatically resend',async()=>{
  let submitted;
  let saved=[];
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>['vera-local:latest'],
    v2_list_sessions:async()=>[sessionId],
    v2_history:async()=>saved,
    v2_chat:async args=>{submitted=args;throw Error('uncertain')}
  });
  await settle();
  const d=window.document;
  d.querySelector('#prompt').value='still uncertain';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  saved=[{request_id:submitted.requestId,user:'different question',
    assistant:'an answer',model:submitted.model}];
  d.querySelector('#connect').click();
  await settle();
  assert.equal(calls.filter(c=>c.name==='v2_chat').length,1,'never auto retry');
  assert.equal(d.querySelector('#prompt').value,'still uncertain');
  assert.match(d.querySelector('#status').textContent,/uncertain delivery not confirmed/i);
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  const sends=calls.filter(c=>c.name==='v2_chat');
  assert.equal(sends[0].args.requestId,sends[1].args.requestId,
    'same explicitly retried payload preserves uncertain identity');
  window.close();
});

test('Confirmed history does not erase a newer unsent draft',async()=>{
  let submitted;
  let saved=[];
  const {window,calls}=ui({
    v2_enrolled:async()=>true,
    v2_models:async()=>['vera-local:latest'],
    v2_list_sessions:async()=>[sessionId],
    v2_history:async()=>saved,
    v2_chat:async args=>{submitted=args;throw Error('lost response')}
  });
  await settle();
  const d=window.document;
  d.querySelector('#prompt').value='old uncertain question';
  d.querySelector('#composer').dispatchEvent(new window.Event('submit',{cancelable:true}));
  await settle();
  d.querySelector('#prompt').value='new unsent draft';
  saved=[{request_id:submitted.requestId,user:submitted.content,
    assistant:'old persisted answer',model:submitted.model}];
  d.querySelector('#connect').click();
  await settle();
  assert.equal(d.querySelector('#prompt').value,'new unsent draft');
  assert.equal(calls.filter(c=>c.name==='v2_chat').length,1);
  assert.match(d.querySelector('#history').textContent,/old persisted answer/);
  window.close();
});
