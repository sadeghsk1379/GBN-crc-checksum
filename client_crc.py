import socket
import random

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x8005
            else:
                crc <<= 1
    return crc & 0xFFFF

def add_crc(message):
    data = message.encode()
    crc = calculate_crc(data)
    return message + f"<CRC:{crc:04X}>"

def check_crc(message):
    parts = message.rsplit('<CRC:', 1)
    if len(parts) != 2 or not parts[1].endswith('>'):
        return False, message
    received_message = parts[0]
    received_crc = int(parts[1][:-1], 16)
    calculated_crc = calculate_crc(received_message.encode())
    return received_crc == calculated_crc, received_message

def main():
    host = '127.0.0.1'
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        
        tf = input("Enter the Total number of frames : ")
        message = add_crc(tf)
        print(f"Sending: {message}")
        s.send(message.encode())
        
        N = input("Enter the Window Size : ")
        message = add_crc(N)
        print(f"Sending: {message}")
        s.send(message.encode())
        
        print("\nCommunication started:")
        while True:
            data = s.recv(1024).decode()
            if not data:
                break
            is_valid, message = check_crc(data)
            if is_valid:
                print(f"Received (Valid CRC): {message}")
                if "Sending Frame" in message:
                    # Simulate random packet loss
                    if random.random() > 0.2:  # 80% chance of successful transmission
                        ack = add_crc(f"ACK for {message}")
                        print(f"Sending: {ack}")
                        s.send(ack.encode())
                    else:
                        print(f"Simulated packet loss: No ACK sent for {message}")
            else:
                print(f"Received (CRC Error): {data}")

if __name__ == "__main__":
    main()