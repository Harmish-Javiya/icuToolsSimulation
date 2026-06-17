from __future__ import annotations

import random


class FilterModel:

    def __init__(self):

        self.health = 100.0
        self.clotting_rate = 0.08
        self.status = "Healthy"
        self.pressure_drop = 0.0
        self.clotting_risk = 0.0

    def update(self, patient, pressure, machine):

        wear = random.uniform(self.clotting_rate, self.clotting_rate + 0.22)
        wear += max(0.0, pressure.tmp - 180) * 0.004
        wear += max(0.0, patient.potassium - 5.5) * 0.02

        if machine.running:
            wear += 0.03

        self.health = max(0.0, self.health - wear)
        self.pressure_drop = pressure.pressure_drop
        self.clotting_risk = max(0.0, min(100.0, (100.0 - self.health) * 0.8 + max(0.0, pressure.tmp - 160) * 0.15))
        self.update_status()

    def update_status(self):

        if self.health >= 75:
            self.status = "Healthy"
        elif self.health >= 45:
            self.status = "Warning"
        elif self.health >= 20:
            self.status = "Critical"
        else:
            self.status = "Replace Filter"

    def replace_filter(self):

        self.health = 100.0
        self.status = "Healthy"
        self.clotting_risk = 0.0

    def get_snapshot(self):

        return {
            "health": round(self.health, 2),
            "status": self.status,
            "pressure_drop": round(self.pressure_drop, 2),
            "clotting_risk": round(self.clotting_risk, 1),
        }
