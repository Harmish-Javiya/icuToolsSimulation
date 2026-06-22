from core.state_machine import StateMachine, PumpState
from core.event_logger import EventLogger
from monitoring.pressure import PressureMonitor
from monitoring.battery import BatteryMonitor
from monitoring.air_detector import AirDetector
from monitoring.door_sensor import DoorSensor
from monitoring.occlusion import OcclusionDetector
from alarms.alarm_manager import AlarmManager

# ---> IMPORT THE SHARED HARDWARE ENGINE <---
# (Adjust this import path if the file is in a different folder, e.g., 'from core.shared_hardware_engine...')
from shared_hardware_engine import UnifiedHardwareEngine

class PumpController:

    def __init__(self):
        self.flow_rate = 100.0
        self.vtbi = 50.0
        self.infused = 0.0
        self.completed = False
        self.kvo_enabled = False
        self.kvo_rate = 1.0
        self.bolus_active = False
        self.previous_flow_rate = 0.0

        self.state_machine = StateMachine()
        self.logger = EventLogger()
        self.alarm_manager = AlarmManager()
        self.pressure_monitor = PressureMonitor()
        self.battery_monitor = BatteryMonitor()
        self.air_detector = AirDetector()
        self.door_sensor = DoorSensor()
        self.occlusion_detector = OcclusionDetector()

        # ---> INITIALIZE THE UNIFIED HARDWARE ENGINE <---
        self.hardware = UnifiedHardwareEngine(
            mode="Ethernet UDP",
            network_protocol="UDP",
            ip="127.0.0.1",
            net_port=8000,
            device_name="InfusionPump",
            auto_connect=True
        )

    @property
    def remaining(self):
        return max(0, self.vtbi - self.infused)

    def set_parameters(self, flow_rate, vtbi):
        self.flow_rate = flow_rate
        self.vtbi = vtbi

    def start(self):
        self.state_machine.set_state(PumpState.RUNNING)
        self.logger.add_event("Pump Started")

    def pause(self):
        self.state_machine.set_state(PumpState.PAUSED)
        self.logger.add_event("Pump Paused")

    def stop(self):
        self.state_machine.set_state(PumpState.STOPPED)

    def reset(self):
        self.infused = 0
        self.state_machine.set_state(PumpState.IDLE)

    def get_state(self):
        return self.state_machine.get_state()

    def enter_kvo(self):
        self.flow_rate = self.kvo_rate
        self.logger.add_event("Entered KVO Mode")

    def start_bolus(self, bolus_rate=300):
        self.previous_flow_rate = self.flow_rate
        self.flow_rate = bolus_rate
        self.bolus_active = True
        self.logger.add_event("Bolus Started")

    def stop_bolus(self):
        if self.bolus_active:
            self.flow_rate = self.previous_flow_rate
            self.bolus_active = False
            self.logger.add_event("Bolus Stopped")

    def publish_snapshot(self):
        snapshot = {
            "device_id": "PUMP-MED-01",
            "state": self.state_machine.get_state().value,
            "flow_rate": round(self.flow_rate, 2),
            "vtbi": round(self.vtbi, 2),
            "infused": round(self.infused, 3),
            "remaining": round(self.remaining, 3),
            "pressure": round(self.pressure_monitor.pressure, 1),
            "battery": round(self.battery_monitor.level, 1)
        }

        try:
            # Your shared engine handles the JSON dumps internally inside _packet_bytes()!
            self.hardware.send_data(snapshot)
        except Exception:
            pass