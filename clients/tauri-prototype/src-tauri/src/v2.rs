//! Device-scoped Vera V2 API for explicitly paired Windows preview clients.
//! The legacy V1 gateway remains a separate compatibility path.
//! Never expose the bearer or owner ID through JavaScript IPC.

use serde_json::{json, Value};
use std::{env, fs, path::PathBuf, time::Duration};

const V2_ROOT: &str = "http://127.0.0.1:18781";

fn credential() -> Result<String, String> {
    let local = env::var("LOCALAPPDATA").map_err(|_| "Local profile unavailable")?;
    let path = PathBuf::from(local)
        .join("VeraDesktop").join("device-v2-token.txt");
    let raw = fs::read_to_string(path).map_err(|_| "Device pairing required for V2")?;
    let token = raw.trim();
    if !(32..=128).contains(&token.len()) || !token.bytes().all(|b|
        b.is_ascii_alphanumeric() || b == b'-' || b == b'_') {
        return Err("Invalid local device credential".into());
    }
    Ok(token.into())
}

fn agent() -> ureq::Agent {
    ureq::AgentBuilder::new()
        .redirects(0).try_proxy_from_env(false)
        .timeout_connect(Duration::from_secs(5))
        .timeout_read(Duration::from_secs(95))
        .timeout_write(Duration::from_secs(5))
        .build()
}

fn fail(reason: &str) -> String { reason.to_owned() }

fn get(path: &str) -> Result<Value, String> {
    let token = credential()?;
    let req = agent().get(&format!("{V2_ROOT}{path}"))
        .set("Authorization", &format!("Bearer {token}"));
    let resp = req.call().map_err(|_| fail("V2 gateway denied request or is unavailable"))?;
    if resp.status() != 200 {
        return Err(fail("V2 request was rejected"));
    }
    let len = resp.header("Content-Length").and_then(|x| x.parse::<usize>().ok());
    if len.is_some_and(|len| len > 65536) { return Err(fail("V2 response exceeds limit")); }
    let value: Value = resp.into_json().map_err(|_| fail("Malformed V2 JSON"))?;
    Ok(value)
}

fn post(path: &str, data: Value, expected: u16) -> Result<Value, String> {
    let token = credential()?;
    if data.to_string().len() > 8192 { return Err(fail("V2 request exceeds limit")); }
    let resp = agent().post(&format!("{V2_ROOT}{path}"))
        .set("Authorization", &format!("Bearer {token}"))
        .set("Content-Type", "application/json")
        .send_json(data)
        .map_err(|_| fail("V2 gateway denied request or is unavailable"))?;
    if resp.status() != expected { return Err(fail("V2 response status mismatch")); }
    let len = resp.header("Content-Length").and_then(|x| x.parse::<usize>().ok());
    if len.is_some_and(|len| len > 65536) { return Err(fail("V2 response exceeds limit")); }
    resp.into_json().map_err(|_| fail("Malformed V2 JSON"))
}

fn check_id(value: &str) -> bool {
    (16..=128).contains(&value.len()) &&
        value.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
}

fn verify_mode(v: &Value) -> Result<(), String> {
    if v.get("node").and_then(Value::as_str) != Some("local")
        || v.get("mode").and_then(Value::as_str) != Some("response_only") {
        return Err(fail("Unexpected V2 gateway authority"));
    }
    Ok(())
}

#[tauri::command]
pub fn v2_enrolled() -> bool {
    credential().is_ok()
}

#[tauri::command]
pub fn v2_models() -> Result<Vec<String>, String> {
    let body = get("/v2/models")?;
    verify_mode(&body)?;
    let models = body.get("models").and_then(Value::as_array)
        .ok_or("Missing V2 models")?;
    if models.len() > 32 { return Err(fail("Unbounded V2 models")); }
    models.iter().map(|v| {
        let name = v.as_str().ok_or("Invalid V2 model name")?;
        if name.is_empty() || name.len() > 128 {return Err(fail("Invalid V2 model name"));}
        Ok(name.to_owned())
    }).collect()
}

#[tauri::command]
pub fn v2_create_session() -> Result<String, String> {
    let value = post("/v2/sessions", json!({}), 201)?;
    let sid = value.get("session_id").and_then(Value::as_str)
        .ok_or("Missing server-created session")?;
    if !check_id(sid) {return Err(fail("Invalid server-created session"));}
    Ok(sid.into())
}

#[tauri::command]
pub fn v2_list_sessions() -> Result<Vec<String>, String> {
    let value = get("/v2/sessions")?;
    let items = value.get("sessions").and_then(Value::as_array)
        .ok_or("Missing owner sessions")?;
    if items.len() > 50 {return Err(fail("Unbounded session inventory"));}
    items.iter().map(|v| {
        let id = v.as_str().ok_or("Invalid session list")?;
        if !check_id(id) {return Err(fail("Invalid V2 session ID"));}
        Ok(id.to_owned())
    }).collect()
}

#[tauri::command]
pub fn v2_history(session_id: String) -> Result<Vec<Value>, String> {
    if !check_id(&session_id) {return Err(fail("Invalid V2 session ID"));}
    let value = get(&format!("/v2/sessions/{session_id}/history"))?;
    if value.get("session_id").and_then(Value::as_str) != Some(session_id.as_str()) {
        return Err(fail("V2 history session mismatch"));
    }
    let turns = value.get("turns").and_then(Value::as_array)
        .ok_or("Missing conversation turns")?;
    if turns.len() > 20 {return Err(fail("Unbounded history"));}
    for entry in turns {
        for key in ["user", "assistant", "model"] {
            let text = entry.get(key).and_then(Value::as_str).ok_or("Malformed history turn")?;
            if text.is_empty() || text.len() > 16000 {
                return Err(fail("Invalid history item"));
            }
        }
    }
    Ok(turns.clone())
}

#[tauri::command]
pub fn v2_chat(model: String, session_id: String, request_id: String,
    content: String) -> Result<String, String> {
    if model.is_empty() || model.len() > 128 || !check_id(&session_id)
        || !check_id(&request_id) || content.is_empty()
        || content.chars().count() > 4096 {
        return Err(fail("Invalid V2 bounded request"));
    }
    let reply = post("/v2/chat", json!({"model":model,"session_id":session_id,
                                     "request_id":request_id,"content":content}), 200)?;
    verify_mode(&reply)?;
    if reply.get("model").and_then(Value::as_str) != Some(model.as_str()) {
        return Err(fail("V2 response model mismatch"));
    }
    let text = reply.get("reply").and_then(Value::as_str)
        .ok_or("V2 reply missing")?;
    if text.is_empty() || text.len() > 16000 {return Err(fail("Invalid V2 reply"));}
    Ok(text.into())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn ids_are_strict() {
        assert!(check_id("abcdef0123456789"));
        assert!(!check_id("bad"));
        assert!(!check_id("../../0123456789abcdef"));
    }
    #[test] fn response_authority_required() {
        assert!(verify_mode(&json!({"node":"local","mode":"response_only"})).is_ok());
        assert!(verify_mode(&json!({"node":"remote","mode":"response_only"})).is_err());
    }
}
