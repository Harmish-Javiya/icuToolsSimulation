import json
import logging
import socket
from datetime import datetime

try:
    import serial
except ImportError:
    serial = None


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class HardwareInterface:
    """
    Defibrillator telemetry adapter with Ventilator-style output routing.

    Existing simulator calls are preserved:
    connect(), disconnect(), send(device, patient, alarm), and status().
    """

    def __init__(
        self,
        mode="Console",
        serial_port="/tmp/ttyV0",
        baudrate=9600,
        ip="127.0.0.1",
        net_port=5007,
    ):
        self.mode = mode
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.ip = ip
        self.net_port = net_port
        self.target_address = (self.ip, self.net_port)

        self.connected = False
        self.connection = None
        self.socket = None
        self.last_packet = None

    def connect(self):
        if self.connected:
            return True

        if self.mode in ["RS232", "USB"]:
            self.connection = self._open_serial()
            self.connected = self.connection is not None
        elif self.mode == "Ethernet":
            self.socket = self._open_socket()
            self.connected = self.socket is not None
        elif self.mode == "Both":
            self.connection = self._open_serial()
            self.socket = self._open_socket()
            self.connected = self.connection is not None or self.socket is not None
        elif self.mode == "Console":
            self.connected = True
            logger.info("Defibrillator hardware output set to Console")
        else:
            logger.warning(f"Unknown defibrillator hardware mode: {self.mode}")
            self.connected = False

        return self.connected

    def _open_serial(self):
        if serial is None:
            logger.error("pyserial is not installed; serial telemetry is unavailable")
            return None

        try:
            connection = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=0)
            logger.info(f"Defibrillator {self.mode} connected on {self.serial_port}")
            return connection
        except Exception as exc:
            logger.error(f"Failed to connect defibrillator serial output on {self.serial_port}: {exc}")
            return None

    def _open_socket(self):
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.info(f"Defibrillator Ethernet UDP streaming to {self.ip}:{self.net_port}")
            return udp_socket
        except Exception as exc:
            logger.error(f"Failed to create defibrillator Ethernet socket: {exc}")
            return None

    def disconnect(self):
        self.close()
        self.connected = False

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception as exc:
                logger.warning(f"Defibrillator serial close error: {exc}")
            finally:
                self.connection = None

        if self.socket:
            try:
                self.socket.close()
            except Exception as exc:
                logger.warning(f"Defibrillator Ethernet close error: {exc}")
            finally:
                self.socket = None

    def create_packet(self, device, patient, alarm):
        packet = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "device": device.status(),
            "patient": patient.status(),
            "alarm": alarm.status(),
        }

        self.last_packet = packet
        return packet

    def send_data(self, packet):
        packet_string = json.dumps(packet) + "\n"
        packet_bytes = packet_string.encode("utf-8")

        if self.mode in ["RS232", "USB", "Both"] and self.connection:
            try:
                self.connection.write(packet_bytes)
            except Exception as exc:
                logger.warning(f"Defibrillator serial transmission error: {exc}")

        if self.mode in ["Ethernet", "Both"] and self.socket:
            try:
                self.socket.sendto(packet_bytes, self.target_address)
            except Exception as exc:
                logger.warning(f"Defibrillator Ethernet transmission error: {exc}")

    def send(self, device, patient, alarm):
        if not self.connected:
            return False

        packet = self.create_packet(device, patient, alarm)
        self.send_data(packet)

        print("\n=== HARDWARE PACKET ===")
        print(json.dumps(packet, indent=4))
        print("=======================\n")

        return True

    def status(self):
        return {
            "connected": self.connected,
            "mode": self.mode,
            "serial_port": self.serial_port,
            "ip": self.ip,
            "net_port": self.net_port,
            "last_packet": self.last_packet,
        }
