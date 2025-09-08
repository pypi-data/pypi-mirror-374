import requests
import json
import threading
import time
import os
import sys

FIREBASE_URL = "https://sever-login-ae5cc-default-rtdb.firebaseio.com/chatnhom.json"

def listen_messages():
    last_seen = None
    while True:
        try:
            res = requests.get(FIREBASE_URL)
            if res.status_code == 200:
                data = res.json() or {}
                sorted_msgs = sorted(data.items(), key=lambda x: x[0])
                for k, v in sorted_msgs:
                    if last_seen is None or k > last_seen:
                        print(f"\n💬 {v.get('name')}: {v.get('msg')}")
                        last_seen = k
        except Exception:
            pass
        time.sleep(2)

def send_message(name):
    while True:
        msg = input("")
        if msg.strip() == "":
            continue
        data = {"name": name, "msg": msg}
        try:
            requests.post(FIREBASE_URL, data=json.dumps(data))
        except Exception:
            print("❌ Lỗi gửi tin nhắn!")

def main():
    os.system("clear")
    print("══════════════════════════════════════")
    print("🌐   CHAT NHÓM STVTermux (Realtime)   🌐")
    print("══════════════════════════════════════")

    # 👉 lấy tên từ sys.argv (username đã login)
    name = sys.argv[1] if len(sys.argv) > 1 else "Ẩn danh"

    t = threading.Thread(target=listen_messages, daemon=True)
    t.start()

    print(f"✨ {name}, bắt đầu trò chuyện...")
    send_message(name)

if __name__ == "__main__":
    main()