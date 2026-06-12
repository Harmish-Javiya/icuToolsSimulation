import json
import logging
import socket
import struct
import threading
import time
from datetime import datetime, timezone
from typing import Callable, Optional


class DataPacket:
    """Simple framed packet for medical device telemetry."""

    START_BYTE = 0x7E
    END_BYTE = 0x7F

    def __init__(self, device_id: str, payload: dict, mode: str = "ascii", timestamp: Optional[str] = None):
        self.device_id = device_id
        self.payload = dict(payload)
        self.mode = mode.lower()
        self.timestamp = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def encode(self) -> bytes:
        payload = {
            "device_id": self.device_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }
        payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

        if self.mode == "ascii":
            body = b"A" + payload_bytes
        elif self.mode == "binary":
            body = b"B" + struct.pack(">H", len(payload_bytes)) + payload_bytes
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

        checksum = self._checksum(body)
        return bytes([self.START_BYTE]) + body + bytes([checksum]) + bytes([self.END_BYTE])

    @classmethod
    def decode(cls, data: bytes) -> "DataPacket":
        if len(data) < 5:
            raise ValueError("Packet too short")
        if data[0] != cls.START_BYTE or data[-1] != cls.END_BYTE:
            raise ValueError("Invalid framing")

        body = data[1:-2]
        checksum = data[-2]
        if cls._checksum(body) != checksum:
            raise ValueError("Checksum mismatch")

        marker = body[0:1]
        if marker == b"A":
            payload = json.loads(body[1:].decode("utf-8"))
            return DataPacket(
                device_id=payload.get("device_id", "UNKNOWN"),
                payload=payload.get("payload", {}),
                mode="ascii",
                timestamp=payload.get("timestamp"),
            )

        if marker == b"B":
            length = struct.unpack(">H", body[1:3])[0]
            payload_bytes = body[3:3 + length]
            payload = json.loads(payload_bytes.decode("utf-8"))
            return DataPacket(
                device_id=payload.get("device_id", "UNKNOWN"),
                payload=payload.get("payload", {}),
                mode="binary",
                timestamp=payload.get("timestamp"),
            )

        raise ValueError("Unknown packet mode")

    @staticmethod
    def _checksum(data: bytes) -> int:
        checksum = 0
        for byte in data:
            checksum = (checksum + byte) % 256
        return checksum


class VirtualDevicePort:
    """A simple TCP-based virtual device output port for lab and educational use."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9000,
        device_id: str = "MEDCRT-01",
        mode: str = "ascii",
        transmit_interval: float = 1.0,
        logger: Optional[logging.Logger] = None,
    ):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.mode = mode
        self.transmit_interval = transmit_interval
        self.logger = logger or logging.getLogger("virtual_port")
        self._payload_builder: Optional[Callable[[], dict]] = None
        self._server_socket: Optional[socket.socket] = None
        self._client_socket: Optional[socket.socket] = None
        self._stop_event = threading.Event()
        self._accept_thread: Optional[threading.Thread] = None
        self._transmit_thread: Optional[threading.Thread] = None
        self.connected = False
        self.bytes_sent = 0
        self.last_error = None
        self.connection_state = "DISCONNECTED"

    def set_payload_builder(self, builder: Callable[[], dict]) -> None:
        self._payload_builder = builder

    def connect(self) -> bool:
        if self.connected:
            return True

        try:
            self._stop_event.clear()
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(1)
            self.connection_state = "LISTENING"
            self.last_error = None

            self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self._accept_thread.start()
            self._transmit_thread = threading.Thread(target=self._transmit_loop, daemon=True)
            self._transmit_thread.start()
            return True
        except OSError as exc:
            self.last_error = str(exc)
            self.connection_state = "ERROR"
            self.logger.exception("Unable to start virtual output port")
            return False

    def disconnect(self) -> None:
        self._stop_event.set()
        self.connection_state = "DISCONNECTED"

        for sock in (self._client_socket, self._server_socket):
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass

        self._client_socket = None
        self._server_socket = None
        self.connected = False

    def send_now(self, payload: Optional[dict] = None) -> bool:
        if self._client_socket is None:
            return False
        try:
            packet = self._build_packet(payload)
            self._client_socket.sendall(packet.encode())
            self.bytes_sent += len(packet.encode())
            return True
        except OSError as exc:
            self.last_error = str(exc)
            self.connected = False
            self.connection_state = "ERROR"
            self.logger.exception("Failed to send data packet")
            return False

    def status(self) -> dict:
        return {
            "connected": self.connected,
            "connection_state": self.connection_state,
            "host": self.host,
            "port": self.port,
            "mode": self.mode,
            "bytes_sent": self.bytes_sent,
            "last_error": self.last_error,
        }

    def _accept_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                if self._server_socket is None:
                    break
                self._server_socket.settimeout(0.5)
                client_socket, _ = self._server_socket.accept()
                self._client_socket = client_socket
                self.connected = True
                self.connection_state = "CONNECTED"
                self.logger.info("Virtual output client connected")
                break
            except socket.timeout:
                continue
            except OSError:
                break

    def _transmit_loop(self) -> None:
        while not self._stop_event.is_set():
            if self.connected and self._client_socket is not None:
                try:
                    payload = self._payload_builder() if self._payload_builder else {}
                    self.send_now(payload)
                except Exception as exc:  # pragma: no cover - defensive logging
                    self.last_error = str(exc)
                    self.connection_state = "ERROR"
                    self.logger.exception("Transmit loop failure")
            time.sleep(self.transmit_interval)

    def _build_packet(self, payload: Optional[dict] = None) -> DataPacket:
        if payload is None and self._payload_builder is not None:
            payload = self._payload_builder()
        if payload is None:
            payload = {}
        return DataPacket(device_id=self.device_id, payload=payload, mode=self.mode)


class ConnectionManager:
    """Simple wrapper to manage the virtual device output connection."""

    def __init__(self, port: VirtualDevicePort):
        self.port = port

    def connect(self) -> bool:
        return self.port.connect()

    def disconnect(self) -> None:
        self.port.disconnect()

    def send_now(self, payload: Optional[dict] = None) -> bool:
        return self.port.send_now(payload)

    def status(self) -> dict:
        return self.port.status()


class VirtualBoxConnector:
    """A generic connector that can be reused by other medical device simulators."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9000,
        device_id: str = "MEDCRT-01",
        mode: str = "ascii",
        transmit_interval: float = 1.0,
        logger: Optional[logging.Logger] = None,
    ):
        self.port = VirtualDevicePort(
            host=host,
            port=port,
            device_id=device_id,
            mode=mode,
            transmit_interval=transmit_interval,
            logger=logger,
        )
        self.connection_manager = ConnectionManager(self.port)

    def configure(self, host: Optional[str] = None, port: Optional[int] = None, transmit_interval: Optional[float] = None):
        if host is not None:
            self.port.host = host
        if port is not None:
            self.port.port = port
        if transmit_interval is not None:
            self.port.transmit_interval = transmit_interval

    def set_payload_builder(self, builder: Callable[[], dict]) -> None:
        self.port.set_payload_builder(builder)

    def connect(self) -> bool:
        return self.connection_manager.connect()

    def disconnect(self) -> None:
        self.connection_manager.disconnect()

    def send_now(self, payload: Optional[dict] = None) -> bool:
        return self.connection_manager.send_now(payload)

    def status(self) -> dict:
        return self.connection_manager.status()
