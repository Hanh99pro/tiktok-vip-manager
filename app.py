import os
import requests
import subprocess
import urllib.parse
import secrets
import hashlib
import base64
from pathlib import Path
import json

from flask import Flask, jsonify, request, send_from_directory, redirect

APP_DIR = Path(__file__).resolve().parent
GUI_DIR = APP_DIR / "gui"


app = Flask(__name__, static_folder=str(GUI_DIR), static_url_path="")
ACCOUNTS_FILE = APP_DIR / "accounts.json"


def load_accounts():
    if not ACCOUNTS_FILE.exists():
        return {}

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)
bot_process = None
PKCE_VERIFIER = None


ACCOUNTS = {
    "1": "minhanhbg9866",
    "2": "thamvongnhungluoibieng9x",
    "3": "lammyjqjco2",
}
CLIENT_KEY = "sbawbx46zmog615y0k"
CLIENT_SECRET = "iLN92eRoJosLXH22ac97vQSxF2xvoQ0g"
# CLIENT_KEY = "aw4wh43nndnvqdab"
# CLIENT_SECRET = "UYLmisRtQj5Qm9e9nM2dIT5aCy0p1d8a"
# REDIRECT_URI = "http://127.0.0.1:5000/callback"
# REDIRECT_URI = "https://example.com/callback"
# REDIRECT_URI = "https://written-dingy-zen.ngrok-free.dev/callback"
# REDIRECT_URI = "https://tiktok-vip-manager.onrender.com/callback"
# REDIRECT_URI = "http://localhost:5000/callback"
REDIRECT_URI = "https://vip-manager-online.onrender.com/callback"
SCOPES = "user.info.basic,video.upload"

def generate_pkce():
    verifier = secrets.token_urlsafe(64)

    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")

    return verifier, challenge
@app.route("/api/tiktok/exchange")
def exchange_code():
    code = request.args.get("code")

    if not code:
        return "Thiếu code"

    if not PKCE_VERIFIER:
        return "Thiếu PKCE_VERIFIER. Hãy login lại từ /api/tiktok/login"

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"

    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": PKCE_VERIFIER
    }

    r = requests.post(token_url, data=data)
    token_data = r.json()

    if "access_token" not in token_data:
        return f"Lỗi lấy token: {token_data}"

    accounts = load_accounts()
    used_ids = [int(k) for k in accounts.keys() if k.isdigit()]
    next_id = max(used_ids, default=0) + 1
    token_file = f"nick{next_id}_token.txt"

    with open(token_file, "w", encoding="utf-8") as f:
        f.write(token_data["access_token"])

    return f"✅ Đã lưu token vào {token_file}<br><pre>{token_data}</pre>"
@app.route("/")
def index():
    return send_from_directory(GUI_DIR, "index.html")


@app.route("/api/accounts")
def api_accounts():
    data = load_accounts()

    result = {}
    for key, acc in data.items():
        result[key] = acc["name"]

    return jsonify(result)

@app.route("/api/tiktok/login")
def tiktok_login():
    global PKCE_VERIFIER

    verifier, challenge = generate_pkce()
    PKCE_VERIFIER = verifier

    params = {
        "client_key": CLIENT_KEY,
        "scope": SCOPES,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": "add_account",

        "code_challenge": challenge,
        "code_challenge_method": "S256"
    }

    url = (
        "https://www.tiktok.com/v2/auth/authorize/?"
        + urllib.parse.urlencode(params)
    )

    # return jsonify({
    #     "url": url,
    #     "verifier": verifier
    # })
  
    return redirect(url)



@app.route("/callback")
def callback():
    global PKCE_VERIFIER
    
    code = request.args.get("code")

    if not code:
        return "Không có code từ TikTok"

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"

    data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": code,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
    "code_verifier": PKCE_VERIFIER
}

    r = requests.post(token_url, data=data)
    token_data = r.json()

    if "access_token" not in token_data:
        return f"Lỗi lấy token: {token_data}"

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token", "")
    expires_in = token_data.get("expires_in", 86400)
    accounts = load_accounts()

    used_ids = [int(k) for k in accounts.keys() if k.isdigit()]
    next_id = max(used_ids, default=0) + 1



    user_res = requests.get(
        "https://open.tiktokapis.com/v2/user/info/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"fields": "open_id,display_name,avatar_url"}
    )

    user_data = user_res.json()
    print(user_data)
    user = user_data.get("data", {}).get("user", {})

    display_name = user.get("display_name", f"nick{next_id}")
    open_id = user.get("open_id", "")
    # accounts = load_accounts()
    for acc_id, acc in accounts.items():
        if acc.get("open_id") == open_id:
            old_token_file = acc.get("token_file", f"nick{acc_id}_token.txt")

            with open(old_token_file, "w", encoding="utf-8") as f:
                f.write(access_token)

            acc["name"] = display_name
            acc["refresh_token"] = refresh_token
            acc["expires_in"] = expires_in
            acc["token_file"] = old_token_file

            save_accounts(accounts)

            return redirect("/")

    token_file = f"nick{next_id}_token.txt"

    with open(token_file, "w", encoding="utf-8") as f:
        f.write(access_token)

    # accounts = load_accounts()

    accounts[str(next_id)] = {
        "name": display_name,
        "open_id": open_id,
        "token_file": token_file,
         "refresh_token": refresh_token,
        "expires_in": expires_in
    }

    save_accounts(accounts)
    
    return """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <title>Success</title>
        </head>
        <body>

        <h2>✅ Đã thêm tài khoản TikTok thành công</h2>

        <script>
        if (window.opener) {
            window.opener.location.reload();
            window.close();
        } else {
            setTimeout(function() {
                window.location.href = "/";
            }, 1000);
        }
        </script>

        </body>
        </html>
        """
@app.route("/api/accounts/<account_id>", methods=["DELETE"])
def delete_account(account_id):

    accounts = load_accounts()

    if account_id not in accounts:
        return jsonify({"ok": False, "message": "Không thấy tài khoản"}), 404

    token_file = accounts[account_id].get("token_file")

    if token_file:
        token_path = APP_DIR / token_file
        if token_path.exists():
            token_path.unlink()

    del accounts[account_id]

    save_accounts(accounts)

    return jsonify({
        "ok": True,
        "message": "Đã xoá tài khoản"
    })
@app.route("/api/topics")
def topics():
    folders_dir = APP_DIR / "folders"
    folders_dir.mkdir(exist_ok=True)

    topics = []
    for item in folders_dir.iterdir():
        if item.is_dir():
            topics.append(item.name)

    return jsonify(sorted(topics))


@app.route("/api/status")
def status():
    running = bot_process is not None and bot_process.poll() is None
    return jsonify({"running": running})


@app.route("/api/start", methods=["POST"])
def start():
    global bot_process

    data = request.json or {}

    account = str(data.get("account", "")).strip()
    topic = str(data.get("topic", "")).strip()
    wait_seconds = str(data.get("wait_seconds", "")).strip()
    run_mode = str(data.get("run_mode", "now")).strip()
    start_time = str(data.get("start_time", "")).strip()
    print("WEB RUN_MODE =", run_mode)
    print("WEB START_TIME =", start_time)

    if not account:
        return jsonify({"ok": False, "message": "Bạn chưa chọn nick TikTok"}), 400

    if not topic:
        return jsonify({"ok": False, "message": "Bạn chưa chọn folder chủ đề"}), 400

    if not wait_seconds.isdigit():
        return jsonify({"ok": False, "message": "Khoảng cách phải là số giây"}), 400

    topic_path = APP_DIR / "folders" / topic
    if not topic_path.exists():
        return jsonify({"ok": False, "message": f"Không thấy folder: {topic}"}), 400

    if bot_process is not None and bot_process.poll() is None:
        return jsonify({"ok": False, "message": "Bot đang chạy rồi"}), 400

    env = os.environ.copy()
    env["SELECTED_ACCOUNT"] = account
    env["SELECTED_TOPIC"] = topic
    env["WAIT_SECONDS"] = wait_seconds
    env["RUN_MODE"] = run_mode
    env["START_TIME"] = start_time

    bot_process = subprocess.Popen(
        ["python", "vip_manager.py"],
        cwd=str(APP_DIR),
        env=env,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
    )

    return jsonify({
        "ok": True,
        "message": f"Đã chạy bot: nick {account}, folder {topic}, cách {wait_seconds} giây"
    })


@app.route("/api/stop", methods=["POST"])
def stop():
    global bot_process

    if bot_process is None or bot_process.poll() is not None:
        return jsonify({"ok": False, "message": "Bot chưa chạy"}), 400

    bot_process.terminate()
    bot_process = None

    return jsonify({"ok": True, "message": "Đã dừng bot"})


@app.route("/api/stats")
def stats():
    topic = request.args.get("topic", "").strip()

    if not topic:
        return jsonify({
            "videos": 0,
            "pending": 0,
            "uploaded": 0,
        })

    base = APP_DIR / "folders" / topic

    def count_mp4(name):
        folder = base / name
        if not folder.exists():
            return 0
        return len([f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".mp4"])

    return jsonify({
        "videos": count_mp4("videos"),
        "pending": count_mp4("pending"),
        "uploaded": count_mp4("uploaded"),
    })

# @app.route("/tiktokBI9SEdpBUc9JELHj5ICi79UnelrjIBS.txt")
# @app.route("/tiktokBI9SEdpBUc9JELHj5ICi79UneIrqjIBS.txt")
# def tiktok_verify_file():
#     return "tiktok-developers-site-verification=BI9SEdpBUc9JELHj5ICi79UneIrqjIBS"
# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=False)
@app.route("/tiktokRAVyV5vq0KPw6F5fQf0uglR8zJWJPgWJ.txt")
def tiktok_verify():
    return (
        "tiktok-developers-site-verification=RAVyV5vq0KPw6F5fQf0uglR8zJWJPgWJ",
        200,
        {"Content-Type": "text/plain"}
    )
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
