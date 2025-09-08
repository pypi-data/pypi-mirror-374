import os
import subprocess

def main():
    # giao diện mở đầu
    os.system("clear")  # nếu bạn dùng Termux/Linux, trên Windows thì thay bằng cls
    print("═" * 40)
    print("🌐   CHÀO MỪNG BẠN ĐẾN VỚI STVTermux   🌐")
    print("═" * 40)
    print("👉 Vui lòng chọn chức năng:")
    print("1️⃣  Nhóm Chat (nhom.py)")
    print("2️⃣  Bot Tự Động (bot.py)")
    print("0️⃣  Thoát")
    print("═" * 40)

    choice = input("➡️  Nhập lựa chọn: ")

    if choice == "1":
        module_path = os.path.join(os.path.dirname(__file__), "nhom.py")
        subprocess.run(["python", module_path])
    elif choice == "2":
        module_path = os.path.join(os.path.dirname(__file__), "bot.py")
        subprocess.run(["python", module_path])
    elif choice == "0":
        print("👋 Tạm biệt!")
    else:
        print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()