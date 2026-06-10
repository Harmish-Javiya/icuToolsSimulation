import csv
import os
import logging

logger = logging.getLogger(__name__)

class DataLogger:
    """Streams multi-parameter ECG telemetry to a CSV file."""

    def __init__(self, filepath: str = "data/ecg_telemetry.csv"):
        self.filepath = filepath
        self.headers = [
            "Time_s",
            "Heart_Rate_BPM",
            "Lead_II_mV",
            "Lead_V1_mV",
            "Lead_V6_mV",
            "Lead_aVR_mV",
            "Active_Rhythm",
            "Active_Alarms"
        ]
        self._initialize_file()

    def _initialize_file(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
        logger.info(f"ECG DataLogger initialized: {self.filepath}")

    def log_step(self, current_time: float, hr: float, voltages: dict, rhythm: str, alarms: list):
        alarms_str = " | ".join(alarms) if alarms else "None"
        row = [
            round(current_time, 2),
            round(hr, 1),
            voltages.get("Lead II", 0.0),
            voltages.get("Lead V1", 0.0),
            voltages.get("Lead V6", 0.0),
            voltages.get("Lead aVR", 0.0),
            rhythm,
            alarms_str
        ]
        with open(self.filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)