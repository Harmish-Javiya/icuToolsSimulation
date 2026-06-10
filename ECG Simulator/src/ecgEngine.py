import math
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ECGEngine:
    def __init__(self, heart_rate: float = 75.0):
        self.target_hr = heart_rate
        self.current_hr = heart_rate
        self.time_passed = 0.0

        self.base_waves = {
            'P': (0.25, 0.04, -0.20),
            'Q': (-0.25, 0.02, -0.05),
            'R': (1.60, 0.03, 0.00),
            'S': (-0.50, 0.04, 0.06),
            'T': (0.35, 0.12, 0.30)
        }

        # The Complete 12-Lead Mathematical Vectors
        self.lead_vectors = {
            "Lead I":   {'P': 0.6,  'Q': 0.8,  'R': 0.5,  'S': 0.3,  'T': 0.5},
            "Lead II":  {'P': 1.0,  'Q': 1.0,  'R': 1.0,  'S': 1.0,  'T': 1.0},
            "Lead III": {'P': 0.4,  'Q': 0.2,  'R': 0.8,  'S': 1.2,  'T': 0.6},
            "Lead aVR": {'P': -1.0, 'Q': 0.0,  'R': -1.0, 'S': -1.0, 'T': -1.0},
            "Lead aVL": {'P': 0.3,  'Q': 0.5,  'R': 0.4,  'S': 0.2,  'T': 0.2},
            "Lead aVF": {'P': 0.8,  'Q': 0.6,  'R': 0.9,  'S': 0.8,  'T': 0.8},
            "Lead V1":  {'P': -0.5, 'Q': 0.0,  'R': 0.2,  'S': 2.0,  'T': -0.4},
            "Lead V2":  {'P': -0.2, 'Q': 0.0,  'R': 0.5,  'S': 1.5,  'T': 0.2},
            "Lead V3":  {'P': 0.3,  'Q': 0.0,  'R': 1.0,  'S': 0.8,  'T': 0.6},
            "Lead V4":  {'P': 0.6,  'Q': 0.5,  'R': 1.5,  'S': 0.4,  'T': 1.0},
            "Lead V5":  {'P': 0.8,  'Q': 0.8,  'R': 1.2,  'S': 0.2,  'T': 0.9},
            "Lead V6":  {'P': 0.8,  'Q': 1.2,  'R': 0.9,  'S': 0.2,  'T': 0.8}
        }

    def apply_intervention(self, scenario: str) -> None:
        scenario = scenario.lower()
        if scenario == "tachycardia": self.target_hr = 160.0
        elif scenario == "bradycardia": self.target_hr = 35.0
        elif scenario == "asystole": self.target_hr = 0.0
        elif scenario == "reset": self.target_hr = 75.0

    def step(self, dt: float, active_leads: list) -> dict:
        self.time_passed += dt
        self.current_hr += (self.target_hr - self.current_hr) * (dt * 0.5)

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