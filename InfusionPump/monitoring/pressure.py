import random


class PressureMonitor:

    def __init__(self):
        self.pressure = 100.0

    def get_pressure(self, global_map=90.0, flow_rate=0.0):
        # Base pressure is the patient's venous/arterial resistance (MAP)
        # Higher flow rates increase the line pressure slightly due to fluid resistance
        resistance = (flow_rate / 100.0) * 15.0

        # Add a small amount of physiological/sensor noise
        noise = random.uniform(-3.0, 3.0)

        self.pressure = global_map + resistance + noise

        return self.pressure