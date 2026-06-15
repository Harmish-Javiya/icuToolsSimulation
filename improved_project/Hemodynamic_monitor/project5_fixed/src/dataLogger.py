import csv
import os


class DataLogger:

    def __init__(self):

        self.filename = "patient_log.csv"

        if not os.path.exists(self.filename):

            with open(self.filename, "w", newline="") as f:

                writer = csv.writer(f)

                writer.writerow([
                    "HR",
                    "SBP",
                    "DBP",
                    "MAP",
                    "CO",
                    "SV",
                    "CVP",
                    "RR",
                    "SpO2",
                    "Scenario",
                    "Alarm"
                ])

    def log(self, data):

        with open(self.filename, "a", newline="") as f:

            writer = csv.writer(f)

            writer.writerow([
                data["HR"],
                data["SBP"],
                data["DBP"],
                data["MAP"],
                data["CO"],
                data["SV"],
                data["CVP"],
                data["RR"],
                data["SpO2"],
                data["Scenario"],
                data["Alarm"]
            ])