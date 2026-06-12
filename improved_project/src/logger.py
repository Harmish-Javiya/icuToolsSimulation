import csv
import os
from datetime import datetime


class DataLogger:

    def __init__(self,
                 filename="Data/logs.csv"):

        self.filename = filename

        self.ensure_file()

    ##################################

    def ensure_file(self):

        folder = os.path.dirname(
            self.filename
        )

        if folder and not os.path.exists(folder):

            os.makedirs(folder)

        if not os.path.exists(self.filename):

            with open(

                self.filename,

                "w",

                newline=""

            ) as f:

                writer = csv.writer(f)

                writer.writerow([

                    "Timestamp",

                    "Event",

                    "Rhythm",

                    "HeartRate",

                    "Energy",

                    "Battery",

                    "Alarm"

                ])

    ##################################

    def log_event(

        self,

        event,

        device,

        patient,

        alarm

    ):

        with open(

            self.filename,

            "a",

            newline=""

        ) as f:

            writer = csv.writer(f)

            writer.writerow([

                datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                ),

                event,

                patient.rhythm.value,

                patient.heart_rate,

                device.energy,

                device.battery,

                alarm.get_alarm()

            ])

    ##################################

    def count(self):

        with open(

            self.filename,

            "r"

        ) as f:

            return max(

                0,

                sum(1 for _ in f) - 1

            )