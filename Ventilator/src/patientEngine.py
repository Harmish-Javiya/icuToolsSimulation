import logging
import random
import math
from core.central_patient_engine import CentralPatientEngine

# Configure basic logging for the backend engine
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PatientEngine:
    """
    Simulates the respiratory mechanics and physiological state of a patient
    connected to a mechanical ventilator.
    """

    def __init__(self, patient_type: str = "Adult"):
        # --- Baseline Physiological Properties ---
        if patient_type.lower() == "adult":
            self.baseline_compliance = 0.05  # C: L/cmH2O
            self.baseline_resistance = 5.0  # R: cmH2O/L/s
            self.target_spo2 = 98.0  # Ideal SpO2 (%)
        elif patient_type.lower() == "pediatric":
            self.baseline_compliance = 0.015
            self.baseline_resistance = 20.0
            self.target_spo2 = 97.0
        else:
            raise ValueError("patient_type must be 'Adult' or 'Pediatric'")

        # --- Current Active Properties ---
        self.compliance = self.baseline_compliance
        self.resistance = self.baseline_resistance
        self.patient = CentralPatientEngine()
        self.spo2 = self.patient.get("spo2") if self.patient.get("spo2") is not None else 98.0
        self.fio2 = 0.21

        # --- Live State Variables ---
        self.current_volume = 0.0  # Volume above FRC/PEEP (Liters)
        self.current_flow = 0.0  # Airflow rate (Liters/second)
        self.airway_pressure = 0.0  # Paw (cmH2O)
        self.peep = 5.0  # Baseline PEEP from ventilator

        # --- Phase 4: Spontaneous Breathing Variables ---
        self.spont_rr = 12.0  # Patient's independent respiratory drive (breaths/min)
        self.patient_time = 0.0
        self.muscle_pressure = 0.0

    def apply_intervention(self, situation: str) -> None:
        """
        Dynamically alters lung mechanics to simulate clinical events or medications.
        """
        situation = situation.lower()
        if situation == "albuterol":
            self.resistance = self.baseline_resistance * 0.60
            logger.info("Intervention: Albuterol given. Resistance decreased.")

        elif situation == "bronchospasm":
            self.resistance = self.baseline_resistance * 4.0
            logger.warning("Condition: Severe bronchospasm! Resistance spiked.")

        elif situation == "ards":
            self.compliance = self.baseline_compliance * 0.30
            logger.warning("Condition: ARDS progression. Lungs are stiffening (Low Compliance).")

        elif situation == "surfactant":
            self.compliance = min(self.baseline_compliance * 1.5, 0.08)
            logger.info("Intervention: Surfactant administered. Compliance improved.")

        elif situation == "reset":
            self.compliance = self.baseline_compliance
            self.resistance = self.baseline_resistance
            logger.info("State Reset: Patient returned to baseline mechanics.")
        else:
            logger.error(f"Unknown intervention: {situation}")

    def update_physics(self, applied_flow: float, dt: float, ventilator_peep: float) -> None:
        """
        Steps the simulation forward by 'dt' seconds using the Equation of Motion.
        """
        self.peep = ventilator_peep
        self.current_flow = applied_flow
        self.patient_time += dt

        # ========================================================
        # 0. LISTEN FOR GLOBAL SCENARIO CHANGES
        # ========================================================
        global_scenario = self.patient.get("scenario")

        if global_scenario in ["Sepsis", "Hemorrhage", "Shock", "Fever"]:
            # Patient starts hyperventilating to compensate
            self.spont_rr = 30.0
        elif global_scenario == "Hypoxia" or global_scenario == "ARDS":
            # Lungs instantly stiffen, destroying the SpO2 calculation
            self.compliance = self.baseline_compliance * 0.30
            self.spont_rr = 35.0
        elif global_scenario == "Arrest":
            # Patient stops breathing entirely
            self.spont_rr = 0.0
        elif global_scenario == "Healthy":
            # Reset to baseline
            self.spont_rr = 12.0
            self.compliance = self.baseline_compliance

        # 1. Update lung volume (Integral of flow)
        self.current_volume += self.current_flow * dt

        # Prevent volume from dropping below zero (cannot empty lungs past PEEP)
        if self.current_volume < 0:
            self.current_volume = 0.0
            self.current_flow = 0.0

        # --- Phase 4: Simulate Diaphragm Effort ---
        spont_breath_period = 60.0 / self.spont_rr if self.spont_rr > 0 else 9999
        time_in_spont_cycle = self.patient_time % spont_breath_period

        # Patient pulls a negative pressure (-2.5 cmH2O) for 1 second to try and inhale
        if time_in_spont_cycle < 1.0:
            self.muscle_pressure = -2.5 * math.sin(time_in_spont_cycle * math.pi)
        else:
            self.muscle_pressure = 0.0

        # 2. Equation of Motion: Paw = (V/C) + (R * F) + PEEP + Muscle_Effort
        elastic_pressure = self.current_volume / self.compliance
        resistive_pressure = self.resistance * self.current_flow

        # The muscle pressure drops the airway pressure, which the ventilator can detect!
        self.airway_pressure = elastic_pressure + resistive_pressure + self.peep + self.muscle_pressure

        # 3. Dynamic SpO2 Estimation (UNIFIED LUNG HEALTH LOGIC)
        # Calculate a health factor for both compliance (stretch) and resistance (airways)
        compliance_health = self.compliance / self.baseline_compliance  # Normal = 1.0
        resistance_health = self.baseline_resistance / self.resistance  # Normal = 1.0

        # Overall lung health combines both (Normal = 1.0. Sick lungs drop toward 0.1)
        lung_health = compliance_health * resistance_health

        # Base oxygen delivery power based on settings
        # Room air (21%) + PEEP of 5 = ~26 baseline delivery power
        oxygen_delivery = (self.fio2 * 100) + ventilator_peep

        # Calculate target SpO2 based on health and delivery
        # If health is 1.0, base is 90% + 7.8% (from delivery) = ~98% SpO2
        target_spo2 = 70.0 + (lung_health * 20.0) + (oxygen_delivery * 0.3)

        if global_scenario in ["Hemorrhage", "Shock"]:
            target_spo2 -= 15.0  # Massive blood loss destroys oxygen delivery!
        elif global_scenario in ["Sepsis", "Fever"]:
            target_spo2 -= 4.0  # High fever burns up oxygen
        elif global_scenario == "Heart Failure":
            target_spo2 -= 8.0  # Fluid backs up into the lungs

        # Cap target at 100%
        target_spo2 = min(100.0, target_spo2)

        # ========================================================
        # 4. CROSS-MODULE PHYSIOLOGY: PERFUSION & CARDIAC ARREST
        # ========================================================
        net_hr = self.patient.get("hr")

        if net_hr is not None:
            if net_hr <= 5.0:
                # Cardiac Arrest: Blood is completely stagnant. SpO2 instantly crashes to 0.
                target_spo2 = 0.0
            elif net_hr < 50.0:
                # Severe Bradycardia: The heart isn't moving enough blood to the lungs.
                # For every beat the HR drops below 50, the SpO2 loses its ability to stay at 100%
                perfusion_penalty = (50.0 - net_hr) * 0.5
                target_spo2 -= perfusion_penalty

        # Smoothly slide the current SpO2 toward the target over time
        spo2_error = target_spo2 - self.spo2

        # Add a penalty if pressures are dangerously high (barotrauma blocks blood flow)
        if self.airway_pressure > 40.0:
            self.spo2 -= (1.0 * dt)
        else:
            self.spo2 += spo2_error * (dt * 0.2)

        # Allow SpO2 to drop all the way to 0.0 if the heart stops!
        self.spo2 = max(0.0, min(100.0, self.spo2))

        # Update global patient state
        self.patient.update(
            source="VENT",
            vital="spo2",
            value=round(self.spo2, 1)
        )

    def get_state(self) -> dict:
        """
        Returns a dictionary of the patient's current vital statistics.
        """
        # Add slight Gaussian noise to simulate sensor inaccuracy & cardiac oscillations
        p_noise = random.gauss(0, 0.3) if self.airway_pressure > 0 else 0
        f_noise = random.gauss(0, 0.02)

        return {
            "pressure": round(max(0.0, self.airway_pressure + p_noise), 2),
            "volume": round(self.current_volume, 3),
            "flow": round(self.current_flow + f_noise, 2),
            "spo2": round(self.spo2, 1),
            "compliance": round(self.compliance, 4),
            "resistance": round(self.resistance, 2)
        }


if __name__ == "__main__":
    # A quick standalone test to verify the file works when run directly
    patient = PatientEngine("Adult")
    logger.info("Testing PatientEngine initialization...")
    logger.info(f"Initial State: {patient.get_state()}")

    # Simulate 1 second of constant flow
    for _ in range(10):
        patient.update_physics(applied_flow=0.5, dt=0.1, ventilator_peep=5.0)

    logger.info(f"State after 1s of 0.5 L/s flow: {patient.get_state()}")

    central = CentralPatientEngine()
    print("Global SpO2:", central.get("spo2"))