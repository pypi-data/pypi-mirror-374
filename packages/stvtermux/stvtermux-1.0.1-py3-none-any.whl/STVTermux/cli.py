from .core import Auth

def main():
    auth = Auth()

    print("===== 🌐 STVTermux Login System 🌐 =====")
    while True:
        choice = input("👉 Bạn muốn (1) Đăng ký hay (2) Đăng nhập? ")
        if choice == "1":
            u = input("Nhập username: ")
            p = input("Nhập password: ")
            auth.register(u, p)
        elif choice == "2":
            u = input("Nhập username: ")
            p = input("Nhập password: ")
            auth.login(u, p)
        else:
            print("Chọn 1 hoặc 2!")