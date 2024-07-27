# TCP Communication with Go-Back-N Protocol and Checksum

This project consists of two Python scripts that implement TCP communication using the Go-Back-N protocol with checksum validation for reliable data transmission. The first script (`client.py`) acts as the client, sending frames to the server with checksum validation. The second script (`server.py`) acts as the server, receiving frames, validating checksums, and acknowledging received frames.

## Features

- **Checksum Calculation:** Ensures data integrity by calculating and validating checksums for transmitted messages.
- **Simulated Packet Loss:** Client script simulates packet loss to test the reliability of the communication.
- **Timeout and Retransmission:** Server script handles timeouts and retransmits frames if acknowledgments are not received within the timeout period.
- **Go-Back-N Protocol:** Implements the Go-Back-N protocol for efficient frame transmission and error handling.

# TCP Communication with Go-Back-N Protocol and CRC Validation

This project consists of two Python scripts that implement TCP communication using the Go-Back-N protocol with CRC validation for reliable data transmission. The first script (`client.py`) acts as the client, sending frames to the server with CRC validation. The second script (`server.py`) acts as the server, receiving frames, validating CRCs, and acknowledging received frames.

## Features

- **CRC Calculation:** Ensures data integrity by calculating and validating CRCs for transmitted messages.
- **Simulated Packet Loss:** Client script simulates packet loss to test the reliability of the communication.
- **Timeout and Retransmission:** Server script handles timeouts and retransmits frames if acknowledgments are not received within the timeout period.
- **Go-Back-N Protocol:** Implements the Go-Back-N protocol for efficient frame transmission and error handling.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sadeghsk1379/GBN-crc-checksum.git

2. **Usage:**
   ```bash
   python server.py
   then
   python client.y
just remember run server first then client.




