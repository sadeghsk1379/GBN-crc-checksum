import socket
import random

# تابعی که محاسبه checksum را انجام می دهد
# ورودی: داده ای که می خواهیم checksum آن محاسبه شود
# خروجی: checksum محاسبه شده برای داده ورودی
def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum += byte
    return checksum & 0xFFFF

# تابعی که پیام را با اضافه کردن checksum رمزگذاری می کند
# ورودی: پیام برای رمزگذاری
# خروجی: پیام رمزگذاری شده به همراه checksum
def add_checksum(message):
    data = message.encode()
    checksum = calculate_checksum(data)
    return message + f"<CHECKSUM:{checksum:04X}>"

# تابعی که پیام را رمزگشایی و checksum آن را بررسی می کند
# ورودی: پیام رمزگذاری شده به همراه checksum
# خروجی: پیام رمزگشایی شده یا False در صورت خطا در checksum
def check_checksum(message):
    parts = message.rsplit('<CHECKSUM:', 1)
    if len(parts) != 2 or not parts[1].endswith('>'):
        return False, message
    received_message = parts[0]
    received_checksum = int(parts[1][:-1], 16)
    calculated_checksum = calculate_checksum(received_message.encode())
    return received_checksum == calculated_checksum, received_message

# تابع اصلی که اجرای برنامه را آغاز می کند
def main():
    host = '127.0.0.1'
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        
        # دریافت تعداد کل فریم ها از کاربر
        tf = input("Enter the Total number of frames : ")
        # اضافه کردن checksum به پیام
        message = add_checksum(tf)
        print(f"Sending: {message}")
        # ارسال پیام به سرور
        s.send(message.encode())
        
        # دریافت اندازه پنجره از کاربر
        N = input("Enter the Window Size : ")
        # اضافه کردن checksum به پیام
        message = add_checksum(N)
        print(f"Sending: {message}")
        # ارسال پیام به سرور
        s.send(message.encode())
        
        print("\nCommunication started:")
        while True:
            # دریافت پیام از سرور
            data = s.recv(1024).decode()
            if not data:
                break
            # بررسی checksum پیام دریافتی
            is_valid, message = check_checksum(data)
            if is_valid:
                print(f"Received (Valid Checksum): {message}")
                if "Sending Frame" in message:
                    # شبیه‌سازی از دست رفتن بسته به صورت تصادفی
                    if random.random() > 0.2:  # 80% احتمال انتقال موفق
                        # اضافه کردن checksum به پیام تأییدیه
                        ack = add_checksum(f"ACK for {message}")
                        print(f"Sending: {ack}")
                        # ارسال پیام تأییدیه به سرور
                        s.send(ack.encode())
                    else:
                        print(f"Simulated packet loss: No ACK sent for {message}")
            else:
                print(f"Received (Checksum Error): {data}")

if __name__ == "__main__":
    main()