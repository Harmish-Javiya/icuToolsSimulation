import random
from core.central_patient_engine import CentralPatientEngine


class Patient:
    def __init__(self):
        # 1. CONNECT TO THE NETWORK BRAIN
        self.central_patient = CentralPatientEngine()

        # Device Parameters
        self.perfusion = 5.0
        self.signal_quality = 100
        self.battery = 100.0

        # Sensor States
        self.sensor_connected = True
        self.finger_present = True
        self.motion = False

        # Local fallback temperature
        self.local_temp = 36.8

    def update(self):
        # If no sensor or finger, return blank UI lines
        if not self.sensor_connected or not self.finger_present:
            return {
                "spo2": "--",
                "heart_rate": "--",
                "temperature": "--",
                "battery": round(self.battery, 1),
                "signal_quality": 0,
                "sensor_connected": self.sensor_connected,
                "finger_present": self.finger_present,
                "motion": self.motion
            }

        # 2. READ VITALS FROM THE NETWORK
        net_spo2 = self.central_patient.get("spo2")
        net_hr = self.central_patient.get("hr")
        net_temp = self.central_patient.get("temperature")

        # Use network data if available, otherwise use defaults
        current_spo2 = net_spo2 if net_spo2 is not None else 98.0
        current_hr = net_hr if net_hr is not None else 72.0
        current_temp = net_temp if net_temp is not None else self.local_temp

        # Motion artifact (Simulates the patient shaking their hand)
        # This adds noise to the UI, but does NOT change the global patient state!
        if self.motion:
            current_spo2 += random.uniform(-3, 3)
            current_hr += random.uniform(-8, 8)
            self.signal_quality = random.randint(30, 60)
        else:
            self.signal_quality = 100

        # Battery drain
        self.battery -= 0.01
        if self.battery <= 0:
            self.battery = 100

        # 3. RETURN DATA TO THE PYSIDE6 UI
        return {
            "spo2": round(current_spo2, 1),
            "heart_rate": round(current_hr),
            "temperature": round(current_temp, 1),
            "battery": round(self.battery, 1),
            "signal_quality": self.signal_quality,
            "sensor_connected": self.sensor_connected,
            "finger_present": self.finger_present,
            "motion": self.motion
        }

    # --------------------
    # Device Controls (These still work perfectly)
    # --------------------
    def toggle_sensor(self):
        self.sensor_connected = not self.sensor_connected

    def toggle_finger(self):
        self.finger_present = not self.finger_present

    def toggle_motion(self):
        self.motion = not self.motion

    # --------------------
    # Global Scenarios (BROADCASTING TO NETWORK)
    # --------------------
    def healthy(self):
        self.central_patient.update(source="PULSE_OX", vital="scenario", value="Healthy")

    def hypoxia(self):
        self.central_patient.update(source="PULSE_OX", vital="scenario", value="Hypoxia")

    def fever(self):
        self.central_patient.update(source="PULSE_OX", vital="scenario", value="Fever")
        self.local_temp = 39.2  # Local visual effect

    def shock(self):
        self.central_patient.update(source="PULSE_OX", vital="scenario", value="Shock")

    def child(self):
        pass

    def athlete(self):
        pass

    def recovery(self):
        pass