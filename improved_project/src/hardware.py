import json
from datetime import datetime


class HardwareInterface:

    def __init__(self):

        self.connected = False

        self.last_packet = None

    ###################################

    def connect(self):

        self.connected = True

    ###################################

    def disconnect(self):

        self.connected = False

    ###################################

    def create_packet(
        self,
        device,
        patient,
        alarm
    ):

        packet = {

            "timestamp":

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "device":

            device.status(),

            "patient":

            patient.status(),

            "alarm":

            alarm.status()

        }

        self.last_packet = packet

        return packet

    ###################################

    def send(
        self,
        device,
        patient,
        alarm
    ):

        if not self.connected:

            return False

        packet = self.create_packet(

            device,

            patient,

            alarm

        )

        print(

            "\n=== HARDWARE PACKET ==="

        )

        print(

            json.dumps(

                packet,

                indent=4

            )

        )

        print(

            "=======================\n"

        )

        return True

    ###################################

    def status(self):

        return {

            "connected":

            self.connected,

            "last_packet":

            self.last_packet

        }