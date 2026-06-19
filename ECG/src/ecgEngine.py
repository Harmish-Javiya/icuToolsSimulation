import math
import random
import logging

# 1. IMPORT THE CENTRAL ENGINE
from core.central_patient_engine import CentralPatientEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ECGEngine:
    def __init__(self, heart_rate: float = 75.0):
        # 2. INITIALIZE CONNECTION TO SHARED PATIENT
        self.patient = CentralPatientEngine()

        self.target_hr = heart_rate
        self.current_hr = heart_rate
        self.time_passed = 0.0

        # Flag to prevent SpO2/ICP from overriding UI scenario buttons
        self.manual_override = False

        self.base_waves = {
            'P': (0.25, 0.04, -0.20),
            'Q': (-0.25, 0.02, -0.05),
            'R': (1.60, 0.03, 0.00),
            'S': (-0.50, 0.04, 0.06),
            'T': (0.35, 0.12, 0.30)
        }

        # The Complete 12-Lead Mathematical Vectors
        self.lead_vectors = {
            "Lead I": {'P': 0.6, 'Q': 0.8, 'R': 0.5, 'S': 0.3, 'T': 0.5},
            "Lead II": {'P': 1.0, 'Q': 1.0, 'R': 1.0, 'S': 1.0, 'T': 1.0},
            "Lead III": {'P': 0.4, 'Q': 0.2, 'R': 0.8, 'S': 1.2, 'T': 0.6},
            "Lead aVR": {'P': -1.0, 'Q': 0.0, 'R': -1.0, 'S': -1.0, 'T': -1.0},
            "Lead aVL": {'P': 0.3, 'Q': 0.5, 'R': 0.4, 'S': 0.2, 'T': 0.2},
            "Lead aVF": {'P': 0.8, 'Q': 0.6, 'R': 0.9, 'S': 0.8, 'T': 0.8},
            "Lead V1": {'P': -0.5, 'Q': 0.0, 'R': 0.2, 'S': 2.0, 'T': -0.4},
            "Lead V2": {'P': -0.2, 'Q': 0.0, 'R': 0.5, 'S': 1.5, 'T': 0.2},
            "Lead V3": {'P': 0.3, 'Q': 0.0, 'R': 1.0, 'S': 0.8, 'T': 0.6},
            "Lead V4": {'P': 0.6, 'Q': 0.5, 'R': 1.5, 'S': 0.4, 'T': 1.0},
            "Lead V5": {'P': 0.8, 'Q': 0.8, 'R': 1.2, 'S': 0.2, 'T': 0.9},
            "Lead V6": {'P': 0.8, 'Q': 1.2, 'R': 0.9, 'S': 0.2, 'T': 0.8}
        }

    def apply_intervention(self, scenario: str) -> None:
        scenario = scenario.lower()
        self.manual_override = True  # Lock out the auto-math so the button works

        if scenario == "tachycardia":
            self.target_hr = 160.0
        elif scenario == "bradycardia":
            self.target_hr = 35.0
        elif scenario == "asystole":
            self.target_hr = 0.0
        elif scenario == "reset":
            self.target_hr = 75.0
            self.manual_override = False  # Give control back to shared patient state

    def step(self, dt: float, active_leads: list) -> dict:
        self.time_passed += dt

        # 3. PHYSIOLOGICAL CROSS-TALK: REACT TO NETWORK SCENARIOS, LUNGS, AND BRAIN
        current_spo2 = self.patient.get("spo2")
        current_icp = self.patient.get("icp")
        global_scenario = self.patient.get("scenario")  # <-- NEW: Read the global scenario

        if not self.manual_override:
            # ---------------------------------------------------------
            # STEP A: BASELINE SHIFT FROM GLOBAL SCENARIOS
            # ---------------------------------------------------------
            calculated_hr = 75.0
            if global_scenario in ["Hemorrhage", "Shock"]:
                calculated_hr = 120.0
            elif global_scenario in ["Sepsis", "Fever"]:
                calculated_hr = 110.0
            elif global_scenario == "Heart Failure":
                calculated_hr = 105.0
            elif global_scenario == "Hypoxia":
                calculated_hr = 130.0  # Extreme compensatory tachycardia
            elif global_scenario == "Arrest":
                calculated_hr = 0.0
                self.rhythm = "Asystole"
            else:
                self.rhythm = "NSR"

            # ---------------------------------------------------------
            # STEP B: HYPOXIA RESPONSE (LUNGS)
            # ---------------------------------------------------------
            if current_spo2 is not None and global_scenario != "Arrest":
                if 80 <= current_spo2 < 92:
                    # Compensatory Tachycardia
                    calculated_hr += ((92 - current_spo2) * 3)
                elif current_spo2 < 80:
                    # Hypoxic Bradycardia
                    calculated_hr -= ((80 - current_spo2) * 5)

            # ---------------------------------------------------------
            # STEP C: CUSHING'S TRIAD (BRAIN)
            # ---------------------------------------------------------
            if current_icp is not None and current_icp > 15.0 and global_scenario != "Arrest":
                # Subtract 2.5 bpm for every 1 mmHg of pressure over 15
                calculated_hr -= (current_icp - 15.0) * 2.5

            # Clamp the final heart rate to realistic human limits
            self.target_hr = max(30.0, min(220.0, calculated_hr)) if global_scenario != "Arrest" else 0.0

        # Smoothly transition current HR toward target HR
        self.current_hr += (self.target_hr - self.current_hr) * (dt * 0.5)

        # 4. PUBLISH BACK TO GLOBAL STATE
        # Hemodynamics relies on this to calculate Blood Pressure!
        self.patient.update(
            source="ECG",
            vital="hr",
            value=round(self.current_hr, 1)
        )

        beat_duration = 60.0 / max(0.1, self.current_hr)
        time_in_beat = self.time_passed % beat_duration
        t_relative = time_in_beat - (beat_duration * 0.3)
        baseline_wander = 0.15 * math.sin(self.time_passed * 0.5)

        results = {"hr": round(self.current_hr, 1), "voltages": {}}

        for lead in active_leads:
            if self.current_hr <= 0.5:
                results["voltages"][lead] = round(random.gauss(0, 0.05), 3)
                continue

            voltage = 0.0
            multipliers = self.lead_vectors.get(lead, self.lead_vectors["Lead II"])

            for wave, (base_amp, width, center) in self.base_waves.items():
                mod_amp = base_amp * multipliers[wave]
                voltage += mod_amp * math.exp(-((t_relative - center) ** 2) / (2 * width ** 2))

            results["voltages"][lead] = round(voltage + baseline_wander + random.gauss(0, 0.02), 3)

        return results