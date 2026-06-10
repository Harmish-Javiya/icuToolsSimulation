import serial
import socket
import json
import logging

logger = logging.getLogger(__name__)

class HardwareInterface:
    """
    Manages outbound JSON telemetry data to hardware ports or network sockets.
    """

    def __init__(self, mode="Ethernet", serial_port="/tmp/ttyV0", baudrate=9600, ip="127.0.0.1", net_port=5005):
        self.mode = mode
        self.connection = None

        try:
            if self.mode in ["RS232", "USB"]:
                self.connection = serial.Serial(serial_port, baudrate=baudrate, timeout=0)
                logger.info(f"✅ ECG Hardware Connected: {self.mode} on {serial_port}")
            elif self.mode == "Ethernet":
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.target_address = (ip, net_port)
                logger.info(f"✅ ECG Hardware Connected: Ethernet UDP streaming to {ip}:{net_port}")
        except Exception as e:
            logger.error(f"⚠️ Failed to connect {self.mode} hardware: {e}")
            self.connection = None

    def send_data(self, telemetry_dict: dict):
        if not self.connection:
            return

        # Package as JSON with newline terminator
        packet_string = json.dumps(telemetry_dict) + "\n"
        packet_bytes = packet_string.encode('utf-8')

        try:
            if self.mode in ["RS232", "USB"]:
                self.connection.write(packet_bytes)
            elif self.mode == "Ethernet":
                self.connection.sendto(packet_bytes, self.target_address)
        except Exception as e:
            logger.warning(f"Transmission error: {e}")

    def close(self):
        if self.connection and self.mode in ["RS232", "USB"]:
            self.connection.close()
        elif self.connection and self.mode == "Ethernet":
            self.connection.close()