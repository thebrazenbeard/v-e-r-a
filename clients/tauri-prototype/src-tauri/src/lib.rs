use serde_json::{json,Value};
use std::{fs,path::PathBuf,time::Duration};

const ROOT:&str="http://127.0.0.1:18777";

fn token() -> Result<String,String> {
    let base=std::env::var("LOCALAPPDATA").map_err(|_|"Local profile unavailable")?;
    let path=PathBuf::from(base).join("VeraPhoneGateway").join("pairing-token.txt");
    let raw=fs::read_to_string(path).map_err(|_|"Local Vera is not paired")?;
    let text=raw.trim();
    if !(32..=128).contains(&text.len()) || !text.bytes().all(|b|
        b.is_ascii_alphanumeric() || b==b'_' || b==b'-') {
        return Err("Invalid local pairing credential".into());
    }
    Ok(text.into())
}

fn agent() -> ureq::Agent {
    ureq::AgentBuilder::new().redirects(0).try_proxy_from_env(false)
        .timeout_connect(Duration::from_secs(10))
        .timeout_read(Duration::from_secs(95))
        .timeout_write(Duration::from_secs(10)).build()
}

fn verified(body:Value) -> Result<Value,String> {
    if body.get("mode").and_then(Value::as_str)!=Some("response_only")
        || body.get("node").and_then(Value::as_str)!=Some("local") {
        return Err("Unexpected gateway authority".into());
    }
    Ok(body)
}

#[tauri::command]
fn models() -> Result<Vec<String>,String> {
    let secret=token()?;
    let result=agent().get(&format!("{ROOT}/v1/models"))
        .set("Authorization",&format!("Bearer {secret}"))
        .call().map_err(|_|"Vera gateway unavailable")?;
    if result.status()!=200 {return Err("Gateway refused models".into());}
    let body:Value=result.into_json().map_err(|_|"Invalid models JSON")?;
    let body=verified(body)?;
    let names=body.get("models").and_then(Value::as_array).ok_or("Invalid inventory")?;
    if names.len()>32 {return Err("Inventory too large".into());}
    names.iter().map(|v| {
        let name=v.as_str().ok_or("Invalid model name")?;
        if name.is_empty() || name.len()>128 {return Err("Invalid model name".into());}
        Ok(name.to_owned())
    }).collect()
}

#[tauri::command]
fn chat(model:String,session_id:String,request_id:String,content:String)
    -> Result<String,String> {
    let good_id=|s:&str| (16..=128).contains(&s.len()) &&
        s.bytes().all(|b| b.is_ascii_alphanumeric()||b==b'_'||b==b'-');
    if model.is_empty()||model.len()>128 || content.is_empty()||
        content.chars().count()>4096 || !good_id(&session_id)||!good_id(&request_id) {
        return Err("Invalid bounded request".into());
    }
    let payload=json!({"model":model,"messages":[{"role":"user","content":content}],
        "session_id":session_id,"request_id":request_id});
    if payload.to_string().len()>32768 {return Err("Request too large".into());}
    let secret=token()?;
    let response=agent().post(&format!("{ROOT}/v1/chat"))
        .set("Authorization",&format!("Bearer {secret}"))
        .set("Content-Type","application/json")
        .send_json(payload).map_err(|_|"Local inference failed")?;
    if response.status()!=200 {return Err("Gateway denied chat".into());}
    let body:Value=response.into_json().map_err(|_|"Invalid chat JSON")?;
    let body=verified(body)?;
    if body.get("model").and_then(Value::as_str)!=Some(model.as_str()) {
        return Err("Mismatched model".into());
    }
    let answer=body.get("reply").and_then(Value::as_str).ok_or("Missing reply")?;
    if answer.is_empty()||answer.len()>16000 {return Err("Invalid reply".into());}
    Ok(answer.into())
}

#[cfg_attr(mobile,tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default().invoke_handler(tauri::generate_handler![models,chat])
        .run(tauri::generate_context!()).expect("Vera desktop launcher failed");
}
