#!/usr/bin/env python3

# Wallbox Server - App + Reev Proxy

# Start: PYTHONPATH=/root/packages python3 wallbox.py

# Dann: http://192.168.178.50:8001

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx, uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[”*”], allow_methods=[”*”], allow_headers=[”*”])

HTML = “””<!DOCTYPE html>

<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Wallbox">
  <meta name="theme-color" content="#060810">
  <title>Wallbox</title>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #060810; --card: #0d1120; --yellow: #f5c400;
      --green: #00c853; --red: #ff3d3d; --text: #f0f4ff;
      --muted: #4a5568; --border: rgba(245,196,0,0.12);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    body { background: var(--bg); color: var(--text); font-family: 'Outfit', sans-serif; min-height: 100vh; }
    .app { max-width: 390px; margin: 0 auto; padding: 0 20px 50px; }
    header { padding: 56px 0 32px; animation: fadeUp 0.5s 0.1s both; }
    .header-tag { font-size: 11px; font-weight: 600; letter-spacing: 0.25em; color: var(--yellow); text-transform: uppercase; margin-bottom: 6px; }
    .header-title { font-family: 'Bebas Neue', sans-serif; font-size: 48px; letter-spacing: 0.04em; color: #fff; line-height: 1; }
    .header-sub { font-size: 13px; color: var(--muted); margin-top: 6px; }
    .input-group { margin-bottom: 12px; }
    .input-group label { font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px; }
    .input-field { width: 100%; background: var(--card); border: 1px solid var(--border); border-radius: 12px; color: var(--text); font-family: 'Outfit', sans-serif; font-size: 16px; padding: 14px 16px; outline: none; transition: border-color 0.2s; }
    .input-field:focus { border-color: var(--yellow); }
    .login-btn { width: 100%; background: var(--yellow); border: none; border-radius: 14px; color: #000; font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 700; padding: 18px; cursor: pointer; margin-top: 8px; }
    .login-btn:active { filter: brightness(0.9); }
    .login-error { background: rgba(255,61,61,0.1); border: 1px solid rgba(255,61,61,0.3); border-radius: 10px; padding: 12px 16px; font-size: 13px; color: var(--red); margin-top: 12px; display: none; }
    #mainScreen { display: none; }
    .user-bar { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
    .logout-btn { background: none; border: 1px solid rgba(255,61,61,0.3); border-radius: 8px; color: var(--red); font-size: 12px; font-family: 'Outfit', sans-serif; padding: 6px 12px; cursor: pointer; }
    .section-label { font-size: 10px; font-weight: 700; letter-spacing: 0.2em; color: var(--muted); text-transform: uppercase; margin-bottom: 14px; }
    .stations-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 14px; }
    .station-btn { background: var(--card); border: 1px solid var(--border); border-radius: 18px; padding: 24px 8px 20px; cursor: pointer; text-align: center; transition: all 0.12s; opacity: 0; animation: fadeUp 0.4s forwards; }
    .station-btn:nth-child(1){animation-delay:0.3s} .station-btn:nth-child(2){animation-delay:0.35s} .station-btn:nth-child(3){animation-delay:0.4s}
    .station-btn:nth-child(4){animation-delay:0.45s} .station-btn:nth-child(5){animation-delay:0.5s} .station-btn:nth-child(6){animation-delay:0.55s}
    .station-btn:active { transform: scale(0.91); }
    .station-btn.selected { border-color: var(--yellow); background: rgba(245,196,0,0.07); }
    .station-num { font-family: 'Bebas Neue', sans-serif; font-size: 46px; line-height: 1; color: var(--text); display: block; transition: color 0.2s; }
    .station-btn.selected .station-num { color: var(--yellow); }
    .station-tag { font-size: 9px; font-weight: 600; letter-spacing: 0.12em; color: var(--muted); text-transform: uppercase; display: block; margin-top: 4px; }
    .status-box { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; margin-bottom: 12px; display: none; align-items: center; gap: 12px; }
    .status-box.visible { display: flex; }
    .status-box.success { border-color: rgba(0,200,83,0.4); }
    .status-box.error { border-color: rgba(255,61,61,0.4); }
    .status-box.loading { border-color: rgba(245,196,0,0.4); }
    .status-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
    .status-box.success .status-dot { background: var(--green); box-shadow: 0 0 8px var(--green); }
    .status-box.error .status-dot { background: var(--red); }
    .status-box.loading .status-dot { background: var(--yellow); animation: blink 1s infinite; }
    .status-text { font-size: 14px; font-weight: 500; }
    .status-box.success .status-text { color: var(--green); }
    .status-box.error .status-text { color: var(--red); }
    .status-box.loading .status-text { color: var(--yellow); }
    .start-btn { width: 100%; background: var(--yellow); border: none; border-radius: 18px; color: #000; font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 700; padding: 22px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; animation: fadeUp 0.5s 0.6s both; }
    .start-btn:disabled { background: #2a2a2a; color: var(--muted); cursor: not-allowed; }
    .start-btn:not(:disabled):active { transform: scale(0.97); filter: brightness(0.9); }
    .start-btn svg { width: 22px; height: 22px; }
    .spinner { width: 20px; height: 20px; border: 2px solid rgba(0,0,0,0.2); border-top-color: #000; border-radius: 50%; animation: spin 0.7s linear infinite; display: none; }
    .start-btn.loading .spinner { display: block; }
    .start-btn.loading .btn-text, .start-btn.loading svg { display: none; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
    @keyframes fadeUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
  </style>
</head>
<body>
<div class="app">
  <header>
    <div class="header-tag">Langen CNC · Wallbox</div>
    <div class="header-title">Ladestation</div>
    <div class="header-sub" id="headerSub">Bitte einloggen</div>
  </header>

  <div id="loginScreen">
    <div class="section-label">Reev Login</div>
    <div class="input-group">
      <label>E-Mail</label>
      <input type="email" class="input-field" id="email" placeholder="deine@email.de" autocomplete="email">
    </div>
    <div class="input-group">
      <label>Passwort</label>
      <input type="password" class="input-field" id="password" placeholder="••••••••" autocomplete="current-password">
    </div>
    <button class="login-btn" onclick="doLogin()">Einloggen</button>
    <div class="login-error" id="loginError"></div>
  </div>

  <div id="mainScreen">
    <div class="user-bar">
      <div style="font-size:13px;color:var(--muted)">✓ Eingeloggt</div>
      <button class="logout-btn" onclick="doLogout()">Ausloggen</button>
    </div>
    <div class="section-label">Station wählen & Laden starten</div>
    <div class="stations-grid" id="stationsGrid"></div>
    <div class="status-box" id="statusBox">
      <div class="status-dot"></div>
      <div class="status-text" id="statusText"></div>
    </div>
    <button class="start-btn" id="startBtn" onclick="startCharging()" disabled>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
      <span class="btn-text">Station wählen</span>
      <div class="spinner"></div>
    </button>
  </div>
</div>

<script>
const BASE = window.location.origin;
const TOKEN_URL = BASE + "/auth/realms/reev/protocol/openid-connect/token";
const API_URL = BASE;

const STATIONS = [
  {num:1,code:"E6583"},{num:2,code:"E5SQZ"},{num:3,code:"EK2TL"},
  {num:4,code:"EU7UW"},{num:5,code:"E2UR9"},{num:6,code:"EQZ6Y"}
];

let accessToken=null, refreshToken=null, selectedStation=null, selectedBtn=null;

function init() {
  const saved = localStorage.getItem("reev_tokens");
  if (saved) { const t=JSON.parse(saved); accessToken=t.access; refreshToken=t.refresh; showMain(); }
  else showLogin();
  buildStations();
}

function showLogin() {
  document.getElementById("loginScreen").style.display="block";
  document.getElementById("mainScreen").style.display="none";
  document.getElementById("headerSub").textContent="Bitte einloggen";
}

function showMain() {
  document.getElementById("loginScreen").style.display="none";
  document.getElementById("mainScreen").style.display="block";
  document.getElementById("headerSub").textContent="Station wählen → Laden starten";
}

async function doLogin() {
  const email=document.getElementById("email").value.trim();
  const password=document.getElementById("password").value;
  const errEl=document.getElementById("loginError");
  const btn=document.querySelector(".login-btn");
  if (!email||!password) { showLoginError("Bitte E-Mail und Passwort eingeben"); return; }
  btn.textContent="Wird eingeloggt..."; btn.disabled=true; errEl.style.display="none";
  try {
    const res=await fetch(TOKEN_URL,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
      body:new URLSearchParams({grant_type:"password",client_id:"reev-mobile",username:email,password,scope:"openid"})});
    const data=await res.json();
    if (data.access_token) {
      accessToken=data.access_token; refreshToken=data.refresh_token;
      localStorage.setItem("reev_tokens",JSON.stringify({access:accessToken,refresh:refreshToken}));
      showMain();
    } else { showLoginError("Login fehlgeschlagen – E-Mail oder Passwort falsch"); }
  } catch(e) { showLoginError("Verbindungsfehler"); }
  btn.textContent="Einloggen"; btn.disabled=false;
}

function showLoginError(msg) { const el=document.getElementById("loginError"); el.textContent=msg; el.style.display="block"; }

function doLogout() {
  accessToken=refreshToken=selectedStation=null;
  localStorage.removeItem("reev_tokens");
  showLogin();
}

function buildStations() {
  const grid=document.getElementById("stationsGrid");
  STATIONS.forEach(s=>{
    const btn=document.createElement("button");
    btn.className="station-btn";
    btn.innerHTML=`<span class="station-num">${s.num}</span><span class="station-tag">Station</span>`;
    btn.onclick=()=>selectStation(s,btn);
    grid.appendChild(btn);
  });
}

function selectStation(station,btn) {
  selectedStation=station;
  if (selectedBtn) selectedBtn.classList.remove("selected");
  btn.classList.add("selected"); selectedBtn=btn;
  const sb=document.getElementById("startBtn");
  sb.disabled=false;
  sb.querySelector(".btn-text").textContent=`Station ${station.num} laden starten`;
  setStatus("","");
}

async function startCharging() {
  if (!selectedStation) return;
  const btn=document.getElementById("startBtn");
  btn.classList.add("loading"); btn.disabled=true;
  setStatus("Verbinde mit Ladestation...","loading");
  try {
    const accountRes=await fetch(`${API_URL}/api/app/invoicing-account/by-evse-id/${selectedStation.code}`,
      {headers:{"Authorization":`Bearer ${accessToken}`}});
    if (accountRes.status===401) {
      const ok=await doRefresh();
      if (!ok) { doLogout(); return; }
      btn.classList.remove("loading"); btn.disabled=false;
      await startCharging(); return;
    }
    const accountData=await accountRes.json();
    const customerId=accountData?.id||accountData?.customerId;
    if (!customerId) { setStatus("Ladestation nicht gefunden","error"); btn.classList.remove("loading"); btn.disabled=false; return; }
    const startRes=await fetch(`${API_URL}/api/app/transactions/start?customerId=${customerId}`,
      {method:"POST",headers:{"Authorization":`Bearer ${accessToken}`,"Content-Type":"application/json"},
       body:JSON.stringify({evseId:selectedStation.code})});
    if (startRes.ok) {
      setStatus(`⚡ Station ${selectedStation.num} lädt!`,"success");
      btn.querySelector(".btn-text").textContent="Laden läuft ✓";
    } else {
      const err=await startRes.json().catch(()=>({}));
      setStatus(err.message||"Fehler beim Starten","error");
      btn.querySelector(".btn-text").textContent=`Station ${selectedStation.num} laden starten`;
      btn.disabled=false;
    }
  } catch(e) {
    setStatus("Verbindungsfehler","error");
    btn.querySelector(".btn-text").textContent=`Station ${selectedStation.num} laden starten`;
    btn.disabled=false;
  }
  btn.classList.remove("loading");
}

async function doRefresh() {
  try {
    const res=await fetch(TOKEN_URL,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
      body:new URLSearchParams({grant_type:"refresh_token",client_id:"reev-mobile",refresh_token:refreshToken})});
    const data=await res.json();
    if (data.access_token) {
      accessToken=data.access_token; refreshToken=data.refresh_token;
      localStorage.setItem("reev_tokens",JSON.stringify({access:accessToken,refresh:refreshToken}));
      return true;
    }
  } catch(e) {}
  return false;
}

function setStatus(msg,type) {
  const box=document.getElementById("statusBox");
  if (!msg) { box.classList.remove("visible"); return; }
  box.className=`status-box visible ${type}`;
  document.getElementById("statusText").textContent=msg;
}

document.addEventListener("DOMContentLoaded",()=>{
  init();
  document.getElementById("password")?.addEventListener("keydown",e=>{ if(e.key==="Enter") doLogin(); });
});
</script>

</body>
</html>"""

@app.get(”/”, response_class=HTMLResponse)
async def serve_app():
return HTML

@app.api_route(”/auth/{path:path}”, methods=[“GET”,“POST”,“PUT”,“DELETE”])
async def proxy_auth(path: str, request: Request):
return await forward(request, f”https://auth.reev.com/{path}”)

@app.api_route(”/api/{path:path}”, methods=[“GET”,“POST”,“PUT”,“DELETE”])
async def proxy_api(path: str, request: Request):
return await forward(request, f”https://api.reev.com/api/{path}”)

async def forward(request: Request, url: str):
headers = {k:v for k,v in request.headers.items() if k.lower() not in [“host”,“content-length”]}
params = dict(request.query_params)
body = await request.body()
async with httpx.AsyncClient(timeout=30) as c:
r = await c.request(request.method, url, headers=headers, content=body, params=params)
return Response(content=r.content, status_code=r.status_code,
media_type=r.headers.get(“content-type”,“application/json”))

if **name** == “**main**”:
print(“🔌 Wallbox Server läuft auf http://0.0.0.0:8001”)
uvicorn.run(app, host=“0.0.0.0”, port=8001)
