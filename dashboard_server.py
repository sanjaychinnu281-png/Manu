# ==================== dashboard_server.py ====================
import os
import time
import asyncio
from collections import deque
from aiohttp import web

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))


class BotState:
    def __init__(self):
        self.accounts = {}
        self.account_credentials = {}
        self.account_workers = {}
        self.refresh_callbacks = {}
        self.logs = deque(maxlen=500)
        self._paused = set()
        self._modes = {}

    def log(self, msg, level="info"):
        self.logs.append({
            "time": time.strftime("%H:%M:%S"),
            "level": level,
            "message": str(msg),
        })

    def register_account(self, uid, nickname="", region="IND", level=1, exp=0, likes=0):
        uid = str(uid)
        if uid not in self.accounts:
            self.accounts[uid] = {
                "uid": uid,
                "nickname": nickname or f"Player_{uid}",
                "region": region,
                "level": level,
                "initial_exp": exp,
                "current_exp": exp,
                "likes": likes,
                "status": "ONLINE",
                "matches_played": 0,
                "active_matches": 0,
                "last_match_time": None,
            }
        else:
            acc = self.accounts[uid]
            if nickname:
                acc["nickname"] = nickname
            acc["level"] = level
            if exp > 0:
                if acc["initial_exp"] == 0:
                    acc["initial_exp"] = exp
                acc["current_exp"] = exp
            acc["likes"] = likes

    def remove_account(self, uid):
        uid = str(uid)
        self.accounts.pop(uid, None)
        self._paused.discard(uid)
        self._modes.pop(uid, None)

    def update_status(self, uid, status, active=0):
        uid = str(uid)
        if uid in self.accounts:
            self.accounts[uid]["status"] = status
            self.accounts[uid]["active_matches"] = active

    def update_exp(self, uid, exp, level):
        uid = str(uid)
        if uid in self.accounts:
            self.accounts[uid]["current_exp"] = exp
            self.accounts[uid]["level"] = level

    def increment_match(self, uid):
        uid = str(uid)
        if uid in self.accounts:
            self.accounts[uid]["matches_played"] += 1
            self.accounts[uid]["last_match_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

    def match_failed(self, uid):
        uid = str(uid)
        if uid in self.accounts:
            self.accounts[uid]["last_match_time"] = time.strftime("%Y-%m-%d %H:%M:%S") + " (failed)"

    def is_paused(self, uid):
        return str(uid) in self._paused

    def set_paused(self, uid, paused):
        uid = str(uid)
        if paused:
            self._paused.add(uid)
        else:
            self._paused.discard(uid)

    def get_account_mode(self, uid):
        return self._modes.get(str(uid), "BR")

    def set_account_mode(self, uid, mode):
        self._modes[str(uid)] = mode


bot_state = BotState()


def _accounts_summary():
    accounts = list(bot_state.accounts.values())
    total_gained = sum((a["current_exp"] - a["initial_exp"]) for a in accounts)
    total_matches = sum(a["matches_played"] for a in accounts)
    return {
        "total_accounts": len(accounts),
        "total_gained_exp": total_gained,
        "total_matches": total_matches,
        "accounts": accounts,
        "logs": list(bot_state.logs),
    }


async def start_web_dashboard(host="0.0.0.0", port=20333):
    app = web.Application()

    async def health(_request):
        return web.Response(text="ok", status=200)

    async def index(_request):
        html_path = os.path.join(DASHBOARD_DIR, "index.html")
        if os.path.exists(html_path):
            return web.FileResponse(html_path)
        return web.Response(text="index.html not found", status=404)

    async def stats(_request):
        return web.json_response(_accounts_summary())

    async def add_account(request):
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"status": "error", "error": "invalid json"}, status=400)

        if not data.get("uid") and not data.get("token"):
            return web.json_response({"status": "error", "error": "uid or token required"}, status=400)

        acc_path = os.path.join(DASHBOARD_DIR, "accounts.json")
        accounts = []
        if os.path.exists(acc_path):
            try:
                import json as _json
                with open(acc_path, "r", encoding="utf-8") as f:
                    accounts = _json.load(f)
                    if not isinstance(accounts, list):
                        accounts = []
            except Exception:
                accounts = []

        accounts.append(data)
        try:
            import json as _json
            with open(acc_path, "w", encoding="utf-8") as f:
                _json.dump(accounts, f, indent=2)
        except Exception as e:
            return web.json_response({"status": "error", "error": f"save failed: {e}"}, status=500)

        cb = bot_state.refresh_callbacks.get("on_account_added")
        if cb:
            try:
                await cb(data)
            except Exception as e:
                return web.json_response({"status": "error", "error": str(e)}, status=500)

        return web.json_response({"status": "ok"})

    async def delete_account(request):
        try:
            data = await request.json()
            uid = str(data.get("uid", ""))
        except Exception:
            return web.json_response({"status": "error", "error": "invalid json"}, status=400)

        worker = bot_state.account_workers.get(uid)
        if worker and not worker.done():
            worker.cancel()

        bot_state.remove_account(uid)

        acc_path = os.path.join(DASHBOARD_DIR, "accounts.json")
        if os.path.exists(acc_path):
            try:
                import json as _json
                with open(acc_path, "r", encoding="utf-8") as f:
                    accounts = _json.load(f)
                accounts = [a for a in accounts if str(a.get("uid", "")) != uid]
                with open(acc_path, "w", encoding="utf-8") as f:
                    _json.dump(accounts, f, indent=2)
            except Exception:
                pass

        return web.json_response({"status": "ok"})

    async def refresh_account(request):
        try:
            data = await request.json()
            uid = str(data.get("uid", ""))
        except Exception:
            return web.json_response({"status": "error", "error": "invalid json"}, status=400)

        cb = bot_state.refresh_callbacks.get("on_refresh_account")
        if cb:
            try:
                await cb(uid)
            except Exception as e:
                return web.json_response({"status": "error", "error": str(e)}, status=500)
        return web.json_response({"status": "ok"})

    async def pause_account(request):
        try:
            data = await request.json()
            uid = str(data.get("uid", ""))
            paused = bool(data.get("paused", True))
        except Exception:
            return web.json_response({"status": "error", "error": "invalid json"}, status=400)
        bot_state.set_paused(uid, paused)
        return web.json_response({"status": "ok"})

    async def mode_account(request):
        try:
            data = await request.json()
            uid = str(data.get("uid", ""))
            mode = str(data.get("mode", "BR")).upper()
            if mode not in ("BR", "LW"):
                return web.json_response({"status": "error", "error": "mode must be BR or LW"}, status=400)
        except Exception:
            return web.json_response({"status": "error", "error": "invalid json"}, status=400)
        bot_state.set_account_mode(uid, mode)
        return web.json_response({"status": "ok"})

    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    app.router.add_get("/index.html", index)
    app.router.add_get("/api/stats", stats)
    app.router.add_post("/api/account/add", add_account)
    app.router.add_post("/api/account/delete", delete_account)
    app.router.add_post("/api/account/refresh", refresh_account)
    app.router.add_post("/api/account/pause", pause_account)
    app.router.add_post("/api/account/mode", mode_account)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    bot_state.log(f"Dashboard listening on http://{host}:{port}", "success")