import os
import time
import json
import random
import shutil
import requests
import threading
from datetime import datetime

# ===== CẤU HÌNH =====
BASE_FOLDER = "folders"
TOPIC_FOLDER = os.environ.get("SELECTED_TOPIC", "thoitrang")

ACCOUNTS = {
    "1": {
        "name": "minhanhbg9866",
        "token_file": "nick1_token.txt"
    },
    "2": {
        "name": "thamvongnhungluoibieng9x",
        "token_file": "nick2_token.txt"
    },
    "3": {
        "name": "lammyjqjco2",
        "token_file": "nick3_token.txt"
    },
    "4": {
        "name": "ten_nick_moi",
        "token_file": "nick4_token.txt"
         },
    "5": {
        "name": "nick_moi",
        "token_file": "nick5_token.txt"
    }


}


# TELEGRAM_BOT_TOKEN = "DAN_BOT_TOKEN_VAO_DAY"
# TELEGRAM_CHAT_ID = "DAN_CHAT_ID_VAO_DAY"
TELEGRAM_BOT_TOKEN = "8301412839:AAHfLwNkO12aI731XgUbSwxAj_UTBzUUVAo"
TELEGRAM_CHAT_ID = "7059524864"

WAIT_SECONDS = int(os.environ.get("WAIT_SECONDS", "240"))

INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
STATE_FILE = "state.json"
# ?Thêm
def load_accounts():
    path = "accounts.json"

    if not os.path.exists(path):
        return ACCOUNTS

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
def choose_account():
    accounts = load_accounts()

    env_choice = os.environ.get("SELECTED_ACCOUNT")

    if env_choice and env_choice in ACCOUNTS:
        choice = env_choice
    else:
        print("Chọn tài khoản để upload:")

        for key, acc in ACCOUNTS.items():
            print(f"{key}. {acc['name']}")

        choice = input("\nChọn: ").strip()

    if choice not in ACCOUNTS:
        raise SystemExit("Tài khoản không hợp lệ")

    token_file = ACCOUNTS[choice]["token_file"]

    with open(token_file, "r", encoding="utf-8") as f:
        token = f.read().strip()

    print(f"Đang dùng: {ACCOUNTS[choice]['name']}")
    return token, ACCOUNTS[choice]["name"], token_file
def send_telegram(text, video_name=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }

    if video_name:
        data["reply_markup"] = json.dumps({
            "inline_keyboard": [
                [
                    {"text": "✅ Y - Đã đăng", "callback_data": f"Y|{video_name}"},
                    {"text": "❌ N - Chưa đăng", "callback_data": f"N|{video_name}"}
                ]
            ]
        })

    r = requests.post(url, data=data)
    print("TELEGRAM:", r.status_code, r.text)


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

    params = {"timeout": 10}
    if offset:
        params["offset"] = offset

    return requests.get(url, params=params).json()




def topic_path():
    return os.path.join(BASE_FOLDER, TOPIC_FOLDER)


def videos_path():
    return os.path.join(topic_path(), "videos")


def uploaded_path():
    return os.path.join(topic_path(), "uploaded")


def captions_path():
    return os.path.join(topic_path(), "captions.txt")


def load_captions():
    path = captions_path()

    if not os.path.exists(path):
        return [""]

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    captions = [c.strip() for c in raw.split("---") if c.strip()]
    return captions if captions else [""]


def pick_random_video():
    folder = videos_path()

    videos = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".mp4")
    ]

    if not videos:
        return None

    return random.choice(videos)


def upload_video(video_name, access_token,account_name):
    video_file = os.path.join(videos_path(), video_name)
    video_size = os.path.getsize(video_file)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    payload = {
        "post_info": {
            "title": "Uploaded from Python",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "privacy_level": "SELF_ONLY"
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": video_size,
            "total_chunk_count": 1
        }
    }

    res = requests.post(INIT_URL, headers=headers, json=payload)
    print("INIT:", res.status_code, res.text)

    if res.status_code != 200:
        send_telegram(f"❌ Upload lỗi INIT\nVideo: {video_name}\n\n{res.text}")
        return False

    data = res.json()["data"]
    upload_url = data["upload_url"]
    publish_id = data["publish_id"]

    with open(video_file, "rb") as f:
        upload_headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(video_size),
            "Content-Range": f"bytes 0-{video_size - 1}/{video_size}"
        }

        upload_res = requests.put(upload_url, headers=upload_headers, data=f)

    print("UPLOAD:", upload_res.status_code, upload_res.text)

    if upload_res.status_code in [200, 201, 204]:
        captions = load_captions()
        random.shuffle(captions)
        selected = captions[:5]

        caption_text = "\n\n".join(
            [f"{i+1}. {cap}" for i, cap in enumerate(selected)]
        )

        msg = (
            f"✅ Video đã lên TikTok Draft\n\n"
            f"Nick: {account_name}\n"
            f"Folder: {TOPIC_FOLDER}\n"
            f"Video: {video_name}\n"
            f"Publish ID: {publish_id}\n\n"
            f"Caption gợi ý:\n\n{caption_text}\n\n"
            f"Sau khi bạn gắn sản phẩm và đăng xong, bấm Y.\n"
            f"Nếu chưa đăng, bấm N."
        )

        send_telegram(msg, video_name=video_name)
        return True

    send_telegram(f"❌ Upload lỗi\nVideo: {video_name}\n\n{upload_res.text}")
    return False


def move_to_uploaded(video_name):
    os.makedirs(uploaded_path(), exist_ok=True)

    # src = os.path.join(videos_path(), video_name)
    src = os.path.join(pending_path(), video_name)
    dst = os.path.join(uploaded_path(), video_name)

    if os.path.exists(src):
        shutil.move(src, dst)
        send_telegram(f"✅ Đã chuyển sang uploaded:\n{video_name}")
        print("Moved:", video_name)
    else:
        send_telegram(f"⚠️ Không thấy file để chuyển:\n{video_name}")
def pending_path():
    return os.path.join(topic_path(), "pending")

def move_to_pending(video_name):
    os.makedirs(pending_path(), exist_ok=True)

    src = os.path.join(videos_path(), video_name)
    dst = os.path.join(pending_path(), video_name)

    if os.path.exists(src):
        shutil.move(src, dst)
        print("Moved to pending:", video_name)
def move_back_to_videos(video_name):
    src = os.path.join(pending_path(), video_name)
    dst = os.path.join(videos_path(), video_name)

    if os.path.exists(src):
        shutil.move(src, dst)
        send_telegram(f"↩️ Đã chuyển lại về videos:\n{video_name}")
    else:
        send_telegram(f"⚠️ Không thấy file trong pending:\n{video_name}")
def has_pending_video():
    folder = pending_path()

    if not os.path.exists(folder):
        return False

    return any(f.lower().endswith(".mp4") for f in os.listdir(folder))
def handle_telegram_confirmations():
    last_update_id = None

    while True:
      
    
        updates = get_updates(last_update_id)

        if not updates.get("ok"):
            time.sleep(5)
            continue

        for item in updates.get("result", []):
            last_update_id = item["update_id"] + 1

            if "callback_query" not in item:
                continue

            callback = item["callback_query"]
            data = callback["data"]

            action, video_name = data.split("|", 1)

            if action == "Y":
                move_to_uploaded(video_name)

            # elif action == "N":
            #     send_telegram(f"⏸ Giữ lại trong videos:\n{video_name}")
            elif action == "N":
                move_back_to_videos(video_name)
            # Xác nhận với Telegram là đã xử lý nút
            callback_id = callback["id"]

            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
                data={"callback_query_id": callback_id}
            )

        time.sleep(3)


def wait_for_schedule():
    print("RUN_MODE =", os.environ.get("RUN_MODE"))
    print("START_TIME =", os.environ.get("START_TIME"))
    run_mode = os.environ.get("RUN_MODE", "now")
    start_time = os.environ.get("START_TIME", "").strip()

    if run_mode != "schedule":
        return

    if not start_time:
        send_telegram("⚠️ Bạn chọn hẹn giờ nhưng chưa nhập giờ.")
        return

    send_telegram(f"⏰ Đã hẹn giờ chạy lúc {start_time}")

    while True:
        now = datetime.now().strftime("%H:%M")

        if now >= start_time:
            send_telegram(f"🚀 Đến giờ {start_time}, bắt đầu upload.")
            return

        print(f"⏳ Chờ tới {start_time}. Hiện tại: {now}")
        time.sleep(20)
def main():
    os.makedirs(videos_path(), exist_ok=True)
    os.makedirs(uploaded_path(), exist_ok=True)
    os.makedirs(pending_path(), exist_ok=True)


    access_token, account_name, token_file = choose_account()
    send_telegram("🤖 VIP TikTok Manager đã chạy.")
    wait_for_schedule()
    threading.Thread(
    target=handle_telegram_confirmations,
    daemon=True
    ).start()

    while True:

        if has_pending_video():
            print("⏳ Đang có video chờ xác nhận trong pending.")
            print("Chưa upload video mới.")
            time.sleep(30)
            continue

        video_name = pick_random_video()

        if not video_name:
            send_telegram(
                f"⚠️ Folder {TOPIC_FOLDER} không còn video."
            )
            break

        print("=" * 50)
        print("Random video:", video_name)

        ok = upload_video(video_name, access_token, account_name)
        if ok:
            move_to_pending(video_name)

            print(f"📦 Đã chuyển sang pending: {video_name}")
            print("⏳ Đang chờ bạn xác nhận trên Telegram...")
            print(f"Chờ {WAIT_SECONDS} giây trước video tiếp theo...")

            time.sleep(WAIT_SECONDS)

        else:
            print("Upload lỗi. Chờ 5 phút rồi thử video khác.")
            time.sleep(300)

        # if ok:
        #     print(f"Đã upload {video_name}. Đang chờ bạn xử lý trên Telegram.")
        #     print(f"Chờ {WAIT_SECONDS} giây trước video tiếp theo...")
        #     time.sleep(WAIT_SECONDS)
        # else:
        #     print("Upload lỗi. Chờ 5 phút rồi thử video khác.")
        #     time.sleep(300)



if __name__ == "__main__":
    main()