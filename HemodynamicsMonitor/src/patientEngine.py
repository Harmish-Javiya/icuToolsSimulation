import random
from core.central_patient_engine import CentralPatientEngine


class PatientEngine:

    def __init__(self):
        # 1. CONNECT TO THE NETWORK
        self.net = CentralPatientEngine()

        self.fluid_effect = 0.0
        self.norad_effect = 0.0
        self.blood_effect = 0.0
        self.cpr_effect = 0.0

        # === THE FIX: Give it baseline values before the network connects! ===
        self.hr = 75.0
        self.spo2 = 98.0
        self.rr = 16.0
        # =====================================================================

        self.currentScenario = "Healthy"
        self.disease_time = 0
        self.setScenario("Healthy")

    def update_calculated(self):
        self.map = round((self.sbp + 2 * self.dbp) / 3, 1)
        self.co = round((self.hr * self.sv) / 1000, 2)

    def update(self):
        self.disease_time += 1

        # 2. READ NETWORK VITALS
        net_hr = self.net.get("hr")
        net_spo2 = self.net.get("spo2")
        net_rr = self.net.get("rr")

        # Properly apply the network SpO2 so it displays on the screen
        if net_hr is not None: self.hr = net_hr
        if net_spo2 is not None: self.spo2 = net_spo2
        if net_rr is not None: self.rr = net_rr

        # --- NEW: LISTEN FOR GLOBAL SCENARIO CHANGES ---
        net_scenario = self.net.get("scenario")
        if net_scenario is not None and net_scenario != self.currentScenario:
            self.currentScenario = net_scenario

            # Apply the Hemodynamics for the incoming network scenario!
            if net_scenario in ["Hemorrhage", "Shock"]:
                self.sbp, self.dbp, self.sv, self.cvp = 85, 50, 45, 3
            elif net_scenario in ["Sepsis", "Fever"]:
                self.sbp, self.dbp, self.sv, self.cvp = 90, 55, 80, 5
            elif net_scenario == "Heart Failure":
                self.sbp, self.dbp, self.sv, self.cvp = 100, 65, 40, 16
            elif net_scenario == "Arrest":
                self.sbp, self.dbp, self.sv, self.cvp = 0, 0, 0, 0
            elif net_scenario == "Healthy":
                self.sbp, self.dbp, self.sv, self.cvp = 120, 80, 70, 8
        # -----------------------------------------------

        if self.currentScenario != "Arrest":
            # Apply natural physiological drift
            self.sbp += random.randint(-1, 1)
            self.dbp += random.randint(-1, 1)
            self.sv += random.uniform(-0.5, 0.5)
            self.cvp += random.uniform(-0.2, 0.2)

            # Clamp local values to realistic limits
            self.sbp = max(0, min(220, self.sbp))
            self.dbp = max(0, min(150, self.dbp))
            self.sv = max(0, min(120, self.sv))
            self.cvp = max(0, min(20, self.cvp))

        self.update_calculated()

        # 3. PUBLISH HEMODYNAMIC VITALS TO NETWORK (Owned by HEMO)
        self.net.update(source="HEMO", vital="bp_sys", value=self.sbp)
        self.net.update(source="HEMO", vital="bp_dia", value=self.dbp)
        self.net.update(source="HEMO", vital="map", value=self.map)
        self.net.update(source="HEMO", vital="co", value=self.co)

    def setScenario(self, scenario):
        self.currentScenario = scenario
        self.disease_time = 0

        # === CRITICAL UPDATE ===
        # Tell the Server what scenario we clicked so ECG and Ventilator react!
        self.net.update(source="HEMO", vital="scenario", value=scenario)

        if scenario == "Healthy":
            self.sbp = 120
            self.dbp = 80
            self.sv = 70
            self.cvp = 8
        elif scenario == "Hemorrhage":
            self.sbp = 85
            self.dbp = 50
            self.sv = 45
            self.cvp = 3
        elif scenario == "Sepsis":
            self.sbp = 90
            self.dbp = 55
            self.sv = 80
            self.cvp = 5
        elif scenario == "Heart Failure":
            self.sbp = 100
            self.dbp = 65
            self.sv = 40
            self.cvp = 16
        elif scenario == "Arrest":
            self.sbp = 0
            self.dbp = 0
            self.sv = 0
            self.cvp = 0

        self.update_calculated()

    def get_vitals(self):
        return {
            "HR": self.hr,
            "SBP": round(self.sbp),
            "DBP": round(self.dbp),
            "MAP": round(self.map),
            "CO": round(self.co, 1),
            "SV": round(self.sv, 1),
            "CVP": round(self.cvp, 1),
            "RR": round(self.rr),
            "SpO2": round(self.spo2),
            "Scenario": self.currentScenario,
            "Alarm": self.get_alarm(),
            "Time": self.disease_time,
            "Fluid": round(self.fluid_effect, 2),
            "Blood": round(self.blood_effect, 2),
            "Norad": round(self.norad_effect, 2),
        }

    # ... (Keep all your therapy engine bolus defs exactly the same)
    def fluid_bolus(self):
        self.fluid_effect += 1
        if self.fluid_effect > 0:
            self.sbp += 0.5
            self.dbp += 0.3
            self.cvp += 0.2
            self.fluid_effect = max(0, self.fluid_effect - 0.02)

    def blood_transfusion(self):
        self.blood_effect += 1
        if self.blood_effect > 0:
            self.sbp += 0.4
            self.dbp += 0.3
            self.sv += 0.2
            self.blood_effect = max(0, self.blood_effect - 0.02)

    def noradrenaline(self):
        self.norad_effect += 1
        if self.norad_effect > 0:
            self.sbp += 0.7
            self.dbp += 0.5
            self.norad_effect = max(0, self.norad_effect - 0.01)

    def cpr(self):
        self.cpr_effect = 1
        if self.currentScenario == "Arrest":
            if self.cpr_effect > 0:
                self.hr = 40
                self.sbp = 60
                self.dbp = 30

    def get_alarm(self):
        if self.hr == 0: return "CARDIAC ARREST"
        if self.map < 65: return "LOW MAP"
        if self.sbp < 90: return "LOW BP"
        if self.hr > 120: return "HIGH HR"
        if self.hr < 50: return "LOW HR"
        if self.spo2 < 90: return "LOW SAT"
        if self.co < 3: return "LOW CO"
        return "NORMAL"