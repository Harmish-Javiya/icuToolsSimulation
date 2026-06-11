import socket
import serial
import json
import logging

logger = logging.getLogger(__name__)


class HardwareInterface:
    def __init__(self, mode="Ethernet", ip="127.0.0.1", net_port=5006, serial_port="/tmp/ttyV2", baudrate=9600):
        self.mode = mode
        self.ip = ip
        self.net_port = net_port
        self.sock = None
        self.ser = None

        if self.mode == "Ethernet":
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                logger.info(f"ICP Ethernet Interface bound to {self.ip}:{self.net_port}")
            except Exception as e:
                logger.error(f"Ethernet Socket Error: {e}")

        elif self.mode == "RS232":
            try:
                self.ser = serial.Serial(serial_port, baudrate)
                logger.info(f"ICP RS232 Interface bound to {serial_port}")
            except Exception as e:
                logger.error(f"RS232 Connection Error on {serial_port}: {e}")

    def send_data(self, payload: dict) -> None:
        data_str = json.dumps(payload) + "\n"

        if self.mode == "Ethernet" and self.sock:
            try:
                self.sock.sendto(data_str.encode('utf-8'), (self.ip, self.net_port))
            except Exception as e:
                logger.error(f"Ethernet send failed: {e}")

        elif self.mode == "RS232" and self.ser:
            try:
                self.ser.write(data_str.encode('utf-8'))
            except Exception as e:
                logger.error(f"Serial write failed: {e}")