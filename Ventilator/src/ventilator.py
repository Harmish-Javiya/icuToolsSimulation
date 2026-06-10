import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VentilatorEngine:
    """
    Simulates the mechanical ventilator control system.
    Manages breath timing, ventilation modes, and flow delivery.
    """

    def __init__(self):
        # --- Default Ventilator Settings ---
        self.mode = "VCV"  # Volume Control Ventilation (default)
        self.rr = 15.0  # Respiratory Rate (breaths per minute)
        self.vt = 0.500  # Tidal Volume (Liters) - Used in VCV
        self.target_pressure = 20.0  # Target Pressure (cmH2O) - Used in PCV
        self.peep = 5.0  # Positive End-Expiratory Pressure (cmH2O)
        self.fio2 = 0.21  # Fraction of Inspired Oxygen (21% Room Air)
        self.ie_ratio = 2.0  # I:E Ratio (e.g., 2.0 means 1:2)
        self.max_pressure_limit = 40.0

        # --- Timing & State Variables ---
        self.time_in_breath = 0.0
        self.breath_phase = "Expiration"  # 'Inspiration' or 'Expiration'
        self.trigger_sensitivity = 2.0

    def update_settings(self, **kwargs) -> None:
        """Safely update ventilator settings from the UI."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"Setting updated: {key} = {value}")
            else:
                logger.warning(f"Attempted to set unknown parameter: {key}")

    def step(self, dt: float, patient_state: dict) -> float:
        """
        Advances the ventilator state by 'dt' seconds.
        Calculates the required flow to send to the patient engine.

        Args:
            dt: Time step in seconds.
            patient_state: Dictionary of the patient's current vitals.

        Returns:
            applied_flow (float): The calculated flow rate (L/s) to send to the patient.
        """
        self.time_in_breath += dt

        # 1. Calculate Breath Timing
        breath_period = 60.0 / self.rr
        inspiratory_time = breath_period / (1 + self.ie_ratio)

        # 2. Phase Switching & Patient Triggering (Assist-Control)
        # Did the patient drop the pressure enough to trigger a breath?
        patient_effort_detected = patient_state["pressure"] < (self.peep - self.trigger_sensitivity)

        if self.breath_phase == "Expiration":
            # Start inhalation IF the machine timer runs out OR the patient asks for it
            if self.time_in_breath >= breath_period or patient_effort_detected:
                self.breath_phase = "Inspiration"
                self.time_in_breath = 0.0  # Reset the clock for the new breath!

                if patient_effort_detected:
                    logger.info("🟢 Patient Triggered Breath Detected!")

        elif self.breath_phase == "Inspiration":
            # Switch back to exhalation when inspiratory time is met
            if self.time_in_breath >= inspiratory_time:
                self.breath_phase = "Expiration"

        # 3. Calculate Flow based on Phase and Mode
        if self.breath_phase == "Inspiration":

            # --- ADD THIS SAFETY CHECK FIRST ---
            # Simulate a mechanical pressure relief valve
            if patient_state["pressure"] >= self.max_pressure_limit:
                logger.warning("Ventilator pop-off valve activated! Flow dumped to room.")
                return 0.0  # Immediately stop pushing air into the patient
            # -----------------------------------

            if self.mode == "VCV":
                # Volume Control: Constant flow to deliver Vt within Ti
                flow = self.vt / inspiratory_time
                return flow

            elif self.mode == "PCV":
                # Pressure Control: Fast initial flow that tapers off as pressure is reached
                pressure_diff = self.target_pressure - patient_state["pressure"]
                # Simple proportional controller for pressure
                flow = max(0.0, pressure_diff * 0.2)
                return flow

        else:
            # Expiration Phase: Ventilator stops pushing air.
            # Exhalation is passive, driven by the patient's lung compliance and resistance.
            # Time Constant (RC) = Compliance * Resistance
            rc_time_constant = patient_state["compliance"] * patient_state["resistance"]

            # Flow is negative during exhalation
            flow = -(patient_state["volume"]) / rc_time_constant

            # If volume drops to 0 (meaning we hit PEEP), flow stops
            if patient_state["volume"] <= 0.001:
                flow = 0.0

            return flow