import requests
import threading
import time
import json
import os

FIREBASE_CHAT = "https://sever-login-ae5cc-default-rtdb.firebaseio.com/chatnhom.json"
FIREBASE_PLAYER = "https://sever-login-ae5cc-default-rtdb.firebaseio.com/player.json"

# Lấy tên user từ player.json dựa vào user_id
def get_name(user_id: str) -> str:
    try:
        res = requests.get(FIREBASE_PLAYER)
        if res.status_code != 200:
            return "Ẩn danh"
        data = res.json() or {}
        user = data.get(user_id, {})
        return user.get("username", "Ẩn danh")
    except Exception:
        return "Ẩn danh"

# Luồng hiển thị tin nhắn
def listen_messages():
    last_data = None
    while True:
        try:
            res = requests.get(FIREBASE_CHAT)
            if res.status_code == 200:
                data = res.json() or {}
                if data != last_data:
                    os.system("clear")
                    print("===== 💬 Tin nhắn nhóm =====")
                    for _, msg in data.items():
                        print(f"[{msg.get('name')}] {msg.get('text')}")
                    print("============================")
                    last_data = data
        except Exception as e:
            print("❌ Lỗi khi lấy tin nhắn:", e)
        time.sleep(2)

def chat():
    # Đọc user_id từ file user.json
    try:
        with open("user.json", "r", encoding="utf-8") as f:
            user_data = json.load(f)
            user_id = user_data.get("user_id")
    except FileNotFoundError:
        print("❌ Bạn chưa đăng nhập!")
        return

    name = get_name(user_id)
    print(f"👋 Xin chào {name}, bạn đã vào nhóm chat!")

    threading.Thread(target=listen_messages, daemon=True).start()

    while True:
        text = input("✍️ Nhập tin nhắn: ")
        if text.lower() in ["exit", "quit"]:
            print("👋 Thoát nhóm chat...")
            break

        msg = {"name": name, "text": text}
        try:
            requests.post(FIREBASE_CHAT, data=json.dumps(msg))
        except Exception as e:
            print("❌ Lỗi gửi tin nhắn:", e)

if __name__ == "__main__":
    chat()