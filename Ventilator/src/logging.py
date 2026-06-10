import csv
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataLogger:
    """
    Handles real-time streaming of ventilator and patient data to a CSV file.
    This prevents memory leaks during long simulations and allows for playback/review.
    """

    def __init__(self, filepath: str = "data/simulation_logs.csv"):
        self.filepath = filepath
        # Define the columns we want to save
        self.headers = [
            "Time_s",
            "Mode",
            "Phase",
            "Flow_L_s",
            "Pressure_cmH2O",
            "Volume_L",
            "SpO2_Percent",
            "Lung_Compliance",
            "Airway_Resistance",
            "Active_Alarms"
        ]
        self._initialize_file()

    def _initialize_file(self):
        """Creates the data directory if it doesn't exist and writes the CSV headers."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        with open(self.filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
        logger.info(f"DataLogger initialized. Writing data to: {self.filepath}")

    def log_step(self, current_time: float, vent_mode: str, breath_phase: str,
                 applied_flow: float, patient_state: dict, active_alarms: list):
        """
        Appends a single "tick" of simulation data to the CSV file.
        """
        # Format the alarms list into a single readable string
        alarms_str = " | ".join(active_alarms) if active_alarms else "None"

        row = [
            round(current_time, 2),
            vent_mode,
            breath_phase,
            round(applied_flow, 3),
            patient_state["pressure"],
            patient_state["volume"],
            patient_state["spo2"],
            patient_state["compliance"],
            patient_state["resistance"],
            alarms_str
        ]

        # Append mode ('a') ensures we add to the end of the file without overwriting
        with open(self.filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)