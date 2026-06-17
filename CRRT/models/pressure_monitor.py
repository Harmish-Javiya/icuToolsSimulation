import random


class PressureMonitor:

    def __init__(self):

        self.access_pressure = -120

        self.return_pressure = 100

        self.filter_pressure = 180

        self.tmp = (
            self.filter_pressure -
            self.return_pressure
        )

    def update(self):

        self.access_pressure += random.randint(-5, 5)

        self.return_pressure += random.randint(-5, 5)

        self.filter_pressure += random.randint(-5, 5)

        self.tmp = (
            self.filter_pressure -
            self.return_pressure
        )

    def get_pressure_data(self):

        return {
            "Access Pressure":
                self.access_pressure,

            "Return Pressure":
                self.return_pressure,

            "Filter Pressure":
                self.filter_pressure,

            "TMP":
                self.tmp
        }