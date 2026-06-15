import json
import logging
import socket

try:
    import serial
except ImportError:  # Keep the UI usable even when pyserial is not installed.
    serial = None


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class HardwareInterface:
    """
    Routes pulse oximeter telemetry to the same kinds of outputs used by the
    Ventilator simulator: RS232, USB serial, and Ethernet UDP.
    """

    def __init__(
        self,
        mode="RS232",
        serial_port="/tmp/ttyV0",
        baudrate=9600,
        ip="127.0.0.1",
        net_port=5005,
    ):
        self.mode = mode
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.ip = ip
        self.net_port = net_port
        self.connection = None
        self.socket = None
        self.target_address = (self.ip, self.net_port)

        if self.mode in ["RS232", "USB"]:
            self.connection = self._open_serial()
        elif self.mode == "Ethernet":
            self.socket = self._open_socket()
        elif self.mode == "Both":
            self.connection = self._open_serial()
            self.socket = self._open_socket()
        elif self.mode == "Console":
            logger.info("Pulse oximeter hardware output set to Console")
        else:
            logger.warning(f"Unknown pulse oximeter hardware mode: {self.mode}")

    def _open_serial(self):
        if serial is None:
            logger.error("pyserial is not installed; serial telemetry is unavailable")
            return None

        try:
            connection = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=0)
            logger.info(f"Pulse oximeter {self.mode} connected on {self.serial_port}")
            return connection
        except Exception as exc:
            logger.error(f"Failed to connect pulse oximeter serial output on {self.serial_port}: {exc}")
            return None

    def _open_socket(self):
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.info(f"Pulse oximeter Ethernet UDP streaming to {self.ip}:{self.net_port}")
            return udp_socket
        except Exception as exc:
            logger.error(f"Failed to create pulse oximeter Ethernet socket: {exc}")
            return None

    def send_data(self, telemetry_dict):
        packet = json.dumps(telemetry_dict) + "\n"
        packet_bytes = packet.encode("utf-8")

        if self.mode == "Console":
            print(packet, end="")
            return

        if self.mode in ["RS232", "USB", "Both"] and self.connection:
            try:
                self.connection.write(packet_bytes)
            except Exception as exc:
                logger.warning(f"Pulse oximeter serial transmission error: {exc}")

        if self.mode in ["Ethernet", "Both"] and self.socket:
            try:
                self.socket.sendto(packet_bytes, self.target_address)
            except Exception as exc:
                logger.warning(f"Pulse oximeter Ethernet transmission error: {exc}")

    def send(self, data):
        self.send_data(data)

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception as exc:
                logger.warning(f"Pulse oximeter serial close error: {exc}")
            finally:
                self.connection = None

        if self.socket:
            try:
                self.socket.close()
            except Exception as exc:
                logger.warning(f"Pulse oximeter Ethernet close error: {exc}")
            finally:
                self.socket = None


class Hardware(HardwareInterface):
    """Backward-compatible name for older pulse oximeter code."""

    def __init__(self, *args, **kwargs):
        if not args and "mode" not in kwargs:
            kwargs["mode"] = "Console"
        super().__init__(*args, **kwargs)
