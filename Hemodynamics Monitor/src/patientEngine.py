import random


class PatientEngine:

    def __init__(self):

        self.fluid_effect = 0.0
        self.norad_effect = 0.0
        self.blood_effect = 0.0
        self.cpr_effect = 0.0

        self.currentScenario = "Healthy"
        self.disease_time = 0
        self.setScenario("Healthy")

    def update_calculated(self):

        self.map = round((self.sbp + 2 * self.dbp) / 3, 1)

        self.co = round((self.hr * self.sv) / 1000, 2)

    def update(self):
        self.disease_time += 1

        if self.currentScenario != "Arrest":

            self.hr += random.randint(-1, 1)
            self.sbp += random.randint(-1, 1)
            self.dbp += random.randint(-1, 1)

            self.sv += random.uniform(-0.5, 0.5)
            self.cvp += random.uniform(-0.2, 0.2)

            self.rr += random.choice([-1, 0, 1])

            self.spo2 += random.choice([0, 0, 0, 1, -1])

            self.hr = max(0, min(180, self.hr))
            self.sbp = max(0, min(220, self.sbp))
            self.dbp = max(0, min(150, self.dbp))

            self.sv = max(0, min(120, self.sv))
            self.cvp = max(0, min(20, self.cvp))

            self.rr = max(0, min(40, self.rr))
            self.spo2 = max(0, min(100, self.spo2))

        self.update_calculated()

    def setScenario(self, scenario):

        self.currentScenario = scenario
        self.disease_time = 0

        if scenario == "Healthy":

            self.hr = 75
            self.sbp = 120
            self.dbp = 80
            self.sv = 70
            self.cvp = 8
            self.rr = 16
            self.spo2 = 98

        elif scenario == "Hemorrhage":

            self.hr = 120
            self.sbp = 85
            self.dbp = 50
            self.sv = 45
            self.cvp = 3
            self.rr = 24
            self.spo2 = 94

        elif scenario == "Sepsis":

            self.hr = 110
            self.sbp = 90
            self.dbp = 55
            self.sv = 80
            self.cvp = 5
            self.rr = 26
            self.spo2 = 95

        elif scenario == "Heart Failure":

            self.hr = 105
            self.sbp = 100
            self.dbp = 65
            self.sv = 40
            self.cvp = 16
            self.rr = 22
            self.spo2 = 93

        elif scenario == "Arrest":

            self.hr = 0
            self.sbp = 0
            self.dbp = 0
            self.sv = 0
            self.cvp = 0
            self.rr = 0
            self.spo2 = 0

        self.update_calculated()

    def get_vitals(self):

        return {

            "HR": self.hr,

            "SBP": self.sbp,

            "DBP": self.dbp,

            "MAP": self.map,

            "CO": self.co,

            "SV": round(self.sv, 1),

            "CVP": round(self.cvp, 1),

            "RR": self.rr,

            "SpO2": self.spo2,

            "Scenario": self.currentScenario,

            "Alarm": self.get_alarm(),

            "Time": self.disease_time,

            "Fluid": round(self.fluid_effect, 2),

            "Blood": round(self.blood_effect, 2),

            "Norad": round(self.norad_effect, 2),
        }

    # FIX: fluid_bolus, blood_transfusion, noradrenaline had self.fluid/blood/norad
    #      which don't exist — they should decrement the effect counters instead.
    def fluid_bolus(self):

        self.fluid_effect += 1
        if self.fluid_effect > 0:

            self.sbp += 0.5
            self.dbp += 0.3
            self.cvp += 0.2

            self.fluid_effect = max(0, self.fluid_effect - 0.02)  # FIX

    def blood_transfusion(self):

        self.blood_effect += 1
        if self.blood_effect > 0:

            self.sbp += 0.4
            self.dbp += 0.3
            self.sv += 0.2

            self.blood_effect = max(0, self.blood_effect - 0.02)  # FIX

    def noradrenaline(self):

        self.norad_effect += 1
        if self.norad_effect > 0:

            self.sbp += 0.7
            self.dbp += 0.5

            self.norad_effect = max(0, self.norad_effect - 0.01)  # FIX

    def cpr(self):
        self.cpr_effect = 1

        if self.currentScenario == "Arrest":
            if self.cpr_effect > 0:
                self.hr = 40
                self.sbp = 60
                self.dbp = 30

    def get_alarm(self):

        if self.hr == 0:
            return "CARDIAC ARREST"

        if self.map < 65:
            return "LOW MAP"

        if self.sbp < 90:
            return "LOW BP"

        if self.hr > 120:
            return "HIGH HR"

        if self.hr < 50:
            return "LOW HR"

        if self.spo2 < 90:
            return "LOW SAT"

        if self.co < 3:
            return "LOW CO"

        return "NORMAL"

    # FIX: import json was misplaced inside class body — moved out (not needed here anyway)
    def loadCase(self, case):

        self.hr = case["hr"]
        self.sbp = case["sbp"]
        self.dbp = case["dbp"]
        self.sv = case["sv"]
        self.cvp = case["cvp"]
        self.rr = case["rr"]
        self.spo2 = case["spo2"]
        self.currentScenario = case["name"]

        self.update_calculated()
