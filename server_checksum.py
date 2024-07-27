
import socket
import random
import time

# ضریب چندجمله ای Checksum
CHECKSUM_POLY = 0xFFFF
TIMEOUT = 2  # زمان انتظار به ثانیه
MAX_RETRIES = 5  # حداکثر تعداد تلاش برای هر فریم


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
# خروجی: True اگر checksum معتبر باشد، False در غیر این صورت
def check_checksum(message):
    parts = message.rsplit('<CHECKSUM:', 1)
    if len(parts) != 2 or not parts[1].endswith('>'):
        return False
    received_message = parts[0]
    received_checksum = int(parts[1][:-1], 16)
    calculated_checksum = calculate_checksum(received_message.encode())
    return received_checksum == calculated_checksum

# تابعی که انتقال پنجره ای را انجام می دهد
# ورودی: اتصال سوکت، اندازه پنجره، تعداد کل فریم ها
# خروجی: تعداد کل فریم هایی که ارسال و مجدداً ارسال شده اند
def transmission(conn, N, tf):
    i = 1
    tt = 0
    while i <= tf:
        window_start = i
        window_end = min(i + N - 1, tf)
        retries = 0
        
        while retries < MAX_RETRIES:
            # Send window
            for k in range(window_start, window_end + 1):
                message = add_checksum(f"Sending Frame {k}")
                conn.send(message.encode())
                tt += 1
                print(f"Sent: Frame {k}")
            
            # Wait for acknowledgments
            acks_received = 0
            for k in range(window_start, window_end + 1):
                conn.settimeout(TIMEOUT)
                try:
                    ack = conn.recv(1024).decode()
                    if check_checksum(ack):
                        print(f"Received ACK for Frame {k}")
                        acks_received += 1
                    else:
                        print(f"Checksum Error in ACK for Frame {k}")
                        break
                except socket.timeout:
                    print(f"Timeout waiting for ACK of Frame {k}")
                    break
            
            # Move window if acks received
            if acks_received > 0:
                i += acks_received
                break
            else:
                retries += 1
                message = add_checksum(f"Timeout!! Retransmitting Window from Frame {window_start}")
                conn.send(message.encode())
                print(f"Retransmitting Window from Frame {window_start}")
        
        if retries == MAX_RETRIES:
            print(f"Max retries reached for window starting at Frame {window_start}. Moving to next window.")
            i = window_end + 1
        
        conn.send(b"\n")
    
    return tt

# تابع اصلی که اجرای برنامه را آغاز می کند
def main():
    host = '127.0.0.1'
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            tf = int(conn.recv(1024).decode().split('<CHECKSUM:')[0])
            N = int(conn.recv(1024).decode().split('<CHECKSUM:')[0])
            
            tt = transmission(conn, N, tf)
            
            final_message = add_checksum(f"Total number of frames which were sent and resent are : {tt}")
            conn.send(final_message.encode())

if __name__ == "__main__":
    main()