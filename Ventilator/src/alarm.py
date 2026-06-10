import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AlarmSystem:
    """
    Evaluates real-time respiratory parameters against configured safety limits.
    Generates and tracks active alarms.
    """

    def __init__(self):
        # Default Safety Thresholds
        self.limits = {
            "high_pressure": 35.0,  # cmH2O
            "low_pressure": 4.0,  # cmH2O (Usually indicates a tube disconnect)
            "low_spo2": 90.0,  # %
            "apnea_time": 15.0  # Seconds without airflow
        }

        self.active_alarms = set()
        self.apnea_timer = 0.0

    def update_limits(self, **kwargs):
        """Allows the user/clinician to adjust alarm thresholds."""
        for key, value in kwargs.items():
            if key in self.limits:
                self.limits[key] = value
                logger.info(f"Alarm Limit Updated: {key} = {value}")

    def evaluate(self, dt: float, patient_state: dict, breath_phase: str) -> list:
        """
        Evaluates the current state against limits and updates active alarms.

        Args:
            dt: Time step in seconds.
            patient_state: Dict from PatientEngine.get_state().
            breath_phase: Current phase from VentilatorEngine ('Inspiration' or 'Expiration').

        Returns:
            A list of currently active alarm strings.
        """
        current_alarms = set()

        # 1. High Airway Pressure Alarm
        if patient_state["pressure"] >= self.limits["high_pressure"]:
            current_alarms.add("HIGH AIRWAY PRESSURE")

        # 2. Low Airway Pressure (Circuit Disconnect)
        # We only evaluate this during Inspiration to avoid false alarms during passive Expiration
        if breath_phase == "Inspiration" and patient_state["pressure"] < self.limits["low_pressure"]:
            current_alarms.add("LOW PRESSURE (DISCONNECT)")

        # 3. Apnea Alarm (No airflow detected)
        # If flow is near zero, accumulate time. Otherwise, reset the timer.
        if abs(patient_state["flow"]) < 0.05:
            self.apnea_timer += dt
        else:
            self.apnea_timer = 0.0

        if self.apnea_timer >= self.limits["apnea_time"]:
            current_alarms.add("APNEA DETECTED")

        # 4. Low Oxygen Alarm
        if patient_state["spo2"] <= self.limits["low_spo2"]:
            current_alarms.add("CRITICAL LOW SpO2")

        # --- Logging New & Resolved Alarms ---
        new_alarms = current_alarms - self.active_alarms
        resolved_alarms = self.active_alarms - current_alarms

        for alarm in new_alarms:
            logger.error(f"ALARM TRIGGERED: {alarm} !!!")

        for alarm in resolved_alarms:
            logger.info(f"Alarm Cleared: {alarm}")

        self.active_alarms = current_alarms
        return list(self.active_alarms)