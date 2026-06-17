import math
import random
import logging

logger = logging.getLogger(__name__)

class ICPEngine:
    def __init__(self, base_icp: float = 10.0, simulated_hr: float = 75.0):
        self.target_icp = base_icp
        self.current_icp = base_icp
        self.target_hr = simulated_hr
        self.current_hr = simulated_hr
        self.time_passed = 0.0

    def apply_intervention(self, scenario: str) -> None:
        if scenario == "normal_neuro":
            self.target_icp = 10.0
            self.target_hr = 75.0
        elif scenario == "mild_swelling":
            self.target_icp = 18.0  # Just below the critical alarm threshold
            self.target_hr = 65.0   # Heart rate starting to drop
        elif scenario == "brain_swelling":
            self.target_icp = 35.0  # Massive, lethal herniation
            self.target_hr = 45.0   # Severe Cushing's Bradycardia
        elif scenario == "treatment_hyperventilation":
            # Medical treatment: Hyperventilating the patient blows off CO2,
            # shrinking blood vessels in the brain and rapidly dropping ICP.
            self.target_icp = 12.0
            self.target_hr = 85.0
        elif scenario == "treatment_drain_csf":
            # Physically opening a valve to let fluid out (Instant physical relief)
            self.target_icp = 8.0  # Drops below normal baseline
            self.target_hr = 75.0  # Heart rate normalizes
        elif scenario == "treatment_mannitol":
            # IV Drug that acts as a sponge, pulling water out of brain cells (Gradual)
            self.target_icp = 14.0  # Safe, but slightly elevated
            self.target_hr = 80.0

    def set_targets(self, target_icp: float, target_hr: float) -> None:
        """Allows direct manual override from the UI sliders."""
        self.target_icp = target_icp
        self.target_hr = target_hr

    def step(self, dt: float) -> dict:
        self.time_passed += dt

        self.current_icp += (self.target_icp - self.current_icp) * (dt * 0.05)
        self.current_hr += (self.target_hr - self.current_hr) * (dt * 0.05)

        beat_duration = 60.0 / max(0.1, self.current_hr)
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
            "simulated_hr": round(self.current_hr, 1)
        }