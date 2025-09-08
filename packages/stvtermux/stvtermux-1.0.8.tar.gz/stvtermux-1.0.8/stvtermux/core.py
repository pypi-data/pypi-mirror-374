import requests
import json
import subprocess

FIREBASE_URL = "https://sever-login-ae5cc-default-rtdb.firebaseio.com/player.json"

class Auth:
    def __init__(self, firebase_url=FIREBASE_URL):
        self.firebase_url = firebase_url

    def register(self, username: str, password: str) -> bool:
        res = requests.get(self.firebase_url)
        if res.status_code != 200:
            print("❌ Lỗi kết nối server!")
            return False

        data = res.json() or {}
        for _, user in data.items():
            if user.get("username") == username:
                print("❌ Username đã tồn tại!")
                return False

        new_user = {"username": username, "password": password}
        post_res = requests.post(self.firebase_url, data=json.dumps(new_user))
        if post_res.status_code == 200:
            print("✅ Đăng ký thành công!")
            return True
        print("❌ Đăng ký thất bại!")
        return False

    def login(self, username: str, password: str):
        res = requests.get(self.firebase_url)
        if res.status_code != 200:
            print("❌ Lỗi kết nối server!")
            return None

        data = res.json() or {}
        for user_id, user in data.items():
            if user.get("username") == username and user.get("password") == password:
                print("✅ Đăng nhập thành công!")
                # Ghi user_id ra file tạm để nhom.py đọc
                with open("user.json", "w", encoding="utf-8") as f:
                    json.dump({"user_id": user_id}, f)
                subprocess.run(["python", "index.py"])
                return user_id

        print("❌ Sai username hoặc password!")
        return None


