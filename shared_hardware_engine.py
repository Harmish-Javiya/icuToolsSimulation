from __future__ import annotations

import json
import logging
import socket
from typing import Any

try:
    import serial
except ImportError:
    serial = None


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class UnifiedHardwareEngine:
    """Single telemetry transport for RS232 and Ethernet UDP/TCP outputs."""

    SERIAL_MODES = {"RS232", "USB"}
    NETWORK_MODES = {"Ethernet"}

    def __init__(
        self,
        mode: str = "RS232",
        serial_port: str = "/tmp/ttyV0",
        baudrate: int = 9600,
        ip: str = "127.0.0.1",
        net_port: int = 5005,
        network_protocol: str = "UDP",
        device_name: str = "Hardware",
        auto_connect: bool = True,
    ):
        self.device_name = device_name
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.ip = ip
        self.net_port = net_port
        self.target_address = (self.ip, self.net_port)

        self.connection = None
        self.socket = None
        self.connected = False
        self.last_packet = None
        self._mode = "Console"
        self.network_protocol = network_protocol.upper()
        self._initializing = True

        parsed_mode, parsed_protocol = self._parse_mode(mode, network_protocol)
        self._mode = parsed_mode
        self.network_protocol = parsed_protocol
        self._initializing = False

        if auto_connect:
            self.connect()

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        parsed_mode, parsed_protocol = self._parse_mode(value, self.network_protocol)
        if self._initializing:
            self._mode = parsed_mode
            self.network_protocol = parsed_protocol
            return
        self.configure(mode=parsed_mode, network_protocol=parsed_protocol)

    def configure(self, mode: str | None = None, network_protocol: str | None = None) -> bool:
        new_mode, new_protocol = self._parse_mode(mode or self._mode, network_protocol or self.network_protocol)
        self.close()
        self._mode = new_mode
        self.network_protocol = new_protocol
        return self.connect()

    def _parse_mode(self, mode: str, network_protocol: str) -> tuple[str, str]:
        value = (mode or "Console").strip()
        normalized = value.replace("_", " ").replace("-", " ").upper()
        protocol = (network_protocol or "UDP").upper()

        if normalized in {"UDP", "ETHERNET UDP"}:
            return "Ethernet", "UDP"
        if normalized in {"TCP", "ETHERNET TCP"}:
            return "Ethernet", "TCP"
        if normalized == "ETHERNET":
            return "Ethernet", protocol if protocol in {"UDP", "TCP"} else "UDP"
        if normalized in {"RS232", "USB", "BOTH", "CONSOLE"}:
            return normalized.title() if normalized in {"BOTH", "CONSOLE"} else normalized, protocol

        logger.warning("%s unknown hardware mode: %s", self.device_name, mode)
        return "Console", protocol

    def connect(self) -> bool:
        if self.connected:
            return True

        if self._mode in self.SERIAL_MODES:
            self.connection = self._open_serial()
            self.connected = self.connection is not None
        elif self._mode == "Ethernet":
            self.socket = self._open_network_socket()
            self.connected = self.socket is not None
        elif self._mode == "Both":
            self.connection = self._open_serial()
            self.socket = self._open_network_socket()
            self.connected = self.connection is not None or self.socket is not None
        elif self._mode == "Console":
            logger.info("%s hardware output set to Console", self.device_name)
            self.connected = True
        return self.connected

    def _open_serial(self):
        if serial is None:
            logger.error("pyserial is not installed; %s serial telemetry is unavailable", self.device_name)
            return None
        try:
            connection = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=0)
            logger.info("%s RS232 connected on %s", self.device_name, self.serial_port)
            return connection
        except Exception as exc:
            logger.error("Failed to connect %s serial output on %s: %s", self.device_name, self.serial_port, exc)
            return None

    def _open_network_socket(self):
        try:
            if self.network_protocol == "TCP":
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.settimeout(0.25)
                try:
                    tcp_socket.connect(self.target_address)
                    logger.info("%s Ethernet TCP connected to %s:%s", self.device_name, self.ip, self.net_port)
                    return tcp_socket
                except Exception as exc:
                    logger.warning("%s Ethernet TCP waiting for %s:%s (%s)", self.device_name, self.ip, self.net_port, exc)
                    tcp_socket.close()
                    return None

            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.info("%s Ethernet UDP streaming to %s:%s", self.device_name, self.ip, self.net_port)
            return udp_socket
        except Exception as exc:
            logger.error("Failed to create %s Ethernet socket: %s", self.device_name, exc)
            return None

    def _packet_bytes(self, telemetry: Any) -> bytes:
        self.last_packet = telemetry
        if isinstance(telemetry, str):
            return (telemetry + "\n").encode("utf-8")
        return (json.dumps(telemetry, default=str) + "\n").encode("utf-8")

    def send_data(self, telemetry: Any) -> None:
        if not self.connected:
            self.connect()

        packet_bytes = self._packet_bytes(telemetry)

        if self._mode == "Console":
            print(packet_bytes.decode("utf-8"), end="")
            return

        if self._mode in {"RS232", "USB", "Both"} and self.connection:
            try:
                self.connection.write(packet_bytes)
            except Exception as exc:
                logger.warning("%s serial transmission error: %s", self.device_name, exc)

        if self._mode in {"Ethernet", "Both"} and self.socket:
            try:
                if self.network_protocol == "TCP":
                    self.socket.sendall(packet_bytes)
                else:
                    self.socket.sendto(packet_bytes, self.target_address)
            except Exception as exc:
                logger.warning("%s Ethernet %s transmission error: %s", self.device_name, self.network_protocol, exc)
                if self.network_protocol == "TCP":
                    self._close_socket()
                    self.socket = self._open_network_socket()
                    self.connected = self.socket is not None

    def send(self, data: Any) -> None:
        self.send_data(data)

    def disconnect(self) -> None:
        self.close()
        self.connected = False

    def close(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            except Exception as exc:
                logger.warning("%s serial close error: %s", self.device_name, exc)
            finally:
                self.connection = None

        self._close_socket()
        self.connected = False

    def _close_socket(self) -> None:
        if self.socket:
            try:
                self.socket.close()
            except Exception as exc:
                logger.warning("%s Ethernet close error: %s", self.device_name, exc)
            finally:
                self.socket = None

    def status(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "mode": self._mode,
            "network_protocol": self.network_protocol,
            "serial_port": self.serial_port,
            "ip": self.ip,
            "net_port": self.net_port,
            "last_packet": self.last_packet,
        }
