from datetime import datetime

from src.device import Defibrillator
from src.patient import Patient
from src.ecg import ECG
from src.alarms import AlarmSystem
from src.hardware import HardwareInterface
from src.logger import DataLogger
from src.virtual_port import VirtualBoxConnector


class Simulator:

    def __init__(self):

        self.device = Defibrillator()
        self.patient = Patient()
        self.ecg = ECG()
        self.alarm = AlarmSystem()

        # --- PATCH 1: THE UNIFIED HARDWARE INITIALIZATION ---
        self.hardware = HardwareInterface(
            mode="Ethernet UDP",
            serial_port="/tmp/ttyV6",  # Unique virtual cable
            ip="127.0.0.1",
            net_port=8000               # Pointing to the Linux Master Aggregator
        )

        self.logger = DataLogger()

        self.virtual_connector = VirtualBoxConnector(device_id="MEDCRT-01", port=9000, transmit_interval=1.0)
        self.monitor_values = {
            "spo2": 98,
            "pulse_rate": 72,
            "perfusion_index": 1.8,
            "signal_strength": 95,
            "alarm_status": "OK",
        }

        self.hardware.connect()
        
        # --- PATCH 2: SECURING THE ARCHITECTURE ---
        # Commented out to prevent the "backdoor" secondary transmission
        # self.virtual_connector.set_payload_builder(self._build_monitor_payload)

        self.events = []

        self.update()

    ################################

    def add_event(self, text):

        self.events.append(text)

        if len(self.events) > 20:
            self.events.pop(0)

    ################################

    def update(self):

        self.patient.simulate()

        self.alarm.evaluate(
            self.device,
            self.patient
        )

    ################################

    def set_monitor_values(self, spo2, pulse_rate, perfusion_index, signal_strength, alarm_status):
        self.monitor_values = {
            "spo2": int(spo2),
            "pulse_rate": int(pulse_rate),
            "perfusion_index": float(perfusion_index),
            "signal_strength": int(signal_strength),
            "alarm_status": alarm_status,
        }
        self.add_event("Monitor values updated")
        return self.monitor_values

    ################################

    def _build_monitor_payload(self):
        payload = dict(self.monitor_values)
        payload.update({
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "device_type": "pulse_oximeter",
            "patient_rhythm": self.patient.rhythm.value,
            "heart_rate": self.patient.heart_rate,
        })
        return payload

    ################################

    def connect_virtual_output(self, host="0.0.0.0", port=9000, transmit_interval=1.0):
        # Disabled for security, returning True to keep UI happy
        # self.virtual_connector.configure(host=host, port=port, transmit_interval=transmit_interval)
        # return self.virtual_connector.connect()
        return True

    ################################

    def disconnect_virtual_output(self):
        # Disabled for security
        # self.virtual_connector.disconnect()
        pass

    ################################

    def transmit_virtual_output(self):
        # Disabled for security, returning True to keep UI happy
        # return self.virtual_connector.send_now(self._build_monitor_payload())
        return True

    ################################

    def charge(self):

        if self.device.charge():

            self.add_event(
                "Charging"
            )

            self.device.ready()

            self.add_event(
                "Ready To Shock"
            )

            self.update()

            self.logger.log_event(
                "CHARGE",
                self.device,
                self.patient,
                self.alarm
            )

    ################################

    def shock(self):

        if self.device.shock():

            self.patient.apply_shock(
                self.device.energy
            )

            self.add_event(
                "Shock Delivered"
            )

            self.update()

            self.logger.log_event(
                "SHOCK",
                self.device,
                self.patient,
                self.alarm
            )

    ################################

    def disarm(self):

        self.device.disarm()

        self.add_event(
            "Disarmed"
        )

        self.update()

    ################################

    def recharge(self):

        self.device.recharge()

        self.add_event(
            "Battery Recharged"
        )

        self.update()

    ################################

    def telemetry(self):

        self.hardware.send(
            self.device,
            self.patient,
            self.alarm
        )

    ################################

    def ecg_sample(self):

        return self.ecg.next_sample(
            self.patient.rhythm
        )

    ################################

    def status(self):

        return {

            "device":

            self.device.status(),

            "patient":

            self.patient.status(),

            "alarm":

            self.alarm.status(),
            "monitor":

            self.monitor_values,

            "virtual_output":

            self.virtual_connector.status(),

            "events":

            self.events

        }