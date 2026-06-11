import csv
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataLogger:
    def __init__(self, log_dir="data"):
        self.log_dir = log_dir

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = os.path.join(self.log_dir, f"icp_telemetry_{timestamp}.csv")

        try:
            with open(self.filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Time_Sec",
                    "Simulated_HR",
                    "Mean_ICP",
                    "Waveform_Value",
                    "Clinical_Status",
                    "Active_Alarms"
                ])
            logger.info(f"ICP Telemetry logger initialized: {self.filepath}")
        except Exception as e:
            logger.error(f"Failed to initialize ICP logger: {e}")

    def log_step(self, time_sec: float, sim_hr: float, mean_icp: float, waveform: float, status: str, alarms: list) -> None:
        alarm_str = " | ".join(alarms) if alarms else "NONE"

        try:
            with open(self.filepath, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    round(time_sec, 3),
                    round(sim_hr, 1),
                    round(mean_icp, 1),
                    round(waveform, 3),
                    status,
                    alarm_str
                ])
        except Exception as e:
            logger.error(f"Failed to write to ICP log: {e}")