from enum import Enum
import random


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

        self.rhythm = Rhythm.NORMAL

        self.heart_rate = 75

        self.spo2 = 98

        self.systolic = 120

        self.diastolic = 80

    def set_rhythm(self, rhythm):

        self.rhythm = rhythm

        self.update_vitals()

    def update_vitals(self):

        r = self.rhythm

        if r == Rhythm.NORMAL:
            self.heart_rate = random.randint(60, 90)
            self.spo2 = random.randint(97, 100)
            self.systolic = random.randint(110, 130)
            self.diastolic = random.randint(70, 85)

        elif r == Rhythm.VF:
            self.heart_rate = 0
            self.spo2 = random.randint(50, 80)
            self.systolic = 0
            self.diastolic = 0

        elif r == Rhythm.VT:
            self.heart_rate = random.randint(150, 220)
            self.spo2 = random.randint(80, 95)
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

        if self.rhythm == Rhythm.VF:

            if random.random() < 0.75:
                self.rhythm = Rhythm.NORMAL

        elif self.rhythm == Rhythm.VT:

            if random.random() < 0.70:
                self.rhythm = Rhythm.NORMAL

        self.update_vitals()

    def status(self):

        return {

            "rhythm": self.rhythm.value,

            "heart_rate": self.heart_rate,

            "spo2": self.spo2,

            "bp": f"{self.systolic}/{self.diastolic}"

        }