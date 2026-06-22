from __future__ import annotations

import random
from dataclasses import dataclass, asdict

@dataclass
class PatientModel:
    hr: float = 80
    bp_sys: float = 120
    bp_dia: float = 80
    spo2: float = 98
    temperature: float = 37.0
    respiratory_rate: float = 16
    bun: float = 80.0
    creatinine: float = 6.0
    potassium: float = 6.2
    sodium: float = 140.0
    hemoglobin: float = 11.0
    fluid_overload: float = 5.0

    def clamp(self):
        self.hr = max(30, min(220, float(self.hr)))
        self.bp_sys = max(40, min(240, float(self.bp_sys)))
        self.bp_dia = max(20, min(160, float(self.bp_dia)))
        self.spo2 = max(50, min(100, float(self.spo2)))
        self.temperature = round(max(33.0, min(42.5, float(self.temperature))), 1)
        self.respiratory_rate = max(4, min(50, float(self.respiratory_rate)))
        self.bun = max(0, min(220, float(self.bun)))
        self.creatinine = max(0, min(20, float(self.creatinine)))
        self.potassium = max(2.0, min(8.5, float(self.potassium)))
        self.sodium = max(120, min(165, float(self.sodium)))
        self.hemoglobin = max(4.0, min(20.0, float(self.hemoglobin)))
        self.fluid_overload = max(0.0, min(20.0, float(self.fluid_overload)))

    def set_field(self, name, value):
        if not hasattr(self, name):
            raise AttributeError(name)
        setattr(self, name, float(value))
        self.clamp()

    def apply_controls(self, updates):
        for name, value in updates.items():
            if hasattr(self, name):
                setattr(self, name, float(value))
        self.clamp()

    def step(self, machine, fluid, pressure, filter_model):
        # NOTE: HR, BP, SpO2, RR, and Temp drift removed.
        # These are now synced dynamically from the Central Server!

        if machine.running:
            therapy_factor = max(0.35, min(1.4, machine.blood_flow_rate / 150.0))
            clearance = 0.6 * therapy_factor
            self.bun -= random.uniform(0.45, 0.95) * clearance
            self.creatinine -= random.uniform(0.02, 0.06) * clearance
            self.potassium -= random.uniform(0.01, 0.05) * clearance
            self.fluid_overload -= random.uniform(0.03, 0.08) * max(0.5, machine.ultrafiltration_rate / 100.0)
            self.hemoglobin -= random.uniform(0.0, 0.03)
            self.sodium += random.uniform(-0.2, 0.2)
            fluid.add_intake(random.uniform(5, 12))
            fluid.add_output(random.uniform(18, 35))
        else:
            self.bun += random.uniform(0.2, 0.6)
            self.creatinine += random.uniform(0.02, 0.06)
            self.potassium += random.uniform(0.01, 0.04)
            self.fluid_overload += random.uniform(0.0, 0.03)
            self.hemoglobin += random.uniform(-0.01, 0.01)
            fluid.add_intake(random.uniform(8, 16))
            fluid.add_output(random.uniform(4, 10))

        # We keep the physiological fluid shifts.
        # These will reflect on the UI between server ticks.
        self.bp_sys -= min(18, self.fluid_overload * 0.9)
        self.bp_dia -= min(10, self.fluid_overload * 0.45)
        self.spo2 -= max(0.0, (self.fluid_overload - 6) * 0.08)
        self.respiratory_rate += max(0.0, self.fluid_overload - 5) * 0.05

        if filter_model.health < 35:
            self.bun += 0.25
            self.creatinine += 0.05
            self.potassium += 0.02

        self.clamp()

    def get_snapshot(self):
        data = asdict(self)
        data["blood_pressure"] = f"{int(round(self.bp_sys))}/{int(round(self.bp_dia))}"
        data["map"] = round((2 * self.bp_dia + self.bp_sys) / 3.0, 1)
        return data