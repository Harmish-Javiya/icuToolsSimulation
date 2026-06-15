import csv
import os


class Logger:

    def __init__(self):

        os.makedirs("Data", exist_ok=True)

        self.filename = os.path.join(
            "Data",
            "simulation_logs.csv"
        )

        if not os.path.exists(self.filename):

            with open(self.filename, "w", newline="") as f:

                writer = csv.writer(f)

                writer.writerow([
                    "Time",
                    "SpO2",
                    "Pulse",
                    "Temperature",
                    "Alarm"
                ])

    def log(self, timestamp, data, alarms):

        with open(self.filename, "a", newline="") as f:

            writer = csv.writer(f)

            writer.writerow([
                timestamp,
                data["spo2"],
                data["heart_rate"],
                data["temperature"],
                ",".join(alarms)
            ])