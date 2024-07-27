import socket

# CRC-16 polynomial
CRC_POLY = 0x8005
TIMEOUT = 2  # Timeout in seconds
MAX_RETRIES = 5  # Maximum number of retries for a frame

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ CRC_POLY
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
        return False
    received_message = parts[0]
    received_crc = int(parts[1][:-1], 16)
    calculated_crc = calculate_crc(received_message.encode())
    return received_crc == calculated_crc

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
                message = add_crc(f"Sending Frame {k}")
                conn.send(message.encode())
                tt += 1
                print(f"Sent: Frame {k}")
            
            # Wait for acknowledgments
            acks_received = 0
            for k in range(window_start, window_end + 1):
                conn.settimeout(TIMEOUT)
                try:
                    ack = conn.recv(1024).decode()
                    if check_crc(ack):
                        print(f"Received ACK for Frame {k}")
                        acks_received += 1
                    else:
                        print(f"CRC Error in ACK for Frame {k}")
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
                message = add_crc(f"Timeout!! Retransmitting Window from Frame {window_start}")
                conn.send(message.encode())
                print(f"Retransmitting Window from Frame {window_start}")
        
        if retries == MAX_RETRIES:
            print(f"Max retries reached for window starting at Frame {window_start}. Moving to next window.")
            i = window_end + 1
        
        conn.send(b"\n")
    
    return tt

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
            tf = int(conn.recv(1024).decode().split('<CRC:')[0])
            N = int(conn.recv(1024).decode().split('<CRC:')[0])
            
            tt = transmission(conn, N, tf)
            
            final_message = add_crc(f"Total number of frames which were sent and resent are : {tt}")
            conn.send(final_message.encode())

if __name__ == "__main__":
    main()