from __future__ import annotations

import random


class PressureModel:

    def __init__(self):

        self.access_pressure = -120
        self.return_pressure = 100
        self.filter_pressure = 180
        self.tmp = self.filter_pressure - self.return_pressure
        self.pressure_drop = self.filter_pressure - self.return_pressure
        self.clotting_risk = 0.0

    def update(self, patient, machine, filter_model):

        flow_factor = max(0.7, machine.blood_flow_rate / 150.0)
        overload_factor = max(0.0, patient.fluid_overload - 4.0)
        filter_factor = max(0.0, (100.0 - filter_model.health) / 100.0)

        self.access_pressure += random.randint(-4, 4) + int(overload_factor * 0.6)
        self.return_pressure += random.randint(-4, 4) + int(flow_factor * 1.5)
        self.filter_pressure += random.randint(-5, 5) + int(overload_factor * 1.2) + int(filter_factor * 16)

        self.access_pressure = max(-300, min(-30, self.access_pressure))
        self.return_pressure = max(10, min(250, self.return_pressure))
        self.filter_pressure = max(40, min(420, self.filter_pressure))

        self.tmp = self.filter_pressure - self.return_pressure
        self.pressure_drop = self.filter_pressure - self.return_pressure
        self.clotting_risk = max(0.0, min(100.0, (100.0 - filter_model.health) * 0.75 + max(0.0, self.tmp - 180) * 0.2))

    def get_snapshot(self):

        return {
            "access": self.access_pressure,
            "return": self.return_pressure,
            "filter": self.filter_pressure,
            "tmp": self.tmp,
            "pressure_drop": self.pressure_drop,
            "clotting_risk": round(self.clotting_risk, 1),
        }
