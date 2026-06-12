import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.virtual_port import DataPacket


def read_packet(sock: socket.socket) -> DataPacket:
    buffer = bytearray()
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Connection closed")
        buffer.extend(chunk)
        if len(buffer) >= 2 and buffer[0] == DataPacket.START_BYTE and buffer[-1] == DataPacket.END_BYTE:
            return DataPacket.decode(bytes(buffer))


def main(host: str = "127.0.0.1", port: int = 9000) -> None:
    with socket.create_connection((host, port), timeout=5) as sock:
        print(f"Connected to {host}:{port}")
        while True:
            try:
                packet = read_packet(sock)
                print(packet.payload)
            except KeyboardInterrupt:
                print("Stopping reader")
                break
            except Exception as exc:
                print(f"Read error: {exc}")
                break


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9000
    main(host=host, port=port)
