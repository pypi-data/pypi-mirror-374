from .core import Auth

def main():
    auth = Auth()

    print("===== 🌐 STVTermux Login System 🌐 =====")
    while True:
        choice = input("👉 Bạn muốn:\n(1) Đăng ký hay\n(2) Đăng nhập ")
        if choice == "1":
            u = input("username: ")
            p = input("password: ")
            auth.register(u, p)
        elif choice == "2":
            u = input("username: ")
            p = input("password: ")
            auth.login(u, p)
        else:
            print("Chọn 1 hoặc 2!")