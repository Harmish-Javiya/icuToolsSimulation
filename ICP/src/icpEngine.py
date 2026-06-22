import math
import random
import logging

# 1. IMPORT CENTRAL ENGINE
from core.central_patient_engine import CentralPatientEngine

logger = logging.getLogger(__name__)


class ICPEngine:
    def __init__(self, base_icp: float = 10.0):
        # 2. CONNECT TO NETWORK
        self.patient = CentralPatientEngine()

        self.target_icp = base_icp
        self.current_icp = base_icp
        self.time_passed = 0.0
        self.current_scenario = "Healthy"

    def apply_intervention(self, scenario: str) -> None:
        """
        Triggered by UI buttons.
        """
        # === THE FIX: BROADCAST SCENARIO TO NETWORK ===
        self.patient.update(source="NEURO", vital="scenario", value=scenario)
        self.current_scenario = scenario

        # Internal physics response
        if scenario == "normal_neuro":
            self.target_icp = 10.0
        elif scenario == "mild_swelling":
            self.target_icp = 18.0
        elif scenario == "brain_swelling":
            self.target_icp = 35.0  # Massive herniation
        elif scenario == "treatment_hyperventilation":
            self.target_icp = 12.0
        elif scenario == "treatment_drain_csf":
            self.target_icp = 8.0
        elif scenario == "treatment_mannitol":
            self.target_icp = 14.0

    def step(self, dt: float) -> dict:
        self.time_passed += dt

        # === THE FIX: LISTEN FOR GLOBAL SCENARIOS ===
        net_scenario = self.patient.get("scenario")
        if net_scenario is not None and net_scenario != self.current_scenario:
            self.current_scenario = net_scenario

            # React to Hemodynamics/Shock scenarios
            if net_scenario in ["Hemorrhage", "Shock", "Arrest"]:
                self.target_icp = 4.0  # BP crashes, so brain pressure drops
            elif net_scenario == "Healthy":
                self.target_icp = 10.0

        # 3. READ HEART RATE FROM NETWORK (Owned by ECG)
        net_hr = self.patient.get("hr")
        current_hr = net_hr if net_hr is not None else 75.0

        # Step the ICP pressure
        self.current_icp += (self.target_icp - self.current_icp) * (dt * 0.05)

        # 4. PUBLISH ICP TO NETWORK (Owned by NEURO)
        self.patient.update(source="NEURO", vital="icp", value=round(self.current_icp, 1))

        # Waveform math relies on the global Heart Rate!
        beat_duration = 60.0 / max(0.1, current_hr)
        time_in_beat = self.time_passed % beat_duration
        t_relative = time_in_beat - (beat_duration * 0.2)

        p1_amp = 4.0
        p2_amp = 2.0
        p3_amp = 1.0

        # PATHOLOGY MATH: As pressure rises, brain compliance drops.
        if self.current_icp > 15.0:
            severity = (self.current_icp - 15.0) / 10.0
            p2_amp = 2.0 + (severity * 5.0)

        # Synthesize the waveform using multi-dimensional Gaussian curves
        wave = 0.0
        wave += p1_amp * math.exp(-((t_relative - 0.05) ** 2) / (2 * 0.03 ** 2))
        wave += p2_amp * math.exp(-((t_relative - 0.15) ** 2) / (2 * 0.04 ** 2))
        wave += p3_amp * math.exp(-((t_relative - 0.25) ** 2) / (2 * 0.03 ** 2))

        resp_wander = 2.0 * math.sin(self.time_passed * 0.3)
        final_pressure = self.current_icp + wave + resp_wander + random.gauss(0, 0.3)

        return {
            "mean_icp": round(self.current_icp, 1),
            "waveform": round(final_pressure, 2),
            "simulated_hr": round(current_hr, 1)
        }