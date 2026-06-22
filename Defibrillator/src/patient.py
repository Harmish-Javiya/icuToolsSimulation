from enum import Enum
import random

# 1. CONNECT TO THE NETWORK
from core.central_patient_engine import CentralPatientEngine


class Rhythm(Enum):
    NORMAL = "Normal Sinus"
    VF = "Ventricular Fibrillation"
    VT = "Ventricular Tachycardia"
    SVT = "SVT"
    BRADY = "Bradycardia"
    TACHY = "Tachycardia"
    PEA = "PEA"
    ASYSTOLE = "Asystole"


class Patient:
    def __init__(self):
        self.net = CentralPatientEngine()
        self.current_scenario = "Healthy"
        self.rhythm = Rhythm.NORMAL

        self.heart_rate = 75
        self.spo2 = 98
        self.systolic = 120
        self.diastolic = 80

    def set_rhythm(self, rhythm):
        self.rhythm = rhythm
        if rhythm in [Rhythm.VF, Rhythm.VT, Rhythm.ASYSTOLE, Rhythm.PEA]:
            self.current_scenario = "Arrest"
            self.net.update(source="DEFIB", vital="scenario", value="Arrest")
        elif rhythm == Rhythm.NORMAL:
            self.current_scenario = "Healthy"
            self.net.update(source="DEFIB", vital="scenario", value="Healthy")
        self.update_vitals()

    def update_vitals(self):
        # LISTEN TO SCENARIO
        net_scenario = self.net.get("scenario")
        if net_scenario is not None and net_scenario != self.current_scenario:
            self.current_scenario = net_scenario
            if net_scenario == "Arrest":
                self.rhythm = random.choice([Rhythm.VF, Rhythm.ASYSTOLE])
            elif net_scenario in ["Hemorrhage", "Shock", "Sepsis", "Fever"]:
                self.rhythm = Rhythm.TACHY
            elif net_scenario == "Healthy":
                self.rhythm = Rhythm.NORMAL

        # === THE FIX: READ EXACT BP, HR, AND SPO2 FROM HEMODYNAMICS / NETWORK ===
        net_hr = self.net.get("hr")
        net_spo2 = self.net.get("spo2")
        net_sys = self.net.get("bp_sys")  # Pulled directly from Hemodynamics!
        net_dia = self.net.get("bp_dia")  # Pulled directly from Hemodynamics!

        # Convert to integers for a clean display, defaulting to healthy baseline if network is offline
        self.heart_rate = int(net_hr) if net_hr is not None else 75
        self.spo2 = int(net_spo2) if net_spo2 is not None else 98
        self.systolic = int(net_sys) if net_sys is not None else 120
        self.diastolic = int(net_dia) if net_dia is not None else 80

        # === LOCAL OVERRIDE FOR LETHAL RHYTHMS ===
        r = self.rhythm
        if r == Rhythm.VF:
            self.heart_rate = 0
            self.spo2 = random.randint(50, 80)
            self.systolic = 0
            self.diastolic = 0
        elif r == Rhythm.VT:
            self.heart_rate = random.randint(150, 220)
            self.systolic = random.randint(70, 100)
            self.diastolic = random.randint(40, 60)
        elif r == Rhythm.ASYSTOLE:
            self.heart_rate = 0
            self.spo2 = 0
            self.systolic = 0
            self.diastolic = 0

    def simulate(self):
        self.update_vitals()

    def apply_shock(self, energy):
        if self.rhythm in [Rhythm.VF, Rhythm.VT]:
            if random.random() < 0.75:
                self.rhythm = Rhythm.NORMAL
                self.current_scenario = "Healthy"
                self.net.update(source="DEFIB", vital="scenario", value="Healthy")
        self.update_vitals()

    def status(self):
        return {
            "rhythm": self.rhythm.value,
            "heart_rate": self.heart_rate,
            "spo2": self.spo2,
            "bp": f"{self.systolic}/{self.diastolic}",
            "scenario": self.current_scenario
        }