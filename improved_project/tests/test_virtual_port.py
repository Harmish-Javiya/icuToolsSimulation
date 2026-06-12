import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.virtual_port import DataPacket


class DataPacketTests(unittest.TestCase):
    def test_ascii_packet_round_trip(self):
        packet = DataPacket(
            device_id="PULSE-01",
            payload={"spo2": 98, "pulse_rate": 72, "alarm": "OK"},
            mode="ascii",
        )

        encoded = packet.encode()
        decoded = DataPacket.decode(encoded)

        self.assertEqual(decoded.device_id, "PULSE-01")
        self.assertEqual(decoded.payload["spo2"], 98)
        self.assertEqual(decoded.payload["pulse_rate"], 72)
        self.assertEqual(decoded.payload["alarm"], "OK")


if __name__ == "__main__":
    unittest.main()
