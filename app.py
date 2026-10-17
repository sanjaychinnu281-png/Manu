# ==================== bg OFFICIAL — BR + LW | IND FORCED | HUMAN MODE ====================
import sys
import asyncio
import httpx
import random
import json
import socket
import struct
import time
import os
import uuid
import itertools
import secrets
import traceback
import base64
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from aiohttp import web

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass

from google_play_scraper import app as play_scraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from protobuf_decoder.protobuf_decoder import Parser
from message_ids import MESSAGE_ID_TO_NAME
import bashant_pb2, BGFF_pb2, thunderFF_pb2

# ==================== CONFIG ====================
WEB_HOST = "0.0.0.0"
WEB_PORT = int(os.environ.get("PORT", 8080))
ACCOUNTS_FILE, TOKEN_CACHE_FILE, DEVICES_FILE = "accounts.json", "token_cache.json", "devices.json"
TOKEN_CACHE_TTL = 1200
START_MATCH_INTERVAL_MIN, START_MATCH_INTERVAL_MAX, START_MATCH_INTERVAL = 4.0, 8.0, 10.0
NEW_MATCH_DELAY, MAX_MATCH_DURATION, MATCH_IDLE_TIMEOUT = 6.0, 800, 20.0
MAX_CONCURRENT_MATCHES, HUMAN_MODE = 1, True
FORCE_REGION = "IND"
MAX_CONSECUTIVE_PARSE_FAILURES, NON_MATCH_RECONNECT_DELAY = 5.0, 1.0
LOGIN_CONCURRENCY, LOGIN_VERSION_CACHE_TTL = 5, 120.0
_LOGIN_SEMAPHORE = asyncio.Semaphore(LOGIN_CONCURRENCY)
_VERSION_CONFIG_CACHE, _VERSION_CONFIG_CACHE_AT = None, 0.0
_VERSION_CONFIG_LOCK, _REFRESH_SEMAPHORE = asyncio.Lock(), asyncio.Semaphore(3)

HTML_CONTENT = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>TEAM NONE | Bot Dashboard</title><link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=JetBrains+Mono&display=swap" rel="stylesheet"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>:root{--bg:#060913;--card:rgba(13,19,36,.75);--bd:rgba(0,242,254,.12);--cy:#00f2fe;--gr:#00ff88;--tx:#f0f4fc;--mt:#8e9bb5}*{box-sizing:border-box;margin:0;padding:0;font-family:'Outfit',sans-serif}body{background:var(--bg);color:var(--tx);min-height:100vh;padding:24px}.container{max-width:1440px;margin:0 auto}header{display:flex;justify-content:space-between;padding:20px 28px;background:var(--card);border:1px solid var(--bd);border-radius:20px;margin-bottom:24px}.brand{display:flex;gap:16px}.logo{width:48px;height:48px;background:linear-gradient(135deg,var(--cy),#4facfe);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;color:#fff}.brand h1{font-size:22px;font-weight:800;color:#fff}.brand p{font-size:13px;color:var(--mt);display:flex;align-items:center;gap:8px}.tag{background:rgba(0,255,136,.12);color:var(--gr);padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}.dot{width:7px;height:7px;background:var(--gr);border-radius:50%;animation:blink 1s infinite}@keyframes blink{50%{opacity:.4}}.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:12px;font-size:14px;font-weight:600;cursor:pointer;border:none;color:#fff;transition:.2s}.btn-p{background:linear-gradient(135deg,#4facfe,var(--cy));color:#040914}.btn-s{background:rgba(255,255,255,.05);border:1px solid var(--bd)}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;margin-bottom:24px}.stat{background:var(--card);border:1px solid var(--bd);border-radius:18px;padding:20px;display:flex;gap:18px}.ico{width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px}.ico-c{background:rgba(0,242,254,.15);color:var(--cy)}.ico-g{background:rgba(0,255,136,.15);color:var(--gr)}.stat h3{font-size:26px;font-weight:800;color:#fff}.stat p{font-size:13px;color:var(--mt)}.main{display:grid;grid-template-columns:2fr 1fr;gap:24px}@media(max-width:1024px){.main{grid-template-columns:1fr}}.box{background:var(--card);border:1px solid var(--bd);border-radius:20px;padding:24px}.box-h{display:flex;justify-content:space-between;margin-bottom:20px}.box-t{font-size:18px;font-weight:700;display:flex;gap:10px}.list{display:flex;flex-direction:column;gap:16px}.acc{background:rgba(10,15,30,.65);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:20px}.acc-t{display:flex;justify-content:space-between;margin-bottom:14px}.prof{display:flex;gap:14px}.av{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#1e293b,#334155);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--cy)}.info h4{font-size:16px;font-weight:700;color:#fff}.info span{font-size:12px;color:var(--mt);font-family:'JetBrains Mono',monospace}.st{display:flex;gap:6px;font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;background:rgba(0,255,136,.12);color:var(--gr)}.logs{flex:1;min-height:480px;background:#03060f;border:1px solid rgba(255,255,255,.05);border-radius:14px;padding:14px;font-family:'JetBrains Mono',monospace;font-size:12px;overflow-y:auto;display:flex;flex-direction:column;gap:8px}.li{line-height:1.4;word-break:break-all}.lt{color:#64748b;margin-right:6px}.l-i{color:#38bdf8}.l-s{color:#4ade80}.l-e{color:#f87171}.mod{position:fixed;inset:0;background:rgba(3,6,15,.82);backdrop-filter:blur(8px);display:none;align-items:center;justify-content:center;z-index:100}.mod.act{display:flex}.mc{background:#0c1224;border:1px solid var(--bd);border-radius:20px;width:100%;max-width:480px;padding:28px}.mh{display:flex;justify-content:space-between;margin-bottom:20px}.fg{margin-bottom:16px}.fg label{display:block;font-size:13px;font-weight:600;color:var(--mt);margin-bottom:6px}.fi{width:100%;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:10px 14px;color:#fff;outline:none}.emp{text-align:center;padding:40px 20px;color:var(--mt)}</style></head><body><div class="container"><header><div class="brand"><div class="logo"><i class="fa-solid fa-bolt"></i></div><div><h1>ANGRY_FF | LEVEL UP BOT</h1><p><span class="tag"><span class="dot"></span> System Live</span></p></div></div><div><button class="btn btn-s" onclick="fetchStats()"><i class="fa-solid fa-rotate"></i> Refresh</button><button class="btn btn-p" onclick="document.getElementById('add-modal').classList.add('act')"><i class="fa-solid fa-plus"></i> Add Account</button></div></header><div class="stats"><div class="stat"><div class="ico ico-c"><i class="fa-solid fa-users"></i></div><div><h3 id="s-acc">0</h3><p>Active Accounts</p></div></div><div class="stat"><div class="ico ico-g"><i class="fa-solid fa-angles-up"></i></div><div><h3 id="s-exp" style="color:var(--gr)">+0 EXP</h3><p>Total EXP Gained</p></div></div></div><div class="main"><div class="box"><div class="box-h"><div class="box-t"><i class="fa-solid fa-user-astronaut" style="color:var(--cy)"></i><span>Live Accounts</span></div></div><div class="list" id="acc-cont"><div class="emp"><p>Loading active accounts...</p></div></div></div><div class="box"><div class="box-h"><div class="box-t"><i class="fa-solid fa-terminal" style="color:var(--gr)"></i><span>Live Logs</span></div></div><div class="logs" id="log-cont"></div></div></div></div><div class="mod" id="add-modal"><div class="mc"><div class="mh"><h3>Add New Account</h3><button class="btn" onclick="document.getElementById('add-modal').classList.remove('act')"><i class="fa-solid fa-xmark"></i></button></div><form id="add-form" onsubmit="subAdd(event)"><div class="fg"><label>Account Type</label><select class="fi" id="acc-type" onchange="document.getElementById('gf').style.display=this.value==='guest'?'block':'none';document.getElementById('tf').style.display=this.value==='token'?'block':'none';"><option value="guest">Guest (UID + Password)</option><option value="token">Access Token</option></select></div><div id="gf"><div class="fg"><label>Guest UID</label><input type="text" class="fi" id="acc-uid" placeholder="e.g. 7644913583"></div><div class="fg"><label>Guest Password</label><input type="text" class="fi" id="acc-password" placeholder="Password"></div></div><div id="tf" style="display:none;"><div class="fg"><label>Access Token</label><textarea class="fi" id="acc-token" rows="3"></textarea></div></div><div style="display:flex;justify-content:flex-end;gap:10px;margin-top:20px;"><button type="button" class="btn btn-s" onclick="document.getElementById('add-modal').classList.remove('act')">Cancel</button><button type="submit" class="btn btn-p">Save & Start</button></div></form></div></div><script>async function subAdd(e){e.preventDefault();const t=document.getElementById('acc-type').value;let p={};if(t==='guest'){p={uid:document.getElementById('acc-uid').value.trim(),password:document.getElementById('acc-password').value.trim()}}else{p={token:document.getElementById('acc-token').value.trim()}}try{const r=await fetch('/api/account/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});const d=await r.json();if(d.status==='ok'){document.getElementById('add-modal').classList.remove('act');fetchStats()}else{alert('Error: '+d.error)}}catch(e){alert('Failed: '+e)}}async function fetchStats(){try{const r=await fetch('/api/stats');const d=await r.json();document.getElementById('s-acc').innerText=d.total_accounts;document.getElementById('s-exp').innerText='+'+d.total_gained_exp.toLocaleString()+' EXP';const c=document.getElementById('acc-cont');if(d.accounts.length===0){c.innerHTML='<div class="emp"><p>No active accounts. Click "+ Add Account" to start!</p></div>'}else{c.innerHTML=d.accounts.map(a=>`<div class="acc"><div class="acc-t"><div class="prof"><div class="av"><i class="fa-solid fa-user"></i></div><div class="info"><h4>${a.nickname}</h4><span>UID: ${a.uid}</span></div></div><div class="st"><span class="dot"></span><span>${a.status}</span></div></div></div>`).join('')}const l=document.getElementById('log-cont');l.innerHTML=d.logs.map(x=>`<div class="li"><span class="lt">[${x.time}]</span><span class="l-${x.level}">${x.message}</span></div>`).join('');l.scrollTop=l.scrollHeight}catch(e){}}fetchStats();setInterval(fetchStats,2500);</script></body></html>"""

# ==================== STATE & LOGGING ====================
class Colors: GREEN, FAIL, WARNING, CYAN, MAGENTA, WHITE, ENDC = '\033[92m', '\033[91m', '\033[93m', '\033[96m', '\033[95m', '\033[97m', '\033[0m'

class BotState:
    def __init__(self):
        self.accounts, self.account_workers, self.account_credentials, self.logs, self.refresh_callbacks = {}, {}, {}, [], {}
    def log(self, message, level="info"):
        t = datetime.now().strftime("%H:%M:%S")
        self.logs.append((t, message, level))
        if len(self.logs) > 200: self.logs.pop(0)
        print(f"{Colors.GREEN if level=='success' else (Colors.FAIL if level=='error' else Colors.CYAN)}[ {t} ] {message}{Colors.ENDC}")
    def register_account(self, uid, nickname, region, level, exp, likes):
        if uid not in self.accounts: self.accounts[uid] = {"nickname": nickname, "region": region, "level": level, "initial_exp": exp, "current_exp": exp, "gained_exp": 0, "likes": likes, "matches_played": 0, "status": "ONLINE"}
    def update_status(self, uid, status, active_count=0):
        if uid in self.accounts: self.accounts[uid]["status"] = status
    def update_exp(self, uid, current_exp, level):
        if uid in self.accounts: self.accounts[uid].update({"current_exp": current_exp, "level": level, "gained_exp": current_exp - self.accounts[uid]["initial_exp"]})
    def increment_match(self, uid):
        if uid in self.accounts: self.accounts[uid]["matches_played"] += 1
    def match_failed(self, uid): pass
    def is_paused(self, uid): return False
    def get_account_mode(self, uid): return "BR"

bot_state = BotState()

async def start_html_server():
    app = web.Application()
    async def idx(req): return web.Response(text=HTML_CONTENT, content_type='text/html')
    async def stats(req):
        try:
            accs = [{"uid": u, "nickname": a.get("nickname"), "status": a.get("status")} for u, a in bot_state.accounts.items()]
            logs = [{"time": l[0], "message": l[1], "level": l[2]} for l in reversed(bot_state.logs[-50:])]
            return web.json_response({"total_accounts": len(bot_state.accounts), "total_gained_exp": sum(a.get("gained_exp", 0) for a in bot_state.accounts.values()), "accounts": accs, "logs": logs})
        except Exception as e: return web.json_response({"error": str(e)}, status=500)
    async def add(req):
        try:
            d = await req.json()
            if "on_account_added" in bot_state.refresh_callbacks: await bot_state.refresh_callbacks["on_account_added"](d)
            return web.json_response({"status": "ok"})
        except Exception as e: return web.json_response({"status": "error", "error": str(e)}, status=500)
    app.router.add_get('/', idx)
    app.router.add_get('/api/stats', stats)
    app.router.add_post('/api/account/add', add)
    runner = web.AppRunner(app); await runner.setup(); await web.TCPSite(runner, WEB_HOST, WEB_PORT).start()
    print(f"[ SYSTEM ] Dashboard LIVE on {WEB_PORT}")

# ==================== ENGINE HELPERS ====================
async def human_delay(base=1.0, variance=0.5): return max(0.1, base + random.uniform(-variance, variance))
async def human_jitter(): return random.uniform(0.05, 0.35)

def get_device_for_account(account_identifier: str) -> dict:
    devices = {}
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, "r", encoding="utf-8") as f: devices = json.load(f)
        except: pass
    acc_key = str(account_identifier)
    if acc_key in devices: return devices[acc_key]
    brand, model, gpu, os_ver = random.choice([("Samsung", "SM-G998B", "Adreno (TM) 660", "Android OS 12 / API-31"), ("Xiaomi", "2201122G", "Adreno (TM) 730", "Android OS 13 / API-33"), ("Realme", "RMX3700", "Mali-G710", "Android OS 14 / API-34")])
    new_device = {"unique_device_id": f"Google|{str(uuid.uuid4())}", "brand": brand, "model": model, "gpu_renderer": gpu, "system_software": os_ver, "screen_width": 1080, "screen_height": 2400, "screen_dpi": "420", "memory": 6500, "processor_details": "ARM64 FP ASIMD AES VMH | 2800 | 8", "client_ip": f"{random.randint(103, 223)}.{random.randint(10, 250)}.{random.randint(10, 250)}.{random.randint(10, 250)}", "android_id": secrets.token_hex(8), "gsf_id": secrets.token_hex(8), "build_fingerprint": f"{brand.lower()}/{model.lower()}/{model.lower()}:{os_ver.split(' / ')[0].replace(' ', '_')}/user/release-keys", "serial_number": secrets.token_hex(8), "hardware_id": secrets.token_hex(8)}
    devices[acc_key] = new_device
    try:
        with open(DEVICES_FILE, "w", encoding="utf-8") as f: json.dump(devices, f, indent=4)
    except: pass
    return new_device

_DNS_CACHE: Dict[str, Tuple[str, float]] = {}
async def resolve_host_cloudflare(hostname: str) -> str:
    if not hostname: return hostname
    parts = hostname.split('.')
    if len(parts) == 4 and all(p.isdigit() for p in parts): return hostname
    now = time.time()
    if hostname in _DNS_CACHE and now < _DNS_CACHE[hostname][1]: return _DNS_CACHE[hostname][0]
    def _query(server_ip):
        s = None
        try:
            tx_id = random.randint(1000, 65535)
            header = struct.pack(">HHHHHH", tx_id, 0x0100, 1, 0, 0, 0)
            qname = b"".join(bytes([len(p)]) + p.encode('ascii') for p in hostname.split('.')) + b"\x00"
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(1.2)
            s.sendto(header + qname + struct.pack(">HH", 1, 1), (server_ip, 53))
            resp, _ = s.recvfrom(1024)
            if len(resp) >= 12:
                offset = 12 + len(qname) + 4
                for _ in range(struct.unpack(">H", resp[6:8])[0]):
                    if offset >= len(resp): break
                    if (resp[offset] & 0xC0) == 0xC0: offset += 2
                    else:
                        while offset < len(resp) and resp[offset] != 0: offset += 1 + resp[offset]
                        offset += 1
                    if offset + 10 > len(resp): break
                    rtype, rclass, ttl, rdlen = struct.unpack(">HHIH", resp[offset:offset+10]); offset += 10
                    if rtype == 1 and rdlen == 4: return socket.inet_ntoa(resp[offset:offset+4])
                    offset += rdlen
        except: pass
        finally:
            if s:
                try: s.close()
                except: pass
        return None
    loop = asyncio.get_running_loop()
    ip = await loop.run_in_executor(None, _query, "1.1.1.1")
    if ip: _DNS_CACHE[hostname] = (ip, now + 300.0)
    return ip or hostname

def optimize_tcp_socket(sock):
    try: sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1); sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    except: pass
def optimize_udp_socket(sock):
    try: sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072); sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
    except: pass

client = httpx.AsyncClient(verify=False, timeout=10.0)
headers = {'User-Agent': 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)', 'Connection': 'Keep-Alive', 'Content-Type': 'application/x-www-form-urlencoded', 'X-Unity-Version': '2018.4.12f1'}
AES_KEY, AES_IV = b'Yg&tc%DEuh6%Zc^8', b'6oyZDr22E3ychjM%'
async def aes_encrypt(payload, key, iv): return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(payload, AES.block_size))
async def get_playstore_version():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: play_scraper('com.dts.freefireth', lang='hi', country='id'))
    return result.get("version")

async def version_config():
    global _VERSION_CONFIG_CACHE, _VERSION_CONFIG_CACHE_AT
    now = time.monotonic()
    if _VERSION_CONFIG_CACHE and (now - _VERSION_CONFIG_CACHE_AT) < LOGIN_VERSION_CACHE_TTL: return _VERSION_CONFIG_CACHE
    async with _VERSION_CONFIG_LOCK:
        now = time.monotonic()
        if _VERSION_CONFIG_CACHE and (now - _VERSION_CONFIG_CACHE_AT) < LOGIN_VERSION_CACHE_TTL: return _VERSION_CONFIG_CACHE
        app_version = await get_playstore_version()
        api_url = f"https://version.ggwhitehawk.com/live/ver.php?version={app_version}&lang=hi&device=android&channel=android&appstore=googleplay&region=ID&whitelist_version=1.3.0&whitelist_sp_version=1.0.0"
        try:
            response = await client.get(api_url); response.raise_for_status(); data = response.json()
            server_url, remote_version, latest_release_version = data.get("server_url"), data.get("remote_version"), data.get("latest_release_version")
            if not server_url or not remote_version or not latest_release_version: return None
            _VERSION_CONFIG_CACHE = (latest_release_version, remote_version, server_url); _VERSION_CONFIG_CACHE_AT = time.monotonic()
            return _VERSION_CONFIG_CACHE
        except: return None

async def get_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    hdrs = {"Host": "100067.connect.garena.com", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B Build/SP1A.210812.016)", "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip, deflate, br", "Connection": "close"}
    data = {"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3", "client_id": "100067"}
    for attempt in range(5):
        try:
            response = await client.post(url, headers=hdrs, data=data)
            if response.status_code == 200:
                d = response.json()
                if d.get("open_id") and d.get("access_token"): return d.get("open_id"), d.get("access_token"), d.get("platform", 4)
            if response.status_code == 429: await asyncio.sleep(1); continue
        except: pass
        await asyncio.sleep(0.5)
    return None

def encode_varint(n):
    if n < 0: return b''
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

def build_proto(fields):
    parts = []
    for k, v in fields.items():
        if isinstance(v, dict):
            nested = build_proto(v); parts.append(encode_varint((k << 3) | 2) + encode_varint(len(nested)) + nested)
        elif isinstance(v, int): parts.append(encode_varint((k << 3) | 0) + encode_varint(v))
        elif isinstance(v, (str, bytes)):
            ev = v.encode() if isinstance(v, str) else v
            parts.append(encode_varint((k << 3) | 2) + encode_varint(len(ev)) + ev)
    return b''.join(parts)

def encrypt_api_bytes(plain_bytes): return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(plain_bytes, AES.block_size))

async def build_majorlogin_payload(open_id, access_token, platform, client_version, device_info):
    try:
        p = {3: str(datetime.now())[:-7], 4: "free fire", 5: "1", 7: str(client_version) if client_version else "1.132.8", 8: str(device_info.get("system_software", "Android OS 15 / API-35")), 9: "Handheld", 10: "Airtel", 11: "CarrierDataNetwork", 12: str(device_info.get("screen_width", 1639)), 13: str(device_info.get("screen_height", 720)), 14: str(device_info.get("screen_dpi", 320)), 15: str(device_info.get("processor_details", "ARM64 FP ASIMD AES | 2000 | 8")), 16: str(device_info.get("memory", 5653)), 17: str(device_info.get("gpu_renderer", "Mali-G52 MC2")), 18: "OpenGL ES 3.2 v1.r49p1-03bet0.19498e0ae1d5dac223383c39a2e58f04", 19: str(device_info.get("unique_device_id", f"Google|{uuid.uuid4()}")), 20: str(device_info.get("client_ip", "182.5.135.225")), 21: "en", 22: str(open_id), 23: str(platform), 24: "Handheld", 25: str(device_info.get("model", "Xiaomi 2409BRN2CY")), 26: "IND", 29: str(access_token), 30: "1", 41: "Airtel", 42: "4G", 57: "7428b253defc164018c604a1ebbfebdf", 60: "109278", 61: "55402", 62: "868", 64: "55927", 65: "109278", 66: "55927", 67: "109278", 73: "2", 74: "/data/app/~~6Cw028g_ld-8Z0z2qhrOLA==/com.dts.freefireth-i3wiaEmpx8CbiRVhUMx_ag==/lib/arm64", 76: "1", 77: "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~6Cw028g_ld-8Z0z2qhrOLA==/com.dts.freefireth-i3wiaEmpx8CbiRVhUMx_ag==/base.apk", 78: "3", 79: "2", 81: "64", 83: "2019121229", 85: "3", 86: "OpenGLES2", 87: "8191", 88: str(platform), 90: "Mumbai", 91: "MH", 92: "14466", 93: "android", 94: "KqsHTyb7yHjsAiyNWUUZa0DSOD6U0AhDQ76smAo1WeHHHpSmJ8KMRyRrxb2ttgJqO9YOqO/K6AORAvDMAX/qBS8+JahIkrM7kHfzlfULbgRAoZ9r", 95: "111207", 96: "{\"cur_rate\":[60,90,120],\"support_etc2\":false}", 97: "1", 98: "1", 99: str(platform), 100: str(platform), 102: "D]C\x15\x05T\x0eU3", 103: "1", 104: "52837", 105: "1", 106: "https://dl.gmc.freefiremobile.com/live/ABHotUpdates/|https://core-gmc.freefiremobile.com/live/ABHotUpdates/|211c933168f55902c7dfbfd8c4e2957d", 107: "1.3fb8adbf45f44ce9"}
        return encrypt_api_bytes(build_proto(p))
    except Exception as e: return None

async def send_majorlogin(data, release_version, server_url):
    try:
        res = await client.post(f"{server_url.rstrip('/')}/MajorLogin", headers={**headers, "ReleaseVersion": release_version}, data=data)
        if res.status_code == 200:
            p = bashant_pb2.MajorLoginRes(); p.ParseFromString(res.content)
            if p.region and p.token: return p
            for offset in range(min(128, len(res.content))):
                try:
                    c = bashant_pb2.MajorLoginRes(); c.ParseFromString(res.content[offset:])
                    if c.region and c.token: return c
                except: pass
    except: pass
    return None

async def send_getlogin(data, base_url, token, release_version):
    try:
        res = await client.post(f"{base_url.rstrip('/')}/GetLoginData", headers={**headers, "ReleaseVersion": release_version, "Authorization": f"Bearer {token}"}, data=data)
        if res.status_code == 200:
            p = bashant_pb2.GetLoginDataRes(); p.ParseFromString(res.content)
            return p, {}
    except: pass
    return None

async def build_tcp_startup_packet(account_id, token, server_time, key, iv, region="IND", typ='OnLine'):
    uid_hex = f"{int(account_id):016x}"; ts = f"{int(server_time):08x}"
    enc = (await aes_encrypt(token.encode(), key, iv)).hex(); el = f"{len(enc) // 2:08x}"
    reg = str(region).upper() if region else "IND"
    if typ == 'OnLine': return f"{'7119' if reg == 'ID' else ('7114' if reg == 'IND' else '7115')}{uid_hex}{ts}00000000{el}{enc}"
    return f"{'9219' if reg == 'ID' else ('9214' if reg == 'IND' else '9215')}{uid_hex}{ts}{el}{enc}"

async def send_keep_alive(region="IND"):
    reg = str(region).upper() if region else "IND"
    return bytes.fromhex("0214" if reg in ("IND", "IN") else ("0219" if reg == "ID" else "0215"))

async def start_game_battle_royale(region, client_version, writer, key, iv):
    packet = bytes.fromhex("080112800a0a010110013a110a044944433110aa011a064555524f50453a100a044944433210311a064555524f504540014a0801090a0b1219202758016291090a8001303838463832424630324139363736373032303130313030303030303030303030303136303030313030313530303032323246393745454530463030303030303436373632353134303030303030303030303030303030303030303030303030303030303030303030303030303066663030303030303030636163666131366410241afb02735d5e571400024a775d45414d1a041b1c001f11010449715f4243481a001e1d071c1703004b1a4066785c524570735c51486775421b5c5a4c07504042685a63610816054e19025e75196001477c015165406370195f5547404e4550640103020f1304064863754268676c755f65576e40467e5f0a417a4701026d675d6e73670b1108495a4c6a0b78470b740065645e525a057258425f584a447d4e6759440c11044e7c596d7f4b625f7d04055a47505c4e1d6b5b4107447d7201057d7f0f14084e430457674f7e517d72015172415d027473577c4d615f79535256780911030f4d5e027a797f614165067806505d53777750475e75064257076500460817014e741e7e5078487e7a7c465e7669767153497064605a7376677773550d160148037e18675966787f4c42607a645f577e7b441b460776026b18685d0b110205490060020f70676175654674706671797f41067346677c4e06585e780f15074c57047b40517075415f6364027259674b5b0166407f7340600407770a22047a5d5c52300b3a0a167305067162727516134208312e3133302e3232480350015ae90403626253513635686e556f4e36416456324b796f566c636f477776484f624e56526c4d727073504b4f43654177616848494176795556497273743752737149734a7a786b3247525268377a2f637664626d504f6a73552f79626d38547a4c69586d2f474351696d494b53486833447955726f39515152756c34545350626d6d624b7949565937545671577059455372323646572f59624578507338514f706d317372785455736c30796a434144444d4f34616a654b615753366361496c554b4963797a494e396d52516f715277687939797257476d337a644345337a6a61436f492f5a585233656f65365a42647a64677654636b6b665733356e4d4c6a6a565072564b6433523172756174394e50514150724a5546627859696c4c5a3859707336654d5447666b6649793574666a526c314d4648706b51774c6373374439656378566c41636f374e664f6d2b30654756466c4434744478706771385533595973587645384842502f70666c767a737138316a32524f4d7857437556445442492f684735625462773166456e4249725162762b636144775147696f74554e316d4c4b77734379456f4766706746614251457645672b736a764c4c78704743334c304a5344532f74526169504354553344374e6249306547516651622f5a466f4c36455630775a324d6f583932414c572f5049752f56634663584e70596b356f7966326151416a536971486a2f363276354843644f525551303578754e6171795251625653704654303137655237675255636b4966366c6f447476342b514e4a4670766d74757077707774396a5a5974437a4b56743657726d6e36785837706658456251555434684f3758a201050803108703a201050804108103a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815")
    proto = thunderFF_pb2.StartMatch(); proto.ParseFromString(packet)
    if hasattr(proto.main, 'region_list') and len(proto.main.region_list) > 0:
        proto.main.region_list[0].region = region
        if len(proto.main.region_list) > 1: proto.main.region_list[1].region = region
    if hasattr(proto.main, 'client_version'): proto.main.client_version.remote_version = client_version
    packet = proto.SerializeToString(); enc = (await aes_encrypt(packet, key, iv)).hex(); pl = len(enc) // 2
    hl = hex(pl)[2:]; hl = hl if len(hl) > 1 else "0" + hl
    reg = str(region).upper() if region else "IND"
    final_packet = ("031900" if reg == "BD" else ("031400" if reg == "IND" else "031500")) + "0" * (6 - len(hl)) + hl + enc
    writer.write(bytes.fromhex(final_packet)); await writer.drain()

async def start_game_lone_wolf(region, client_version, writer, key, iv):
    packet = bytes.fromhex("080112800a0a010b102b3a110a044944433110aa011a064555524f50453a100a044944433210311a064555524f504540014a0801090a0b1219202758016291090a8001303838463832424630324139363736373032303130313030303030303030303030303136303030313030313530303032323246393745454530463030303030303436373632353134303030303030303030303030303030303030303030303030303030303030303030303030303066663030303030303030636163666131366410241afb02735d5e571400024a775d45414d1a041b1c001f11010449715f4243481a001e1d071c1703004b1a4066785c524570735c51486775421b5c5a4c07504042685a63610816054e19025e75196001477c015165406370195f5547404e4550640103020f1304064863754268676c755f65576e40467e5f0a417a4701026d675d6e73670b1108495a4c6a0b78470b740065645e525a057258425f584a447d4e6759440c11044e7c596d7f4b625f7d04055a47505c4e1d6b5b4107447d7201057d7f0f14084e430457674f7e517d72015172415d027473577c4d615f79535256780911030f4d5e027a797f614165067806505d53777750475e75064257076500460817014e741e7e5078487e7a7c465e7669767153497064605a7376677773550d160148037e18675966787f4c42607a645f577e7b441b460776026b18685d0b110205490060020f70676175654674706671797f41067346677c4e06585e780f15074c57047b40517075415f6364027259674b5b0166407f7340600407770a22047a5d5c52300b3a0a167305067162727516134208312e3133302e3232480350015ae90403626253513635686e556f4e36416456324b796f566c636f477776484f624e56526c4d727073504b4f43654177616848494176795556497273743752737149734a7a786b3247525268377a2f637664626d504f6a73552f79626d38547a4c69586d2f474351696d494b53486833447955726f39515152756c34545350626d6d624b7949565937545671577059455372323646572f59624578507338514f706d317372785455736c30796a434144444d4f34616a654b615753366361496c554b4963797a494e396d52516f715277687939797257476d337a644345337a6a61436f492f5a585233656f65365a42647a64677654636b6b665733356e4d4c6a6a565072564b6433523172756174394e50514150724a5546627859696c4c5a3859707336654d5447666b6649793574666a526c314d4648706b51774c6373374439656378566c41636f374e664f6d2b30654756466c4434744478706771385533595973587645384842502f70666c767a737138316a32524f4d7857437556445442492f684735625462773166456e4249725162762b636144775147696f74554e316d4c4b77734379456f4766706746614251457645672b736a764c4c78704743334c304a5344532f74526169504354553344374e6249306547516651622f5a466f4c36455630775a324d6f583932414c572f5049752f56634663584e70596b356f7966326151416a536971486a2f363276354843644f525551303578754e6171795251625653704654303137655237675255636b4966366c6f447476342b514e4a4670766d74757077707774396a5a5974437a4b56743657726d6e36785837706658456251555434684f3758a201050803108703a201050804108103a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815")
    proto = bashant_pb2.StartMatch(); proto.ParseFromString(packet)
    if hasattr(proto.main, 'region_list') and len(proto.main.region_list) > 0:
        proto.main.region_list[0].region = region
        if len(proto.main.region_list) > 1: proto.main.region_list[1].region = region
    if hasattr(proto.main, 'client_version'): proto.main.client_version.remote_version = client_version
    packet = proto.SerializeToString(); enc = (await aes_encrypt(packet, key, iv)).hex(); pl = len(enc) // 2
    hl = hex(pl)[2:]; hl = hl if len(hl) > 1 else "0" + hl
    final_packet = "031400" + "0" * (6 - len(hl)) + hl + enc
    writer.write(bytes.fromhex(final_packet)); await writer.drain()

async def has_ssan_zig(n):
    z = (n << 1) & 0xFFFFFFFFFFFFFFFF; out = bytearray()
    while z >= 0x80: out.append((z & 0x7F) | 0x80); z >>= 7
    out.append(z); return bytes(out)

async def uleb_encode(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

async def tea_enc(v0, v1, k0, k1, k2, k3):
    s = 0
    for _ in range(16):
        s = (s + 0x9E3779B9) & 0xFFFFFFFF
        v0 = (v0 + (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^ ((v1 + s) & 0xFFFFFFFF) ^ (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v1 = (v1 + (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^ ((v0 + s) & 0xFFFFFFFF) ^ (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
    return v0, v1

async def tea_dec(v0, v1, k0, k1, k2, k3):
    s = (0x9E3779B9 * 16) & 0xFFFFFFFF
    for _ in range(16):
        v1 = (v1 - (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^ ((v0 + s) & 0xFFFFFFFF) ^ (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v0 = (v0 - (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^ ((v1 + s) & 0xFFFFFFFF) ^ (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        s = (s - 0x9E3779B9) & 0xFFFFFFFF
    return v0, v1

async def tea_cbc_encrypt(padded, key):
    k = struct.unpack("<4I", key); out = bytearray(len(padded)); pc, pi = bytearray(8), bytearray(8)
    for i in range(0, len(padded), 8):
        x = bytearray(a ^ b for a, b in zip(padded[i:i+8], pc)); e0, e1 = await tea_enc(struct.unpack_from("<I", x, 0)[0], struct.unpack_from("<I", x, 4)[0], *k)
        enc = bytearray(8); struct.pack_into("<I", enc, 0, e0); struct.pack_into("<I", enc, 4, e1)
        for j in range(8): out[i + j] = enc[j] ^ pi[j]
        pc[:] = out[i:i+8]; pi[:] = x
    return bytes(out)

async def build_padded(content):
    p = (8 - (len(content) + 10) % 8) % 8
    return bytes([p, 0, 0]) + b"\x00" * p + content + b"\x00" * 7

async def encode_header(layout, so, cmd, oid, flags, length, k, v80):
    out = bytearray()
    for c in layout:
        v = {0: so, 1: cmd, 2: oid, 3: flags, 4: length}[c]
        if c in [0, 3]: out.append((v & 0xFF) ^ k)
        else:
            vv = ((v & 0xFFFF) ^ v80) & 0xFFFF; out.append(vv & 0xFF); out.append((vv >> 8) & 0xFF)
    return bytes(out)

async def crc7_buff(crc, buf):
    c = crc & 0x7F
    for b in buf: c = CRC7_TABLE[((2 * (c & 0xFF)) ^ (b & 0xFF)) & 0xFF] & 0x7F
    return c & 0x7F

async def sv_frame(msg_key, layout, so, cmd, oid, flags, content, key, encrypted=True):
    k = key[0]; body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0]) + await encode_header(layout, so, cmd, oid, flags, len(body), k, ((k << 8) | k) & 0xFFFF)
    packet = bytearray(hdr + body); packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def build_match_startup_packets(token, udp_key, match_code, account_id, block_val, server_ip="", region="IND", client_version="1.132.6", client_version_code="2019121229", access_token="", mode_id=43, map_id=11):
    token = token.strip(); udp_key = bytes.fromhex(udp_key); match_code = [int(ch) for ch in str(match_code).strip()]
    thunder_jwt = token[:660] if len(token) > 660 else token; sharma_jwt = token[660:] if len(token) > 660 else ""
    etj = thunder_jwt.encode() if isinstance(thunder_jwt, str) else thunder_jwt; esj = sharma_jwt.encode() if isinstance(sharma_jwt, str) else sharma_jwt
    garena420 = await has_ssan_zig(len(etj)) + etj
    reg = str(region).upper() if region else "IND"
    csoversea_block = bytes.fromhex("ca0163736f7665727365612e7374726f6e67686f6c642e66726565666972656d6f62696c652e636f6d3b302e302e302e303b33342e3132362e37362e34353b33342e38372e3137372e31343b33342e38372e3137302e3233303b33352e3138352e3138332e3537000000000000010000000000000000000000000100000800000100000000000100a8a2d7bebd8d8bdf110200")
    mid = bytes.fromhex('0000000001000102030101') + await has_ssan_zig(len(reg)) + reg.encode()
    mid += bytes.fromhex('0001030003000004') + await has_ssan_zig(len(client_version)) + client_version.encode() + await has_ssan_zig(len(client_version_code)) + client_version_code.encode() + csoversea_block
    clean_ip = server_ip.split(':')[0] if server_ip else "0.0.0.0"; mid += await has_ssan_zig(len(clean_ip)) + clean_ip.encode()
    clean_acc_tok = access_token.strip() if access_token else ""
    if clean_acc_tok: mid += await has_ssan_zig(len(clean_acc_tok)) + clean_acc_tok.encode()
    mid += await has_ssan_zig(len(esj)) + esj
    tg_garena420 = await uleb_encode(int(account_id)) + await uleb_encode(int(block_val)) + await uleb_encode(1) + await uleb_encode(int(mode_id)) + await uleb_encode(int(block_val)) + await uleb_encode(int(map_id)) + mid
    return (await sv_frame(0x5E, match_code, 2, 447, 0, 1, garena420, udp_key)).hex(), (await sv_frame(0x5A, match_code, 2, 448, 1, 1, tg_garena420, udp_key)).hex()

async def tea_cbc_decrypt(body, key):
    k = struct.unpack("<4I", key); out = bytearray(len(body)); pi, pc = bytearray(8), bytearray(8); dec = bytearray(8)
    for i in range(0, len(body), 8):
        x = bytearray(a ^ b for a, b in zip(body[i:i+8], pi)); d0, d1 = await tea_dec(struct.unpack_from("<I", x, 0)[0], struct.unpack_from("<I", x, 4)[0], *k)
        struct.pack_into("<I", dec, 0, d0); struct.pack_into("<I", dec, 4, d1)
        for j in range(8): out[i + j] = dec[j] ^ pc[j]
        pc[:] = body[i:i+8]; pi[:] = dec
    return bytes(out)

async def build_hello_packet(text, key, layout):
    d = text.encode()
    if len(d) > 25: raise ValueError()
    c = b"\x10\x00\x00\x00" + d + b"\x00" * (29 - 4 - len(d))
    pkt = bytearray([0x63, 0x00]) + await encode_header(await parse_layout(layout), 1, 1, 0, 1, len(await build_padded(c)), key[0], ((key[0] << 8) | key[0]) & 0xFFFF) + await tea_cbc_encrypt(await build_padded(c), key)
    pkt[1] = await crc7_buff(0, pkt[2:]) & 0x7F
    return bytes(pkt).hex()

async def parse_layout(layout): return [int(c) for c in str(layout).strip()]
async def layouts_from_mask(mask): return [int(c) for c in str(mask).strip()], [int(c) for c in str(mask).strip() if c != '2']

async def build_packet(mk, layout, so, cmd, oid, flags, content, key, encrypted=True):
    k = key[0]; body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([mk, 0])
    for c in layout:
        v = {0: so, 1: cmd, 2: oid, 3: flags, 4: len(body)}[c]
        if c in [0, 3]: hdr.append((v & 0xFF) ^ k)
        else:
            vv = ((v & 0xFFFF) ^ ((k << 8) | k)) & 0xFFFF; hdr.append(vv & 0xFF); hdr.append((vv >> 8) & 0xFF)
    pkt = bytearray(hdr + body); pkt[1] = await crc7_buff(0, pkt[2:]) & 0x7F
    return bytes(pkt)

async def classify(frame):
    m = MESSAGE_ID_TO_NAME.get(frame["cmd"], f"UNKNOWN_{frame['cmd']}")
    return "HELLO" if m == "UDP_HELLO" else ("ACK" if m == "UDP_ACK" else ("PING" if m == "UDP_PING" else ("JOIN_MATCH" if m == "RUDP_JOIN_MATCH" else "DATA")))

async def reply_for(frame, key, mask, ack_key=0x68, ping_key=0x6D, hello_key=0x5B, ack_style="short"):
    nr = (await layouts_from_mask(mask))[1]; t = await classify(frame)
    if t == "HELLO": return t, await build_packet(ack_key, nr, 0, 2, None, 1, frame["content"] if ack_style == "echo" and frame["content"] else b"\x01\x00", key)
    if t == "ACK": return t, await build_packet(ack_key, nr, 0, 2, None, 1, frame["content"] if frame["content"] else b"\x01\x00", key)
    if t == "PING": return t, await build_packet(ping_key, nr, 0, 3, None, 0, (frame["content"][:4] if len(frame["content"]) >= 4 else frame["content"]) + b"\x00\x00\x00", key, encrypted=False)
    if t == "JOIN_MATCH": return t, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x02\x00", key)
    return t, None

async def keepalive_ping(sock, ip, port, k, mask, stop):
    nr = (await layouts_from_mask(mask))[1]; keys = [0x66, 0x6D, 0x69, 0x6C]; i = 0
    while not stop.is_set():
        pkt = await build_packet(keys[i % 4], nr, 0, 3, None, 0, struct.pack("<I", int(time.time() * 1000) & 0xFFFFFFFF) + b"\x00\x00\x00", k, encrypted=False)
        try: await asyncio.get_event_loop().sock_sendto(sock, pkt, (ip, port))
        except: pass
        i += 1
        try: await asyncio.wait_for(stop.wait(), timeout=3.0)
        except asyncio.TimeoutError: pass

async def try_header(buf, layout, k, v80):
    off = 2; out = {}
    for c in layout:
        sz = {0: 1, 1: 2, 2: 2, 3: 1, 4: 2}[c]
        if off + sz > len(buf): return None
        out[c] = (buf[off] ^ k) if sz == 1 else ((buf[off] | (buf[off + 1] << 8)) ^ v80) & 0xFFFF
        off += sz
    out[5] = off; return out

async def oicq_unpad(padded):
    if not padded or len(padded) < 8 or not all(padded[-1 - i] == 0 for i in range(7)): return None
    p = padded[0] & 0x07; s = 3 + p; e = len(padded) - 7
    return padded[s:e] if s < e else b""

async def decode_packet(packet, key, mask=None):
    data = bytes(packet) if isinstance(packet, bytes) else bytes.fromhex(packet)
    if len(data) < 8: return None
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF; crc_ok = (data[1] & 0x7F) == await crc7_buff(0, data[2:])
    layouts = [("RUDP", (await layouts_from_mask(mask))[0]), ("nonRUDP", (await layouts_from_mask(mask))[1])] if mask else [("RUDP", list(p)) for p in itertools.permutations([0, 1, 2, 3, 4])] + [("nonRUDP", list(p)) for p in itertools.permutations([0, 1, 3, 4])]
    candidates = []
    for kind, layout in layouts:
        f = await try_header(data, layout, k, v80)
        if not f or f.get(3, 0) > 7 or f.get(0, 0) > 7 or f.get(4, 0) != len(data) - f[5]: continue
        body = data[f[5]:f[5]+f[4]]; content = None; padded = None
        if f[3] & 1:
            if len(body) < 8 or len(body) % 8 != 0: continue
            padded = await tea_cbc_decrypt(body, key); content = await oicq_unpad(padded)
            if content is None: continue
        else: content = body
        candidates.append({"kind": kind, "layout": layout, "headerLen": f[5], "msgKey": data[0], "cmd": f[1], "flags": f[3], "sendOption": f[0], "orderId": f.get(2), "length": f[4], "content": content, "crcOk": crc_ok, "padded": padded, "score": (1 if crc_ok else 0) + (1 if content is not None else 0), "total": len(data)})
    if not candidates: return None
    candidates.sort(key=lambda c: (c["kind"] == "RUDP", c["score"]), reverse=True)
    return candidates[0]

async def play_game(srv, thndr, shrm, ukey, mcode, acc_id, reg, cver, k, iv, midx):
    start = time.time(); ping_task = None; sock = None; stop = asyncio.Event(); uid = str(acc_id); done = False; sent = False
    try:
        ip, port = srv.split(":"); rip = await resolve_host_cloudflare(ip)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); optimize_udp_socket(sock); sock.setblocking(False)
        ukey_b = bytes.fromhex(ukey); hello = await build_hello_packet(f"{acc_id}_2585", ukey_b, mcode)
        await asyncio.get_event_loop().sock_sendto(sock, bytes.fromhex(hello), (rip, int(port)))
        ack = "wait_hello"; join = False; local_c = False
        ping_task = asyncio.create_task(keepalive_ping(sock, rip, int(port), ukey_b, mcode, stop))
        last_act = time.time()
        bot_state.log(f"[MATCH #{midx}] UDP -> {srv}", "info")
        async def send_ts():
            nonlocal ack, sent
            if sent: return
            try:
                if HUMAN_MODE: await human_delay(0.15, 0.08)
                await asyncio.get_event_loop().sock_sendto(sock, bytes.fromhex(thndr), (rip, int(port))); sent = True
                await asyncio.sleep(0.15); await asyncio.get_event_loop().sock_sendto(sock, await build_packet(0x68, (await layouts_from_mask(mcode))[1], 0, 2, None, 1, b"\x01\x00", ukey_b), (rip, int(port)))
                await asyncio.sleep(0.25); await asyncio.get_event_loop().sock_sendto(sock, bytes.fromhex(shrm), (rip, int(port))); ack = "done"
            except: pass
        while not local_c:
            if time.time() - start > MAX_MATCH_DURATION: break
            try:
                resp, saddr = await asyncio.wait_for(asyncio.get_event_loop().sock_recvfrom(sock, 65535), timeout=1.5)
                if resp:
                    last_act = time.time(); frame = await decode_packet(resp, ukey_b, mcode)
                    if frame:
                        pt = await classify(frame)
                        if frame['cmd'] in [103, 107]: done = True; local_c = True; continue
                        if frame['cmd'] == 101:
                            try: await asyncio.get_event_loop().sock_sendto(sock, await build_packet(0x68, (await layouts_from_mask(mcode))[1], 0, 2, None, 1, b"\x01\x00", ukey_b), saddr)
                            except: pass
                            continue
                        if pt in ["ACK", "PING", "HELLO", "JOIN_MATCH"]:
                            if pt == "HELLO" and ack == "wait_hello": await asyncio.get_event_loop().sock_sendto(sock, (await reply_for(frame, ukey_b, mcode, ack_style="short"))[1], saddr); ack = "ack_wait"
                            elif pt == "ACK":
                                if ack == "wait_hello": await asyncio.get_event_loop().sock_sendto(sock, (await reply_for(frame, ukey_b, mcode))[1], saddr); ack = "ready"
                                elif ack == "ack_wait": ack = "ready"
                            elif pt == "PING": await asyncio.get_event_loop().sock_sendto(sock, (await reply_for(frame, ukey_b, mcode))[1], saddr)
                            elif pt == "JOIN_MATCH" and not join: await asyncio.get_event_loop().sock_sendto(sock, (await reply_for(frame, ukey_b, mcode))[1], saddr); join = True
            except asyncio.TimeoutError:
                if ack == "ready" and not sent: await send_ts()
                elif ack == "wait_hello" and (time.time() - last_act) > 7:
                    try: await asyncio.get_event_loop().sock_sendto(sock, bytes.fromhex(await build_hello_packet(f"{acc_id}_2585", ukey_b, mcode)), (rip, int(port)))
                    except: pass
                    last_act = time.time()
                elif ack == "done" and (time.time() - last_act) > MATCH_IDLE_TIMEOUT: done = True; break
                continue
            except: await asyncio.sleep(0.5)
            if ack == "ready" and not sent: await send_ts()
    except: pass
    finally:
        if done: bot_state.increment_match(uid)
        else: bot_state.match_failed(uid)
        stop.set()
        if ping_task: ping_task.cancel()
        if sock: sock.close()
        bot_state.log(f"[MATCH #{midx}] Closed", "info")
async def functional_lone_wolf(addrs, starter, region, cver, k, iv, acc_id="", acc_data=None):
    rec = 0; ip, port = addrs.split(":"); matches = []; no_resp = 0; attempts = 0; last_start = 0.0; uid = str(acc_id); fails = 0
    cur_tok, cur_k, cur_iv, cur_data = starter, k, iv, acc_data
    try:
        while True:
            writer = None
            try:
                if cur_data:
                    if cur_data.get('auth_type') == 'guest': fresh = cache_get(str(cur_data['auth_uid']))
                    else: fresh = cache_get(f"tok_{cur_data['auth_token'][:20]}")
                    if fresh:
                        cur_data = fresh; cur_k = fresh['aes_ak']; cur_iv = fresh['iv_i']
                        cur_tok = await build_tcp_startup_packet(fresh['account_id'], fresh['token'], fresh['server_time'], cur_k, cur_iv, region=region)
                    else: raise ConnectionError("expired")
                rip = await resolve_host_cloudflare(ip)
                reader, writer = await asyncio.open_connection(rip, int(port)); optimize_tcp_socket(writer.get_extra_info('socket'))
                writer.write(bytes.fromhex(cur_tok)); await writer.drain()
                await asyncio.wait_for(writer.drain(), timeout=3); rec = 0; no_resp = 0; last_start = 0.0
                bot_state.log(f"TCP connected | UID: {uid}", "success")
                async def send_start():
                    nonlocal attempts, last_start
                    attempts += 1
                    if bot_state.is_paused(uid): last_start = asyncio.get_running_loop().time(); return
                    mode = bot_state.get_account_mode(uid); label = "BR" if mode == "BR" else "LW"
                    bot_state.log(f"[{label}] StartMatch #{attempts}", "info")
                    try:
                        if HUMAN_MODE: await human_delay(1.2, 0.6)
                        else: await asyncio.sleep(random.uniform(0.3, 0.6))
                        if mode == "BR": await start_game_battle_royale(region, cver, writer, cur_k, cur_iv)
                        else: await start_game_lone_wolf(region, cver, writer, cur_k, cur_iv)
                        bot_state.update_status(uid, f"SEARCHING ({label})")
                    except: pass
                    last_start = asyncio.get_running_loop().time()
                await send_start()
                while True:
                    matches[:] = [m for m in matches if not m.done()]
                    if bot_state.is_paused(uid):
                        bot_state.update_status(uid, "PAUSED")
                        try:
                            if not await asyncio.wait_for(reader.read(8192), timeout=1.0): raise ConnectionError("closed")
                        except asyncio.TimeoutError: pass
                        continue
                    now = asyncio.get_running_loop().time(); itv = random.uniform(4.0, 8.0) if HUMAN_MODE else 10.0
                    if now - last_start >= itv:
                        if len(matches) < 1: await send_start()
                        else: last_start = now
                    try: data = await asyncio.wait_for(reader.read(8192), timeout=0.5)
                    except asyncio.TimeoutError:
                        no_resp += 1
                        if no_resp > 80: raise ConnectionError("timeout")
                        continue
                    if not data: raise ConnectionError("closed")
                    hx = data.hex(); plen = len(data); no_resp = 0
                    if hx.startswith("0300") and 10 < plen < 30: continue
                    if hx.startswith("0300") and plen >= 300:
                        bot_state.log(f"MATCH FOUND! UID: {uid}", "success")
                        try:
                            res = json.loads(await decode_protobuf(hx[10:])); tok = ukey = mcode = srv = macc = blk = None
                            if '42' in res: mcode = res['42'].get('data')
                            if '5' in res and 'data' in res['5']:
                                f5 = res['5']['data']; srv = f5.get('2', {}).get('data'); ukey = f5.get('3', {}).get('data'); tok = f5.get('4', {}).get('data')
                                if '42' in f5: mcode = f5['42'].get('data')
                            if '1' in res: macc = res['1'].get('data')
                            if '5' in res: blk = res['5']['data'].get('1', {}).get('data')
                            if tok and ukey and mcode and srv:
                                acc_tok = cur_data.get('access_token', '') if cur_data else ""
                                mode = bot_state.get_account_mode(uid); mid, mapid = (1, 1) if mode == "BR" else (43, 11)
                                thndr, shrm = await build_match_startup_packets(tok, ukey, mcode, macc or acc_id, blk or 0, srv, region, cver, acc_tok, mid, mapid)
                                midx = await _inc_match(uid)
                                bot_state.log(f"[{mode}] Match #{midx} -> UDP {srv}", "success")
                                matches.append(asyncio.create_task(play_game(srv, thndr, shrm, ukey, mcode, macc or acc_id, region, cver, cur_k, cur_iv, midx)))
                                fails = 0
                                try: writer.close(); await writer.wait_closed()
                                except: pass
                                await asyncio.sleep(6); rec = 0; break
                            else: raise Exception("parse")
                        except:
                            fails += 1
                            try: writer.close(); await writer.wait_closed()
                            except: pass
                            await asyncio.sleep(1); break
            except asyncio.CancelledError:
                for m in matches:
                    if not m.done(): m.cancel()
                break
            except Exception as e:
                matches[:] = [m for m in matches if not m.done()]
                if writer:
                    try: writer.close(); await writer.wait_closed()
                    except: pass
                if "expired" in str(e): break
                rec += 1
                await asyncio.sleep(min(rec, 2))
    except: pass

async def _inc_match(uid): return 1
async def _get_match_count(uid): return 0
async def _get_total_match_count(): return 0
async def _dec_match(uid): return 0

async def informational(addrs, starter, region="IND", max_reconnects=3):
    rec = 0; ip, port = addrs.split(":")
    while True:
        writer = None; ping_task = None
        try:
            rip = await resolve_host_cloudflare(ip)
            reader, writer = await asyncio.open_connection(rip, int(port)); optimize_tcp_socket(writer.get_extra_info('socket'))
            writer.write(bytes.fromhex(starter)); await writer.drain(); rec = 0
            try:
                ka = await send_keep_alive(region)
                if ka and writer and not writer.is_closing(): writer.write(ka); await asyncio.wait_for(writer.drain(), timeout=3)
            except: pass
            async def info_ka():
                ka = await send_keep_alive(region)
                while True:
                    await asyncio.sleep(5)
                    try:
                        if writer and not writer.is_closing(): writer.write(ka); await writer.drain()
                    except: break
            ping_task = asyncio.create_task(info_ka())
            while True:
                if not await reader.read(8192): raise ConnectionError("Closed")
        except asyncio.CancelledError:
            if ping_task: ping_task.cancel()
            if writer:
                try: writer.close(); await writer.wait_closed()
                except: pass
            raise
        except:
            if ping_task: ping_task.cancel()
            if writer:
                try: writer.close(); await writer.wait_closed()
                except: pass
            rec += 1
            await asyncio.sleep(3 if rec > max_reconnects else 1)
            if rec > max_reconnects: rec = 0

async def decode_protobuf(data):
    parsed = Parser().parse(data); res = {}
    for r in parsed:
        fd = {"wire_type": r.wire_type}
        if r.wire_type in ["varint", "string", "bytes"]: fd["data"] = r.data
        elif r.wire_type == "length_delimited": fd["data"] = await decode_protobuf(r.data.results)
        res[r.field] = fd
    return json.dumps(res)

def get_proto_field(d, key, default=None):
    if not d or not isinstance(d, dict): return default
    if key in d: return d[key].get('data', default)
    if str(key) in d: return d[str(key)].get('data', default)
    return default

async def refresh_account_profile(acc_data_or_uid):
    try:
        if isinstance(acc_data_or_uid, str): acc_data = bot_state.account_credentials.get(str(acc_data_or_uid))
        else: acc_data = acc_data_or_uid
        if not acc_data: return
        url, token, rv, payload = acc_data.get('server_url'), acc_data.get('token'), acc_data.get('release_version'), acc_data.get('login_payload_data')
        if not (url and token and rv and payload): return
        async with _REFRESH_SEMAPHORE: res = await send_getlogin(payload, url, token, rv)
        if res:
            p, d = res; lvl = int(get_proto_field(d, 6, 1)); exp = int(get_proto_field(d, 7, 0)); likes = int(get_proto_field(d, 8, 0)); nick = p.nickname or get_proto_field(d, 4, "")
            acc_id = str(acc_data['account_id'])
            if exp > 0:
                old = bot_state.accounts.get(acc_id, {}).get("current_exp", 0); bot_state.update_exp(acc_id, exp, lvl)
                if old and exp > old: bot_state.log(f"+{exp - old:,} EXP | UID: {acc_id} | Lv {lvl}", "success")
            if likes > 0 and acc_id in bot_state.accounts: bot_state.accounts[acc_id]["likes"] = likes
            if nick and acc_id in bot_state.accounts: bot_state.accounts[acc_id]["nickname"] = nick
    except: pass

async def _process_account_uid_pass(uid, password):
    cached = cache_get(uid)
    if cached:
        bot_state.register_account(cached['account_id'], cached.get('nickname', f"Player_{cached['account_id']}"), "IND", cached.get('level', 1), cached.get('exp', 0), cached.get('likes', 0))
        _register_credentials(cached)
        bot_state.log(f"Cache HIT for UID {uid}", "success")
        return cached
    bot_state.log(f"Authenticating UID {uid}...", "info")
    try:
        vc = await version_config()
        if not vc: return None
        rv, cv, surl = vc
        tk = await get_access_token(uid, password)
        if not tk: return None
        oid, at, plat = tk
        dev = get_device_for_account(uid); payload = await build_majorlogin_payload(oid, at, plat, cv, dev)
        m = await send_majorlogin(payload, rv, surl)
        if not m: return None
        g = await send_getlogin(payload, m.url, m.token, rv)
        if not g: return None
        p, d = g; acc_id = str(m.account_id); lvl = int(get_proto_field(d, 6, 1)); exp = int(get_proto_field(d, 7, 0)); likes = int(get_proto_field(d, 8, 0)); nick = p.nickname or get_proto_field(d, 4, f"Player_{acc_id}")
        bot_state.register_account(acc_id, nick, "IND", lvl, exp, likes)
        bot_state.log(f"Login OK | UID: {acc_id} | {nick} | Lv{lvl} | EXP: {exp:,}", "success")
        ad = {'account_id': m.account_id, 'nickname': nick, 'region': "IND", 'level': lvl, 'exp': exp, 'likes': likes, 'open_id': oid, 'access_token': at, 'platform': str(plat), 'token': m.token, 'server_time': m.server_time, 'aes_ak': m.aes_ak, 'iv_i': m.iv_i, 'functional_addrs': p.functional_addrs or get_proto_field(d, 14), 'informational_addrs': p.informational_addrs or get_proto_field(d, 32), 'release_version': rv, 'client_version': cv, 'server_url': m.url, 'login_payload_data': payload, 'auth_type': 'guest', 'auth_uid': uid, 'auth_password': password}
        _register_credentials(ad); cache_set(uid, ad); return ad
    except Exception as e: bot_state.log(f"process_account_uid_pass: {e}", "error"); return None

async def _process_account_token(at):
    ck = f"tok_{at[:20]}"; cached = cache_get(ck)
    if cached:
        bot_state.register_account(cached['account_id'], cached.get('nickname', f"Player_{cached['account_id']}"), "IND", cached.get('level', 1), cached.get('exp', 0), cached.get('likes', 0))
        _register_credentials(cached)
        bot_state.log(f"Cache HIT for token", "success"); return cached
    bot_state.log("Authenticating with Token...", "info")
    try:
        vc = await version_config()
        if not vc: return None
        rv, cv, surl = vc
        import requests
        resp = await asyncio.to_thread(requests.get, f"https://100067.connect.garena.com/oauth/token/inspect?token={at}", headers={"Accept-Encoding": "gzip", "Connection": "close", "Host": "100067.connect.garena.com", "User-Agent": "GarenaMSDK"}, timeout=10)
        d = resp.json()
        if 'error' in d: return None
        oid, plat = d.get('open_id'), d.get('platform', 4)
        if not oid: return None
        dev = get_device_for_account(oid); payload = await build_majorlogin_payload(oid, at, str(plat), cv, dev)
        m = await send_majorlogin(payload, rv, surl)
        if not m: return None
        g = await send_getlogin(payload, m.url, m.token, rv)
        if not g: return None
        p, d = g; acc_id = str(m.account_id); lvl = int(get_proto_field(d, 6, 1)); exp = int(get_proto_field(d, 7, 0)); likes = int(get_proto_field(d, 8, 0)); nick = p.nickname or get_proto_field(d, 4, f"Player_{acc_id}")
        bot_state.register_account(acc_id, nick, "IND", lvl, exp, likes)
        bot_state.log(f"Token OK | UID: {acc_id} | {nick} | Lv{lvl} | EXP: {exp:,}", "success")
        ad = {'account_id': m.account_id, 'nickname': nick, 'region': "IND", 'level': lvl, 'exp': exp, 'likes': likes, 'open_id': oid, 'access_token': at, 'platform': str(plat), 'token': m.token, 'server_time': m.server_time, 'aes_ak': m.aes_ak, 'iv_i': m.iv_i, 'functional_addrs': p.functional_addrs or get_proto_field(d, 14), 'informational_addrs': p.informational_addrs or get_proto_field(d, 32), 'release_version': rv, 'client_version': cv, 'server_url': m.url, 'login_payload_data': payload, 'auth_type': 'token', 'auth_token': at}
        _register_credentials(ad); cache_set(ck, ad); return ad
    except Exception as e: bot_state.log(f"process_account_token: {e}", "error"); return None

def _register_credentials(ad):
    try:
        aid = str(ad['account_id']); bot_state.account_credentials[aid] = ad
        if ad.get('auth_uid'): bot_state.account_credentials[str(ad['auth_uid'])] = ad
        if ad.get('auth_token'): bot_state.account_credentials[f"tok_{ad['auth_token'][:20]}"] = ad
    except: pass

def load_accounts():
    accs = []
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r") as f: d = json.load(f); accs = d if isinstance(d, list) else []
        except: pass
    return accs

async def account_loop_guest(uid, password):
    while True:
        try:
            while bot_state.is_paused(str(uid)): bot_state.update_status(str(uid), "PAUSED"); await asyncio.sleep(5)
            bot_state.update_status(str(uid), "CONNECTING")
            ad = await process_account_uid_pass(uid, password)
            if not ad: bot_state.update_status(str(uid), "ERROR"); await asyncio.sleep(15); continue
            acc_id = str(ad['account_id']); reg = "IND"
            tcp_online = await build_tcp_startup_packet(ad['account_id'], ad['token'], ad['server_time'], ad['aes_ak'], ad['iv_i'], region=reg, typ='OnLine')
            tcp_chat = await build_tcp_startup_packet(ad['account_id'], ad['token'], ad['server_time'], ad['aes_ak'], ad['iv_i'], region=reg, typ='ChaT')
            info_task = asyncio.create_task(informational(ad['informational_addrs'], tcp_chat, region=reg))
            func_task = asyncio.create_task(functional_lone_wolf(ad['functional_addrs'], tcp_online, reg, ad['client_version'], ad['aes_ak'], ad['iv_i'], account_id=acc_id, account_data=ad))
            await func_task
            if not info_task.done(): info_task.cancel()
        except asyncio.CancelledError: break
        except Exception as e: bot_state.log(f"Error for UID {uid}: {e}. Retry 10s...", "error"); await asyncio.sleep(10)

async def account_loop_token(token):
    while True:
        try:
            ad = await process_account_token(token)
            if not ad: await asyncio.sleep(15); continue
            acc_id = str(ad['account_id']); reg = "IND"
            tcp_online = await build_tcp_startup_packet(ad['account_id'], ad['token'], ad['server_time'], ad['aes_ak'], ad['iv_i'], region=reg, typ='OnLine')
            tcp_chat = await build_tcp_startup_packet(ad['account_id'], ad['token'], ad['server_time'], ad['aes_ak'], ad['iv_i'], region=reg, typ='ChaT')
            info_task = asyncio.create_task(informational(ad['informational_addrs'], tcp_chat, region=reg))
            func_task = asyncio.create_task(functional_lone_wolf(ad['functional_addrs'], tcp_online, reg, ad['client_version'], ad['aes_ak'], ad['iv_i'], account_id=acc_id, account_data=ad))
            await func_task
            if not info_task.done(): info_task.cancel()
        except asyncio.CancelledError: break
        except Exception as e: bot_state.log(f"Token error: {e}. Retry 10s...", "error"); await asyncio.sleep(10)
async def process_account_uid_pass(uid, password):
    return await _process_account_uid_pass(uid, password)

async def process_account_token(token):
    return await _process_account_token(token)
def cache_get(uid):
    try:
        cache = _load_token_cache()
        return cache.get(str(uid))
    except: return None

def cache_set(uid, account_data):
    try:
        cache = _load_token_cache()
        entry = dict(account_data)
        entry["cached_at"] = time.time()
        cache[str(uid)] = entry
        _save_token_cache(cache)
    except: pass

async def main():
    try: await start_html_server()
    except Exception as e: print(f"Dashboard failed: {e}")

    async def on_account_added(data):
        if "token" in data and data["token"]:
            t = str(data["token"]).strip(); k = t[:10]
            if not bot_state.account_workers.get(k) or bot_state.account_workers[k].done():
                bot_state.account_workers[k] = asyncio.create_task(account_loop_token(t))
        elif "uid" in data and "password" in data:
            u, p = str(data["uid"]).strip(), str(data["password"]).strip()
            if not bot_state.account_workers.get(u) or bot_state.account_workers[u].done():
                bot_state.account_workers[u] = asyncio.create_task(account_loop_guest(u, p))

    bot_state.refresh_callbacks["on_account_added"] = on_account_added
    for acc in load_accounts():
        if "token" in acc and acc["token"]:
            t = asyncio.create_task(account_loop_token(acc["token"])); bot_state.account_workers[acc["token"][:10]] = t
        elif "uid" in acc and "password" in acc and acc["uid"]:
            u = str(acc["uid"]); t = asyncio.create_task(account_loop_guest(u, acc["password"])); bot_state.account_workers[u] = t
    try:
        while True: await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        for t in bot_state.account_workers.values(): t.cancel()
        await asyncio.gather(*bot_state.account_workers.values(), return_exceptions=True)
        try: await client.aclose()
        except: pass

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
