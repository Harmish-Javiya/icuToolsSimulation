import math
import random


class ECG:

    def __init__(self):
        self.t = 0
        self.step = 0.1

    def next_sample(self, rhythm):

        self.t += self.step

        r = rhythm.value

        if r == "Normal Sinus":

            return (
                math.sin(self.t * 2)
                + 0.2 * math.sin(self.t * 8)
            )

        elif r == "Ventricular Fibrillation":

            return random.uniform(-2, 2)

        elif r == "Ventricular Tachycardia":

            return math.sin(self.t * 8)

        elif r == "SVT":

            return 0.8 * math.sin(self.t * 6)

        elif r == "Bradycardia":

            return math.sin(self.t)

        elif r == "Tachycardia":

            return math.sin(self.t * 4)

        elif r == "PEA":

            return 0.3 * math.sin(self.t * 2)

        elif r == "Asystole":

            return random.uniform(-0.02, 0.02)

        return 0

    def get_samples(self, rhythm, count=20):

        data = []

        for _ in range(count):
            data.append(
                round(
                    self.next_sample(rhythm),
                    3
                )
            )

        return data