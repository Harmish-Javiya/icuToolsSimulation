import random


class Patient:

    def __init__(self):

        # Vital Signs
        self.spo2 = 98
        self.heart_rate = 72
        self.temperature = 36.8

        # Device Parameters
        self.perfusion = 5.0
        self.signal_quality = 100
        self.battery = 100.0

        # Sensor States
        self.sensor_connected = True
        self.finger_present = True
        self.motion = False

    def update(self):

        # If no sensor or finger, no readings
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

        # Small natural variation
        self.spo2 += random.uniform(-0.2, 0.2)
        self.heart_rate += random.uniform(-1, 1)
        self.temperature += random.uniform(-0.05, 0.05)

        # Motion artifact
        if self.motion:
            self.spo2 += random.uniform(-2, 2)
            self.heart_rate += random.uniform(-5, 5)

        # Limits
        self.spo2 = max(70, min(100, self.spo2))
        self.heart_rate = max(30, min(220, self.heart_rate))
        self.temperature = max(30, min(42, self.temperature))

        # Battery drain
        self.battery -= 0.01
        if self.battery <= 0:
            self.battery = 100

        return {
            "spo2": round(self.spo2, 1),
            "heart_rate": round(self.heart_rate),
            "temperature": round(self.temperature, 1),
            "battery": round(self.battery, 1),
            "signal_quality": self.signal_quality,
            "sensor_connected": self.sensor_connected,
            "finger_present": self.finger_present,
            "motion": self.motion
        }

    # --------------------
    # Demo Scenarios
    # --------------------

    def healthy(self):
        self.spo2 = 98
        self.heart_rate = 72
        self.temperature = 36.8

    def hypoxia(self):
        self.spo2 = 84
        self.heart_rate = 115
        self.temperature = 37.0

    def fever(self):
        self.spo2 = 97
        self.heart_rate = 110
        self.temperature = 39.2

    def shock(self):
        self.spo2 = 86
        self.heart_rate = 130
        self.temperature = 35.5

    # --------------------
    # Device Controls
    # --------------------

    def toggle_sensor(self):
        self.sensor_connected = not self.sensor_connected

    def toggle_finger(self):
        self.finger_present = not self.finger_present

    def toggle_motion(self):
        self.motion = not self.motion

    def child(self):
        self.spo2 = 99
        self.heart_rate = 110
        self.temperature = 37.0

    def athlete(self):
        self.spo2 = 99
        self.heart_rate = 50
        self.temperature = 36.5

    def recovery(self):
        self.spo2 = 95
        self.heart_rate = 85
        self.temperature = 36.9