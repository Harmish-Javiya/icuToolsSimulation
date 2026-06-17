from datetime import datetime
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared_hardware_engine import UnifiedHardwareEngine


class HardwareInterface(UnifiedHardwareEngine):
    """
    Defibrillator telemetry adapter.

    Existing simulator calls are preserved:
    connect(), disconnect(), send(device, patient, alarm), and status().
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("mode", "Console")
        kwargs.setdefault("net_port", 5007)
        kwargs.setdefault("device_name", "Defibrillator")
        super().__init__(*args, **kwargs)

    def create_packet(self, device, patient, alarm):
        packet = {
            "device_id": "DEFIB-CARDIO-01",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "device": device.status(),
            "patient": patient.status(),
            "alarm": alarm.status(),
        }
        self.last_packet = packet
        return packet

    def send(self, device, patient=None, alarm=None):
        if patient is None or alarm is None:
            self.send_data(device)
            return True

        if not self.connected:
            return False

        packet = self.create_packet(device, patient, alarm)
        self.send_data(packet)

        print("\n=== HARDWARE PACKET ===")
        print(json.dumps(packet, indent=4))
        print("=======================\n")

        return True
