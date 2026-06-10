import serial
import socket
import logging
import json
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HardwareInterface:
    """
    Manages outbound telemetry data to physical or virtual hardware ports.
    Supports RS-232 (Serial), USB (Serial), and Ethernet (UDP Socket).
    """

    def __init__(self, mode="RS232", serial_port="/tmp/ttyV0", baudrate=9600, ip="127.0.0.1", net_port=5005):
        self.mode = mode
        self.connection = None

        try:
            if self.mode in ["RS232", "USB"]:
                # Both RS232 and USB use serial communication
                self.connection = serial.Serial(serial_port, baudrate=baudrate, timeout=0)
                logger.info(f"✅ Hardware Connected: {self.mode} on {serial_port}")

            elif self.mode == "Ethernet":
                # Ethernet uses a UDP Network Socket for high-speed streaming
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.target_address = (ip, net_port)
                logger.info(f"✅ Hardware Connected: Ethernet broadcasting to {ip}:{net_port}")

        except Exception as e:
            logger.error(f"⚠️ Failed to connect {self.mode} hardware: {e}")
            self.connection = None


    #send data JSON Version

    def send_data(self, telemetry_dict: dict):
        """Formats the data and routes it through the active connection."""

        if not self.connection:
            return

        # Package the data as a JSON string with a newline terminator
        packet_string = json.dumps(telemetry_dict) + "\n"
        packet_bytes = packet_string.encode('utf-8')

        try:
            if self.mode in ["RS232", "USB"]:
                self.connection.write(packet_bytes)
            elif self.mode == "Ethernet":
                self.connection.sendto(packet_bytes, self.target_address)
        except Exception as e:
            logger.warning(f"Transmission error: {e}")


    """
    #send data ASCII Version
    def send_data(self, telemetry_dict: dict):
        Formats the data as a raw ASCII string and routes it to the port.
        if not self.connection:
            return

        # 1. Convert the alarms list into a simple binary status code
        # (e.g., 0 = Normal, 1 = Alarm Active)
        alarm_status = 1 if telemetry_dict["alarms"] else 0

        # 2. Format as a raw Comma-Separated ASCII string (Realistic RS-232 Format)
        # Format: $VENT, Time, Pressure, Flow, Volume, SpO2, AlarmStatus \r\n
        raw_string = (
            f"$VENT,"
            f"{telemetry_dict['time']:.1f},"
            f"{telemetry_dict['paw']:.1f},"
            f"{telemetry_dict['flow']:.2f},"
            f"{telemetry_dict['vol']:.0f},"
            f"{telemetry_dict['spo2']:.1f},"
            f"{alarm_status}\r\n"
        )

        # 3. Encode the raw text to bytes
        packet_bytes = raw_string.encode('ascii')

        try:
            if self.mode in ["RS232", "USB"]:
                self.connection.write(packet_bytes)
            elif self.mode == "Ethernet":
                self.connection.sendto(packet_bytes, self.target_address)
        except Exception as e:
            logger.warning(f"Transmission error: {e}")
    """

    def close(self):
        """Safely shuts down the port when switching modes."""
        if self.connection and self.mode in ["RS232", "USB"]:
            self.connection.close()
        elif self.connection and self.mode == "Ethernet":
            self.connection.close()