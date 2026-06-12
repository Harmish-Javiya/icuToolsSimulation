import matplotlib.pyplot as plt


class RealtimeGraphs:

    def __init__(self):

        plt.ion()

        self.times = []

        self.hr_values = []

        self.tmp_values = []

        self.k_values = []

        self.filter_values = []

        self.figure = plt.figure(
            figsize=(10, 6)
        )

    def update(
        self,
        step,
        patient,
        pressure,
        filter_obj
    ):

        self.times.append(step)

        self.hr_values.append(
            patient.hr
        )

        self.tmp_values.append(
            pressure.tmp
        )

        self.k_values.append(
            patient.potassium
        )

        self.filter_values.append(
            filter_obj.health
        )

        plt.clf()

        plt.subplot(2, 2, 1)
        plt.title("Heart Rate")
        plt.plot(
            self.times,
            self.hr_values
        )

        plt.subplot(2, 2, 2)
        plt.title("TMP")
        plt.plot(
            self.times,
            self.tmp_values
        )

        plt.subplot(2, 2, 3)
        plt.title("Potassium")
        plt.plot(
            self.times,
            self.k_values
        )

        plt.subplot(2, 2, 4)
        plt.title("Filter Health")
        plt.plot(
            self.times,
            self.filter_values
        )

        plt.tight_layout()

        plt.pause(0.01)